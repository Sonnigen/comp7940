#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import configparser
import os
import redis
import random
import requests

import sys
sys.path.append('/home/sunny/.local/lib/python3.10/site-packages')

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CallbackContext, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv(verbose=True)

os.environ['TMDB_API_KEY'] = '27c6396d2fae1acfa68be73c504f48d5'
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

global redis1

myToken = "5881114142:AAG2uG1SsE81QUj7GRGKI9I20-eUAZRNbT4"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


movies = {
    'Action': ['The Dark Knight', 'Avengers: Endgame', 'John Wick', 'Die Hard', 'Mad Max: Fury Road', 'Terminator 2: Judgment Day', 'Mission: Impossible - Fallout', 'The Matrix', 'Jurassic Park', 'Inception'],
    'Comedy': ['The Hangover', 'Bridesmaids', 'Borat', 'Superbad', 'Mean Girls', 'This Is Spinal Tap', 'Shaun of the Dead', 'Airplane!', 'The Grand Budapest Hotel', 'Napoleon Dynamite'],
    'Drama': ['The Shawshank Redemption', 'Forrest Gump', 'The Godfather', 'A Star is Born', 'Schindler\'s List', 'The Silence of the Lambs', 'Goodfellas', 'The Departed', 'The Green Mile', 'The Revenant'],
    'Romance': ['The Notebook', 'Titanic', 'The Fault in Our Stars', 'The Proposal', 'Crazy Rich Asians', 'La La Land', 'The Best of Me', 'The Lucky One', 'The Vow', 'The Time Traveler\'s Wife'],
    'Horror': ['The Shining', 'The Exorcist', 'Psycho', 'Halloween', 'A Nightmare on Elm Street', 'Scream', 'The Conjuring', 'Get Out', 'Us', 'The Babadook'],
    'Science Fiction': ['Blade Runner', 'Star Wars', 'The Terminator', 'Back to the Future', '2001: A Space Odyssey', 'Interstellar', 'The Martian', 'Avatar', 'The Day the Earth Stood Still', 'War of the Worlds'],
    'Thriller': ['The Silence of the Lambs', 'Seven', 'The Usual Suspects', 'Memento', 'Zodiac', 'Gone Girl', 'Prisoners', 'Shutter Island', 'No Country for Old Men', 'Oldboy'],
    'Adventure': ['Indiana Jones', 'Pirates of the Caribbean', 'The Mummy', 'Jumanji', 'National Treasure', 'The Goonies', 'The Lion King', 'The Jungle Book', 'Aladdin', 'Mulan'],
    'Fantasy': ['The Lord of the Rings', 'Harry Potter', 'The Chronicles of Narnia', 'The Hobbit', 'The NeverEnding Story', 'Pan\'s Labyrinth', 'The Dark Crystal', 'Labyrinth', 'The Princess Bride', 'Willow'],
    'Animation': ['Toy Story', 'Finding Nemo', 'The Lion King', 'Up', 'Spirited Away', 'Inside Out', 'Wall-E', 'Frozen', 'The Incredibles', 'Coco'],
    'Musical': ['The Sound of Music', 'West Side Story', 'Chicago', 'Mamma Mia!', 'Les Miserables', 'Grease', 'The Phantom of the Opera', 'Hairspray', 'La La Land', 'The Greatest Showman'],
    'Documentary': ['Blackfish', 'Fahrenheit 9/11', 'The Cove', 'Bowling for Columbine', 'Super Size Me', 'An Inconvenient Truth', 'March of the Penguins', 'The Act of Killing', 'Icarus', 'Making a Murderer']
}

def get_movie_poster(movie_name: str) -> str:
    """Get the poster of a movie using TMDb API."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0]['poster_path']
        poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
        return poster_url
    return ''

async def recommend_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a recommended movie based on user input."""
    user_input = context.args[0]
    movie_list = movies.get(user_input, [])
    if len(movie_list) > 0:
        recommended_movie = random.choice(movie_list)
        poster_url = get_movie_poster(recommended_movie)
        if poster_url:
            await update.message.reply_photo(photo=poster_url, caption=f"I recommend {recommended_movie} for you!")
        else:
            await update.message.reply_text(f"I recommend {recommended_movie} for you!")
    else:
        await update.message.reply_text("I'm sorry, I don't have any recommendations for that genre.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Helping you helping you.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        await update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')

    except(IndexError, ValueError):
        await update.message.reply_text('Usage: /add <keyword>')

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /hello Kevin is issued."""
    await update.message.reply_text("Good day, " + context.args[0] + "!")

def main() -> None:
    """Start the bot."""
    
    config = configparser.ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config.read(os.path.join(path, 'config.ini'))
    # config.read('config.ini')

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config['TELEGRAM']['ACCESS_TOKEN']).build()

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))


    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("hello", hello))

    # 添加一个命令处理程序，用于根据用户的输入推荐电影
    application.add_handler(CommandHandler("recommend", recommend_movie))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()