from environs import Env
import loguru
import json

logger = loguru.logger
logger.add('Logs/bot_log.log', format='{time} {level} {message}', rotation='512 KB', compression='zip')

env = Env()
env.read_env()

vk_api_version = '5.131'

db_host = 'host.docker.internal'
db_port = 5532
db_user = env.str("POSTGRES_USER")
db_password = env.str("POSTGRES_PASSWORD")
db_name = 'vk_bot_farm'

test_user_id = env.int("test_user_id")
test_user_login = env.str("test_user_login")
test_user_pass = env.str("test_user_pass")
test_user_token = env.str("test_user_token")
test_post_url = env.str("test_post_url")

delay_factor = 1

debug = True
