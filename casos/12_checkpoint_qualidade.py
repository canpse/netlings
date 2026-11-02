TITULO = "Checkpoint: perda, atraso e tamanho de pacote (para 13 e 14)"
CHECKPOINT = True
CAUSA = "nenhuma: rede sã, treino dos comandos de qualidade"
CHAMADO = """
Rede sã. Nos últimos casos funciona... às vezes. Pra achar defeito
intermitente, primeiro MEDIR. Rode, olhe e anote em respostas/12.md.

em cliente:
  ping -c20 -i 0.2 10.0.0.10       a última linha: % de perda e rtt min/avg/max/mdev
                                   (mdev = quanto o tempo varia)
  mtr -n -r -c 20 10.0.0.10        relatório por salto: Loss% e Avg
  ip link show eth0                procure "mtu": o maior pacote que a placa manda
  ping -M do -s 1472 -c2 10.0.0.10 1472 de dados + 28 de cabeçalho = 1500: passa
  ping -M do -s 1473 -c2 10.0.0.10 um byte a mais: o que acontece?
                                   (-M do = proibido fragmentar)
  curl -s -o /dev/null -w '%{size_download} bytes em %{time_total} s\\n' http://site.lab/grande.bin
                                   o download grande: quanto e em quanto tempo

em roteador:
  ip link | grep mtu               a MTU de cada placa. batem entre si?
  tc qdisc show                    a fila de cada placa. noqueue ou fq_codel = normal
                                   netem = alguém pôs perda ou atraso de propósito
  nft list ruleset                 vazio = nada filtrado

pra consertar (casos 13 e 14):
  tc qdisc del dev <placa> root    tira o que alguém pôs na fila
  ip link set <placa> mtu 1500     acerta a MTU
  nft flush ruleset                apaga as regras de firewall
"""
DICAS = ["não tem defeito: a ideia é saber como o normal se parece, pra reconhecer o anormal."]
RESPOSTA = """# Checkpoint 12: perda, atraso e tamanho de pacote

## Como o normal se parece
<!-- um por linha: comando (em que nó) -> o que apareceu -> o que isso quer dizer -->


## O que eu não entendi
"""
def quebrar(lab):
    pass
