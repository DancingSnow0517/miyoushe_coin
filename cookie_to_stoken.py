import asyncio
import contextlib
import os
import re
import sys
from typing import Optional

import httpx

STOKEN_API = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket'


async def get_stoken_by_login_ticket(login_ticket: str, mys_id: str) -> Optional[str]:
    with contextlib.suppress(Exception):
        async with httpx.AsyncClient() as client:
            data = await client.get(
                STOKEN_API,
                headers={
                    'x-rpc-app_version': '2.11.2',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
                    'x-rpc-client_type': '5',
                    'Referer': 'https://webstatic.mihoyo.com/',
                    'Origin': 'https://webstatic.mihoyo.com',
                },
                params={'login_ticket': login_ticket, 'token_types': '3', 'uid': mys_id},
            )
        data = data.json()
        return data['data']['list'][0]['token']
    return None


async def to_stoken(cookie: str):
    if mys_id := re.search(r'(?:(?:login_uid|account_mid|account_id|stmid|ltmid|stuid|ltuid)(?:_v2)?)=(\d+)', cookie):
        mys_id = mys_id[1]
    login_ticket_match = re.search(r'(?:login_ticket|login_ticket_v2)=([0-9a-zA-Z]+)', cookie)
    login_ticket = login_ticket_match[1] if login_ticket_match else None
    stoken_match = re.search(r'(?:stoken|stoken_v2)=([0-9a-zA-Z]+)', cookie)
    stoken = stoken_match[1] if stoken_match else None
    if login_ticket and not stoken:
        # 如果有login_ticket但没有stoken，就通过login_ticket获取stoken
        stoken = await get_stoken_by_login_ticket(login_ticket, mys_id)

    return f'stuid={mys_id};stoken={stoken};'


if __name__ == '__main__':
    ck = sys.argv[1:]
    cookie = ' '.join(ck) or os.environ.get('COOKIE', '')
    if cookie == '':
        print('未找到COOKIE')
        sys.exit(-1)

    print(asyncio.run(to_stoken(cookie)))
