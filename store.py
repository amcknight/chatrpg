import redis
import logging

class Store:
    def __init__(self):
        self.default_job = 'lurker'
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

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
            xp = 0
        return int(xp)

    def get_job(self, player):
        job_key = f"{player}:job"
        job = self.redis.get(job_key)
        if not job:
            self.redis.set(job_key, self.default_job)
            job = self.default_job
        return str(job)
