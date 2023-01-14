import asyncio
import os
import logging

from aiogram import Dispatcher, Bot, types
import nest_asyncio
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from dotenv import load_dotenv

from event_parser import EventParser

nest_asyncio.apply()

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
tg_bot = Bot(token=TG_TOKEN)
CHAT_ID = os.getenv('CHAT_ID')
dp = Dispatcher(tg_bot)

VK_TOKEN = os.getenv('VK_TOKEN')
vk_session = vk_api.VkApi(token=VK_TOKEN)
GROUP_ID = os.getenv('GROUP_ID')

long_poll = VkBotLongPoll(vk_session, group_id=GROUP_ID)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


async def main():
    for event in long_poll.listen():
        event = EventParser(event)
        if event.has_attachment:
            media = types.MediaGroup()
            for url in event.extract_pictures():
                media.attach_photo(url, caption=event.text)
            await tg_bot.send_media_group(CHAT_ID, media)
            continue
        await tg_bot.send_message(CHAT_ID, event.text)


if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
        loop.close()
    except:
        pass
    asyncio.run(main())
