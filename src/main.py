import os
import requests
import json
import datetime
import logging
import time
from pathlib import Path
from setting import *

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """确保必要的目录存在"""
    Path(IMAGE_ROOT).mkdir(parents=True, exist_ok=True)
    logger.info(f"图片目录已准备: {IMAGE_ROOT}")

def get_bing_wallpaper():
    """获取Bing每日壁纸数据"""
    try:
        logger.info("正在获取Bing壁纸数据...")
        
        # 创建唯一的时间戳参数强制跳过缓存
        timestamp = int(time.time())
        api_url = f"{BING_API}&t={timestamp}"
        
        # 添加headers明确要求不缓存
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 记录API返回的enddate
        logger.info(f"API返回壁纸日期: {data['images'][0]['enddate']}")
        logger.info(f"壁纸数据：{data}")
        
        return data['images'][0]
    except Exception as e:
        logger.error(f"获取Bing壁纸数据失败: {e}")
        return None

def get_wallpaper_date(data):
    """获取中国人看到的壁纸日期"""
    # 直接使用API返回的enddate作为壁纸日期
    end_date_str = data['enddate']
    
    # 转换为中国人习惯的日期格式
    display_date = (
        f"{end_date_str[:4]}-{end_date_str[4:6]}-{end_date_str[6:8]}"
    )
    return display_date

def save_daily_wallpaper(data):
    """保存每日壁纸"""
    if not data:
        return None
        
    try:
        # 获取壁纸日期（中国人看到的日期）
        display_date = get_wallpaper_date(data)
        year, month, day = display_date.split('-')
        
        # 创建目录
        save_dir = Path(IMAGE_ROOT) / year / month
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件路径
        base_filename = display_date
        md_path = save_dir / f"{base_filename}.md"
        img_path = save_dir / f"{base_filename}.jpg"
        
        # 图片URL
        img_url = BASE_URL + data['url']
        
        # 下载图片（如果不存在）
        if not img_path.exists():
            logger.info(f"正在下载图片: {img_url}")
            response = requests.get(img_url, timeout=15)
            response.raise_for_status()
            
            with open(img_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"图片已保存: {img_path}")
        else:
            logger.info(f"图片已存在，跳过下载: {img_path}")
        
        # 本地图片的相对路径
        local_image_url = f"images/{year}/{month}/{base_filename}.jpg"
        
        # 生成Markdown内容
        md_content = DAILY_TEMPLATE.format(
            title=data['title'],
            date=display_date,
            image_url=img_url,
            local_image_url=local_image_url,
            copyright=data['copyright'],
            copyright_link=data['copyrightlink']
        )
        
        # 保存Markdown文件
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        logger.info(f"Markdown文件已生成: {md_path}")
        
        return {
            "date": display_date,
            "md_content": md_content
        }
    except Exception as e:
        logger.error(f"保存壁纸时出错: {e}")
        return None

def get_recent_days():
    """获取最近7天的壁纸数据"""
    recent_days = []
    
    # 获取当前日期（UTC）
    base_date = datetime.datetime.utcnow()
    
    logger.info("正在收集最近7天的壁纸数据...")
    
    # 获取包括今天在内的最近7天
    for i in range(7):
        date = base_date - datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        year, month = date_str.split('-')[0], date_str.split('-')[1]
        
        md_path = Path(IMAGE_ROOT) / year / month / f"{date_str}.md"
        
        if md_path.exists():
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                recent_days.append({
                    "date": date_str,
                    "md_content": md_content
                })
                logger.info(f"找到壁纸: {date_str}")
            except Exception as e:
                logger.error(f"读取{md_path}时出错: {e}")
        else:
            logger.warning(f"壁纸不存在: {date_str}")
    
    # 按日期倒序排列（最近的在前面）
    recent_days.sort(key=lambda x: x['date'], reverse=True)
    return recent_days

def generate_readme(recent_days):
    """生成README文件"""
    try:
        logger.info("正在生成README...")
        
        # 拼接最近7天的md内容
        recent_content = "\n\n".join(day['md_content'] for day in recent_days)
        
        readme_content = README_TEMPLATE.format(recent_days=recent_content)
        
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.info(f"README已生成: {README_PATH}")
    except Exception as e:
        logger.error(f"生成README时出错: {e}")

def main():
    """主程序逻辑"""
    logger.info("=" * 50)
    logger.info("Bing壁纸自动更新程序启动")
    logger.info("=" * 50)
    
    # 准备目录
    setup_directories()
    
    # 获取并保存今日壁纸
    wallpaper_data = get_bing_wallpaper()
    today_data = save_daily_wallpaper(wallpaper_data) if wallpaper_data else None
    
    # 获取最近7天壁纸数据
    recent_days = get_recent_days()
    
    # 如果今天成功获取但不在最近7天列表中，则加入
    if today_data and today_data['date'] not in [d['date'] for d in recent_days]:
        recent_days.insert(0, {
            "date": today_data['date'],
            "md_content": today_data['md_content']
        })
        logger.info(f"将今日壁纸({today_data['date']})加入最近7天列表")
    
    # 确保只有7天内容
    recent_days = recent_days[:7]
    
    # 生成README
    generate_readme(recent_days)
    
    logger.info("程序执行完成")

if __name__ == "__main__":
    main()