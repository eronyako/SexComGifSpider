#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Subj: SexGifSpider
# @File: SexGifSpider.py
# @Date: 2023/1/4 22:22
import json
import os
import requests
from loguru import logger
from lxml import etree
from pymysql import Connection


def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            obj = cls(*args, **kwargs)
            _instance[cls] = obj
        return _instance[cls]

    return inner


@singleton
class Client(object):
    def __init__(self, settings=''):
        self.root_url = "https://www.sex.com/"
        self.catalogue_url = "https://www.sex.com/gifs/"
        self.query_url = "https://www.sex.com/search/gifs"
        self.catalogue_list = [
            "amateur",
            "anal",
            "asian",
            "ass",
            "babes",
            "bbw",
            "bdsm",
            "big-tits",
            "blonde",
            "blowjob",
            "brunette",
            "celebrity",
            "college",
            "creampie",
            "cumshots",
            "double-penetration",
            "ebony",
            "emo",
            "female-ejaculation",
            "fisting",
            "footjob",
            "gangbang",
            "gay",
            "girlfriend",
            "group-sex",
            "hairy",
            "handjob",
            "hardcore",
            "hentai",
            "indian",
            "interracial",
            "latina",
            "lesbian",
            "lingerie",
            "masturbation",
            "mature",
            "milf",
            "non-nude",
            "panties",
            "penis",
            "pornstar",
            "public-sex",
            "pussy",
            "redhead",
            "selfshot",
            "shemale",
            "solo-male",
            "teen",
            "threesome",
            "toys"
        ]
        self.key_words = []
        self.sort = "latest"
        self.pages = []
        self.lib_dir = "sexcom_lib"
        self.json_path = "gif_urls.json"
        self.use_mysql = False
        self.mysql_conf = {}
        self.use_proxy = False
        self.proxy = {}

        self.phase = {
            "get_urls": True,
            "get_gifs": True
        }
        self.headers = {
            "referer": "https://www.sex.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        self.gif_xpath = "//div[@id=\"masonry_container\"]/div[@class=\"masonry_box small_pin_box\"]/a[@class=\"image_wrapper\"]/img/@data-src"

        if settings != '':
            self._load_settings(settings)

        self.img_urls = {}
        self.pending_urls = []

        if self.use_proxy:
            self.proxies = {
                "http": "socks5://" + self.proxy['host'] + ":" + str(self.proxy['port']),
                "https": "socks5://" + self.proxy['host'] + ":" + str(self.proxy['port'])
            }
        else:
            self.proxies = None

        if self.use_mysql:
            self.mysql_coon = Connection(
                host=self.mysql_conf['host'],
                port=self.mysql_conf['port'],
                user=self.mysql_conf['user'],
                password=self.mysql_conf['password']
            )
            self.mysql_coon.select_db(self.mysql_conf['db'])
            self.mysql_cursor = self.mysql_coon.cursor()
            # cursor.close()

        if not os.path.exists(self.lib_dir):
            os.mkdir(self.lib_dir)

    def _load_settings(self, path: str):
        with open(path, "r", encoding="utf-8") as fp:
            raw_dict = json.load(fp)
        for item in raw_dict:
            if hasattr(self, item):
                self.__setattr__(item, raw_dict[item])
            else:
                logger.warning(f"\"{item}\": 多余的选项存在于配置文件")
        logger.info("配置文件读取完毕")

    def _urls_to_json(self):
        with open(os.path.join(self.lib_dir, self.json_path), 'w', encoding='UTF-8') as fp:
            json.dump(self.img_urls, fp, ensure_ascii=False, indent=2)

    def _get_urls_net(self):
        if self.pages[0] > self.pages[1]:
            logger.warning("\"pages\": 起始页大于终止页，已翻转")
            self.pages[0], self.pages[1] = self.pages[1], self.pages[0]
        for item in self.key_words:
            self.img_urls[item] = []
            params = {
                "sort": self.sort,
                "page": self.pages[0]
            }
            if item.lower() in self.catalogue_list:
                url = self.catalogue_url + item + "/"
            else:
                url = self.query_url
                params["query"] = item

            while params["page"] <= self.pages[1]:
                logger.info(f'正在获取 {item} 第 {params["page"]} 页')
                res = etree.HTML(requests.get(url=url, proxies=self.proxies, headers=self.headers, params=params).text)
                for value in res.xpath(self.gif_xpath):
                    value = value.split("?")[0]
                    self.img_urls[item].append(value)
                params["page"] += 1
            self.img_urls[item] = list(set(self.img_urls[item]))
        logger.info("图片地址解析完毕")
        self._urls_to_json()

    def _data_to_pending(self):
        for key in self.img_urls:
            for url in self.img_urls[key]:
                name_part = url.split('/')
                gif_name = '_'.join(name_part[-4:-1]) + '-' + name_part[-1]
                self.pending_urls[gif_name] = url
            logger.info(f'"{key}" 已添加至待处理列表，共 {len(self.img_urls[key])} 条')
        logger.info(f"待处理列表整理完成，共 {len(self.pending_urls)} 条")

    def _get_urls_disk(self):
        with open(os.path.join(self.lib_dir, self.json_path), 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        self.img_urls = data
        logger.info("图片地址解析完毕")

    def _sync_mysql(self):
        if self.mysql_conf['create_table']:
            self.mysql_cursor.execute(
                f"CREATE TABLE IF NOT EXISTS `{self.mysql_conf['table']}`( `name` varchar(50) NOT NULL DEFAULT '2001_01_01-10000000.gif' COMMENT '图片名', `url` varchar(100) NOT NULL DEFAULT 'https://' COMMENT '图片 url', `tag` varchar(100) NOT NULL DEFAULT 'unknown' COMMENT '图片标签', `finish` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已下载', PRIMARY KEY (`name`)) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;")
            self.mysql_coon.commit()

        self.mysql_cursor.execute(f"SELECT `name` FROM {self.mysql_conf['table']};")
        all_pic_name = []
        for v in self.mysql_cursor.fetchall():
            all_pic_name.append(v[0])

        for key in self.img_urls:
            count = 0
            for url in self.img_urls[key]:
                name_part = url.split('/')
                gif_name = '_'.join(name_part[-4:-1]) + '-' + name_part[-1]
                if gif_name in all_pic_name:
                    continue
                else:
                    count += 1
                    self.mysql_cursor.execute(
                        f"INSERT IGNORE INTO {self.mysql_conf['table']} (`name`, `url`, `tag`, `finish`) VALUES ('{gif_name}', '{url}', '{key}', 0);")
            self.mysql_coon.commit()
            logger.info(f'"{key}" 已与数据库同步，新增 {count} 条数据')

    def _mysql_to_pending(self):
        self.mysql_cursor.execute(f"SELECT `name`,`url` FROM {self.mysql_conf['table']} WHERE `finish` = 0;")
        for v in self.mysql_cursor.fetchall():
            self.pending_urls[v[0]] = v[1]

    def get_urls(self):
        logger.info("正在获取图片地址...")
        self.pending_urls = {}
        if self.phase['get_urls']:
            self._get_urls_net()
        elif os.path.isfile(os.path.join(self.lib_dir, self.json_path)):
            self._get_urls_disk()
        else:
            logger.error(f'"{self.json_path}" 文件未找到')

        if self.use_mysql:
            self._sync_mysql()
            self._mysql_to_pending()
        else:
            self._data_to_pending()
        logger.info(f"待下载图片共 {len(self.pending_urls)} 张")

    def _download_gif(self, name: str, url: str) -> Exception or None:
        if os.path.exists(os.path.join(self.lib_dir, name)):
            return FileExistsError(name)
        try:
            gif_data = requests.get(url, proxies=self.proxies, headers=self.headers).content
        except Exception as err:
            return err
        else:
            with open(os.path.join(self.lib_dir, name), 'wb') as fp:
                fp.write(gif_data)
            if self.use_mysql:
                self.mysql_cursor.execute(f"UPDATE {self.mysql_conf['table']} SET `finish`=1 WHERE url = '{url}';")
                self.mysql_coon.commit()
            return None

    def download(self):
        logger.info("正在下载图片...")
        count = 0
        total = len(self.pending_urls)
        count_err = 0
        for name in self.pending_urls:
            count += 1
            err = self._download_gif(name, self.pending_urls[name])
            if err is not None:
                count_err += 1
                logger.warning(f'[{count}/{total}] {name} 下载失败：{err}')
            logger.info(f'[{count}/{total}] 下载完成：{name}')
        if self.use_mysql:
            self.mysql_cursor.close()
        logger.info("所有图片下载完成")
