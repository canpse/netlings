# netlings: instruções para agentes de IA

O netlings monta redes pequenas e quebradas (em namespaces de rede, sem sudo) pra uma pessoa
treinar diagnóstico. Se te pediram pra instalar, siga a parte 1. Se a pessoa está jogando e te
pede ajuda, siga a parte 2: ela importa mais que a instalação.

O jeito recomendado de instalar é exatamente este: a pessoa te passa o link do repositório e
pede pra instalar. Isso basta. Não pergunte nada que você consegue descobrir sozinho.

## 1. Instalar

```sh
git clone https://github.com/canpse/netlings ~/netlings   # ou onde a pessoa preferir
cd ~/netlings && python3 nl.py conferir
```

`conferir` testa os programas e se dá pra criar namespaces sem sudo. Termina com
`ok: tudo pronto` (saída 0) ou diz o que falta, com o comando de instalação pra Fedora,
Debian/Ubuntu e Arch (saída 1). Não precisa de pip nem de venv: é Python puro, só a biblioteca
padrão.

**sudo:** instalar pacotes e mexer em sysctl precisa de sudo. Mostre à pessoa o comando que o
`conferir` deu e peça pra ela rodar (ou peça licença antes de rodar você). Nunca desligue
proteções do sistema de forma permanente sem ela pedir. O `sysctl` do AppArmor que o
`conferir` sugere vale só até reiniciar. Depois rode `conferir` de novo, até dar `ok`.

**Quando terminar**, diga em duas linhas: abrir um terminal na pasta e rodar
`python3 nl.py 0`, que é a rede sã, pra conhecer o normal. O laboratório é um shell
interativo: **quem joga é a pessoa, num terminal dela**. Não abra o laboratório por ela.

## 2. Ajudar quem está jogando

O objetivo é a pessoa ganhar intuição de diagnóstico. Se você entregar a causa, o caso foi
desperdiçado.

- **Não abra `casos/` nem `teste.py` pra contar a resposta.** A causa e o conserto estão lá.
  Leia só se a pessoa pedir explicitamente o gabarito, ou depois que ela fechou o caso.
- **Ajude como as dicas do jogo:** uma pergunta ou empurrão por vez, do mais vago ao mais
  concreto. "Antes do IP, o link está de pé?" é melhor que "a eth0 está down". O comando
  `dica` dentro do laboratório faz o mesmo.
- **Ensine a escada:** do sintoma pra baixo e depois de baixo pra cima (link → IP → rota →
  vizinho → caminho → nome → porta → filtros → pacote). `guia.md` e `cola.txt` dizem o que
  cada ferramenta responde. Pode ler esses dois à vontade.
- **Peça a saída, não a conclusão.** Se a pessoa diz "o DNS está errado", pergunte qual
  comando mostrou isso e o que ele imprimiu. Ler a saída é metade do treino.
- **Comente o raciocínio.** Ao fechar um caso, a pessoa anota em `respostas/NN.md`:
  comando → o que viu → o que concluiu. Leia e comente a ordem dos testes, o que cada saída
  descartava, o que dava pra pular e o que faltou olhar. Acertar com sorte não conta.

## 3. Mexer no projeto

- Caso novo: `casos/NN_nome.py` com `TITULO` (o sintoma, sem entregar), `CAUSA`, `CHAMADO`,
  `DICAS` (do vago ao concreto), `quebrar(lab)` e, se precisar, `verificar(lab)`. Os
  checkpoints têm `CHECKPOINT = True` e não quebram nada.
- Ponha o conserto em `CONSERTO` no `teste.py` e rode `python3 teste.py NN` (sem número, roda
  todos): ele monta, confere que está quebrado, conserta e confere que voltou a funcionar.
  Nenhum caso entra sem passar nesse teste.
- Um defeito por caso, a não ser que o caso seja sobre dois defeitos. Casos novos entram no
  fim de um grupo, ou num grupo novo com checkpoint próprio.
- Textos em português, direto. Mensagens de erro aparecem em português e em inglês, porque o
  `ping` fala a língua do sistema.
