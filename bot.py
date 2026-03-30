import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from handlers import common, garden, shops, admin
from config import my_token

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

start_time = time.time()
async def main():
    bot = Bot(token=my_token)
    dp = Dispatcher()

    dp.include_routers(
        common.router,
        garden.router,
        shops.router,
        admin.router
    )

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.info('Бот запущен')
    asyncio.run(main())