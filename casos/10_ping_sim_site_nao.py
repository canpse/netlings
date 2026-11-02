TITULO = "Ping responde, o site fica carregando"
CAUSA = "nftables no servidor descarta (drop) TCP na porta 80"
CHAMADO = """
"ping site.lab funciona perfeito. Mas o navegador fica girando, girando, e
desiste. Não dá erro, só demora."
"""
DICAS = ["ping é ICMP. site é TCP 80. são coisas diferentes pra um filtro",
         "'fica girando' (timeout) e 'recusado na hora' (refused) apontam pra causas diferentes. qual é este?",
         "em servidor: tcpdump -ni eth0 port 80 chega SYN? sai SYN-ACK? e nft list ruleset"]
def quebrar(lab):
    lab.sh("ip netns exec servidor nft add table inet filtro")
    lab.sh("ip netns exec servidor nft add chain inet filtro entrada '{ type filter hook input priority 0; }'")
    lab.sh("ip netns exec servidor nft add rule inet filtro entrada tcp dport 80 drop")
