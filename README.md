# SexComGifSpider
本项目为使用 python3 编写的 SexCom 爬虫工具。

## 使用
本项目可以使用直接使用 .py 文件（需要安装 Python3 并添加到环境变量），或使用 Releases 的 exe 文件。

所需文件如下：

- 程序主体：SexComGifSpider.py / SexComGifSpider.exe
- 配置文件：settings.json

### 配置文件要求

配置文件需要使用 UTF-8 Without BOM 编码，json 示例如下:

``` json
{
    "key_words": [
        // 搜索关键字，可多个
        "Orgasm",
        "Squirting"
    ],
    
    "sort": "latest",
    // 搜索的排序方式，可选值：
    // "popular-week": 本周最热
    // "popular-month": 本月最热
    // "popular-year": 本年最热
    // "popular-all": 累计最热
    // "latest": 最新
   
    "start_page": 1,        // 开始页码
    "end_page": 3,          // 结束页码
    "use_mysql": false,     // 是否使用数据库
    "mysql_conf": {
        // 数据库配置
        // 数据库表需要特定的列：
        // name: vaechar
        // url: vaechar
        // tag: vaechar
        // finish: tinyint
        "host": "10.2.0.109",
        "port": 3306,
        "user": "spider",
        "password": "123456",
        "db":"spider_db",
        "table": "sexcom",
        // 是否创建表，建议第一次选 true ，避免手动配置
        "create_table": true
    },
    "phase": {
        // 过程，分为两个阶段，可自行设置是否执行：
        // get_urls: 从网络获取最新的图片地址
        // get_gifs: 从数据库（finish 值为 0 的记录）、变量（当 get_urls 执行时）、本地 json 文件（如有）获得图片地址
        "get_urls": true,
        "get_gifs": true
    }
}
```

避免在配置文件中增加其他内容，程序启动后会读取此文件作为爬取条件。

### 使用源码

#### 普通版依赖

- json
- requests
- lxml
- pymysql

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

程序会将该次下载的 gif 文件放入 `sexcom_lib` 文件夹中。

## 使用许可

[MIT](LICENSE) © Eronyako
