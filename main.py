import asyncio
import pathlib

import httpx

cookie = pathlib.Path('cookie.txt').read_text()

limits = httpx.Limits(max_connections=10)
client = httpx.AsyncClient(
    cookies={'.ROBLOSECURITY': cookie},
    limits=limits
)


async def fetch_csrf():
    req = await client.post('https://auth.roblox.com/v1/xbox/disconnect')
    return req.headers['x-csrf-token']


async def clear_page(page_number):
    req = await client.get(f'https://privatemessages.roblox.com/v1/messages?pageNumber={page_number}&pageSize=20&messageTab=Inbox')
    res = req.json()

    msg_ids = [i.get('id') for i in res.get('collection', [])]
    await client.post(
        'https://privatemessages.roblox.com/v1/messages/archive',
        data={"messageIds": msg_ids},
        headers={'x-csrf-token': await fetch_csrf()})


async def main():
    req = await client.get('https://privatemessages.roblox.com/v1/messages?pageNumber=1&pageSize=20&messageTab=Inbox')
    res = req.json()

    if pages := res.get('totalPages', None):
        await asyncio.gather(
            *(clear_page(i) for i in range(pages))
        )

asyncio.run(main())
