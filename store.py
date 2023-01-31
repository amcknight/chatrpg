import redis
import logging
from math import floor, sqrt

class Store:
    def __init__(self):
        self.default_job = 'lurker'

    def connect(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def connected(self):
        try:
            return self.redis and self.redis.ping()
        except:
            return False

    def update_xp(self, players, dxp):
        for p in players:
            job = self.get_job(p)
            self.redis.incrby(f"{p}:xp:{job}", dxp)

    def get_xp(self, player):
        job = self.get_job(player)
        xp_key = f"{player}:xp:{job}"
        xp = self.redis.get(xp_key)
        if not xp:
            self.redis.set(xp_key, 0)
            return 0
        return floor(int(xp)/60)

    def get_xp_left(self, player):
        return self.get_level_xp(self.get_level(player) + 1) - self.get_xp(player)

    def get_job(self, player):
        job_key = f"{player}:job"
        job = self.redis.get(job_key)
        if not job:
            self.redis.set(job_key, self.default_job)
            return self.default_job
        return job.decode()

    def get_level(self, player):
        return floor(sqrt(self.get_xp(player)/10))

    def get_level_xp(self, level):
        return level*level*10

    def add_battle(self, player):
        battle = self.build_battle(player)
        self.add_event(battle)

    # TODO: Build a real battle
    def build_battle(self, player):
        return 1

    def add_event(self, event):
        self.redis.rpush('events', event)
