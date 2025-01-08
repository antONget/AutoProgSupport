from yoomoney import Quickpay, Client
from uuid import uuid4
from time import sleep
from config_data.config import Config, load_config

config: Config = load_config()

client = Client(
    token=config.tg_bot.yoomoney_access_token
)

label = str(uuid4())

quickpay = Quickpay(
    receiver=config.tg_bot.yoomoney_receiver,
    quickpay_form="paid",
    targets="Платная подписка",
    paymentType="SB",
    sum=2,
    label=label
)

print(quickpay.base_url, quickpay.redirected_url, sep="\n")

history = client.operation_history(label=label)

start = True
while start:
    sleep(10)
    for operation in history.operations:
        if operation.status == "success":
            start = False
            print("Оплпата прошла успешно")
        else:
            print("Оплата не прошла")