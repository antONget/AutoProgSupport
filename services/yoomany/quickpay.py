from yoomoney import Quickpay, Client
from uuid import uuid4
from time import sleep
from config_data.config import Config, load_config

config: Config = load_config()

client = Client(
    token=config.tg_bot.yoomoney_access_token
)


async def yoomany_payment(amount: int):
    user_id = uuid4()
    quickpay = Quickpay(
        receiver=config.tg_bot.yoomoney_receiver,
        quickpay_form='shop',
        targets='Оплата услуги',
        paymentType='SB',
        sum=amount,
        label=f'{user_id}'
    )
    return quickpay.base_url, quickpay.redirected_url, user_id


async def yoomany_chek_payment(payment_id: str):
    history = client.operation_history(label=payment_id)
    for operation in history.operations:
        if operation.status == "success":
            return True
        else:
            return False
