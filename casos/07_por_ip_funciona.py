TITULO = "Pelo IP funciona, pelo nome não"
CAUSA = "resolv.conf do cliente aponta pra 10.0.0.99 (servidor DNS inexistente)"
CHAMADO = """
"Descobri um truque: http://10.0.0.10/ abre! Mas http://site.lab/ não.
Todo mundo usa o nome, então preciso disso funcionando."
"""
DICAS = ["por IP funciona = rede ok até o servidor. o que transforma nome em IP?",
         "dig site.lab: qual SERVER ele usou e o que respondeu?",
         "cat /etc/resolv.conf e confira com a topologia"]
def quebrar(lab):
    from pathlib import Path
    Path("/run/systemd/resolve/stub-resolv.conf").write_text("nameserver 10.0.0.99\n")
