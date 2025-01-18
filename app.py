import threading
from flask import Flask
import time
from trader import main
from trader_15m import main_15m
from trader_30m import main_30m
from trader_1h import main_1h
from trader_4h import main_4h
from trader_1d import main_1d
import datetime
import pytz
import asyncio

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the Flask App!'


@app.route('/start-task')
def start_task():
    thread = threading.Thread(target=main)
    thread.start()
    return 'Task has been started in the background!'
@app.route('/start-task-15m')
def start_task_15m():
    thread = threading.Thread(target=main_15m)
    thread.start()
    return 'Task has been started in the background 15m!'
@app.route('/start-task-30m')
def start_task_30m():
    thread = threading.Thread(target=main_30m)
    thread.start()
    return 'Task has been started in the background 30m!'
@app.route('/start-task-1h')
def start_task_1h():
    thread = threading.Thread(target=main_1h)
    thread.start()
    return 'Task has been started in the background 1 Hour!'
@app.route('/start-task-4h')
def start_task_4h():
    thread = threading.Thread(target=main_4h)
    thread.start()
    return 'Task has been started in the background 4 Hour!'
@app.route('/start-task-1d')
def start_task_1d():
    thread = threading.Thread(target=main_1d)
    thread.start()
    return 'Task has been started in the background 1 day!'

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Specify your desired port number here
