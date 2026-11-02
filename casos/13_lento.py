TITULO = "Lento, às vezes trava"
CAUSA = "netem no roteador (lan0) com 25% de perda"
CHAMADO = """
"Não é que não funcione. Às vezes abre, às vezes demora muito, às vezes dá erro.
Videochamada nem pensar."
"""
DICAS = ["intermitência quase sempre é perda ou atraso. meça antes de supor: ping -c 50 -i 0.2",
         "mtr -n site.lab: em que salto a perda COMEÇA e continua até o fim?",
         "perda que aparece num salto e some nos seguintes é o roteador ignorando ICMP, não perda real",
         "no nó suspeito: tc qdisc show"]
def quebrar(lab):
    lab.sh("ip netns exec roteador tc qdisc add dev lan0 root netem loss 25%")
def verificar(lab):
    r = lab.em("cliente", "ping -q -c 40 -i 0.05 -W 1 10.0.0.10", timeout=20)
    return [(" 0% packet loss" in r.stdout, "40 pings sem perda")]
