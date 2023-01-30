import redis

def move_xp():
    r = redis.Redis(host='localhost', port=6379, db=0)
    dirty_keys = list( map( lambda k: k.decode(), r.keys("*:xp:b'*'") ) )
    clean_keys = []
    for key in dirty_keys:
        key_parts = key.split(':')
        clean_keys.append(':'.join(list( map (safe_decode, key_parts))))
    
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

def safe_decode(bytes_or_str):
    try:
        return bytes_or_str.decode()
    except (UnicodeDecodeError, AttributeError):
        return bytes_or_str

if __name__ == '__main__':
    move_xp()
