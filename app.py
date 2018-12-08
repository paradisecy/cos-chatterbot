from flask import Flask, render_template, request
from bot import Bot
from string import Template
from scrapy.crawler import CrawlerProcess
from spiders.ouc_modules import OucModulesSpider
import os
import json
app = Flask(__name__)
current_path = os.path.dirname(os.path.realpath(__file__))
module_json = "cos-chatterbot/modules.json"
module_yml = os.path.join(current_path, "data/cos/modules.yml")

if os.path.exists(module_json):
    os.remove(module_json)

crawler = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': module_json
})

crawler.crawl(OucModulesSpider)
crawler.start()

if os.path.exists(module_yml):
    os.remove(module_yml)

with open(module_yml, "w") as f:
    f.write('categories:' + '\n')
    f.write('- modules' + '\n')
    f.write('conversations:' + '\n')
    with open(module_json) as mj:
        for item in json.load(mj):
            f.write('- - ' + item['code']+'\n')
            f.write('  - ' + '^' + item['code'] + '\n')
f.close()
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
    app.run(debug=True, use_reloader=False)
