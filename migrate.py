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

# Warning, this is not idempotent! Also uses slow 'keys' so not good for massive changes
def add_key_prefix(key_pattern, prefix, dry = False):
    for old_key in r.keys(key_pattern):
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

def backup_db_to(db_id):
    for key_bytes in r.scan_iter():
        key = key_bytes.decode()
        r.copy(key, key, destination_db=db_id)

def restore_db_from(db_id):
    r.flushdb()
    r.select(db_id)
    for key_bytes in r.scan_iter():
        key = key_bytes.decode()
        r.copy(key, key, destination_db=0)
    r.select(0)

def reground_from_primary_info():
    # TODO: Sync for rebuilding `place:<place>:players` from `player:<player>:place`
    pass

if __name__ == '__main__':
    add_key_prefix('*:place', 'player', dry=True)
    add_key_prefix('*:job', 'player', dry=True)
    add_key_prefix('*:xp:*', 'player', dry=True)
