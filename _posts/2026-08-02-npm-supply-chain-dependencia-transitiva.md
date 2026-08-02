---
title: "Você nunca instalou o chalk. Mas ele está no seu projeto."
date: 2026-08-02 10:00:00 -0300
categories: [fundamentos, appsec]
tags: [supply chain, npm, dependencias, devsecops, nodejs, inicio]
description: "A Amazon atribuiu a um grupo norte-coreano uma série de ataques a pacotes npm muito populares. O caso é uma aula sobre dependências transitivas, e sobre por que `npm install` e `npm ci` não são a mesma coisa."
image:
  path: /assets/img/npm-supply-chain/capa.png
  alt: "Árvore de dependências com um nó comprometido"
---

Em 29 de julho de 2026, a Amazon publicou uma análise atribuindo a um grupo
ligado à Coreia do Norte uma série de comprometimentos de pacotes do npm. Entre
eles estão dois nomes que quase ninguém instala de propósito, mas que estão
em praticamente todo projeto Node.js: **`debug`** e **`chalk`**.

Antes de seguir, um ajuste importante, e ele diz muito sobre como consumir
notícia de segurança.

## Isso não é um ataque desta semana

As manchetes dão a entender que houve um incidente novo. Não houve. Olhando a
[publicação original da AWS][aws], a linha do tempo é outra:

| Pacote | Comprometido em |
| --- | --- |
| `typo-crypto` | março de 2025 |
| `debug` e `chalk` | **setembro de 2025** |
| `axios` | março de 2026 |

O que é novo é a **atribuição**: a Amazon conectou esses eventos, que pareciam
isolados, a um mesmo ator, chamado de *Sapphire Sleet*, *BlueNoroff* ou
*Stardust Chollima*, dependendo de quem escreve. E a própria empresa classifica
essa ligação como de **confiança média**, com base em semelhança de técnicas e
de infraestrutura de comando e controle.

Guarde esse detalhe. "Confiança média" não é detalhe burocrático: é o
pesquisador dizendo com honestidade que as evidências apontam para lá, mas não
fecham a conta. Quem lê relatório de ameaça precisa aprender a enxergar isso.

## A parte que interessa a quem está começando

Abra o `package.json` de qualquer projeto Node que você já tenha feito.
Provavelmente `chalk` não está lá. Agora rode:

```bash
npm ls chalk
```

Se o projeto tiver qualquer ferramenta de linha de comando, é bem possível que
apareça algo assim:

```text
meu-projeto@1.0.0
└─┬ alguma-ferramenta@4.2.0
  └─┬ outro-pacote@2.1.0
    └── chalk@4.1.2
```

Você não instalou o `chalk`. Você instalou algo que instalou algo que instalou
o `chalk`. Isso se chama **dependência transitiva**, e é o conceito central
para entender esse tipo de ataque.

Um projeto Node moderno de tamanho médio costuma ter algumas dezenas de
dependências diretas, e **centenas ou milhares** de transitivas. Para ver o
tamanho real da sua árvore:

```bash
# quantos pacotes existem de fato em node_modules
ls node_modules | wc -l

# a árvore inteira, com quem depende de quem
npm ls --all
```

O número costuma assustar na primeira vez. E cada um daqueles pacotes é um
mantenedor que pode ser alvo de engenharia social.

## Como o ataque funcionou

Segundo a AWS, o acesso inicial **não foi por falha técnica**. Foi por
engenharia social contra os mantenedores dos pacotes, ou seja, convencer a pessoa certa
a dar acesso ao repositório. Com o acesso, os atacantes publicaram versões novas
que o ecossistema distribuiu sozinho.

O código malicioso se apoiava em um recurso legítimo do npm: os **post-install
hooks**. São scripts declarados no `package.json` que rodam automaticamente
logo após a instalação:

```json
{
  "scripts": {
    "postinstall": "node ./setup.js"
  }
}
```

Esse recurso existe por bons motivos, como compilar binário nativo, baixar um
runtime. Mas ele significa que **instalar um pacote pode executar código na sua
máquina**, sem você rodar nada.

O payload descrito pela AWS era de múltiplos estágios: ofuscado com XOR e
base64, executando apenas sob condições específicas, buscando um segundo estágio
em servidores de comando e controle, e ajustando o comportamento conforme o
sistema operacional. Isso é desenho deliberado para escapar de análise
automatizada. Um scanner que olha só o conteúdo do pacote não vê o que
realmente vai acontecer.

## O número que resume o problema

O dado mais eloquente do relatório: no episódio do `debug` e do `chalk`,
**cerca de 1 em cada 10 ambientes de nuvem foi afetado em uma janela de duas
horas**.

Duas horas. Não é tempo de reunião, de comitê, de abrir chamado. É o tempo que
o seu pipeline de CI leva para rodar algumas vezes.

Para dar escala: o `axios`, também na lista, tem mais de **100 milhões de
downloads por semana**.

## O que fazer, na prática

### 1. Use `npm ci`, não `npm install`

Essa é a mudança de maior impacto e menor esforço.

```bash
# instala resolvendo versões de novo, pode trazer versão nova
npm install

# instala EXATAMENTE o que está no package-lock.json
npm ci
```

O `npm install` pode atualizar dependências dentro das faixas permitidas
(`^4.1.0` aceita `4.9.0`). O `npm ci` instala o que está travado no lockfile,
e falha se o lockfile estiver dessincronizado. Em CI, **sempre** `npm ci`.

Isso implica versionar o `package-lock.json`. Se ele está no seu `.gitignore`,
tire de lá.

### 2. Desligue os scripts de instalação

Ataca exatamente o vetor usado aqui:

```bash
# pontual
npm ci --ignore-scripts

# para o projeto inteiro
echo "ignore-scripts=true" >> .npmrc
```

**Onde isso dói:** alguns pacotes legítimos precisam do post-install para
funcionar. Os casos clássicos são `esbuild`, `sharp` e drivers nativos.
Ligar isso pode quebrar seu build.

O caminho equilibrado é desligar por padrão e liberar só o que precisa:

```bash
npm rebuild esbuild
```

Não vou dizer que é indolor. É uma troca: um pouco de atrito no build por uma
redução real de superfície de ataque. Vale a pena testar em um projeto antes de
adotar em todos.

### 3. Verifique assinaturas e consulte a base de pacotes maliciosos

```bash
# confere as assinaturas do registro npm
npm audit signatures

# vulnerabilidades conhecidas
npm audit
```

Este caso está catalogado na base [OSV][osv] sob o identificador
`MAL-2026-3400`. Vale conhecer a OSV: ela indexa **pacotes maliciosos**, não só
vulnerabilidades, categorias diferentes, e o `npm audit` sozinho não cobre a
primeira.

### 4. Saiba o que você tem antes de precisar saber

Quando sai um aviso, a pergunta é sempre "eu uso isso?". Ter a resposta em
segundos muda o dia:

```bash
# gera um inventário de dependências (SBOM) em formato aberto
npm sbom --sbom-format cyclonedx > sbom.json

# checagem rápida de um pacote específico
npm ls axios
```

## O que eu penso disso

Vou ser direto sobre onde eu acho que está o aprendizado aqui, e não é
"instale a ferramenta X".

Repare que **nenhuma das quatro invasões começou com uma falha de software**.
Todas começaram com uma pessoa sendo convencida a dar acesso. Gastamos muita
energia discutindo CVE e pontuação CVSS, enquanto o caminho de entrada foi o de
sempre, o humano. Isso não desqualifica a análise técnica; só recoloca a
prioridade.

O segundo ponto incomoda mais. O ecossistema npm foi construído para tornar
trivial reaproveitar código, e isso é uma conquista real: você monta hoje, em
uma tarde, o que exigiria semanas há quinze anos. O preço é uma cadeia de
confiança que ninguém consegue auditar por inteiro. Não existe desenvolvedor,
por mais experiente, que tenha lido as mil dependências do próprio projeto.
Quem diz o contrário está vendendo alguma coisa.

Então não trate isso como uma falha sua a ser corrigida com mais esforço. Trate
como uma característica do terreno, que exige controle em vez de vigilância:
lockfile versionado, `npm ci` no pipeline, scripts de instalação desligados por
padrão, inventário à mão. São medidas chatas, que não rendem post bonito, e que
funcionam.

E se você está começando agora, fica minha sugestão de estudo: antes de decorar
ferramenta, rode `npm ls --all` em um projeto seu e leia a árvore com calma.
Entender o que você realmente carrega vale mais que qualquer scanner que você
possa instalar por cima.

<!-- ESPAÇO PARA SUA LEITURA PESSOAL: substitua ou complemente o fechamento acima -->

---

**Fontes**

- [Amazon identifies North Korean hacker group behind open source supply chain attacks][aws], AWS Security Blog, 29/07/2026 (fonte primária)
- [Open Source Vulnerabilities, `MAL-2026-3400`][osv]

[aws]: https://aws.amazon.com/blogs/security/amazon-identifies-north-korean-hacker-group-behind-open-source-supply-chain-attacks/
[osv]: https://osv.dev/
