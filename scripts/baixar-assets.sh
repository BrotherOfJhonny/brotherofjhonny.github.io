#!/usr/bin/env bash
#
# Baixa para dentro do repositório as bibliotecas e fontes que o tema
# Chirpy carregaria de CDNs externas (jsdelivr e Google Fonts).
#
# Motivo: o blog não deve depender de terceiros nem entregar o IP dos
# visitantes para outros domínios. Com tudo local, a CSP pode ficar
# restrita a 'self'.
#
# Todas as bibliotecas aqui são de licença permissiva, que autoriza a
# redistribuição e a auto-hospedagem:
#   bootstrap, tocbot, glightbox, clipboard.js, dayjs,
#   simple-jekyll-search, loading-attribute-polyfill ... MIT
#   Font Awesome Free ... ícones CC BY 4.0, fontes SIL OFL 1.1, código MIT
#   Lato e Source Sans Pro/3 ......................... SIL OFL 1.1
#
# Rode de novo sempre que atualizar a versão do tema.
#
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
LIB="$RAIZ/assets/lib"
UA_MODERNO="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

baixar() { # url destino
  mkdir -p "$(dirname "$2")"
  curl -fsSL --max-time 120 -o "$2" "$1" || { echo "  ERRO ao baixar $1" >&2; return 1; }
  printf '  %-58s %6s KB\n' "${2#$RAIZ/}" "$(( $(stat -c%s "$2") / 1024 ))"
}

echo "== Bibliotecas (jsDelivr, versões fixadas) =="
baixar "https://cdn.jsdelivr.net/npm/tocbot@4/dist/tocbot.min.css"  "$LIB/tocbot/tocbot.min.css"
baixar "https://cdn.jsdelivr.net/npm/tocbot@4/dist/tocbot.min.js"   "$LIB/tocbot/tocbot.min.js"
baixar "https://cdn.jsdelivr.net/npm/glightbox@3/dist/css/glightbox.min.css" "$LIB/glightbox/glightbox.min.css"
baixar "https://cdn.jsdelivr.net/npm/glightbox@3/dist/js/glightbox.min.js"   "$LIB/glightbox/glightbox.min.js"
baixar "https://cdn.jsdelivr.net/npm/clipboard@2/dist/clipboard.min.js"      "$LIB/clipboard/clipboard.min.js"
baixar "https://cdn.jsdelivr.net/npm/simple-jekyll-search@1/dest/simple-jekyll-search.min.js" \
       "$LIB/simple-jekyll-search/simple-jekyll-search.min.js"
baixar "https://cdn.jsdelivr.net/npm/loading-attribute-polyfill@2/dist/loading-attribute-polyfill.min.css" \
       "$LIB/loading-attribute-polyfill/loading-attribute-polyfill.min.css"
baixar "https://cdn.jsdelivr.net/npm/loading-attribute-polyfill@2/dist/loading-attribute-polyfill.umd.min.js" \
       "$LIB/loading-attribute-polyfill/loading-attribute-polyfill.umd.min.js"

echo
echo "== dayjs (com locale pt) =="
baixar "https://cdn.jsdelivr.net/npm/dayjs@1/dayjs.min.js"                 "$LIB/dayjs/dayjs.min.js"
baixar "https://cdn.jsdelivr.net/npm/dayjs@1/locale/pt.js"                 "$LIB/dayjs/locale/pt.js"
baixar "https://cdn.jsdelivr.net/npm/dayjs@1/plugin/relativeTime.js"       "$LIB/dayjs/plugin/relativeTime.js"
baixar "https://cdn.jsdelivr.net/npm/dayjs@1/plugin/localizedFormat.js"    "$LIB/dayjs/plugin/localizedFormat.js"

echo
echo "== Font Awesome Free (CSS + fontes) =="
FA="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7"
baixar "$FA/css/all.min.css" "$LIB/fontawesome-free/css/all.min.css"
for f in fa-solid-900 fa-regular-400 fa-brands-400; do
  baixar "$FA/webfonts/$f.woff2" "$LIB/fontawesome-free/webfonts/$f.woff2" || true
done

echo
echo "== Fontes de texto (Lato e Source Sans 3, SIL OFL) =="
CSS_URL="https://fonts.googleapis.com/css2?family=Lato:wght@300;400&family=Source+Sans+3:wght@400;600;700;900&display=swap"
TMP="$(mktemp)"
curl -fsSL --max-time 60 -A "$UA_MODERNO" "$CSS_URL" -o "$TMP"

mkdir -p "$LIB/fonts/files"
: > "$LIB/fonts/main.css"

# Baixa cada .woff2 referenciado e reescreve a URL para o caminho local.
mapfile -t URLS < <(grep -oE 'https://fonts\.gstatic\.com/[^)]+\.woff2' "$TMP" | sort -u)
for u in "${URLS[@]}"; do
  nome="$(basename "$u")"
  baixar "$u" "$LIB/fonts/files/$nome" >/dev/null
done
echo "  ${#URLS[@]} arquivo(s) de fonte baixado(s)"

python3 - "$TMP" "$LIB/fonts/main.css" <<'PY'
import re, sys
origem, destino = sys.argv[1], sys.argv[2]
css = open(origem, encoding="utf-8").read()
css = re.sub(r'https://fonts\.gstatic\.com/[^)]+/([^/)]+\.woff2)',
             r'/assets/lib/fonts/files/\1', css)
cabecalho = (
    "/* Fontes auto-hospedadas (SIL OFL 1.1).\n"
    "   Gerado por scripts/baixar-assets.sh a partir da API do Google Fonts.\n"
    "   Nenhuma requisição sai para fonts.googleapis.com ou fonts.gstatic.com. */\n\n"
)
open(destino, "w", encoding="utf-8").write(cabecalho + css)
PY
printf '  %-58s %6s KB\n' "assets/lib/fonts/main.css" "$(( $(stat -c%s "$LIB/fonts/main.css") / 1024 ))"
rm -f "$TMP"

echo
echo "Total: $(du -sh "$LIB" | cut -f1) em assets/lib/"
echo
echo "Confirme que nao restou referencia externa:"
echo "  grep -rn 'jsdelivr\|googleapis\|gstatic' assets/lib/ | grep -v '^Binary'"
