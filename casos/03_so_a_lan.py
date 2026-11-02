TITULO = "O roteador responde, o site não"
CAUSA = "cliente sem rota padrão"
CHAMADO = """
"Consigo acessar a página do roteador (192.168.1.1) normalmente, mas nenhum
site abre. Já reiniciei o navegador."
"""
DICAS = ["quando o ping falha, leia a MENSAGEM de erro, ela diz muito",
         "'A rede está fora de alcance' (Network is unreachable) é o kernel do próprio cliente dizendo que não sabe pra onde mandar"]
def quebrar(lab):
    lab.sh("ip -n cliente route del default")
