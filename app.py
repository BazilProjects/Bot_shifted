import threading
from flask import Flask
import time
from trader import main
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Specify your desired port number here
