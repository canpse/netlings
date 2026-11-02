TITULO = "Nem a rede local responde"
CAUSA = "gateway padrão do cliente aponta pra 192.168.1.254, que não existe"
CHAMADO = """
"O técnico anterior mexeu na configuração do meu computador (cliente) e
agora não acesso nada fora. A interface tá ligada, tem IP, eu já olhei."
"""
DICAS = ["ele tem IP. o próximo degrau é: por onde os pacotes saem?",
         "ip route, e depois tente pingar o próximo salto que aparece lá",
         "ip neigh: FAILED/INCOMPLETE quer dizer que ninguém respondeu o ARP daquele IP"]
def quebrar(lab):
    lab.sh("ip -n cliente route replace default via 192.168.1.254")
