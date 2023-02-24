import asyncio
import contextlib
import hashlib
import json
import os
import random
import string
import sys
import time
from typing import Optional

import httpx

# 米游社的API列表
bbs_cookie_url = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
bbs_cookie_url2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'
bbs_tasks_list = 'https://bbs-api.mihoyo.com/apihub/sapi/getUserMissionsState'
bbs_sign_url = 'https://bbs-api.mihoyo.com/apihub/app/api/signIn'
bbs_list_url = 'https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1'
bbs_detail_url = 'https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}'
bbs_share_url = 'https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1'
bbs_like_url = 'https://bbs-api.mihoyo.com/apihub/sapi/upvotePost'

STOKEN_API = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket'

mihoyo_bbs_List = [
    {
        'id': '1',
        'forumId': '1',
        'name': '崩坏3',
        'url': 'https://bbs.mihoyo.com/bh3/',
    },
    {
        'id': '2',
        'forumId': '26',
        'name': '原神',
        'url': 'https://bbs.mihoyo.com/ys/',
    },
    {
        'id': '3',
        'forumId': '30',
        'name': '崩坏2',
        'url': 'https://bbs.mihoyo.com/bh2/',
    },
    {
        'id': '4',
        'forumId': '37',
        'name': '未定事件簿',
        'url': 'https://bbs.mihoyo.com/wd/',
    },
    {
        'id': '5',
        'forumId': '34',
        'name': '大别野',
        'url': 'https://bbs.mihoyo.com/dby/',
    },
    {
        'id': '6',
        'forumId': '52',
        'name': '崩坏：星穹铁道',
        'url': 'https://bbs.mihoyo.com/sr/',
    },
    {
        'id': '8',
        'forumId': '57',
        'name': '绝区零',
        'url': 'https://bbs.mihoyo.com/zzz/'
    }
]


def random_hex(length: int) -> str:
    """
    生成指定长度的随机字符串
    :param length: 长度
    :return: 随机字符串
    """
    result = hex(random.randint(0, 16 ** length)).replace('0x', '').upper()
    if len(result) < length:
        result = '0' * (length - len(result)) + result
    return result


def random_text(length: int) -> str:
    """
    生成指定长度的随机字符串
    :param length: 长度
    :return: 随机字符串
    """
    return ''.join(random.sample(string.ascii_lowercase + string.digits, length))


def md5(text: str) -> str:
    """
    md5加密
    :param text: 文本
    :return: md5加密后的文本
    """
    md5_ = hashlib.md5()
    md5_.update(text.encode())
    return md5_.hexdigest()


def get_ds(q: str = '', b: dict = None, mhy_bbs_sign: bool = False) -> str:
    """
    生成米游社headers的ds_token
    :param q: 查询
    :param b: 请求体
    :param mhy_bbs_sign: 是否为米游社讨论区签到
    :return: ds_token
    """
    br = json.dumps(b) if b else ''
    if mhy_bbs_sign:
        s = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'
    else:
        s = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5(f'salt={s}&t={t}&r={r}&b={br}&q={q}')
    return f'{t},{r},{c}'


def get_old_version_ds(mhy_bbs: bool = False) -> str:
    """
    生成米游社旧版本headers的ds_token
    """
    if mhy_bbs:
        s = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    else:
        s = 'z8DRIUjNDT7IT5IZXvrUAxyupA1peND9'
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5(f"salt={s}&t={t}&r={r}")
    return f"{t},{r},{c}"


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


async def send_to_kook(content: str):
    token = os.environ.get("KOOK_TOKEN", None)
    kook_id = os.environ.get("KOOK_ID", None)
    if token is None:
        print('未找到推送机器人token')
        return
    if kook_id is None:
        print('未找到推送 KOOK id')
        return

    headers = {'Authorization': f'Bot {token}'}
    async with httpx.AsyncClient() as client:
        rep = await client.post(
            url='https://www.kookapp.cn/api/api/v3/direct-message/create',
            headers=headers,
            data={'target_id': kook_id, 'content': content}
        )
        data = rep.json()
        if data['code'] != 0:
            print(f'消息推送失败：{data["message"]}')


async def main(cookie: str):
    headers = {
        'DS': get_old_version_ds(),
        'cookie': cookie,
        'x-rpc-client_type': '2',
        'x-rpc-app_version': '2.34.1',
        'x-rpc-sys_version': '6.0.1',
        'x-rpc-channel': 'miyousheluodi',
        'x-rpc-device_id': random_hex(32),
        'x-rpc-device_name': random_text(random.randint(1, 10)),
        'x-rpc-device_model': 'Mi 10',
        'Referer': 'https://app.mihoyo.com',
        'Host': 'bbs-api.mihoyo.com',
        'User-Agent': 'okhttp/4.8.0'
    }

    posts_list = []
    task_do = {
        'bbs_Sign': False,
        'bbs_Read_posts': False,
        'bbs_Read_posts_num': 3,
        'bbs_Like_posts': False,
        'bbs_Like_posts_num': 5,
        'bbs_Share': False
    }

    # await get_tasks_list()
    async with httpx.AsyncClient() as client:
        req = await client.get(url=bbs_tasks_list, headers=headers)
    data = req.json()
    if data['retcode'] != 0:
        is_valid = False
        print('Cookie已失效' if data['retcode'] in [-100, 10001] else f"出错了:{data['message']} {data['message']}")
        return data['retcode']

    available_coins = data['data']['can_get_points']
    received_coins = data['data']['already_received_points']
    total_coins = data['data']['total_points']

    # 判断今天是否完成
    if available_coins == 0:
        task_do['bbs_Sign'] = True
        task_do['bbs_Read_posts'] = True
        task_do['bbs_Like_posts'] = True
        task_do['bbs_Share'] = True
    else:
        if data['data']['states'][0]['mission_id'] < 62:
            for i in data['data']['states']:
                # 58是讨论区签到
                if i['mission_id'] == 58:
                    if i['is_get_award']:
                        task_do['bbs_Sign'] = True
                # 59是看帖子
                elif i['mission_id'] == 59:
                    if i['is_get_award']:
                        task_do['bbs_Read_posts'] = True
                    else:
                        task_do['bbs_Read_posts_num'] -= i[
                            'happened_times'
                        ]
                # 60是给帖子点赞
                elif i['mission_id'] == 60:
                    if i['is_get_award']:
                        task_do['bbs_Like_posts'] = True
                    else:
                        task_do['bbs_Like_posts_num'] -= i[
                            'happened_times'
                        ]
                # 61是分享帖子
                elif i['mission_id'] == 61:
                    if i['is_get_award']:
                        task_do['bbs_Share'] = True
                        # 分享帖子，是最后一个任务，到这里了下面都是一次性任务，直接跳出循环
                        break
        print(f'今天还可获取 {available_coins} 个米游币')
    # await get_list()
    async with httpx.AsyncClient() as client:
        req = await client.get(
            url=bbs_list_url.format(random.choice([bbs['forumId'] for bbs in mihoyo_bbs_List])),
            headers=headers
        )
    data = req.json()
    posts_list = [[d['post']['post_id'], d['post']['subject']] for d in data['data']['list'][:5]]
    print('获取帖子列表成功')

    async def signing():
        if task_do['bbs_Sign']:
            return '讨论区签到：已经完成过了~'
        header = headers.copy()
        for i in mihoyo_bbs_List:
            header['DS'] = get_ds('', {'gids': i['id']}, True)
            async with httpx.AsyncClient() as client:
                req = await client.post(url=bbs_sign_url, json={'gids': i['id']}, headers=header)
            data = req.json()
            if data['retcode'] != 0:
                if data['retcode'] != 1034:
                    print('Cookie已失效' if data['retcode'] in [-100,
                                                                10001] else f"出错了:{data['retcode']} {data['message']}" if
                    data['retcode'] != 1034 else '遇验证码阻拦')
                return '讨论区签到：失败'
            await asyncio.sleep(random.randint(15, 30))
        print('讨论区签到完成')
        return '讨论区签到：完成！'

    async def read_posts():
        if task_do['bbs_Read_posts']:
            return '浏览帖子：已经完成过了~'
        num_ok = 0
        for i in range(task_do['bbs_Read_posts_num']):
            async with httpx.AsyncClient() as client:
                req = await client.get(url=bbs_detail_url.format(posts_list[i][0]), headers=headers)
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            await asyncio.sleep(random.randint(5, 10))
        print('看帖任务完成')
        return f'浏览帖子：完成{str(num_ok)}个！'

    async def like_posts():
        if task_do['bbs_Like_posts']:
            return '点赞帖子：已经完成过了~'
        num_ok = 0
        num_cancel = 0
        for i in range(task_do['bbs_Like_posts_num']):
            async with httpx.AsyncClient() as client:
                req = await client.post(url=bbs_like_url,
                                        headers=headers,
                                        json={
                                            'post_id': posts_list[i][0],
                                            'is_cancel': False,
                                        })
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            # 取消点赞
            await asyncio.sleep(random.randint(3, 6))
            async with httpx.AsyncClient() as client:
                req = await client.post(url=bbs_like_url,
                                        headers=headers,
                                        json={
                                            'post_id': posts_list[i][0],
                                            'is_cancel': True,
                                        })
            data = req.json()
            if data['message'] == 'OK':
                num_cancel += 1
        print('点赞任务完成')
        await asyncio.sleep(random.randint(5, 10))
        return f'点赞帖子：完成{str(num_ok)}个{"，遇验证码" if num_ok == 0 else ""}！'

    async def share_post():
        if task_do['bbs_Share']:
            return '分享帖子：已经完成过了~'
        for _ in range(3):
            async with httpx.AsyncClient() as client:
                req = await client.get(
                    url=bbs_share_url.format(posts_list[0][0]),
                    headers=headers)
            data = req.json()
            if data['message'] == 'OK':
                return '分享帖子：完成！'
            else:
                await asyncio.sleep(random.randint(5, 10))
        print('分享任务完成')
        await asyncio.sleep(random.randint(5, 10))
        return '分享帖子：完成！'

    tasks_list = [
        signing,
        read_posts,
        like_posts,
        share_post
    ]

    result = '米游币获取结果：\n'
    for task in tasks_list:
        msg = await task()
        result += msg + '\n'

    print(result)

    await send_to_kook(result)


if __name__ == '__main__':
    st = sys.argv[1:]
    stoken = ' '.join(st) or os.environ.get('STOKEN', '')
    if stoken == '':
        print('未找到STOKEN')
        sys.exit(-1)

    sys.exit(asyncio.run(main(stoken)))
