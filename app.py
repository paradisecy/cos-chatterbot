from flask import Flask, render_template, request
from bot import Bot
from string import Template

app = Flask(__name__)

cos_bot = Bot(train=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    return cos_bot.get_response(user_text)


@app.route("/retrain")
def retrain():
    cos_bot.retrain()
    return "done"


@app.route("/train")
def train():
    is_training = int(request.args.get('msg'))
    cos_bot.is_training = bool(is_training)
    return "done"


@app.route("/state")
def state():
    value = Template('$is_training@$is_read_only')
    return value.substitute(is_training=cos_bot.is_training,
                            is_read_only=cos_bot.bot.read_only)


@app.route("/readonly")
def readonly():
    is_readonly = int(request.args.get('msg'))
    cos_bot.set_readonly(bool(is_readonly))
    return "done"


if __name__ == "__main__":
    app.run(debug=True)
