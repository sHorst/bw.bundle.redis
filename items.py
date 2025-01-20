
files = {}
directories = {}
svc_systemd = {}

for key,server in node.metadata.get('redis', {}).get('servers', {}).items():
    port = server.get('port', 6379)
    maxmemory = server.get('maxmemory', '200G')

    config = [
        'include /etc/redis/redis.conf',
        '',
    ]
    if server.get('bind', False):
        config += [
            'bind ' + ' '.join(server['bind']),
        ]

    config += [
        f'port {port}',
        '',
        f'pidfile /var/run/redis/redis-server-{key}.pid',
        f'logfile /var/log/redis/redis-server-{key}.log',
        '',
        f'dbfilename dump-{key}.rdb',
        f'dir /var/lib/redis/{key}/',
        # disable Protected Mode
        'protected-mode no',
    ]

    if server.get('replicaof', False):
        (server, port) = server['replicaof']
        config += [
            f'replicaof {server} {port}'
        ]

    config += [
        '',
        f'maxmemory {maxmemory}',
    ]


    svc_systemd[f'redis-server@{key}.service'] = {
        'needs': [
            'pkg_apt:redis-server',
            f'file:/etc/redis/redis-{key}.conf',
            f'directory:/var/lib/redis/{key}',
        ],
    }

    files[f'/etc/redis/redis-{key}.conf'] = {
        'triggers': [
            f'svc_systemd:redis-server@{key}.service:restart',
        ],
        'needs': [
            'pkg_apt:redis-server',
        ],
        'content': "\n".join(config) + "\n",
        'owner': 'redis',
        'group': 'redis',
        'mode': '0640',
    }

    directories[f'/var/lib/redis/{key}'] = {
        'needs': [
            'pkg_apt:redis-server',
        ],
        'owner': 'redis',
        'group': 'redis',
        'mode': '0750',
    }
