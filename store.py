import redis
import time
from fight.fighter import Fighter
from math import floor, sqrt

class Store:
    def __init__(self):
        self.default_job = 'lurker'
        self.default_place = 'home'

    def connect(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def connected(self):
        try:
            return self.redis and self.redis.ping()
        except:
            return False

    def update_xp(self, players, dxp):
        for player in players:
            job = self.get_job(player)
            self.redis.incrby(f"player:{player}:xp:{job}", dxp)

    def get_xp(self, player):
        job = self.get_job(player)
        xp_key = f"player:{player}:xp:{job}"
        xp = self.redis.get(xp_key)
        if not xp:
            self.redis.set(xp_key, 0)
            return 0
        return floor(int(xp)/60)

    def get_xp_left(self, player):
        return self.get_level_xp(self.get_level(player) + 1) - self.get_xp(player)

    def get_job(self, player):
        job_key = f"player:{player}:job"
        job = self.redis.get(job_key)
        if not job:
            self.redis.set(job_key, self.default_job)
            return self.default_job
        return job.decode()

    def get_place(self, player):
        place_key = f"player:{player}:place"
        place = self.redis.get(place_key)
        if not place:
            self.redis.set(place_key, self.default_place)
            return self.default_place
        return place.decode()

    def set_place(self, player, new_place):
        place_key = f"player:{player}:place"
        old_place = self.redis.set(place_key, new_place, get=True)

        new_players_key = f"place:{new_place}:players"
        old_players_key = f"place:{old_place}:players"
        self.redis.sadd(new_players_key, player)
        self.redis.srem(old_players_key, player)

    def get_players_at(self, place):
        players_key = f"place:{place}:players"
        players_bytes = self.redis.smembers(players_key)
        if not players_bytes:
            return []
        
        return list(map(lambda player: player.decode(), players_bytes))

    def get_level(self, player):
        return floor(sqrt(self.get_xp(player)/10))

    def get_level_xp(self, level):
        return level*level*10

    def add_event(self, event):
        self.redis.rpush('events', event)

    def clear_events(self):
        key = 'events'
        events = list(map(lambda b: b.decode(), self.redis.lrange(key, 0, -1)))
        self.redis.delete(key)
        return events

    def next_shown(self):
        return self.redis.lpop('shown')

    def clear_shown(self):
        key = 'events'
        shown = list(map(lambda b: b.decode(), self.redis.lrange(key, 0, -1)))
        self.redis.delete(key)
        return shown

    def schedule_brawl(self, place, sched_time):
        self.redis.zadd("brawltimes", {place:sched_time})

    def next_brawl_place(self):
        brawl_singleton = self.redis.zpopmin("brawltimes")
        if not brawl_singleton: return
        if not len(brawl_singleton) > 0: return

        place, sched_time = brawl_singleton[0]
        place = place.decode()
        sched_time = int(sched_time)

        if sched_time > int(time.time()):
            self.schedule_brawl(place, sched_time)
            return
        
        return place

    def clear_brawls(self):
        key = 'brawltimes'
        vals = list(map(lambda b: b.decode(), self.redis.zrange(key, 0, -1)))
        self.redis.delete(key)
        return vals

    def get_fighter(self, player):
        # TODO: Something correct
        return Fighter(f'{player}1', player, 4, 12, 5, 1, 4, 3)

    def send_all_home(self):
        for key in self.redis.scan_iter(f'place:*:players'):
            self.redis.delete(key.decode())
        for key in self.redis.scan_iter(f'player:*:place'):
            self.redis.delete(key.decode())
