import asyncio


async def loop() -> None:
    while True:
        print("loop")

        await asyncio.sleep(60)
