import logging
import configparser
import os
import redis

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
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

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

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()