#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Subj: SexGifSpider
# @File: main.py.py
# @Date: 2023/1/4 22:22

from SexGifSpider import Client

if __name__ == '__main__':
    client = Client(settings='settings.json')
    client.get_urls()
    client.download()
