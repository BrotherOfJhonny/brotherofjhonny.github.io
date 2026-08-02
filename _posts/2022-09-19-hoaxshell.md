---
title: "hoaxshell - Fiz poc no Windows 11 (build 22000.co) e funciona!"
date: 2022-09-19 15:00:00 -0300
categories: [artigo]
tags: [inicio, artigo, shell, pentest, fundamentos, vulnerabilidade, relatorio, xmlrpc, wordpress, scrpy]
description: "Quantas vezes vemos ou curtimos a postagem de algum colega e não damos a devida importância ao que esta sendo compartilhado? Outro dia vi a postagem do Rafael Brinhosa sobre o hoaxshell no linkedin e marquei para ler com calma depois."
image:
  path: /assets/img/hoaxshell/imagen4.jpg
  alt: "hoaxshell — PoC no Windows 11"
---

Quantas vezes vemos ou curtimos a postagem de algum colega e não damos a devida importância ao que esta sendo compartilhado? Outro dia vi a postagem do [Rafael Brinhosa](<https://www.linkedin.com/post/edit/6969045721308119040/#>) sobre o hoaxshell no linkedin e marquei para ler com calma depois.

![Hoaxshell](/assets/img/hoaxshell/imagen1.jpg)

**Este artigo resultado disso!**

Quem está familiarizado com pentest em sistema operacional da [Microsoft](<https://www.linkedin.com/post/edit/6969045721308119040/#>) tem percebido a evolução de segurança aplicada no Windows. As proteções como UCA (user account Control) ou o próprio Defender, tem proporcionado uma camada a mais que acaba dificultando a pós-exploração, talvez isso tenha me chamado a atenção para o artigo postando pelo Rafael. (https://www.linkedin.com/feed/update/urn:li:activity:6966411478182576128/)

## Configurações da POC

Para esta prova de conceito foram utilizados os sistemas operacionais:

  * **Kali linux 2022.3**
  * **Windows 11 Enterprise - Build 22000.co_release.210604-1628**. ![Kalli Linux 2022.3](/assets/img/hoaxshell/imagen2.jpg)

![Windows 11 Build 22000.co](/assets/img/hoaxshell/imagen3.jpg)

**Observação:**

Sistemas operacionais desta POC foram obtidos gratuitamente no links dos fabricantes:

  * **Kali** \- _https://www.kali.org/get-kali/#kali-virtual-machines_
  * **Windows 11** \- _https://developer.microsoft.com/pt-br/windows/downloads/virtual-machines/_

## hoaxshell

hoaxshell é um shell reverso para Windows não convencional, baseado exclusivamente no tráfego http(s). Recentemente foi divulgada a CVE-2022-30190 , esse bug de dia zero no MSDT pode habilitar a execução remota de código quando o MSDT é chamado usando o protocolo de URL de um aplicativo de chamada como o Microsoft Word .

O projeto pode ser baixado no github (https://github.com/t3l3machus/hoaxshell), a instalação é bastante simples:

`git clone https://github.com/t3l3machus/hoaxshell` `cd ./hoaxshell` `sudo pip3 install -r requirements.txt` `chmod +x hoaxshell.py`

Após realizada a instalação é só executar o comando:

`sudo python3 hoaxshell.py -s <your_ip>`

Deste modo será gerado uma carga no terminal : ![gerando payload](/assets/img/hoaxshell/imagen4.jpg)

É necessário enviar o código gerado para o computador com Windows, abra powershell e cole o código.

![colando payload no terminal do powershell](/assets/img/hoaxshell/imagen5.jpg)

Após colar o código clique enter que a conexão será aberta no sistema onde foi gerado o shell reverso (kalil linux)

![Recebendo a conexão no terminal do Kali](/assets/img/hoaxshell/imagen6.jpg)

Estando conectado os comandos realizados no terminal do linux serão executados no windows, deste ponto em diante é explorar o sistema atacado.

![verificando documentos do usuário](/assets/img/hoaxshell/imagen7.jpg)

## Verificando o alvo

Podemos ver que o Windows 11 estava com os módulos do defender instalados.

![Modulos do Windows defender ativos](/assets/img/hoaxshell/imagen8.jpg))

### **Conclusão:**

O Hoaxshell utiliza técnicas de econdamento para ofuscar suas cargas, confundindo as proteções do sistema operacional, mas com a divulgação destas ferramentas a Microsoft e outros fornecedores geram atualizações buscando mitigar as vulnerabilidades.
