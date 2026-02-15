import asyncio
from apify_client import ApifyClientAsync

apify_client_async = ApifyClientAsync("apify_api_wV8knzAbg6CPxsQe1gHRP82QZOydWb1pnGf5")

def start_apify_actor(run_input):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_apify_actor(run_input))

async def run_apify_actor(run_input):
    await apify_client_async.actor('nwua9Gu5YrADL7ZDj').start(run_input=run_input)
