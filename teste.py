"""Testa cada caso: monta, confere que está quebrado, aplica o conserto do gabarito, confere que passou.
   python3 teste.py [NN ...]   (cada caso no seu unshare)"""
import os, subprocess, sys, tempfile, time
from pathlib import Path
NL = Path(__file__).resolve().parent
CONSERTO = {
 "00": "true",
 "06": "true",
 "09": "true",
 "12": "true",
 "01": "ip -n cliente link set eth0 up && ip -n cliente route add default via 192.168.1.1",
 "02": "ip -n cliente route replace default via 192.168.1.1",
 "03": "ip -n cliente route add default via 192.168.1.1",
 "04": "ip netns exec roteador sysctl -qw net.ipv4.ip_forward=1",
 "05": "ip -n servidor route add default via 10.0.0.1",
 "07": "echo nameserver 10.0.0.53 > /run/systemd/resolve/stub-resolv.conf",
 "08": "grep -v 10.0.0.77 /etc/hosts > $NL_PASTA/h; cat $NL_PASTA/h > /etc/hosts",
 "10": "ip netns exec servidor nft flush ruleset",
 "11": "ip netns exec servidor ss -tlnpH; kill $(ip netns exec servidor ss -tlnpH | grep -o 'pid=[0-9]*' | cut -d= -f2); sleep .3; ip netns exec servidor python3 -m http.server 80 --bind 0.0.0.0 -d $NL_PASTA/www >/dev/null 2>&1 & sleep 1",
 "13": "ip netns exec roteador tc qdisc del dev lan0 root",
 "14": "ip netns exec roteador nft flush ruleset",
}
casos = sys.argv[1:] or sorted(CONSERTO)
for k in casos:
    r = subprocess.run(["unshare", "-rnm", "--", sys.executable, "-c", f"""
import os, subprocess, sys, tempfile
sys.path.insert(0, {str(NL)!r}); import nl
mod = nl.carregar({k!r}); pasta = tempfile.mkdtemp(); os.environ['NL_PASTA'] = pasta
lab = nl.Lab(pasta); nl.montar(lab); mod.quebrar(lab)
chk = lambda: nl.checar_site(lab) + (mod.verificar(lab) if hasattr(mod, 'verificar') else [])
antes = all(ok for ok, _ in chk())
subprocess.run({CONSERTO[k]!r}, shell=True)
depois = chk()
print('antes', 'ok' if antes else 'quebrado', '| depois', depois)
nl.matar_o_resto()
import shutil; shutil.rmtree(pasta, ignore_errors=True)
"""], capture_output=True, text=True, timeout=120)
    print(k, r.stdout.strip(), r.stderr.strip()[-300:])
