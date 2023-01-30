import redis

def move_xp():
    r = redis.Redis(host='localhost', port=6379, db=0)
    dirty_keys = list( map( lambda k: k.decode(), r.keys("*:xp:b'*'") ) )
    clean_keys = list( map( clean_key, dirty_keys ) )
    print(f"{dirty_keys, clean_keys}")

def clean_key(key):
    key_part = key.split(':')
    key_prefix = ':'.join(key_part[:-1])
    dirty_part = key_part[-1]
    clean_part = dirty_part[2:-1]
    return f"{key_prefix}:{clean_part}"

if __name__ == '__main__':
    move_xp()
