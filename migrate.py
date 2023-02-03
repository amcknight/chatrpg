import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def fill_event_queue():
    es = [1,2] * 10
    r.rpush('events', *es)

def merge_xp():
    dirty_keys = list( map( lambda k: k.decode(), r.keys("*:xp:b'*'") ) )
    clean_keys = list( map( clean_key, dirty_keys ) )

    for (dk, ck) in zip(dirty_keys, clean_keys):
        r.incrby(ck, r.get(dk))
        r.delete(dk)

# Warning, this is not idempotent!
def add_key_prefix(key_pattern, prefix, dry = False):
    for old_key in r.scan_iter(key_pattern):
        old_key = old_key.decode()
        val = r.get(old_key).decode()
        new_key = f'{prefix}:{old_key}'
        print(f"Moving {old_key} to {new_key}")
        if not dry:
            r.set(new_key, val)
            r.delete(old_key)

def clean_key(key):
    key_part = key.split(':')
    key_prefix = ':'.join(key_part[:-1])
    dirty_part = key_part[-1]
    clean_part = dirty_part[2:-1]
    return f"{key_prefix}:{clean_part}"

def copy_db(db_id):
    for key_bytes in r.scan_iter():
        key = key_bytes.decode()
        r.copy(key, key, destination_db=db_id)

if __name__ == '__main__':
    copy_db(1)
    add_key_prefix('*:place', 'player', dry=True)
    add_key_prefix('*:job', 'player', dry=True)
    add_key_prefix('*:xp:*', 'player', dry=True)
