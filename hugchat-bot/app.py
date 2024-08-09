import logging
from payagram.bot import *
from payagram.containers import *
from payagram.keyboards import *
from payagram.tools import *
from decouple import config
from models.user import UserStates, User
from tools import manuwriter
from typing import Union
from tools.exceptions import *
from hugchat_interface import HugchatInterface
import shutil


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
INTRACTIVE_STORY_PROMPT = "Generate a random interactive story with random genre. Then inside the stpry, as story is going give the me choices, then i will input my choice and you should continue the story with my decisions. return ENDOFGAME when the story is completed."

async def play_handler(bot: TelegramBot, message: GenericMessage) -> Union[GenericMessage, Keyboard|InlineKeyboard]:
    try:
        user = User.Get(message.chat_id)
        response_msg = GenericMessage.Text(user.chat_id, bot.text("wait_to_generate_story", user.language))
        keyboard = Keyboard(bot.keyword("gameover", user.language))
        update = await bot.send(response_msg, keyboard)
        response_msg.id = update['result']['message_id']
        hi = HugchatInterface(HUGCHAT_EMAIL, HUGCHAT_PASSWORD, user.chat_id)
        answer = hi.activate(pattern_prompt=INTRACTIVE_STORY_PROMPT)
        user.hugchat = hi
        user.state = UserStates.PLAYING
        response_msg.text = str(answer)
        # response_msg.replace_on_previous = True
    except Exception as ex:
        print(ex)
    return response_msg, keyboard

async def playing_state_handler(bot: TelegramBot, message: GenericMessage) -> Union[GenericMessage, Keyboard|InlineKeyboard]:
    choice = message.text
    user = User.Get(message.chat_id)
    if choice == bot.keyword("gameover", user.language):
        lang = "en"
        try:
            shutil.rmtree(user.hugchat.cookie_dir_path)
            user.hugchat = None
            lang = user.language
            del User.Instances[user.chat_id]
        except Exception as ex:
            print("Game end for user", message.chat_id, "failed:", ex)
        return GenericMessage.Text(message.chat_id, bot.text("game_ended", lang)), None
    keyboard = Keyboard(bot.keyword("gameover", user.language))
    response_msg = GenericMessage.Text(user.chat_id, bot.text("wait_to_take_action", user.language))
    update = await bot.send(response_msg, keyboard)
    response_msg.id = update['result']['message_id']
    res = user.hugchat.prompt(choice)
    response_msg.text = str(res)
    # response_msg.replace_on_previous = True
    return response_msg, keyboard

main_keyboard = {
    'en': Keyboard(text_resources["keywords"]["play"]["en"]),
    'fa': Keyboard(text_resources["keywords"]["play"]["fa"])
}

bot = TelegramBot(token=BOT_TOKEN, username=BOT_USERNAME, host_url=HOST_URL, text_resources=text_resources, _main_keyboard=main_keyboard)
bot.add_command_handler(command="start", handler=play_handler)
bot.add_state_handler(state=UserStates.PLAYING, handler=playing_state_handler)
bot.add_message_handler(message=bot.keyword('play'), handler=play_handler)

if __name__ == '__main__':
    bot.go(debug=False, polling=True, polling_interval=0.1)  # Run the Flask app
