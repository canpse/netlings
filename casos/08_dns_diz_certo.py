TITULO = "O DNS diz certo, o computador vai pro lugar errado"
CAUSA = "entrada velha em /etc/hosts: site.lab -> 10.0.0.77"
CHAMADO = """
"site.lab não abre. Mas o estranho: rodei dig site.lab e veio o IP certo,
10.0.0.10! Então não é DNS... ou é?"
"""
DICAS = ["dig pergunta direto ao servidor DNS. curl e ping perguntam ao sistema (NSS). são caminhos diferentes",
         "getent hosts site.lab mostra o que o SISTEMA resolve",
         "antes do DNS, o sistema consulta um arquivo local (veja /etc/nsswitch.conf)"]
def quebrar(lab):
    with open(lab.pasta / "hosts", "a") as f:
        f.write("10.0.0.77 site.lab\n")
