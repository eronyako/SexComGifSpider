# SexComGifSpider
本项目为使用 python3 编写的 SexCom 爬虫工具。

## 使用
本项目可以使用直接使用 .py 文件（需要安装 Python3 并添加到环境变量），或使用 Releases 的 exe 文件。

所需文件如下：

- 程序主体：SexComGifSpider.py / SexComGifSpider.exe
- 配置文件：settings.json

### 配置文件要求

配置文件需要使用 UTF-8 Without BOM 编码，json 形式如下:

```
{
    "key_word": "xxx",
    "start_page": 1,
    "end_page": 3
}
```

`key_word` 为搜索的关键词，用英文的双引号包括，`start_page` 和 `end_page` 为开始和结束的页码，为整数，没有双引号，此外不要加其他内容。
程序启动后会读取此文件作为爬取条件。

### 使用源码

#### 普通版依赖

- json
- requests
- lxml

#### 使用

双击运行 SexComGifSpider.py

在当前目录运行：

```shell
python SexComGifSpider.py
```

#### 打包 exe 文件

可使用 pyinstaller 包，用如下命令将会在 `./dist/` 目录下创建 windows 可执行程序：

```shell
pyinstaller -F --icon=icon.ico SexComGifSpider.py
```

### 使用封装版

双击运行 SexComGifSpider.exe

## 输出

若正常运行后将会在当前文件夹创建 `sexcom_lib` 文件夹。

解析的 url 存放在 `./sexcom_lib/gif_urls.json`

程序会按照关键字创建文件夹，将该次下载的 gif 文件放入各文件夹中。

## 使用许可

[MIT](LICENSE) © Eronyako
