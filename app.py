from flask import Flask
from flask import url_for
from flask import render_template
from markupsafe import escape
import redis
import json

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route("/")
def event_worker():
    return render_template('app.html')

@app.route("/event")
def event():
    e = r.lpop(f'events')
    if e:
        return e
    else :
        return 'No Events', 204

@app.route("/<name>")
def player(name):
    return f"<p>Hello, {escape(name)}! This should show stuff about you, but not doesn't yet.</p>"

with app.test_request_context():
    url_for('static', filename='style.css')
