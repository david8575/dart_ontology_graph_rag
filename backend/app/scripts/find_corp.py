import asyncio
import sys

import httpx

from app.config import get_settings
from app.dart.client import DartClient


async def main(keyword: str) -> None:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30.0) as http:
        client = DartClient(settings.dart_api_key.get_secret_value(), http)
        corps = await client.corp_codes()

    for corp in corps:
        if keyword in corp.corp_name and corp.stock_code:
            print(corp.corp_code, corp.stock_code, corp.corp_name)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
