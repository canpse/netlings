TITULO = "Checkpoint: nomes (para 07 e 08)"
CHECKPOINT = True
CAUSA = "nenhuma: rede sã, treino dos comandos de nome"
CHAMADO = """
Rede sã de novo. Nos próximos casos o pacote chega: o problema é transformar
o NOME no endereço certo. Rode, olhe e anote em respostas/06.md.

em cliente:
  cat /etc/resolv.conf             quem é o DNS do cliente (linha nameserver)
  dig site.lab                     pergunta ao DNS. olhe: status, ANSWER SECTION
                                   e, no fim, SERVER (quem respondeu)
  dig @10.0.0.53 site.lab          pergunta a um DNS escolhido, ignorando o resolv.conf
  dig naoexiste.lab                um nome que não existe. qual status?
  dig +time=2 +tries=1 @10.0.0.99 site.lab
                                   um DNS que não existe. como é a falta de resposta?
  cat /etc/hosts                   a lista local de nomes
  cat /etc/nsswitch.conf           linha hosts: a ordem em que o sistema procura
                                   (files = /etc/hosts, vem antes do dns)
  getent hosts site.lab            o que o SISTEMA resolve. é isso que ping e curl usam
  ping -c1 naoexiste.lab           compare a mensagem com: cola erros

pra consertar (casos 07 e 08):
  nano /etc/resolv.conf            muda o DNS do cliente
  nano /etc/hosts                  edita a lista local
  (sed -i não funciona nesses arquivos aqui no laboratório; use o nano)

Pergunta pra anotar: se o dig e o getent derem IPs diferentes, quem o curl segue?
"""
DICAS = ["não tem defeito: a ideia é saber como o normal se parece, pra reconhecer o anormal."]
RESPOSTA = """# Checkpoint 06: nomes

## Como o normal se parece
<!-- um por linha: comando (em que nó) -> o que apareceu -> o que isso quer dizer -->


## Se o dig e o getent discordarem, quem o curl segue?


## O que eu não entendi
"""
def quebrar(lab):
    pass
