from bot import bot
cosbot = bot(train=True)
previous_st = cosbot.bot.get_response("test")
new_st = cosbot.bot.get_response("hello")
cosbot.bot.learn_response(new_st, previous_st)

value = cosbot.bot.get_response("test")
print(value)
