from loader import dp
from aiogram.contrib.middlewares.logging import LoggingMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(LoggingMiddleware())
