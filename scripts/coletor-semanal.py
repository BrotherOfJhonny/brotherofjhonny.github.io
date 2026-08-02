#!/usr/bin/env python3
"""Coletor semanal de publicações de segurança da informação.

Usa apenas feeds RSS/Atom oficiais e APIs públicas — nunca raspagem de
página, que criaria problema de Termos de Uso e de bloqueio.

A saída é matéria-prima para curadoria: título, link, data e fonte. O texto
dos artigos NÃO é copiado; o post final é análise própria com atribuição
e link para a fonte primária.
"""
import datetime as dt
import json
import re
import sys
from collections import defaultdict

import feedparser
import urllib.request

JANELA_DIAS = 7
AGORA = dt.datetime.now(dt.timezone.utc)

# Fonte -> (url, tipo, peso de credibilidade 1-5)
FONTES = {
    "CISA KEV":            ("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", "kev", 5),
    "SANS ISC":            ("https://isc.sans.edu/rssfeed.xml", "rss", 5),
    "Krebs on Security":   ("https://krebsonsecurity.com/feed/", "rss", 5),
    "Schneier on Security":("https://www.schneier.com/feed/atom/", "rss", 4),
    "Project Zero":        ("https://googleprojectzero.blogspot.com/feeds/posts/default?alt=rss", "rss", 5),
    "Google Security":     ("https://security.googleblog.com/feeds/posts/default?alt=rss", "rss", 5),
    "Cisco Talos":         ("https://feeds.feedburner.com/feedburner/Talos", "rss", 5),
    "Unit 42":             ("https://unit42.paloaltonetworks.com/feed/", "rss", 5),
    "MSRC":                ("https://msrc.microsoft.com/blog/feed", "rss", 5),
    "GitHub Security Lab": ("https://github.blog/tag/github-security-lab/feed/", "rss", 4),
    "PortSwigger":         ("https://portswigger.net/research/rss", "rss", 5),
    "BleepingComputer":    ("https://www.bleepingcomputer.com/feed/", "rss", 3),
    "The Hacker News":     ("https://feeds.feedburner.com/TheHackersNews", "rss", 3),
    "Dark Reading":        ("https://www.darkreading.com/rss.xml", "rss", 3),
    "Ars Technica Sec":    ("https://feeds.arstechnica.com/arstechnica/security", "rss", 3),
}


def recente(entrada):
    for campo in ("published_parsed", "updated_parsed"):
        t = entrada.get(campo)
        if t:
            d = dt.datetime(*t[:6], tzinfo=dt.timezone.utc)
            return d, (AGORA - d).days <= JANELA_DIAS
    return None, False


def coletar_rss(nome, url, cred):
    itens = []
    try:
        f = feedparser.parse(url, agent="PowerArcades-Curadoria/1.0")
        for e in f.entries[:40]:
            data, dentro = recente(e)
            if not dentro:
                continue
            itens.append({
                "fonte": nome, "credibilidade": cred,
                "titulo": (e.get("title") or "").strip(),
                "link": e.get("link") or "",
                "data": data.strftime("%Y-%m-%d") if data else "",
            })
    except Exception as ex:
        print(f"  [!] {nome}: {ex}", file=sys.stderr)
    return itens


def coletar_kev(nome, url, cred):
    """Catálogo de vulnerabilidades exploradas ativamente (domínio público)."""
    itens = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curadoria/1.0"})
        d = json.load(urllib.request.urlopen(req, timeout=45))
        limite = (AGORA - dt.timedelta(days=JANELA_DIAS)).strftime("%Y-%m-%d")
        for v in d.get("vulnerabilities", []):
            if v.get("dateAdded", "") >= limite:
                itens.append({
                    "fonte": nome, "credibilidade": cred,
                    "titulo": f"{v['cveID']} — {v.get('vendorProject','')} {v.get('product','')}: {v.get('vulnerabilityName','')}",
                    "link": f"https://nvd.nist.gov/vuln/detail/{v['cveID']}",
                    "data": v.get("dateAdded", ""),
                    "kev": True,
                    "acao": v.get("requiredAction", ""),
                    "prazo": v.get("dueDate", ""),
                    "ransomware": v.get("knownRansomwareCampaignUse", ""),
                })
    except Exception as ex:
        print(f"  [!] {nome}: {ex}", file=sys.stderr)
    return itens


PARADAS = set("a o e de da do das dos em no na para por com que the and for of to in on with is".split())


def chave(titulo):
    t = re.sub(r"[^\w\s-]", " ", titulo.lower())
    palavras = [p for p in t.split() if len(p) > 3 and p not in PARADAS]
    return set(palavras[:12])


def agrupar(itens):
    """Junta a mesma história noticiada por veículos diferentes."""
    grupos = []
    for it in itens:
        k = chave(it["titulo"])
        alvo = None
        for g in grupos:
            inter = len(k & g["chave"])
            if inter >= 3 and inter / max(1, min(len(k), len(g["chave"]))) >= 0.5:
                alvo = g
                break
        if alvo:
            alvo["itens"].append(it)
            alvo["chave"] |= k
        else:
            grupos.append({"chave": k, "itens": [it]})
    return grupos


if __name__ == "__main__":
    todos = []
    print("Coletando fontes oficiais...", file=sys.stderr)
    for nome, (url, tipo, cred) in FONTES.items():
        itens = coletar_kev(nome, url, cred) if tipo == "kev" else coletar_rss(nome, url, cred)
        print(f"  {nome:<22} {len(itens):>3} item(ns)", file=sys.stderr)
        todos.extend(itens)

    grupos = agrupar(todos)
    grupos.sort(key=lambda g: (len(g["itens"]),
                               max(i["credibilidade"] for i in g["itens"])),
                reverse=True)

    saida = []
    for g in grupos:
        principal = max(g["itens"], key=lambda i: i["credibilidade"])
        saida.append({
            "titulo": principal["titulo"],
            "link": principal["link"],
            "data": principal["data"],
            "fonte_principal": principal["fonte"],
            "veiculos": sorted({i["fonte"] for i in g["itens"]}),
            "cobertura": len(g["itens"]),
            "credibilidade_max": max(i["credibilidade"] for i in g["itens"]),
            "kev": any(i.get("kev") for i in g["itens"]),
            "ransomware": next((i.get("ransomware") for i in g["itens"] if i.get("ransomware")), ""),
            "prazo": next((i.get("prazo") for i in g["itens"] if i.get("prazo")), ""),
        })

    print(f"\nTotal bruto: {len(todos)} | após agrupar: {len(saida)}", file=sys.stderr)
    json.dump(saida, sys.stdout, ensure_ascii=False, indent=1)
