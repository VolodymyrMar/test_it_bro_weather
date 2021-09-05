import os
from flask import Flask
from threading import Thread
from weather import parse

app = Flask(__name__)


@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)


if __name__ == '__main__':
    thread = Thread(target=parse)
    thread.daemon = True
    thread.start()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
