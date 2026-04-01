import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from handlers import common, garden, shops, admin
from config import my_token
from logic.admin_logic import restore_all_energy_cycle, random_weather_choise, hydration_min

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

    asyncio.create_task(restore_all_energy_cycle(300)) # каждые 5 минут будет обновление энергии
    asyncio.create_task(random_weather_choise(bot, 1800)) #смена погоды каждый 30 мину 
    asyncio.create_task(hydration_min(300)) # каждые 5 минут понижение/повышение влажности почвы в зависимости от погодных условий

    logging.info('Бот и фоновые задачи запущены')
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.info('Бот запущен')
    asyncio.run(main())
