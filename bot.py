from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import logging
import json
import os


class Bot:
    dbName = "db.sqlite3"
    bot = None
    is_training = False
    teach_placeholder = '>>'
    input_statement = None
    is_read_only = False
    logic_adapters = [
        {
            'import_path': 'chatterbot.logic.BestMatch'
        },
        {
            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
            'threshold': 0.30,
            'default_response': 'I am sorry, but I do not understand.'
        },
    ]

    def __init__(self, train=True):
        logging.basicConfig(level=logging.INFO)
        self.create_bot(train)

    def retrain(self):
        self.bot.storage.drop()
        self.create_bot(True)

    def create_bot(self, train):
        self.bot = ChatBot("cosbot",
                           storage_adapter="chatterbot.storage.SQLStorageAdapter",
                           logic_adapters=self.logic_adapters,
                           filters=["chatterbot.filters.RepetitiveResponseFilter"],
                           read_only=self.is_read_only)
        if train:
            self.bot.set_trainer(ChatterBotCorpusTrainer)
            self.bot.train(os.path.join(os.getcwd(), "data/cos/"))

    def get_response(self, input_text):
        if not self.is_training:
            response = str(self.bot.get_response(input_text))
            return self.check_for_html_response(response)
        else:
            if input_text.startswith(self.teach_placeholder):
                curr_in_stmt = self.bot.input.process_input_statement(input_text.replace(self.teach_placeholder, ''))
                self.bot.learn_response(curr_in_stmt, self.input_statement)
                return '<Empty>'
            else:
                self.input_statement = self.bot.input.process_input_statement(input_text)
                response = str(self.bot.get_response(input_text))
                return self.check_for_html_response(response)

    @staticmethod
    def check_for_html_response(response):
        with open("html_response.json") as js:
            data = json.load(js)
            for item in data["items"]:
                if item["question"] in response:
                    with open(item["html"]) as fs:
                        return response + fs.read()
            return response
