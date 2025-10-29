import asyncio
import main

async def run():
    print('/health ->', await main.health())
    from main import UserText
    print('/test ->', await main.test_endpoint(UserText(text='test')))
    print('/analyze ->', await main.analyze(UserText(text='Marek, 35 lat, czas na 5km: 22:45')))

if __name__ == '__main__':
    asyncio.run(run())
