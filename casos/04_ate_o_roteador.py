TITULO = "Pinga até o roteador, inclusive o lado de lá"
CAUSA = "roteador com ip_forward=0 (não encaminha entre interfaces)"
CHAMADO = """
"Fiz os testes que me ensinaram: pingo 192.168.1.1, pingo até 10.0.0.1, que é
o roteador do lado dos servidores! Mas 10.0.0.10 não responde. Então o
problema é no servidor, né?"
(é mesmo?)
"""
DICAS = ["10.0.0.1 é um endereço DO roteador. responder por ele não prova que ele repassa pacotes",
         "em roteador: tcpdump -ni br0 icmp enquanto o cliente pinga 10.0.0.10. o pacote sai do outro lado?",
         "o que faz um Linux virar roteador é um sysctl"]
def quebrar(lab):
    lab.sh("ip netns exec roteador sysctl -qw net.ipv4.ip_forward=0")
