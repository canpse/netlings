TITULO = "Checkpoint: portas, serviços e firewall (para 10 e 11)"
CHECKPOINT = True
CAUSA = "nenhuma: rede sã, treino dos comandos de porta"
CHAMADO = """
Rede sã. Nos próximos casos o pacote chega ao servidor, mas o SERVIÇO não
atende. Rode, olhe e anote em respostas/09.md.

em cliente:
  curl -v http://site.lab/         as fases: Trying ip:80 → Connected → o pedido (>)
                                   → a resposta (<). se travar, a fase diz onde
  nc -zv -w2 10.0.0.10 80          só testa se a porta abre: Connected
  nc -zv -w2 10.0.0.10 81          porta sem ninguém: recusa NA HORA
  nc -zv -w2 10.0.0.99 80          IP onde não tem ninguém: demora uns segundos e
                                   No route to host (ninguém respondeu o ARP)

em servidor:
  ss -tlnp                         quem escuta TCP, em que IP e porta
                                   0.0.0.0:80 = todas as placas · 127.0.0.1:80 = só ele mesmo
  nft list ruleset                 o firewall. vazio = nenhuma regra

em dns:
  ss -ulnp                         o dnsmasq, em UDP 53 (DNS é UDP)

ver o aperto de mão do TCP (um comando por linha):
  em cliente
  while sleep 2; do curl -s http://site.lab/ >/dev/null; nc -z 10.0.0.10 81; done &
                                   (a cada 2 s: um acesso ao site e um à porta 81)
  em servidor
  tcpdump -ni eth0 -c 6 port 80    [S] pedido, [S.] aceito, [.] confirmado
  tcpdump -ni eth0 -c 2 port 81    [S] e [R.]: a recusa é um pacote, não silêncio
  exit
  kill %1                          (de volta no cliente: para o laço)

pra consertar (casos 10 e 11):
  nft -a list ruleset              as regras com número (handle N)
  nft delete rule inet <tabela> <chain> handle N    apaga UMA regra
  nft flush ruleset                apaga TODAS
  kill <pid>                       para um programa (o pid aparece no ss -tlnp)
"""
DICAS = ["não tem defeito: a ideia é saber como o normal se parece, pra reconhecer o anormal."]
RESPOSTA = """# Checkpoint 09: portas, serviços e firewall

## Como o normal se parece
<!-- um por linha: comando (em que nó) -> o que apareceu -> o que isso quer dizer -->


## Recusado na hora x demora e desiste: o que cada um quer dizer?


## O que eu não entendi
"""
def quebrar(lab):
    pass
