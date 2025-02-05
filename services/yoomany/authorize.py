from yoomoney import Authorize
from config_data.config import Config, load_config

config: Config = load_config()


Authorize(
    client_id=config.tg_bot.yoomoney_client_id,
    client_secret='',
    redirect_uri="https://site.ru",
    scope=["account-info",
           "operation-history",
           "operation-details",
           "incoming-transfers",
           "payment-p2p",
           "payment-shop",
           ]
)
