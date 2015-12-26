from hf_config import iptables, auths, hosts

frontend = {}
backend = []
variables = {
    "host": {},
    "auth": {},
    "path": {},
    "back": {}
}
stat = None

def s(part, value):
    if value not in variables[part]:
        variables[part][str(value)] = part + ("-" + value if part == "back" else str(len(variables[part]) + 1))
    return variables[part][str(value)]

def tab(value):
    return "        " + value

for host in hosts:
    for config in hosts[host]:

        if str(config["src"]) not in frontend:
            frontend[str(config["src"])] = {"host": [], "path": [], "auth": [], "aclauth": [], "back": []}
        fe = frontend[str(config["src"])]
        be = {"back": None, "if": [s("host", host)]}
        au = {"auth": None, "if": [s("host", host)]}

        fe["host"].append(host)

        if "auth" in config:
            if config["auth"] not in fe["aclauth"]:
                fe["aclauth"].append(config["auth"])
            au["auth"] = s("auth", config["auth"])

        if isinstance(config["dest"], int):
            be["back"] = s("back", str(config["dest"]))

            if str(config["dest"]) not in backend:
                backend.append(str(config["dest"]))

            fe["back"].append(be)

        elif config["dest"] == "stat":
            be["back"] = s("back", "stat")
            stat = be["back"]

            if "stat" not in backend:
                backend.append("stat")

            fe["back"].append(be)

        else:
            for path in config["dest"]:

                if path["path"] not in fe["path"]:
                    fe["path"].append(path["path"])

                bec = dict(be)
                bec["if"] = list(be["if"])
                bec["back"] = s("back", str(path["dest"]))
                bec["if"].append(s("path", path["path"]))

                if str(path["dest"]) not in backend:
                    backend.append(str(path["dest"]))

                fe["back"].append(bec)

        if "auth" in config:
            fe["auth"].append(au)

print("global")
print(tab("log /dev/log local0"))
print(tab("log /dev/log local1 notice"))
print(tab("chroot /var/lib/haproxy"))
print(tab("user haproxy"))
print(tab("group haproxy"))
print(tab("daemon"))
print(tab("stats socket /var/run/haproxy.sock mode 600 level admin"))
print(tab("stats timeout 2m"))
print("")

print("defaults")
print(tab("log global"))
print(tab("mode http"))
print(tab("balance roundrobin"))
print(tab("option httplog"))
print(tab("option dontlognull"))
print(tab("option httpclose"))
print(tab("option forwardfor"))
print(tab("timeout connect 15s"))
print(tab("timeout client 1m"))
print(tab("timeout server 1m"))
print("")

for auth in auths:
    print("userlist " + auth + "Auth")
    for user in auths[auth]:
        print(tab("user " + user["user"] + " insecure-password " + user["password"]))
    print("")

for port in frontend:
    print("frontend port-" + port)
    print(tab("bind *:" + port))
    print("")
    for host in frontend[port]["host"]:
        print(tab("acl " + s("host", host) + " hdr(host) -i " + host))
    print("")
    for path in frontend[port]["path"]:
        print(tab("acl " + s("path", path) + " url_beg " + path))
    print("")
    for acl in frontend[port]["aclauth"]:
        print(tab("acl " + s("auth", acl) + " http_auth(" + acl + "Auth)"))
    for auth in frontend[port]["auth"]:
        print(tab("http-request auth realm AUTH if " + " ".join(auth["if"]) + " !" + auth["auth"]))
    print("")
    for back in frontend[port]["back"]:
        print(tab("use_backend " + back["back"] + " if " + " ".join(back["if"])))
    print("")

for back in backend:
    print("backend " + s("back", back))
    if back == "stat":
        print(tab("stats enable"))
        print(tab("stats refresh 30s"))
        print(tab("stats show-legends"))
        print(tab("stats show-desc HAProxy"))
        print(tab("stats show-node"))
        print(tab("stats uri /"))
    else:
        print(tab("server proxy 127.0.0.1:" + back + " check"))
    print("")

ports = []
for port in iptables["allow"]:
    ports.append(str(port))
for port in frontend:
    if port != "stat":
        ports.append(str(port))

print("")
print("## IPTABLES")
print("# iptables -F")
print("# iptables -A INPUT -i eth0 -p tcp -m multiport --dports " + ",".join(ports) + " -m state --state NEW,ESTABLISHED -j ACCEPT")
if iptables["ping"]:
    print("# iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT")
print("# iptables -P INPUT DROP")
