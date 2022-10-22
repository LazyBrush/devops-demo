from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def hello_world():

    env = os.environ.get('SOMETHING')
    return f'<p>[{env}]</p>'
