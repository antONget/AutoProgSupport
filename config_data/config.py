from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: str
    support_id: int
    yoomoney_client_id: str
    yoomoney_access_token: str
    yoomoney_receiver: str
    yookassa_id: int
    yookassa_key: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_ids=env('ADMIN_IDS'),
                               support_id=env('SUPPORT_ID'),
                               yoomoney_client_id=env('YOOMONEY_CLIENT_ID'),
                               yoomoney_access_token=env('YOOMONEY_ACCESS_TOKEN'),
                               yoomoney_receiver=env('YOOMONEY_RECEIVER'),
                               yookassa_id=env('YOOKASSA_ID'),
                               yookassa_key=env('YOOKASSA_KEY')
                               ))
