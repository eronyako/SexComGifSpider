#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Subj: SexComGifSpider
# @File: SexComGifSpider.py
# @Date: 2022/9/26 13:02


import os
import json
import requests

from lxml import etree
from pymysql import Connection

root_url = 'https://www.sex.com/search/gifs'
# 配置文件路径
settings_path = os.path.join(os.getcwd(), 'settings.json')
# 请求头
headers_root = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}
headers_gif = {
    'referer': 'https://www.sex.com/',
    'user-agent': headers_root['User-Agent']
}
# 解析 xpath
gif_xpath = '//div[@id="masonry_container"]/div[@class="masonry_box small_pin_box"]/a[@class="image_wrapper"]/img/@data-src'


def get_settings(path: str) -> tuple[list[str], int, int, dict, bool, dict, dict]:
    """
    读取配置文件
    :param path: 配置文件路径
    :return: keys: 关键字列表, start: 开始页面, end: 结束页面, params: 用于请求的参数框架, use_db: 是否使用数据库方式, db_conf: 数据库配置
    """
    with open(path, 'r', encoding='UTF-8') as f:
        json_data = json.load(f)
    keys = json_data['key_words']
    start = json_data['start_page']
    end = json_data['end_page']
    use_db = json_data['use_mysql']
    db_conf = json_data['mysql_conf']
    phase = json_data['phase']
    params = {'query': None, 'page': None}
    if json_data['sort'] is not None or json_data['sort'] != '':
        params['sort'] = json_data['sort']
    return keys, start, end, params, use_db, db_conf, phase


def mkdir_lib(path: str) -> tuple[str, str]:
    """
    创建 lib 目录、关键词目录并返回 lib 路径与 json 路径
    :param path: 工作路径
    :return: lib_p：lib 路径, json_p: json 路径
    """
    # 创建 sexcom_lib 目录
    lib_p = os.path.join(path, 'sexcom_lib')
    if not os.path.exists(lib_p):
        os.mkdir(lib_p)
    json_p = os.path.join(lib_p, 'gif_urls.json')
    return lib_p, json_p


def get_gif_url(url: str, headers: dict, params: dict, keys: list[str], start: int, end: int) -> dict:
    """
    通过 requests 模块和 xpath 解析 gif 图片地址
    :param url: 请求的 url
    :param headers: 请求头
    :param params: 传递关键词和排序方式
    :param keys: 关键词
    :param start: 起始页面
    :param end: 结束页面
    :return: 以关键词作为 key ， url 列表作为 value 的字典
    """
    if end < start:
        start, end = end, start
        print(f'警告：起始页码大于结束页码，已处理为 {start} - {end} 页')
    urls_out = {}
    for key in keys:
        params['page'] = start
        params['query'] = key
        urls_out[key] = []
        while params['page'] <= end:
            res = etree.HTML(requests.get(url=url, headers=headers, params=params).text)
            urls_out[key] = urls_out[key] + res.xpath(gif_xpath)
            params['page'] += 1
        urls_out[key] = list(map(lambda i: i.split('?')[0], urls_out[key]))
        urls_out[key] = list(set(urls_out[key]))
        pass
    return urls_out


def urls_to_json(path: str, data: dict):
    """
    将 urls 写入 json 文件
    :param path: json 路径
    :param data: 需要写入的 url 数据
    :return: None
    """
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def urls_to_mysql(data: dict, conf: dict):
    """
    将 url 列表写入数据库
    :param data: 要写入的 url 字典
    :param conf: 数据库配置字典
    :return: None
    """
    # 创建数据库连接
    coon = Connection(
        host=conf['host'],
        port=conf['port'],
        user=conf['user'],
        password=conf['password']
    )
    cursor = coon.cursor()
    coon.select_db(conf['db'])

    # 创建表
    if conf['create_table'] is True:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS `{conf['table']}`( `name` varchar(50) NOT NULL DEFAULT '2001_01_01-10000000.gif' COMMENT '图片名', `url` varchar(100) NOT NULL DEFAULT 'https://' COMMENT '图片 url', `tag` varchar(100) NOT NULL DEFAULT 'unknown' COMMENT '图片标签', `finish` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已下载', PRIMARY KEY (`name`)) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;")
        coon.commit()

    # 取得数据库中所有的文件名
    cursor.execute(f"SELECT name FROM {conf['table']};")
    all_names = []
    for v in cursor.fetchall():
        all_names.append(''.join(v))

    # 往数据库写入数据
    for tag in data:
        for url in data[tag]:
            gif_name_part = url.split('/')
            gif_name = gif_name_part[-4] + '_' + gif_name_part[-3] + '_' + gif_name_part[-2] + '-' + gif_name_part[-1]
            if gif_name in all_names:
                # 如果数据库中已存在，则跳过
                print(f'{gif_name} 在数据库中已存在')
                continue
            else:
                sql = f"INSERT INTO {conf['table']} (name, url, tag, finish) VALUES ('{gif_name}', '{url}', '{tag}', 0);"
                cursor.execute(sql)
        coon.commit()
        print(f"tag: {tag} 已写入数据库")
    coon.close()


def get_db_urls(conf: dict) -> list[str]:
    """
    获取数据库中未下载的的 gif 链接
    :param conf: 数据库配置文件
    :return: 未下载的 gif 链接列表
    """
    # 创建数据库连接
    coon = Connection(
        host=conf['host'],
        port=conf['port'],
        user=conf['user'],
        password=conf['password']
    )
    cursor = coon.cursor()
    coon.select_db(conf['db'])
    # 取得数据库中未下载的 url
    cursor.execute(f"SELECT url FROM {conf['table']} WHERE finish = 0;")
    urls = []
    for v in cursor.fetchall():
        urls.append(''.join(v))
    cursor.close()
    return urls


def get_json_url(path: str) -> list[str]:
    """
    获取在 json 文件中的 gif 图片链接
    :param path: json 文件路径
    :return: gif 链接列表
    """
    with open(path, 'r', encoding='UTF-8') as f:
        data = json.load(f)
    down_list = []
    for key in data:
        for url in data[key]:
            down_list.append(url)
    return down_list


def get_gif(url: str, headers: dict, count: int, total: int, path: str):
    """
    下载图片
    :param url: 图片url
    :param headers: 请求头
    :param count: 单前计数
    :param total: 总计图片数
    :param path: 保存文件夹
    :return: None
    """
    name_list = url.split('/')
    name = name_list[-4] + '_' + name_list[-3] + '_' + name_list[-2] + '-' + name_list[-1]
    file_path = os.path.join(path, name)
    if os.path.exists(file_path):
        print(f'{name} 已存在，跳过...')
        return
    else:
        try:
            gif = requests.get(url, headers=headers).content
        except Exception as e:
            print(f'网络错误: {e}\n{name} 已跳过...')
            return
        else:
            with open(file_path, 'wb') as f:
                f.write(gif)
            print(f'{name} 下载完成:[{count}:{total}]')


def update_db(down_list: list[str], conf: dict):
    """
    更新数据库，将本次下载的链接标记为已下载
    :param down_list: gif 链接列表
    :param conf: 数据库配置文件
    :return: None
    """
    # 创建数据库连接
    coon = Connection(
        host=conf['host'],
        port=conf['port'],
        user=conf['user'],
        password=conf['password']
    )
    cursor = coon.cursor()
    coon.select_db(conf['db'])
    for url in down_list:
        cursor.execute(f"UPDATE `{conf['table']}` SET `finish`=1 WHERE url = '{url}';")
    coon.commit()
    cursor.close()
    print('已更新数据库')


def main():
    # 取得配置
    key_words, start_page, end_page, params_root, use_mysql, mysql_conf, phase_conf = get_settings(settings_path)
    # 创建目录
    lib_path, json_path = mkdir_lib(os.getcwd())

    # 获取 url 列表
    gif_urls = []
    if phase_conf['get_urls'] is True:
        gif_urls = get_gif_url(root_url, headers_root, params_root, key_words, start_page, end_page)
        # 将 url 列表写入 json 文件
        urls_to_json(json_path, gif_urls)
        # 写入列表到数据库
        if use_mysql is True:
            urls_to_mysql(gif_urls, mysql_conf)

    # 转换下载列表
    if use_mysql is True:
        down_urls = get_db_urls(mysql_conf)
    elif phase_conf['get_urls'] is True:
        down_urls = []
        for key in gif_urls:
            for url in gif_urls[key]:
                down_urls.append(url)
    elif os.path.isfile(json_path):
        down_urls = get_json_url(json_path)
    else:
        print('没有途径获取 url ，请检查配置文件。')
        return 0

    # 获取图片
    if phase_conf['get_gifs'] is True:
        total = len(down_urls)
        count = 1
        for url in down_urls:
            get_gif(url, headers_gif, count, total, lib_path)
            count += 1
        if use_mysql is True:
            update_db(down_urls, mysql_conf)


if __name__ == '__main__':
    main()
