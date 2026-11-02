TITULO = "O pacote chega lá, mas não volta"
CAUSA = "servidor sem rota padrão: não sabe responder pra 192.168.1.0/24"
CHAMADO = """
"O site.lab não abre. O pessoal do servidor jura que o pacote chega lá, viram
no tcpdump. E o DNS tá resolvendo certinho."
"""
DICAS = ["eles estão certos que chega. siga o pacote de VOLTA",
         "tcpdump no servidor mostra request sem reply? então a pergunta é: pra onde ele mandaria a resposta?",
         "toda comunicação tem duas rotas: a de ida no cliente e a de volta no servidor"]
def quebrar(lab):
    lab.sh("ip -n servidor route del default")
