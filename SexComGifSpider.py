#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Subj: SexComGifSpider
# @File: SexComGifSpider.py
# @Date: 2022/9/24 0:24

import os
import json
import requests

from lxml import etree


root_url = 'https://www.sex.com/search/gifs'
# 读取设置
settings_path = os.path.join(os.getcwd(), 'settings.json')

with open(settings_path, 'r', encoding='UTF-8') as f:
    json_data = json.load(f)

key_word = json_data['key_word']
start_page = json_data['start_page']
end_page = json_data['end_page']

# 定义请求头
headers_root = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}
params_root = {'query': key_word, 'page': start_page}
headers_gif = {
    'referer': 'https://www.sex.com/',
    'user-agent': headers_root['User-Agent']
}
# 定义解析 xpath
gif_xpath = '//div[@id="masonry_container"]/div[@class="masonry_box small_pin_box"]/a[@class="image_wrapper"]/img/@data-src'


def get_gif_url(url: str, headers: dict, params: dict, start: int, end: int) -> list[str]:
    urls_out = []
    if end < start:
        start, end = end, start
        print(f'警告：起始页码大于结束页码，已处理为 {start} - {end} 页')
    params['page'] = start
    while params['page'] <= end:
        res = etree.HTML(requests.get(url=url, headers=headers, params=params).text)
        urls_out = urls_out + (res.xpath(gif_xpath))
        params['page'] += 1

    urls_out = list(map(lambda i: i.split('?')[0], urls_out))
    return urls_out


def urls_to_json(path: str, key: str, start: int, end: int, urls: list):
    data = {'key_word': key, 'start_page': start, 'end_page': end, 'gif_urls': urls}
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_gif(url: str, headers: dict, path: str):
    name_list = url.split('/')
    name = name_list[-4] + '-' + name_list[-3] + '-' + name_list[-2] + '-' + name_list[-1]
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
            print(f'{name} 下载完成')


def main():
    # 创建 sexcom_lib 目录
    lib_path = os.path.join(os.getcwd(), 'sexcom_lib')
    if not os.path.exists(lib_path):
        os.mkdir(lib_path)
    json_path = os.path.join(lib_path, 'gif_urls.json')
    # 创建关键词目录目录
    lib_path = os.path.join(lib_path, key_word)
    if not os.path.exists(lib_path):
        os.mkdir(lib_path)

    gif_urls = get_gif_url(root_url, headers_root, params_root, start_page, end_page)
    urls_to_json(json_path, key_word, start_page, end_page, gif_urls)
    for v in gif_urls:
        get_gif(v, headers_gif, lib_path)
    print(f'关键词：{key_word}\n{start_page} - {end_page} 页已爬取完成')


if __name__ == '__main__':
    main()
