import asyncio
from collections import deque

from aiomoney import YooMoney
from aiomoney.schemas import AccountInfo, Operation, OperationDetails


async def main():
    account = YooMoney(access_token="ACCESS_TOKEN")

    account_info: AccountInfo = await account.account_info
    operation_history: deque[Operation] = await account.get_operation_history()
    operation_details: OperationDetails = await account.get_operation_details(operation_id="999")

    print(account_info, operation_history, operation_details, sep="\n\n")


if __name__ == "__main__":
    asyncio.run(main())