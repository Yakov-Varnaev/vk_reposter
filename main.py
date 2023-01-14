import asyncio
import os
import logging
from collections import namedtuple
from threading import Thread
from asyncio.events import AbstractEventLoop

from aiogram import Dispatcher, Bot, types, executor
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

# VK_TOKEN = os.getenv('VK_TOKEN')
# vk_session = vk_api.VkApi(token=VK_TOKEN)
# GROUP_ID = os.getenv('GROUP_ID')

# long_poll = VkBotLongPoll(vk_session, group_id=GROUP_ID)


class GroupConfig(namedtuple('GroupConfig', ['id', 'chat', 'token'])):
    pass


groups = []
for i in range(99):
    id, chat, token = os.getenv(f'GROUP_ID_{i}'), os.getenv(f'CHAT_ID_{i}'), os.getenv(f'VK_TOKEN_{i}')
    if id:
        groups.append(GroupConfig(id, chat, token))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


def poller(config: GroupConfig, events):
    log.info(f'[{config.id}] start polling.')
    vk_session = vk_api.VkApi(token=config.token)
    lp = VkBotLongPoll(vk_session, group_id=config.id)
    for event in lp.listen():
        event = EventParser(event)
        events.append(event)
        log.info(f'[{config.id}] got event: {event.text} | {config.chat} | {config.id}')


async def main():
    loop = asyncio.get_event_loop()
    events = []
    for group_conf in groups:
        Thread(target=poller, args=[group_conf, events]).start()

    while True:
        while events:
            event = events.pop()
            await tg_bot.send_message(groups[0].chat, event.text)
            log.info(f'{event.text}')


if __name__ == '__main__':
    asyncio.run(main())
    # main()
