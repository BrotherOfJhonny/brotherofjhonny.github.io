#!/usr/bin/env python3
"""Aplica o rubrico de relevância aos candidatos da semana.

Notas de 0 a 5 por eixo; pesos diferentes por público. A maior nota define
o post da semana E o público-alvo dele.
"""

PESOS = {
    "inicio": {"impacto": 10, "exploracao": 10, "acionabilidade": 15, "novidade": 10,
               "credibilidade": 15, "longevidade": 15, "didatica": 25, "negocio": 0},
    "senior": {"impacto": 15, "exploracao": 20, "acionabilidade": 25, "novidade": 20,
               "credibilidade": 10, "longevidade": 5, "didatica": 0, "negocio": 5},
    "cto":    {"impacto": 25, "exploracao": 20, "acionabilidade": 15, "novidade": 5,
               "credibilidade": 15, "longevidade": 10, "didatica": 5, "negocio": 25},
}

# Notas atribuídas a partir dos metadados coletados (KEV, cobertura,
# credibilidade da fonte) e do tipo de assunto.
CANDIDATOS = [
    {
        "id": "A", "titulo": "Ataque de cadeia de suprimentos no npm (debug, chalk) atribuído a atores norte-coreanos",
        "fonte": "Amazon / BleepingComputer / The Hacker News",
        "notas": {"impacto": 5, "exploracao": 5, "acionabilidade": 5, "novidade": 4,
                  "credibilidade": 4, "longevidade": 5, "didatica": 5, "negocio": 4},
    },
    {
        "id": "B", "titulo": "CVE-2026-20316 — Cisco Secure Firewall Management Center (KEV, prazo federal vencido)",
        "fonte": "CISA KEV",
        "notas": {"impacto": 4, "exploracao": 5, "acionabilidade": 5, "novidade": 2,
                  "credibilidade": 5, "longevidade": 2, "didatica": 2, "negocio": 3},
    },
    {
        "id": "C", "titulo": "VMware — três falhas críticas: bypass de autenticação e escape de VM",
        "fonte": "BleepingComputer / The Hacker News",
        "notas": {"impacto": 5, "exploracao": 2, "acionabilidade": 4, "novidade": 3,
                  "credibilidade": 4, "longevidade": 3, "didatica": 3, "negocio": 4},
    },
    {
        "id": "D", "titulo": "Ator de língua chinesa usa modelos de IA para ataques autônomos",
        "fonte": "Unit 42 (pesquisa primária)",
        "notas": {"impacto": 3, "exploracao": 4, "acionabilidade": 2, "novidade": 5,
                  "credibilidade": 5, "longevidade": 5, "didatica": 3, "negocio": 5},
    },
    {
        "id": "E", "titulo": "Talos IR Trends Q2/2026 — phishing e ferramentas de acesso remoto legítimas",
        "fonte": "Cisco Talos (pesquisa primária)",
        "notas": {"impacto": 4, "exploracao": 4, "acionabilidade": 4, "novidade": 3,
                  "credibilidade": 5, "longevidade": 4, "didatica": 4, "negocio": 4},
    },
    {
        "id": "F", "titulo": "CVE-2025-68686 — Fortinet FortiOS, exposição de informação sensível (KEV, prazo 10/08)",
        "fonte": "CISA KEV",
        "notas": {"impacto": 4, "exploracao": 5, "acionabilidade": 5, "novidade": 2,
                  "credibilidade": 5, "longevidade": 2, "didatica": 2, "negocio": 3},
    },
]


def pontuar(notas, publico):
    p = PESOS[publico]
    total = sum(notas[eixo] * peso for eixo, peso in p.items())
    return round(total / (5 * sum(p.values())) * 100, 1)


if __name__ == "__main__":
    linhas = []
    for c in CANDIDATOS:
        s = {pub: pontuar(c["notas"], pub) for pub in PESOS}
        melhor = max(s, key=s.get)
        linhas.append((max(s.values()), c, s, melhor))
    linhas.sort(reverse=True, key=lambda x: x[0])

    rot = {"inicio": "Início de carreira", "senior": "Sênior", "cto": "CTO"}
    print(f"{'':<3} {'INÍCIO':>7} {'SÊNIOR':>7} {'CTO':>7}  {'VENCE':<20} TÍTULO")
    print("-" * 118)
    for topo, c, s, melhor in linhas:
        print(f"{c['id']:<3} {s['inicio']:>7} {s['senior']:>7} {s['cto']:>7}  "
              f"{rot[melhor]:<20} {c['titulo'][:52]}")
    print("-" * 118)

    topo, c, s, melhor = linhas[0]
    print(f"\nESCOLHIDO: [{c['id']}] {c['titulo']}")
    print(f"Público-alvo: {rot[melhor]}  ({topo} pontos)")
    print(f"Fonte: {c['fonte']}")
    print("\nNotas por eixo:")
    for eixo, nota in c["notas"].items():
        print(f"  {eixo:<16} {'█' * nota}{'░' * (5 - nota)}  {nota}/5")
