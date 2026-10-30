#!/usr/bin/env python3
"""netlings: redes quebradas pra diagnosticar.

    python3 nl.py lista   # casos e o que já passou
    python3 nl.py N       # abre o caso N (um shell no laboratório)
    python3 nl.py         # lista e diz qual é o próximo
    python3 nl.py zerar [N]   # apaga o ✓ do caso N, ou de todos (respostas ficam)

Dentro do laboratório, `caso N` e `proximo` trocam de caso sem sair.

Tudo roda em namespaces de rede sem sudo (unshare -rnm): nada encosta na
sua rede de verdade, e ao sair do shell o laboratório some.
"""
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CENARIOS = Path.home() / "Assistente/redes2/netlings/cenarios"
PROGRESSO = AQUI / "progresso.json"
RESPOSTAS = AQUI / "respostas"

TOPOLOGIA = """
  ┌─────────────────────────────┐
  │ cliente                     │
  │   eth0  192.168.1.10/24     │
  └──────────────┬──────────────┘
                 │ cabo (rede 192.168.1.0/24)
  ┌──────────────┴──────────────┐
  │ roteador                    │
  │   lan0  192.168.1.1/24      │  ← o gateway do cliente
  │   br0   10.0.0.1/24         │  ← o gateway do servidor e do dns
  │         (br0 é um switch    │
  │          com as portas      │
  │          p-srv e p-dns)     │
  └──────┬───────────────┬──────┘
         │ p-srv         │ p-dns   (rede 10.0.0.0/24)
  ┌──────┴────────┐ ┌────┴──────────┐
  │ servidor      │ │ dns           │
  │ eth0          │ │ eth0          │
  │ 10.0.0.10/24  │ │ 10.0.0.53/24  │
  │ site.lab      │ │ dnsmasq       │
  └───────────────┘ └───────────────┘

  rota padrão: cliente via 192.168.1.1 · servidor e dns via 10.0.0.1
  DNS do cliente: /etc/resolv.conf → nameserver 10.0.0.53
  site.lab → 10.0.0.10
"""

MODELO_RESPOSTA = """# Caso {n}: {titulo}

## Sintoma (com as suas palavras, depois de reproduzir)


## Testes
<!-- um por linha: comando (em que nó) -> o que apareceu -> o que isso me diz -->


## Causa


## Correção (e como confirmei)


## O que eu levo daqui
"""


def carregar(n):
    arqs = sorted(CENARIOS.glob(f"{int(n):02d}_*.py"))
    if not arqs:
        sys.exit(f"não achei o caso {n}")
    spec = importlib.util.spec_from_file_location("cenario", arqs[0])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.NOME = arqs[0].stem
    return mod


def todos():
    return [carregar(p.name[:2]) for p in sorted(CENARIOS.glob("[0-9][0-9]_*.py"))]


def progresso():
    try:
        return json.loads(PROGRESSO.read_text())
    except (OSError, ValueError):
        return {}


def morrer_com_o_pai():
    """Serviço do laboratório recebe SIGKILL se o nl.py morrer (terminal fechado, kill)."""
    import ctypes
    ctypes.CDLL(None).prctl(1, signal.SIGKILL)  # PR_SET_PDEATHSIG


def sair_com_limpeza(sinal, _quadro):
    raise SystemExit(128 + sinal)


class Lab:
    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.servicos = {}

    def sh(self, cmd):
        subprocess.run(cmd, shell=True, check=True)

    def em(self, no, cmd, timeout=15):
        return subprocess.run(["ip", "netns", "exec", no, "sh", "-c", cmd],
                              capture_output=True, text=True, timeout=timeout)

    def servico(self, no, cmd):
        log = open(self.pasta / f"{no}.log", "a")
        self.servicos[no] = subprocess.Popen(["ip", "netns", "exec", no, "sh", "-c", cmd],
                                             stdout=log, stderr=log, start_new_session=True,
                                             preexec_fn=morrer_com_o_pai)


def montar(lab):
    p = lab.pasta
    lab.sh("mount -t tmpfs none /run && mkdir -p /run/netns /run/systemd/resolve")
    for no in ("cliente", "roteador", "servidor", "dns"):
        lab.sh(f"ip netns add {no} && ip -n {no} link set lo up")
    lab.sh("ip link add eth0 netns cliente type veth peer name lan0 netns roteador")
    lab.sh("ip -n roteador link add br0 type bridge")
    for no, porta in (("servidor", "p-srv"), ("dns", "p-dns")):
        lab.sh(f"ip link add eth0 netns {no} type veth peer name {porta} netns roteador")
        lab.sh(f"ip -n roteador link set {porta} master br0 up")
    lab.sh("ip -n roteador link set br0 up && ip -n roteador link set lan0 up")
    lab.sh("ip -n roteador addr add 192.168.1.1/24 dev lan0")
    lab.sh("ip -n roteador addr add 10.0.0.1/24 dev br0")
    lab.sh("ip netns exec roteador sysctl -qw net.ipv4.ip_forward=1")
    for no, ip, gw in (("cliente", "192.168.1.10/24", "192.168.1.1"),
                       ("servidor", "10.0.0.10/24", "10.0.0.1"),
                       ("dns", "10.0.0.53/24", "10.0.0.1")):
        lab.sh(f"ip -n {no} addr add {ip} dev eth0 && ip -n {no} link set eth0 up")
        lab.sh(f"ip -n {no} route add default via {gw}")

    # /etc/resolv.conf no Fedora aponta pra /run/systemd/resolve, que agora é nosso
    Path("/run/systemd/resolve/stub-resolv.conf").write_text("nameserver 10.0.0.53\n")
    hosts = p / "hosts"
    hosts.write_text("127.0.0.1 localhost\n::1 localhost\n")
    lab.sh(f"mount --bind {hosts} /etc/hosts")

    www = p / "www"
    www.mkdir()
    (www / "index.html").write_text("site.lab ok\n")
    with open(www / "grande.bin", "wb") as f:
        f.write(os.urandom(2 * 1024 * 1024))
    lab.servico("servidor", f"exec python3 -m http.server 80 --bind 0.0.0.0 -d {www}")
    lab.servico("dns", "exec dnsmasq -d --no-resolv --no-hosts --address=/site.lab/10.0.0.10 --local=/lab/ "
                       "--listen-address=10.0.0.53 --bind-interfaces -u root -g root --pid-file=")
    for _ in range(40):
        ok_web = lab.em("servidor", "ss -tln | grep -q ':80 '").returncode == 0
        ok_dns = lab.em("dns", "ss -uln | grep -q '10.0.0.53:53 '").returncode == 0
        if ok_web and ok_dns:
            break
        time.sleep(0.1)


def checar_site(lab):
    r = lab.em("cliente", "curl -s -m 4 http://site.lab/")
    return [(r.stdout.strip() == "site.lab ok", "curl http://site.lab/ no cliente")]


def rcfile(pasta, n):
    rc = pasta / "rc"
    nl = f"python3 {AQUI / 'nl.py'}"
    rc.write_text(f"""
[ -f ~/.bashrc ] && . ~/.bashrc
export NL_PASTA={pasta}
alias tcpdump='tcpdump -Z root'
em() {{ ip netns exec "$1" env NL_NO="$1" bash --rcfile {rc}; }}
topologia() {{ {nl} _topologia; }}
chamado() {{ {nl} _chamado {n}; }}
dica() {{ {nl} _dica {n}; }}
verificar() {{ {nl} _verificar {n}; }}
lista() {{ {nl} lista; }}
caso() {{ {nl} _existe "$1" && echo "$1" > "$NL_PROXIMO" && kill -HUP "$NL_FORA"; }}
proximo() {{ caso "$({nl} _seguinte {n})"; }}
reiniciar() {{ caso {n}; }}
cola() {{ {nl} _cola "$@"; }}
[ -z "$NL_FORA" ] && export NL_FORA=$$
PS1="\\[\\e[1;33m\\][caso {n} | ${{NL_NO:-fora}}]\\[\\e[0m\\] \\w \\$ "
""")
    return rc


def matar_o_resto():
    """Mata tudo que ficou vivo dentro deste user namespace (serviços, coisas que ele subiu)."""
    eu = os.readlink("/proc/self/ns/user")
    for d in Path("/proc").iterdir():
        if d.name.isdigit() and int(d.name) != os.getpid():
            try:
                if os.readlink(d / "ns/user") == eu:
                    os.kill(int(d.name), 9)
            except OSError:
                pass


def dentro(n):
    for sinal in (signal.SIGHUP, signal.SIGTERM):
        signal.signal(sinal, sair_com_limpeza)
    mod = carregar(n)
    pasta = Path(tempfile.mkdtemp(prefix="netlings-"))
    os.environ["NL_PASTA"] = str(pasta)
    lab = Lab(pasta)
    try:
        montar(lab)
        mod.quebrar(lab)
        rc = rcfile(pasta, n)
        print(f"\n\033[1mCaso {int(n):02d}: {mod.TITULO}\033[0m")
        mostrar_chamado(mod)
        print("comandos do laboratório:\n"
              "  em <nó>      abre um shell no nó (cliente, roteador, servidor, dns); exit volta\n"
              "  topologia    o desenho da rede como ela DEVERIA ser\n"
              "  cola         os comandos por degrau (cola erros · cola tcpdump · cola consertar)\n"
              "  chamado      relê a reclamação\n"
              "  dica         uma dica por vez (não dá a resposta)\n"
              "  verificar    testa se resolveu\n"
              "  caso N       troca pro caso N (proximo: o seguinte; lista: todos)\n"
              "  reiniciar    monta este caso de novo, quebrado como no começo\n"
              "  exit         (aqui fora) fecha o laboratório; tudo some\n"
              f"anote o raciocínio em respostas/{mod.NOME[:2]}.md\n")
        subprocess.run(["bash", "--rcfile", str(rc)])
    finally:
        matar_o_resto()
        shutil.rmtree(pasta, ignore_errors=True)


def mostrar_chamado(mod):
    print("\n\033[36m" + mod.CHAMADO.strip() + "\033[0m\n")


def verificar(n):
    mod = carregar(n)
    lab = Lab(os.environ["NL_PASTA"])
    resultados = checar_site(lab) + (mod.verificar(lab) if hasattr(mod, "verificar") else [])
    for ok, msg in resultados:
        print(("  \033[32m✓\033[0m " if ok else "  \033[31m✗\033[0m ") + msg)
    if all(ok for ok, _ in resultados):
        prog = progresso()
        prog[mod.NOME[:2]] = time.strftime("%Y-%m-%d %H:%M")
        PROGRESSO.write_text(json.dumps(prog, indent=1))
        resp = RESPOSTAS / f"{mod.NOME[:2]}.md"
        if getattr(mod, "CHECKPOINT", False):
            print(f"\ncheckpoint feito. o que estranhou fica em {resp}; proximo abre o primeiro caso.")
        else:
            print("\nresolvido. " + (f"agora escreve a causa e o caminho em {resp}"
                                    if resp.read_text().count("\n") < 20 else "resposta anotada, boa."))
    else:
        print("\nainda não.")


def dica(n):
    mod = carregar(n)
    cont = Path(os.environ["NL_PASTA"]) / "dicas"
    i = int(cont.read_text()) if cont.exists() else 0
    if i >= len(mod.DICAS):
        print("acabaram as dicas. volta pro último teste que te surpreendeu.")
        return
    print(f"dica {i + 1}/{len(mod.DICAS)}: {mod.DICAS[i]}")
    cont.write_text(str(i + 1))


def lista():
    prog = progresso()
    for mod in todos():
        k = mod.NOME[:2]
        marca = f"\033[32m✓\033[0m {prog[k]}" if k in prog else " "
        if getattr(mod, "CHECKPOINT", False):
            print(("\n" if k != "00" else "") + f"  {k}  \033[1m{mod.TITULO}\033[0m  {marca}")
        else:
            print(f"  {k}    {mod.TITULO:<45} {marca}")
    pendentes = [m.NOME[:2] for m in todos() if m.NOME[:2] not in prog]
    if pendentes:
        print(f"\npróximo: python3 nl.py {int(pendentes[0])}")


def cola(tema="escada"):
    secoes = {}
    for bloco in (AQUI / "cola.txt").read_text().split("## ")[1:]:
        nome, _, corpo = bloco.partition("\n")
        secoes[nome.strip()] = corpo.rstrip()
    print(secoes.get(tema) or f"temas: {', '.join(secoes)}")


def zerar(n=None):
    prog = progresso()
    if n is None:
        prog = {}
    else:
        prog.pop(f"{int(n):02d}", None)
    PROGRESSO.write_text(json.dumps(prog, indent=1))
    print("progresso zerado" + (f" do caso {int(n):02d}" if n is not None else "") +
          ". as respostas em respostas/ continuam lá.")


def seguinte(n):
    nomes = [m.NOME[:2] for m in todos()]
    depois = [k for k in nomes if int(k) > int(n)]
    return int(depois[0]) if depois else None


def varrer_sobras():
    """Apaga pastas de laboratórios que morreram sem limpar (ex.: kill -9)."""
    em_uso = subprocess.run(["ps", "-eo", "cmd"], capture_output=True, text=True).stdout
    tmp = Path(tempfile.gettempdir())
    for d in tmp.glob("netlings-*"):
        if d.name.startswith("netlings-proximo-"):
            if time.time() - d.stat().st_mtime > 86400:
                d.unlink(missing_ok=True)
        elif d.is_dir() and str(d) not in em_uso:
            shutil.rmtree(d, ignore_errors=True)


def abrir(n):
    """Abre o caso n; se lá dentro ele pedir outro (caso N / proximo), abre o outro."""
    varrer_sobras()
    proximo = Path(tempfile.mkstemp(prefix="netlings-proximo-")[1])
    try:
        while n is not None:
            mod = carregar(n)
            RESPOSTAS.mkdir(exist_ok=True)
            resp = RESPOSTAS / f"{mod.NOME[:2]}.md"
            if not resp.exists():
                resp.write_text(getattr(mod, "RESPOSTA", None) or
                                MODELO_RESPOSTA.format(n=mod.NOME[:2], titulo=mod.TITULO))
            proximo.write_text("")
            env = dict(os.environ, NL_PROXIMO=str(proximo))
            env.pop("NL_FORA", None)
            subprocess.run(["unshare", "-rnm", "--", sys.executable,
                            str(AQUI / "nl.py"), "_dentro", str(n)], env=env)
            n = proximo.read_text().strip() or None
    finally:
        proximo.unlink(missing_ok=True)


def main():
    a = sys.argv[1:]
    if not a or a[0] == "lista":
        lista()
    elif a[0] == "zerar":
        zerar(a[1] if len(a) > 1 else None)
    elif a[0] == "_cola":
        cola(*a[1:2])
    elif a[0] == "_dentro":
        dentro(a[1])
    elif a[0] == "_verificar":
        verificar(a[1])
    elif a[0] == "_dica":
        dica(a[1])
    elif a[0] == "_chamado":
        mostrar_chamado(carregar(a[1]))
    elif a[0] == "_topologia":
        print(TOPOLOGIA)
    elif a[0] == "_existe":
        ok = len(a) > 1 and a[1].isdigit() and any(CENARIOS.glob(f"{int(a[1]):02d}_*.py"))
        if not ok:
            print("caso não existe. lista mostra os que tem." if len(a) > 1 and a[1] else "acabaram os casos.")
        sys.exit(0 if ok else 1)
    elif a[0] == "_seguinte":
        print(seguinte(a[1]) or "")
    elif a[0].isdigit():
        abrir(a[0])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
