import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.handlers import quick, start, wizard

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(
        token=os.environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(quick.router)
    dp.include_router(wizard.router)

    webhook_url = os.getenv("WEBHOOK_URL")

    if webhook_url:
        # Railway / Render deployment — webhook mode
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
        port = int(os.getenv("PORT", "8080"))

        await bot.set_webhook(
            url=webhook_url + webhook_path,
            drop_pending_updates=True,
        )
        logger.info("Starting webhook on port %d", port)

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=webhook_path)
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=port)
        await site.start()
        logger.info("Webhook server running on port %d", port)
        await asyncio.Event().wait()  # run forever
    else:
        # Local development — long polling
        logger.info("Starting polling (local dev mode)")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
