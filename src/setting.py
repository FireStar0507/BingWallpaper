import os

# 基础配置
WIDTH, HEIGHT = 3840, 2160
BING_API = f"https://cn.bing.com/HPImageArchive.aspx?format=js&n=1&mkt=zh-CN&uhd=1&uhdwidth={WIDTH}&uhdheight={HEIGHT}"
BASE_URL = "https://cn.bing.com"
IMAGE_ROOT = os.path.abspath('images')
README_PATH = os.path.abspath('README.md')

# 每日壁纸的Markdown模板
DAILY_TEMPLATE = """## {title} - {date}
![{title}]({image_url})

> {copyright}
> [了解更多]({copyright_link})

[原图下载]({image_url}) | [本地下载]({local_image_url})

"""

# README模板
README_TEMPLATE = """# Bing每日壁纸

> 自动抓取Bing每日精美壁纸

## 最近7天壁纸

{recent_days}

[历史壁纸](images/)

"""
