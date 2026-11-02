TITULO = "Não tem internet nenhuma"
CAUSA = "eth0 do cliente está down (cabo/placa)"
CHAMADO = """
"Oi, aqui no meu computador (cliente) não abre nada. NADA. Ontem funcionava."
"""
DICAS = ["comece pelo próprio cliente, de baixo pra cima: antes de IP, existe link?",
         "ip -br link: olhe o estado de cada interface",
         "'state DOWN' sem NO-CARRIER é interface desligada administrativamente",
         "subiu e ainda não vai? quando uma interface cai, o kernel apaga as rotas que dependiam dela"]
def quebrar(lab):
    lab.sh("ip -n cliente link set eth0 down")
