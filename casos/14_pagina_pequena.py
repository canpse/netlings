TITULO = "Página pequena abre, download trava"
CAUSA = "MTU 1300 na lan0 do roteador + roteador bloqueia o ICMP 'frag needed' (buraco negro de PMTU)"
CHAMADO = """
"http://site.lab/ abre na hora. Mas http://site.lab/grande.bin (2 MB) começa
e trava, sempre. Já troquei de navegador."
"""
DICAS = ["pacotes pequenos passam, grandes não. o que limita o tamanho de um pacote num enlace?",
         "ping -M do -s 1472 10.0.0.10 (proíbe fragmentar). vá diminuindo o -s até passar",
         "ip link | grep mtu em cada nó do caminho: as MTUs batem?",
         "quando o pacote não cabe e tem DF, o roteador avisa com ICMP. alguém pode estar engolindo esse aviso (nft list ruleset)"]
def quebrar(lab):
    lab.sh("ip -n roteador link set lan0 mtu 1300")
    lab.sh("ip netns exec roteador nft add table inet filtro")
    lab.sh("ip netns exec roteador nft add chain inet filtro saida '{ type filter hook output priority 0; }'")
    lab.sh("ip netns exec roteador nft add rule inet filtro saida icmp type destination-unreachable drop")
def verificar(lab):
    r = lab.em("cliente", "curl -s -m 8 -o /dev/null -w '%{size_download}' http://site.lab/grande.bin", timeout=12)
    return [(r.stdout.strip() == str(2 * 1024 * 1024), "download de grande.bin (2 MB) completo")]
