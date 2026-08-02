#!/usr/bin/env bash
#
# Verificação semanal de saúde e segurança dos sites.
#
# Existe por causa de um caso real: ao ligar o proxy do Cloudflare, a
# plataforma passou a injetar um script de terceiros nas páginas sem aviso.
# Só foi descoberto por acaso, durante um teste. Este script transforma
# aquela descoberta acidental em verificação contínua.
#
# Roda tanto local quanto no GitHub Actions. Imprime um relatório em
# Markdown e retorna diferente de zero se algo regrediu.
#
set -uo pipefail

BLOG="${BLOG:-https://dozeroaobasico.com.br}"
ARCADE="${ARCADE:-https://arcade.dozeroaobasico.com.br}"
DOMINIO="${DOMINIO:-dozeroaobasico.com.br}"
DIAS_ALERTA_DOMINIO="${DIAS_ALERTA_DOMINIO:-45}"

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
ACCEPT='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

falhas=0
alertas=0

falha() { echo "- ❌ **$1**"; falhas=$((falhas + 1)); }
alerta() { echo "- ⚠️ $1"; alertas=$((alertas + 1)); }
ok()    { echo "- ✅ $1"; }

pega() { curl -s --max-time 30 -A "$UA" -H "Accept: $ACCEPT" "$1"; }
codigo() { curl -s -o /dev/null -w '%{http_code}' --max-time 30 -A "$UA" "$1"; }

echo "# Verificação semanal"
echo
echo "Executada em $(date -u '+%Y-%m-%d %H:%M UTC')."
echo

# ---------------------------------------------------------------------------
echo "## 1. Disponibilidade"
echo
for alvo in "$BLOG" "$ARCADE"; do
  c=$(codigo "$alvo/")
  [[ "$c" == "200" ]] && ok "\`$alvo\` responde 200" \
                      || falha "\`$alvo\` respondeu $c"
done
echo

# ---------------------------------------------------------------------------
echo "## 2. Páginas principais"
echo
POSTS=(start hoaxshell Villain Osint_Recon Pentest Modelagem defect_dojo SCRCPY xmlrpc)
quebrados=0
for p in "${POSTS[@]}"; do
  [[ "$(codigo "$BLOG/posts/$p/")" == "200" ]] || { quebrados=$((quebrados + 1)); echo "  - \`/posts/$p/\` fora do ar"; }
done
[[ "$quebrados" -eq 0 ]] && ok "os ${#POSTS[@]} posts respondem 200" \
                         || falha "$quebrados post(s) fora do ar"

JOGOS=(captain-america-and-the-avengers super-mario-world tmnt-4-turtles-in-time top-gear-2)
quebrados=0
for j in "${JOGOS[@]}"; do
  [[ "$(codigo "$ARCADE/games/$j/")" == "200" ]] || { quebrados=$((quebrados + 1)); echo "  - \`/games/$j/\` fora do ar"; }
done
[[ "$quebrados" -eq 0 ]] && ok "os ${#JOGOS[@]} jogos respondem 200" \
                         || falha "$quebrados jogo(s) fora do ar"

# A capitalização importa: o GitHub Pages diferencia maiúsculas.
[[ "$(codigo "$ARCADE/roms/TopGear2.sfc")" == "200" ]] \
  && ok "ROM \`TopGear2.sfc\` acessível com a capitalização correta" \
  || falha "ROM \`TopGear2.sfc\` inacessível"
echo

# ---------------------------------------------------------------------------
echo "## 3. Cabeçalhos de segurança"
echo
verifica_cabecalhos() {
  local alvo="$1"; shift
  local esperados=("$@")
  local cab
  cab=$(curl -sI --max-time 30 -A "$UA" "$alvo/" | tr 'A-Z' 'a-z')
  local ausentes=()
  for h in "${esperados[@]}"; do
    grep -q "^${h}:" <<< "$cab" || ausentes+=("$h")
  done
  if [[ ${#ausentes[@]} -eq 0 ]]; then
    ok "\`$alvo\` com todos os ${#esperados[@]} cabeçalhos"
  else
    falha "\`$alvo\` sem: $(IFS=', '; echo "${ausentes[*]}")"
  fi
}

BASE_HEADERS=(strict-transport-security x-frame-options x-content-type-options
              referrer-policy permissions-policy)
verifica_cabecalhos "$BLOG" "${BASE_HEADERS[@]}"
verifica_cabecalhos "$ARCADE" "${BASE_HEADERS[@]}" \
  cross-origin-opener-policy cross-origin-embedder-policy cross-origin-resource-policy
echo

# ---------------------------------------------------------------------------
echo "## 4. Scripts e recursos de terceiros"
echo
# Domínios que podem aparecer legitimamente em links de navegação.
PERMITIDOS='dozeroaobasico\.com\.br|github\.com|youtube\.com|instagram\.com|tiktok\.com|sitemaps\.org|w3\.org|aws\.amazon\.com|osv\.dev'

for alvo in "$BLOG" "$ARCADE"; do
  # Só tags que CARREGAM recurso. Link de navegação (<a href>) aponta para
  # fora por natureza e não significa que o site executa código de terceiro.
  externos=$(pega "$alvo/" \
    | grep -oE '<(script|link|img|iframe|source|video|audio|embed|object)[^>]+>' \
    | grep -oE '(src|href)="https?://[^"]+"' \
    | sed -E 's/^(src|href)="//; s/"$//' \
    | grep -vE "$PERMITIDOS" \
    | sed -E 's#^(https?://[^/]+).*#\1#' \
    | sort -u)
  if [[ -z "$externos" ]]; then
    ok "\`$alvo\` sem recursos de domínio inesperado"
  else
    falha "\`$alvo\` carregando de terceiros:"
    while IFS= read -r e; do echo "  - \`$e\`"; done <<< "$externos"
  fi
done
echo

# ---------------------------------------------------------------------------
echo "## 5. Content Security Policy"
echo
for alvo in "$BLOG/posts/Pentest/" "$ARCADE/games/top-gear-2/"; do
  if pega "$alvo" | grep -q 'http-equiv="Content-Security-Policy"'; then
    ok "CSP presente em \`$alvo\`"
  else
    falha "CSP ausente em \`$alvo\`"
  fi
done
echo

# ---------------------------------------------------------------------------
echo "## 6. Certificado TLS"
echo
for host in "${BLOG#https://}" "${ARCADE#https://}"; do
  fim=$(echo | timeout 25 openssl s_client -connect "$host:443" -servername "$host" 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  if [[ -z "$fim" ]]; then
    falha "não foi possível ler o certificado de \`$host\`"
    continue
  fi
  restam=$(( ( $(date -d "$fim" +%s) - $(date +%s) ) / 86400 ))
  if   [[ "$restam" -lt 10 ]]; then falha "certificado de \`$host\` expira em $restam dia(s)"
  elif [[ "$restam" -lt 25 ]]; then alerta "certificado de \`$host\` expira em $restam dias"
  else ok "certificado de \`$host\` válido por mais $restam dias"; fi
done
echo

# ---------------------------------------------------------------------------
echo "## 7. Registro do domínio"
echo
if command -v whois >/dev/null 2>&1; then
  venc=$(whois "$DOMINIO" 2>/dev/null | grep -iE '^expires:' | head -1 | awk '{print $2}')
  if [[ -n "$venc" ]]; then
    iso="${venc:0:4}-${venc:4:2}-${venc:6:2}"
    restam=$(( ( $(date -d "$iso" +%s) - $(date +%s) ) / 86400 ))
    if   [[ "$restam" -lt 15 ]]; then falha "domínio \`$DOMINIO\` expira em $restam dia(s), em $iso"
    elif [[ "$restam" -lt "$DIAS_ALERTA_DOMINIO" ]]; then alerta "domínio \`$DOMINIO\` expira em $restam dias, em $iso"
    else ok "domínio \`$DOMINIO\` válido por mais $restam dias"; fi
  else
    alerta "não foi possível ler a data de expiração de \`$DOMINIO\`"
  fi
else
  alerta "\`whois\` indisponível, expiração do domínio não verificada"
fi
echo

# ---------------------------------------------------------------------------
echo "---"
echo
if [[ "$falhas" -gt 0 ]]; then
  echo "**Resultado: $falhas falha(s) e $alertas alerta(s).**"
  exit 1
fi
if [[ "$alertas" -gt 0 ]]; then
  echo "**Resultado: nenhuma falha, $alertas alerta(s).**"
  exit 0
fi
echo "**Resultado: tudo em ordem.**"
exit 0
