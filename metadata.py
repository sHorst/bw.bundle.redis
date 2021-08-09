defaults = {}

if node.has_bundle('apt'):
    defaults['apt'] = {
        'packages': {
            'redis-server': {'installed': True, },
        }
    }
