import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# token = "2058815292:AAFpWPRwz4PDbwyy9QGXviuPl5TvN3e9PvM"
# heroku = "https://powermuslimbot.herokuapp.com/"

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 5000))