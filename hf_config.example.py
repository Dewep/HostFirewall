hosts = {
    "manage.domain.com": [
        {
            "src": 80,
            "auth": "haproxy",
            "dest": "stat"
        }
    ],
    "seedbox.domain.com": [
        {
            "src": 80,
            "auth": "seedbox",
            "dest": [
                {
                    "path": "/files",
                    "dest": 9090
                },
                {
                    "path": "/",
                    "dest": 9091
                }
            ]
        }
    ],
    "public.domain.com": [
        {
            "src": 80,
            "dest": 9090
        }
    ]
}

auths = {
    "haproxy": [
        {
            "user": "xxxxxxxxx",
            "password": "yyyyyyyyy"
        }
    ],
    "seedbox": [
        {
            "user": "xxxxxxxxx",
            "password": "yyyyyyyyy"
        }
    ]
}

iptables = {
    "ping": True,
    "allow": [22]
}
