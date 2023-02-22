import asyncio
import os
import re
import sys

from main import get_stoken_by_login_ticket

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