from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import logging
import json
import os
from string import Template


class Bot:
    bot = None
    is_training = False
    teach_placeholder = '>>'
    input_statement = None
    current_path = os.path.dirname(os.path.realpath(__file__))
    logic_adapters = [
        {
            'import_path': 'chatterbot.logic.BestMatch'
        },
        {
            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
            'threshold': 0.50,
            'default_response': 'I am sorry, but I do not understand.'
        },
    ]

    def __init__(self, train=True):
        """
        Constructor
        Initialize the bot

        :param train:
        """
        logging.basicConfig(level=logging.INFO)
        self.create_bot(train)

    def retrain(self):
        """
        Retrain the model
        """
        self.bot.storage.drop()
        self.create_bot(True)

    def create_bot(self, train):
        """
        Creates a new ChatBot instances
        and passing the init parameters

        :param train:
        """
        self.bot = ChatBot("cosbot",
                           storage_adapter={
                               'import_path': 'chatterbot.storage.SQLStorageAdapter',
                               'database_uri': 'sqlite:///db.sqlite3'})
                           #logic_adapters=self.logic_adapters)
        if train:
            self.bot.set_trainer(ChatterBotCorpusTrainer)
            self.bot.train(os.path.join(self.current_path, "data/cos/"))

    def get_response(self, input_text):
        """
        Takes an input text and gets back a response.

        The response is passed to some other methods
        to check if the response need to reformatted
        when is related to academic board questions.

        Then checks if needs to show an html content
        and checks for url's and emails and constructs
        html links

        If the bot is in training mode checks if the input
        statement contains a training placeholder at the beginning
        and and update the previous response accordingly

        :param input_text:
        :return:
        """
        if not self.is_training:
            response = str(self.bot.get_response(input_text))
            return self.check_for_href(self.check_for_html_response(self.check_board(response)))
        else:
            if input_text.startswith(self.teach_placeholder):
                curr_in_stmt = self.bot.input.process_input_statement(input_text.replace(self.teach_placeholder, ''))
                self.bot.learn_response(curr_in_stmt, self.input_statement)
                return '<Empty>'
            else:
                self.input_statement = self.bot.input.process_input_statement(input_text)
                response = str(self.bot.get_response(input_text))
                return self.check_for_href(self.check_for_html_response(self.check_board(response)))

    def check_for_html_response(self, response):
        """
        Check if the response is in html_response.json
        and append the html content to the response

        :param response:
        :return:
        """
        with open(os.path.join(self.current_path, "html_response.json")) as js:
            data = json.load(js)
            for item in data["items"]:
                if item["question"] in response:
                    with open(os.path.join(self.current_path, item["html"])) as fs:
                        return response + fs.read()
            return response

    def check_for_href(self, response):
        """
        Check for urls and emails on the response
        text and surround them with the html link tag

        :param response:
        :return:
        """
        extensions = ['@', 'http']
        if any(ext in response for ext in extensions):
            words = response.split(' ')
            for e in extensions:
                for idx, w in enumerate(words):
                    if e in w:
                        if e == extensions[0]:
                            template = Template('<a href="mailto:$mail">$mail</a>')
                            words[idx] = template.substitute(mail=w)
                        elif e == extensions[1]:
                            template = Template('<a href="$url">$url</a>')
                            words[idx] = template.substitute(url=w)
            sep = ' '
            return sep.join(words)
        else:
            return response

    def check_board(self, response):
        """
        Check if the response contains the hash placeholder
        and constructs the text based on the values of board.json

        :param response:
        :return:
        """
        placeholder = '$'
        if response.startswith(placeholder):
            split = list(filter(None, response.split(placeholder)))
            with open(os.path.join(self.current_path, "board.json")) as js:
                data = json.load(js)
                text = ''
                for item in data["board"]:
                    if split[1] == item[split[0]]:
                        pronoun = 'His' if item['gender'] == 'man' else 'Her'
                        phone = ' and phone ' + item['phone'] if item['phone'] else ''
                        text += Template('$name has title of $title. $pronoun email is $email$phone .') \
                            .substitute(name=item['name'],
                                        title=item['title'],
                                        pronoun=pronoun,
                                        email=item['email'],
                                        phone=phone)
                return text
        else:
            return response

    def set_readonly(self, value):
        """
        Sets bot read only property

        :param value:
        """
        self.bot.read_only = value
