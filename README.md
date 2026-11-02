# netlings

Redes quebradas pra você diagnosticar, no estilo Ziglings/Rustlings.

Cada caso monta uma rede pequena de verdade (cliente, roteador, servidor web e
DNS) com **um** defeito e te entrega a reclamação do usuário: *"não abre
nada"*, *"por IP funciona, pelo nome não"*, *"a página pequena abre, a grande
trava"*. Você entra nos nós, investiga com as ferramentas de sempre (`ip`,
`ping`, `dig`, `ss`, `tcpdump`, `nft`...), conserta e roda `verificar`.

Fiz isso porque eu sabia a teoria de redes, mas travava na hora de
diagnosticar. Faltava prática com as ferramentas, ler a saída delas e ter
intuição de por onde começar.

## Rodar

    git clone https://github.com/canpse/netlings && cd netlings
    python3 nl.py         # lista os casos, o que já passou e qual é o próximo
    python3 nl.py 0       # comece pelo 00: a rede sã, pra conhecer o normal

**Não precisa de sudo.** Tudo roda em namespaces de rede (`unshare -rnm`),
então não toca na sua rede real. Ao dar `exit` no shell de fora, o
laboratório some. Pode quebrar à vontade: abrir de novo zera tudo.

Precisa de Linux com user namespaces liberados (o padrão no Fedora, no Arch
e no Ubuntu recente), Python 3 e destes programas:

| Programa | Fedora | Debian/Ubuntu |
|---|---|---|
| ip, tc, ss | iproute | iproute2 |
| nft | nftables | nftables |
| dnsmasq | dnsmasq | dnsmasq-base |
| dig | bind-utils | dnsutils |
| tcpdump, traceroute, mtr, curl, nc | mesmos nomes (nc = nmap-ncat) | mesmos nomes (nc = netcat-openbsd) |

No Ubuntu 24.04 ou mais novo, o AppArmor pode bloquear `unshare` sem root. Se
der `Operation not permitted`, veja `kernel.apparmor_restrict_unprivileged_userns`.

## Dentro do laboratório

    em cliente      # shell dentro de um nó (cliente, roteador, servidor, dns); exit volta
    topologia       # como a rede DEVERIA ser
    cola            # comandos por degrau (cola erros · cola tcpdump · cola consertar)
    chamado         # a reclamação de novo
    dica            # uma por vez, empurra sem entregar
    verificar       # resolveu?
    caso N          # troca pro caso N (funciona até de dentro de um nó)
    proximo         # vai pro caso seguinte
    reiniciar       # monta o caso de novo, quebrado como no começo
    lista           # todos os casos
    exit            # no shell de fora: fecha o laboratório

## A trilha

É semi-guiada. Cada grupo começa num **checkpoint**, uma rede sã que ensina
os comandos do grupo e o que olhar em cada saída. Os casos seguintes usam só
esses comandos.

| Grupo | Checkpoint | Casos |
|---|---|---|
| Camadas 1 a 3 | 00 | 01–05: link, gateway, rota, repasse, volta |
| Nomes | 06 | 07–08 |
| Portas | 09 | 10–11 |
| Qualidade | 12 | 13–14: perda, MTU |

`guia.md` é a cola: o que cada ferramenta responde e como ler a saída.

**O que conta não é passar, é o caminho.** Ao fechar cada caso, anote em
`respostas/NN.md` cada teste que fez: comando → o que viu → o que concluiu.
Depois mostre pra alguém, ou pro seu agente de IA, e peça comentário sobre o
raciocínio, não só sobre a resposta.

**Spoiler:** a causa e o conserto de cada caso estão em `casos/` e
`teste.py`. Não abra antes de jogar.

## Contribuir

Caso novo é um arquivo em `casos/NN_nome.py` com `TITULO` (o sintoma, sem
entregar a causa), `CAUSA`, `CHAMADO`, `DICAS`, `quebrar(lab)` e, se precisar,
`verificar(lab)`. Ponha o conserto em `teste.py` e rode `python3 teste.py NN`:
ele monta o caso, confere que está quebrado, aplica o conserto e confere que
voltou a funcionar.

Ideias que ainda não viraram caso: IP duplicado, DHCP, rota assimétrica com
`rp_filter`, laço de roteamento, `ip rule` com tabela extra, NAT faltando,
dois defeitos ao mesmo tempo e chamados vagos sem dica.

Os textos estão em português. Os comandos e as mensagens de erro em inglês
também aparecem na cola.

Fiz o projeto com agentes de IA: eu decidi o que queria aprender e como, e
boa parte do código foi escrita com o Claude Code.

## Licença

MIT
