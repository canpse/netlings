# Guia de diagnóstico: ferramentas e como ler

## O método (sempre o mesmo)

1. **Reproduza** o sintoma você mesmo. Reclamação não é dado; o que você vê é.
2. **Suba as camadas**: link → IP → rota → vizinho (ARP) → caminho → DNS → porta → aplicação.
3. **Cada teste divide o problema ao meio.** Escolha o teste cujo resultado
   descarta mais coisa. "Pelo IP funciona" descarta toda a rede de uma vez.
4. **Uma hipótese, um teste, uma mudança.**
5. **Siga o pacote** quando as ferramentas "de ponta" (ping, curl) não bastam:
   tcpdump em cada salto mostra até onde ele vai e se a volta existe.
6. **Toda conversa tem ida e volta.** Metade dos problemas "misteriosos" está
   na volta.

## As perguntas e quem responde

| Pergunta | Comando | Normal | Suspeito |
|---|---|---|---|
| Interface existe e está de pé? | `ip -br link` | `UP` | `DOWN` (desligada), `NO-CARRIER` (sem cabo/par), `LOWER_UP` ausente |
| Tenho IP? Na rede certa? | `ip -br addr` | IP/máscara coerente com a rede | sem IP, `169.254.x.x` (DHCP falhou), máscara errada |
| Por onde saio? | `ip route` | `default via <gw> dev ...` | sem default, gw fora da sub-rede |
| Qual rota um destino usa? | `ip route get 10.0.0.10` | mostra via/dev/src | `unreachable`, src estranho |
| O vizinho responde ARP? | `ip neigh` | `REACHABLE`/`STALE` com MAC | `FAILED`/`INCOMPLETE`: ninguém tem esse IP no enlace |
| Políticas de roteamento? | `ip rule`, `ip route show table all` | só main/local/default | tabelas extras (VPN, Tailscale = tabela 52) |
| Encaminha? (num roteador) | `sysctl net.ipv4.ip_forward` | `1` | `0` |
| Quem resolve nomes? | `cat /etc/resolv.conf` · `resolvectl status` | servidor alcançável | IP errado, inalcançável |
| O DNS responde o quê? | `dig nome` · `dig @servidor nome` | `status: NOERROR` + ANSWER | `NXDOMAIN` (não existe), `SERVFAIL`, `timed out` |
| O que o *sistema* resolve? | `getent hosts nome` | mesmo IP do dig | diferente do dig → `/etc/hosts` ou NSS |
| Quem escuta e onde? | `ss -tlnp` (TCP) · `ss -ulnp` (UDP) | `0.0.0.0:80` ou IP da interface | `127.0.0.1:80` = só local |
| Porta abre? | `nc -zv -w2 host 80` · `curl -v` | `succeeded` / resposta HTTP | ver tabela de erros abaixo |
| Tem firewall? | `nft list ruleset` (`iptables -S` em sistemas velhos) | vazio ou regras esperadas | `drop`/`reject` no caminho |
| Onde perde/atrasa? | `mtr -n destino` | 0% em todos | perda que começa num salto e **continua** até o fim |
| Tamanho máximo do caminho? | `ping -M do -s 1472 destino` | passa (1472+28 = 1500) | `message too long` ou silêncio → MTU menor no caminho |
| Mexeram na fila? | `tc qdisc show` | `noqueue`/`fq_codel` | `netem` (perda/atraso artificial), `tbf` (limite) |
| O que passa de fato? | `tcpdump -ni eth0 host X and port 80` | ida e volta | só ida; SYN sem SYN-ACK; retransmissões |

## Ler mensagens de erro (a parte que mais economiza tempo)

**ping**
- `Network is unreachable` → o **próprio host** não tem rota. Problema local, nem saiu pacote.
- `Destination Host Unreachable` vindo **do seu IP** → rota existe, mas o ARP do próximo salto falhou (vizinho não responde).
- `Destination Host/Net Unreachable` vindo **de um roteador** → aquele roteador não tem rota adiante.
- `Destination Port Unreachable` → host vivo, porta UDP fechada (comum no traceroute).
- `Frag needed and DF set` → pacote grande demais pra algum enlace.
- **silêncio (100% loss)** → pacote ou resposta morreu sem aviso: firewall com drop, rota de volta faltando, ICMP filtrado. É o caso que exige tcpdump.
- `ttl=` na resposta: diz quantos saltos a resposta deu (64 − saltos no Linux, 128 − saltos no Windows).

**curl / conexões TCP**
- `Could not resolve host` → DNS/NSS. A rede pode estar perfeita.
- `Connection refused` (instantâneo) → chegou, alguém respondeu RST: ninguém escutando naquele IP:porta, ou firewall com `reject`. **A rede até lá está boa.**
- `Connection timed out` / trava → SYN sem resposta: firewall com `drop`, rota (ida ou volta), host fora.
- `No route to host` → ICMP host-unreachable (ARP falhou ou firewall `reject with icmp`).
- conecta mas trava no meio de transferência grande → MTU/PMTU (buraco negro).
- `curl -v` mostra em que fase parou: resolução, `Trying ip:porta`, `Connected`, TLS, HTTP.

**traceroute / mtr**
- `* * *` num salto, mas os seguintes respondem → aquele roteador só não responde ICMP. Ignore.
- `* * *` dali até o fim → o problema está entre o último que respondeu e o primeiro que não.
- Perda alta num salto intermediário que **não continua** → limitação de ICMP do roteador, não perda real. Só conta a perda que se propaga até o destino.
- Salto repetido / ping-pong entre dois IPs → laço de roteamento.

**tcpdump** (no nó certo, na interface certa)
- `Flags [S]` repetido sem `[S.]` voltando → SYN sem resposta (drop, rota de volta).
- `Flags [S]` seguido de `[R.]` → recusado (porta fechada / reject).
- `ARP, Request who-has X` sem `Reply` → ninguém tem X no enlace.
- request ICMP visto no servidor, mas o reply não sai pela interface certa → rota de volta.
- Mesmo pacote várias vezes, espaçado → retransmissão: perda no caminho.
- Filtros úteis: `-ni any`, `host X`, `port 53`, `icmp`, `arp`, `'tcp[tcpflags] & tcp-syn != 0'`, `-c 10`, `-e` (mostra MACs).

## Atalhos de intuição

- **Pelo IP funciona, pelo nome não** → DNS. Sempre comece separando esses dois.
- **dig certo, aplicação errada** → `/etc/hosts`, cache, NSS (`getent`).
- **Ping ok, serviço não** → camada 4+: porta, firewall, serviço escutando onde.
- **Funciona pra mim, não pra ele** → compare: rota, DNS, sub-rede, firewall por origem.
- **Pequeno passa, grande trava** → MTU.
- **Às vezes** → perda, Wi-Fi, IP duplicado (`ip neigh` com MAC mudando), DHCP, balanceador.
- **Parou depois de uma mudança** → o que mudou é suspeito número 1. Pergunte sempre.
- **Pinga o roteador "do outro lado"** não prova encaminhamento: aquele IP é do próprio roteador.
