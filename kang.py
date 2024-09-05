import hashlib
import os
import math
import urllib.request as urllib
from io import BytesIO
from PIL import Image
from pyrogram import Client
import telegram
import logging
import json
from typing import Optional, List
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import TelegramError, Update, Bot
from telegram.ext import CommandHandler, run_async, Updater, Handler, InlineQueryHandler
from telegram.utils.helpers import escape_markdown
from telegram import Message, Chat, MessageEntity, InlineQueryResultArticle
from os import path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Direct token added here
TOKEN = '7314483805:AAHRJNDWLblogkdkwqITcgFh6ZSjrwl8tmg'

updater = telegram.ext.Updater(token=TOKEN)
bot = updater.bot
dispatcher = updater.dispatcher

# Admin chat IDs added here
ADMIN_CHAT_IDS = [7165556607, 5985044373]

START_TEXT = """
Hey! I'm {}, Welcome To Devil Sticker Bot\n\nThis Bot Created By @Shahil44 & @D3VIL_BOY)
""".format(dispatcher.bot.first_name)

# Notify admins about new users
def notify_admins(user):
    for admin_id in ADMIN_CHAT_IDS:
        bot.send_message(chat_id=admin_id, text=f"New user {user.full_name} ({user.id}) started using the bot!")

@run_async
def start(bot: Bot, update: Update):
    if update.effective_chat.type == "private":
        # Notify the admin on new user registration
        notify_admins(update.effective_user)
        
        update.effective_message.reply_text(START_TEXT, parse_mode=ParseMode.MARKDOWN)

@run_async
def kang(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message
    user = update.effective_user
    packnum = 0
    packname = f"a{str(user.id)}_by_{bot.username}"
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = f"a{packnum}_{str(user.id)}_by_{bot.username}"
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1
    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Yea, I can't kang that.")
        kang_file = bot.get_file(file_id)
        kang_file.download('kangsticker.png')
        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"
        kangsticker = "kangsticker.png"
        try:
            im = Image.open(kangsticker)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512/size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512/size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                maxsize = (512, 512)
                im.thumbnail(maxsize)
            if not msg.reply_to_message.sticker:
                im.save(kangsticker, "PNG")
            bot.add_sticker_to_set(user_id=user.id, name=packname,
                                    png_sticker=open('kangsticker.png', 'rb'), emojis=sticker_emoji)
            msg.reply_text(f"Sticker successfully added to [pack](t.me/addstickers/{packname})" +
                            f"\nEmoji is: {sticker_emoji}", parse_mode=ParseMode.MARKDOWN)
        except OSError as e:
            msg.reply_text("I can only kang images m8.")
            print(e)
            return
        except TelegramError as e:
            if (
                e.message
                == "Internal Server Error: sticker set not found (500)"
            ):
                msg.reply_text(
                    (
                        (
                            (
                                f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                                + "\n"
                                "Emoji is:"
                            )
                            + " "
                        )
                        + sticker_emoji
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )

            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "PNG")
                bot.add_sticker_to_set(user_id=user.id, name=packname,
                                        png_sticker=open('kangsticker.png', 'rb'), emojis=sticker_emoji)
                msg.reply_text(f"Sticker successfully added to [pack](t.me/addstickers/{packname})" +
                                f"\nEmoji is: {sticker_emoji}", parse_mode=ParseMode.MARKDOWN)
            elif e.message == "Stickers_too_much":
                msg.reply_text("Max packsize reached. Press F to pay respecc.")
            elif e.message == "Stickerset_invalid":
                makepack_internal(msg, user, open('kangsticker.png', 'rb'), sticker_emoji, bot, packname, packnum)
            print(e)
    else:
        packs = "Please reply to a sticker, or image to kang it!\nOh, by the way. here are your packs:\n"
        if packnum > 0:
            firstpackname = f"a{str(user.id)}_by_{bot.username}"
            for i in range(packnum + 1):
                if i == 0:
                    packs += f"[pack](t.me/addstickers/{firstpackname})\n"
                else:
                    packs += f"[pack{i}](t.me/addstickers/{packname})\n"
        else:
            packs += f"[pack](t.me/addstickers/{packname})"
        msg.reply_text(packs, parse_mode=ParseMode.MARKDOWN)
    if os.path.isfile("kangsticker.png"):
        os.remove("kangsticker.png")


# Existing handlers remain
kang_handler = CommandHandler('kang', kang, pass_args=True)
start_handler = CommandHandler('start', start)

dispatcher.add_handler(kang_handler)
dispatcher.add_handler(start_handler)

updater.start_polling(timeout=15, read_latency=4)
updater.idle()
