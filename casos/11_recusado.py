TITULO = "Conexão recusada"
CAUSA = "o serviço web foi reiniciado escutando só em 127.0.0.1"
CHAMADO = """
"Depois da manutenção de ontem no servidor, o site dá 'Connection refused'.
O admin diz que o serviço está rodando, ele viu no ps."
(se precisar subir o serviço de novo no servidor:
 python3 -m http.server 80 --bind <endereço> -d $NL_PASTA/www >/dev/null 2>&1 &)
"""
DICAS = ["refused na hora = alguém respondeu com RST. a rede até lá está boa",
         "em servidor: ss -tlnp. está rodando, sim. mas escutando ONDE?"]
def quebrar(lab):
    import time
    lab.servicos["servidor"].kill()
    lab.servicos["servidor"].wait()
    time.sleep(0.3)
    lab.servico("servidor", f"exec python3 -m http.server 80 --bind 127.0.0.1 -d {lab.pasta / 'www'}")
    for _ in range(40):
        if lab.em("servidor", "ss -tln | grep -q '127.0.0.1:80 '").returncode == 0:
            break
        time.sleep(0.1)
