TITULO = "Checkpoint: link, IP, rota e roteador (para 01 a 05)"
CHECKPOINT = True
CAUSA = "nenhuma: caso de treino pra conhecer a rede sã"
CHAMADO = """
Nada quebrado aqui. Estes são os comandos dos casos 01 a 05. Rode um por um,
olhe a saída e anote em respostas/00.md como o NORMAL se parece.

  topologia                        o desenho de como a rede DEVERIA estar

em cliente:
  ip -br link                      as placas. normal: UP, e LOWER_UP no ip link
  ip -br addr                      IP e máscara de cada placa. bate com a topologia?
  ip route                         as rotas. procure a linha "default via"
  ip route get 10.0.0.10           por onde ESSE destino sai (via, dev, src)
  ping -c3 192.168.1.1             o gateway responde?
  ping -c3 10.0.0.10               e quem está do outro lado do roteador?
  ip neigh                         quem o cliente conhece por MAC (REACHABLE, STALE)
  traceroute -n 10.0.0.10          os saltos até o servidor

em roteador:  (exit volta pro nó de antes)
  ip -br addr                      um pé em cada rede: lan0 e br0
  ip route                         ele conhece as duas redes sem gateway nenhum. por quê?
  sysctl net.ipv4.ip_forward       1 = repassa pacotes de uma rede pra outra

em servidor:
  ip route                         o servidor também precisa de rota pra RESPONDER

ver o pacote passando (um comando por linha):
  em cliente
  ping 10.0.0.10 >/dev/null &      pinga SEM PARAR, em segundo plano (o tcpdump só
                                   olha; sem alguém mandando pacote, não há o que ver)
  em roteador
  tcpdump -ni lan0 -c 6 icmp       request e reply se alternando
  tcpdump -ni br0 -c 6 icmp        o mesmo pacote, do outro lado do roteador
  exit                             volta pro cliente (o ping é dele)
  kill %1                          para o ping

pra consertar (é aqui que você mexe nos casos 01 a 05):
  ip link set eth0 up              liga a placa
  ip route add default via X       cria a rota padrão
  ip route replace default via X   troca a rota padrão (ou cria)
  sysctl -w net.ipv4.ip_forward=1  liga o repasse num roteador

No fim: verificar. O teste final de todo caso é o curl http://site.lab/ no cliente.
"""
DICAS = ["não tem defeito: a ideia é saber como o normal se parece, pra reconhecer o anormal."]
RESPOSTA = """# Checkpoint 00: link, IP, rota e roteador

## Como o normal se parece
<!-- um por linha: comando (em que nó) -> o que apareceu -> o que isso quer dizer -->


## O que eu não entendi
"""
def quebrar(lab):
    pass
