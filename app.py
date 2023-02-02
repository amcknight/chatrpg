from flask import Flask, url_for, render_template, request
from waitress import serve
from markupsafe import escape
import redis
import json

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route("/")
def event_worker():
    return render_template('app.html')

@app.get("/event")
def event():
    e = r.lpop('events')
    if e:
        return e
    else :
        return 'No Events', 204

@app.post("/shown")
def shown():
    event = request.get_json()
    r.rpush('shown', json.dumps(event))
    return 'Shown Message Recieved', 201

@app.get("/<name>")
def player(name):
    return f"<p>Hello, {escape(name)}! This should show stuff about you, but not doesn't yet.</p>"

with app.test_request_context():
    url_for('static', filename='style.css')

if __name__ == '__main__':
    serve(app)
