# netlings

Redes quebradas pra diagnosticar, no estilo Ziglings. Cada caso monta uma
rede pequena (cliente, roteador, servidor, dns) com **um** defeito e te dá a
reclamação do usuário. Você entra nos nós, investiga com as ferramentas de
verdade, conserta e roda `verificar`.

    python3 nl.py         # casos, o que já passou e qual é o próximo
    python3 nl.py 0       # comece pelo 00: a rede sã, pra conhecer o normal

Roda sem sudo, em namespaces de rede (`unshare -rnm`): não toca na sua rede
real, e ao dar `exit` no shell de fora o laboratório some (pode quebrar à
vontade, abrir de novo zera tudo).

Dentro do laboratório:

    em cliente      # shell dentro do nó (cliente, roteador, servidor, dns); exit volta
    topologia       # como a rede DEVERIA ser
    chamado         # a reclamação de novo
    dica            # uma por vez, empurra sem entregar
    verificar       # resolveu?
    caso N          # troca pro caso N (funciona até de dentro de um nó)
    proximo         # vai pro caso seguinte
    lista           # todos os casos
    exit            # no shell de fora: fecha o laboratório

O que conta não é passar, é o caminho. Em `respostas/NN.md` anote cada teste
(comando → o que viu → o que concluiu). O assistente lê e comenta o raciocínio.

`guia.md` é a cola: o que cada ferramenta responde e como ler a saída.

Os casos ficam fora daqui (`~/Assistente/redes2/netlings/cenarios`), pra
resposta não ficar do lado.
