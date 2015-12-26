# HostFirewall

HAProxy + iptables from a config file

```shell
$> vim hf_config.py
$> python3 hf.py > haproxy.cfg
$> cat haproxy.cfg
global
        log /dev/log local0
        log /dev/log local1 notice
        chroot /var/lib/haproxy
        user haproxy
        group haproxy
        daemon
        stats socket /var/run/haproxy.sock mode 600 level admin
        stats timeout 2m

defaults
        log global
        mode http
        balance roundrobin
        option httplog
        option dontlognull
        option httpclose
        option forwardfor
        timeout connect 15s
        timeout client 1m
        timeout server 1m

userlist haproxyAuth
        user xxxxxxxxx insecure-password yyyyyyyyy

userlist seedboxAuth
        user xxxxxxxxx insecure-password yyyyyyyyy

frontend port-80
        bind *:80

        acl host1 hdr(host) -i public.domain.com
        acl host2 hdr(host) -i manage.domain.com
        acl host3 hdr(host) -i seedbox.domain.com

        acl path1 url_beg /files
        acl path2 url_beg /

        acl auth1 http_auth(haproxyAuth)
        acl auth2 http_auth(seedboxAuth)
        http-request auth realm AUTH if host2 !auth1
        http-request auth realm AUTH if host3 !auth2

        use_backend back-9090 if host1
        use_backend back-stat if host2
        use_backend back-9090 if host3 path1
        use_backend back-9091 if host3 path2

backend back-9090
        server proxy 127.0.0.1:9090 check

backend back-stat
        stats enable
        stats refresh 30s
        stats show-legends
        stats show-desc HAProxy
        stats show-node
        stats uri /

backend back-9091
        server proxy 127.0.0.1:9091 check


## IPTABLES
# iptables -F
# iptables -A INPUT -i eth0 -p tcp -m multiport --dports 22,80 -m state --state NEW,ESTABLISHED -j ACCEPT
# iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT
# iptables -P INPUT DROP
```
