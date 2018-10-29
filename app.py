from flask import Flask, render_template, request
from bot import Bot

app = Flask(__name__)

cosbot = Bot(train=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return cosbot.get_response(userText)

@app.route("/retrain")
def retrain():
    cosbot.retrain()
    return "done"

@app.route("/train")
def train():
    is_training = int(request.args.get('msg'))
    cosbot.is_training = bool(is_training)
    return "done"


if __name__ == "__main__":
    app.run(debug=True)
