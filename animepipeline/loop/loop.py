import asyncio


# 依赖注入 ServerConfig, RssConfig, Store等
async def loop() -> None:
    while True:
        print("loop")

        await asyncio.sleep(60)
