import redis

def move_xp():
    r = redis.Redis(host='localhost', port=6379, db=0)
    dirty_keys = list( map( lambda k: k.decode(), r.keys("*:xp:b'*'") ) )
    clean_keys = list( map( clean_key, dirty_keys ) )
    for key in dirty_keys:
        key_parts = key.split(':')
        clean_keys.append(':'.join(list( map (clean_key, key_parts))))
    
    print(f"{dirty_keys, clean_keys}")

# def dirty_key(key):
#     key_parts = key.split(':')
#     if any(map(dirty_key_part, key_parts)):
#         return True
#     return False

# def dirty_key_part(key_part):
#     try:
#         key_part
#         return True
#     except (UnicodeDecodeError, AttributeError):
#         return False

def clean_key(key):
    key_part = key.split(':')
    key_prefix = key_part[:-1]
    dirty_part = key[-1]
    clean_part = str(dirty_part)
    return f"{key_prefix}:{clean_part}"

if __name__ == '__main__':
    move_xp()
