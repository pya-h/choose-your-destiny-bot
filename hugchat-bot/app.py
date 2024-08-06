import logging
from payagraph.bot import *
from payagraph.containers import *
from payagraph.keyboards import *
from payagraph.tools import *
from decouple import config
from models.user import UserStates, User
from tools import manuwriter
from typing import Union
from tools.exceptions import *
from hugchat_interface import HugchatInterface


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# read .env configs
# You bot data
BOT_TOKEN = config('BOT_TOKEN')
HOST_URL = config('HOST_URL')
BOT_USERNAME = config('BOT_USERNAME')
HUGCHAT_EMAIL = config('HUGCHAT_EMAIL')
HUGCHAT_PASSWORD = config('HUGCHAT_PASSWORD')
# Read the text resource containing the multilanguage data for the bot texts, messages, commands and etc.
# Also you can write your texts by hard coding but it will be hard implementing multilanguage texts that way,
text_resources = manuwriter.load_json('texts', 'resources')

def play_handler(bot: TelegramBot, message: GenericMessage) -> Union[GenericMessage, Keyboard|InlineKeyboard]:
    hi = HugchatInterface(HUGCHAT_EMAIL, HUGCHAT_PASSWORD)
    answer = hi.activate(model_index=0, pattern_prompt="Generate a random interactive story with random genre. Then inside the stpry, as story is going give the me choices, then i will input my choice and you should continue the story with my decisions. return ENDOFGAME when the story is completed.")
    user = User.Get(message.chat_id)
    user.hugchat = hi
    user.state = UserStates.PLAYING
    return GenericMessage.Text(user.chat_id, answer), Keyboard(bot.keyword("gameover", user.language))

def playing_state_handler(bot: TelegramBot, message: GenericMessage) -> Union[GenericMessage, Keyboard|InlineKeyboard]:
    choice = message.text
    user = User.Get(message.chat_id)
    if choice == bot.keyword("gameover", user.language):
        user.hugchat = None
        lang = user.language
        del User.Instances[user.chat_id ]
        return GenericMessage.Text(message.chat_id, bot.text("game_ended", lang)), None
    res = user.hugchat.prompt(choice)
    return GenericMessage.Text(user.chat_id, res), Keyboard(bot.keyword("gameover", user.language))

main_keyboard = {
    'en': Keyboard(text_resources["keywords"]["play"]["en"]),
    'fa': Keyboard(text_resources["keywords"]["play"]["fa"])
}

bot = TelegramBot(token=BOT_TOKEN, username=BOT_USERNAME, host_url=HOST_URL, text_resources=text_resources, _main_keyboard=main_keyboard)
bot.add_command_handler(command="start", handler=play_handler)
bot.add_state_handler(state=UserStates.PLAYING, handler=playing_state_handler)
bot.add_message_handler(message=bot.keyword('play'), handler=play_handler)
bot.start_polling(0.5)

if __name__ == '__main__':
    bot.go(debug=False)  # Run the Flask app
