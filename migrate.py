import redis

def move_xp():
    r = redis.Redis(host='localhost', port=6379, db=0)
    keys = list( map( lambda k: k.decode(), r.keys('*:xp:*') ) )
    
    print(f"{keys}")

if __name__ == '__main__':
    move_xp()
