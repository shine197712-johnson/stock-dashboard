"""
📊 股市观察 v3.8
专业级数据源架构 + 国际资讯 (Reddit / Hacker News / 金十数据)
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="股市观察 - 全球行情与资讯",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Apple风格CSS ====================
st.markdown("""
<style>
.stApp { background: #000000; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }

* { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; }

[data-testid="stSidebar"] { background: #1c1c1e; border-right: 1px solid #2c2c2e; }
[data-testid="stSidebar"] * { color: #f5f5f7 !important; }

.main-title { font-size: 48px; font-weight: 700; color: #f5f5f7; text-align: center; letter-spacing: -0.5px; margin-bottom: 8px; }
.sub-title { font-size: 17px; font-weight: 400; color: #86868b; text-align: center; margin-bottom: 40px; }
.section-header { font-size: 28px; font-weight: 600; color: #f5f5f7; margin: 40px 0 20px 0; }

.index-card {
    background: rgba(28, 28, 30, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}
.index-card:hover { transform: scale(1.02); background: rgba(44, 44, 46, 0.9); }
.index-region { font-size: 13px; font-weight: 500; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.index-name { font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 8px; }
.index-price { font-size: 28px; font-weight: 700; color: #f5f5f7; letter-spacing: -0.5px; }
.index-change { font-size: 15px; font-weight: 500; margin-top: 4px; }

.up { color: #34c759; }
.down { color: #ff3b30; }
.neutral { color: #86868b; }

.futures-card {
    background: rgba(28, 28, 30, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.futures-name { font-size: 13px; color: #86868b; margin-bottom: 4px; }
.futures-price { font-size: 20px; font-weight: 600; color: #f5f5f7; }
.futures-change { font-size: 13px; font-weight: 500; }

.news-section-title { font-size: 22px; font-weight: 600; color: #f5f5f7; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #2c2c2e; }
.news-card { background: rgba(28, 28, 30, 0.5); border-radius: 12px; padding: 16px; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.06); transition: all 0.2s ease; }
.news-card:hover { background: rgba(44, 44, 46, 0.7); }
.news-number { font-size: 12px; font-weight: 600; color: #0a84ff; margin-bottom: 6px; }
.news-title { font-size: 14px; font-weight: 500; color: #f5f5f7; line-height: 1.5; margin-bottom: 8px; }
.news-meta { font-size: 12px; color: #86868b; }

.tag { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; margin-right: 8px; }
.tag-politics { background: rgba(255, 59, 48, 0.15); color: #ff453a; }
.tag-economy { background: rgba(255, 159, 10, 0.15); color: #ff9f0a; }
.tag-tech { background: rgba(10, 132, 255, 0.15); color: #0a84ff; }
.tag-reddit { background: rgba(255, 69, 0, 0.15); color: #ff4500; }
.tag-hn { background: rgba(255, 102, 0, 0.15); color: #ff6600; }
.tag-jin10 { background: rgba(232, 65, 66, 0.15); color: #e84142; }

.divider { height: 1px; background: linear-gradient(90deg, transparent, #3a3a3c, transparent); margin: 40px 0; }
.footer-info { text-align: center; color: #86868b; font-size: 12px; padding: 40px 0 20px 0; }

.stock-card { background: rgba(28, 28, 30, 0.8); backdrop-filter: blur(20px); border-radius: 18px; padding: 24px; margin-bottom: 16px; border: 1px solid rgba(255, 255, 255, 0.1); }
.stock-name { font-size: 17px; font-weight: 600; color: #f5f5f7; }
.stock-code { font-size: 13px; color: #86868b; }
.stock-price { font-size: 34px; font-weight: 700; letter-spacing: -1px; margin: 12px 0; }
.stock-detail { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2c2c2e; }
.stock-detail:last-child { border-bottom: none; }
.detail-label { font-size: 13px; color: #86868b; }
.detail-value { font-size: 13px; color: #f5f5f7; font-weight: 500; }

.timestamp { font-size: 12px; color: #48484a; text-align: right; margin-top: 20px; }
.empty-state { text-align: center; padding: 60px 20px; color: #86868b; }
.empty-state-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state-text { font-size: 17px; font-weight: 500; }

.data-source { font-size: 10px; color: #3a3a3c; margin-top: 4px; }

/* 快讯样式 */
.flash-news { 
    background: rgba(232, 65, 66, 0.08); 
    border-left: 3px solid #e84142;
    padding: 12px 16px;
    margin-bottom: 8px;
    border-radius: 0 12px 12px 0;
}
.flash-time { color: #e84142; font-size: 12px; font-weight: 600; }
.flash-content { color: #f5f5f7; font-size: 13px; margin-top: 4px; line-height: 1.5; }

/* Reddit/HN样式 */
.intl-card {
    background: rgba(28, 28, 30, 0.5);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}
.intl-title { color: #f5f5f7; font-size: 13px; font-weight: 500; line-height: 1.4; margin-bottom: 8px; }
.intl-meta { color: #86868b; font-size: 11px; }
.intl-stats { color: #0a84ff; font-size: 11px; font-weight: 500; }

.stButton > button { background: rgba(10, 132, 255, 0.1) !important; color: #0a84ff !important; border: 1px solid rgba(10, 132, 255, 0.3) !important; border-radius: 10px !important; }
.stButton > button:hover { background: rgba(10, 132, 255, 0.2) !important; }
.stTextInput > div > div > input { background: #1c1c1e !important; color: #f5f5f7 !important; border: 1px solid #3a3a3c !important; border-radius: 10px !important; }
.stExpander { background: rgba(28, 28, 30, 0.5) !important; border: 1px solid #2c2c2e !important; border-radius: 12px !important; }

.tab-container { display: flex; gap: 8px; margin-bottom: 20px; }
.tab-btn { padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.tab-active { background: #0a84ff; color: white; }
.tab-inactive { background: rgba(255,255,255,0.1); color: #86868b; }
</style>
""", unsafe_allow_html=True)

# ==================== 专业级数据获取模块 ====================

class GlobalMarketData:
    """全球市场数据聚合器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.timeout = 8
    
    def get_indices_from_sina(self):
        """新浪财经全球指数"""
        indices = {}
        sina_codes = {
            "s_sh000001": {"name": "上证指数", "region": "中国大陆"},
            "s_sz399001": {"name": "深证成指", "region": "中国大陆"},
            "s_sz399006": {"name": "创业板指", "region": "中国大陆"},
        }
        
        try:
            # A股指数
            url = "https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006"
            headers = {'Referer': 'https://finance.sina.com.cn'}
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '=' in line and '"' in line:
                    data_str = line.split('"')[1]
                    if data_str:
                        parts = data_str.split(',')
                        if len(parts) >= 4:
                            for code, info in sina_codes.items():
                                if code.split('_')[-1] in line:
                                    indices[info["name"]] = {
                                        "name": info["name"],
                                        "region": info["region"],
                                        "price": float(parts[1]) if parts[1] else 0,
                                        "change_amt": float(parts[2]) if parts[2] else 0,
                                        "change_pct": float(parts[3]) if parts[3] else 0,
                                        "source": "新浪"
                                    }
                                    break
            
            # 港股
            url = "https://hq.sinajs.cn/list=rt_hkHSI,rt_hkHSCEI,rt_hkHSTECH"
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            hk_map = {"HSI": "恒生指数", "HSCEI": "国企指数", "HSTECH": "恒生科技"}
            for line in resp.text.strip().split('\n'):
                if '=' in line and '"' in line:
                    data_str = line.split('"')[1]
                    if data_str:
                        parts = data_str.split(',')
                        if len(parts) >= 9:
                            for code, name in hk_map.items():
                                if code in line:
                                    price = float(parts[6]) if parts[6] else 0
                                    prev = float(parts[3]) if parts[3] else price
                                    indices[name] = {
                                        "name": name, "region": "中国香港",
                                        "price": price,
                                        "change_amt": price - prev,
                                        "change_pct": ((price - prev) / prev * 100) if prev else 0,
                                        "source": "新浪"
                                    }
                                    break
            
            # 全球指数
            global_list = [
                ("int_dji", "道琼斯", "美国"), ("int_nasdaq", "纳斯达克", "美国"), ("int_sp500", "标普500", "美国"),
                ("int_ftse", "富时100", "英国"), ("int_dax", "德国DAX", "德国"), ("int_cac", "法国CAC40", "法国"),
                ("int_nikkei", "日经225", "日本"), ("b_TWSE", "台湾加权", "中国台湾"), ("b_KOSPI", "韩国综合", "韩国"),
            ]
            
            codes = ",".join([g[0] for g in global_list])
            url = f"https://hq.sinajs.cn/list={codes}"
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '=' in line and '"' in line:
                    data_str = line.split('"')[1]
                    if data_str:
                        parts = data_str.split(',')
                        for code, name, region in global_list:
                            if code in line:
                                if len(parts) >= 2:
                                    price = float(parts[0]) if parts[0] else 0
                                    change_pct = float(parts[1]) if len(parts) > 1 and parts[1] else 0
                                    indices[name] = {
                                        "name": name, "region": region,
                                        "price": price, "change_amt": 0, "change_pct": change_pct,
                                        "source": "新浪"
                                    }
                                break
        except:
            pass
        return indices
    
    def get_indices_from_eastmoney(self):
        """东方财富全球指数"""
        indices = {}
        em_codes = [
            {"code": "1.000001", "name": "上证指数", "region": "中国大陆"},
            {"code": "0.399001", "name": "深证成指", "region": "中国大陆"},
            {"code": "0.399006", "name": "创业板指", "region": "中国大陆"},
            {"code": "100.HSI", "name": "恒生指数", "region": "中国香港"},
            {"code": "100.HSCEI", "name": "国企指数", "region": "中国香港"},
            {"code": "100.HSTECH", "name": "恒生科技", "region": "中国香港"},
            {"code": "100.DJIA", "name": "道琼斯", "region": "美国"},
            {"code": "100.NDX", "name": "纳斯达克", "region": "美国"},
            {"code": "100.SPX", "name": "标普500", "region": "美国"},
            {"code": "100.FTSE", "name": "富时100", "region": "英国"},
            {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
            {"code": "100.FCHI", "name": "法国CAC40", "region": "法国"},
            {"code": "100.N225", "name": "日经225", "region": "日本"},
            {"code": "100.KS11", "name": "韩国综合", "region": "韩国"},
            {"code": "100.TWII", "name": "台湾加权", "region": "中国台湾"},
        ]
        
        def fetch_single(item):
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {"secid": item["code"], "fields": "f43,f169,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                if data and data.get("f43"):
                    return {
                        "name": item["name"], "region": item["region"],
                        "price": data.get("f43", 0) / 100,
                        "change_amt": data.get("f169", 0) / 100 if data.get("f169") else 0,
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                        "source": "东财"
                    }
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            for result in executor.map(fetch_single, em_codes):
                if result:
                    indices[result["name"]] = result
        return indices
    
    def get_all_indices(self):
        """聚合所有数据源"""
        all_indices = {}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.get_indices_from_eastmoney): "eastmoney",
                executor.submit(self.get_indices_from_sina): "sina",
            }
            source_data = {}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        source_data[futures[future]] = result
                except:
                    pass
        
        target_indices = [
            "上证指数", "深证成指", "创业板指", "恒生指数", "恒生科技", "国企指数",
            "道琼斯", "纳斯达克", "标普500", "日经225", "韩国综合", "台湾加权",
            "富时100", "德国DAX", "法国CAC40"
        ]
        
        region_map = {
            "上证指数": "中国大陆", "深证成指": "中国大陆", "创业板指": "中国大陆",
            "恒生指数": "中国香港", "恒生科技": "中国香港", "国企指数": "中国香港",
            "道琼斯": "美国", "纳斯达克": "美国", "标普500": "美国",
            "日经225": "日本", "韩国综合": "韩国", "台湾加权": "中国台湾",
            "富时100": "英国", "德国DAX": "德国", "法国CAC40": "法国"
        }
        
        for name in target_indices:
            for source in ["eastmoney", "sina"]:
                if source in source_data and name in source_data[source]:
                    data = source_data[source][name]
                    if data["price"] > 0:
                        all_indices[name] = data
                        break
            if name not in all_indices:
                all_indices[name] = {"name": name, "region": region_map.get(name, ""), "price": 0, "change_amt": 0, "change_pct": 0, "source": "-"}
        
        return list(all_indices.values())
    
    def get_futures_data(self):
        """获取期货数据"""
        futures = []
        em_futures = [
            {"code": "113.IH00", "name": "上证50期货", "type": "股指", "div": 100},
            {"code": "113.IF00", "name": "沪深300期货", "type": "股指", "div": 100},
            {"code": "113.IC00", "name": "中证500期货", "type": "股指", "div": 100},
            {"code": "113.AU0", "name": "沪金主力", "type": "贵金属", "div": 1},
            {"code": "113.AG0", "name": "沪银主力", "type": "贵金属", "div": 1},
            {"code": "113.SC0", "name": "原油主力", "type": "能源", "div": 1},
            {"code": "113.CU0", "name": "沪铜主力", "type": "有色", "div": 1},
            {"code": "113.AL0", "name": "沪铝主力", "type": "有色", "div": 1},
        ]
        
        def fetch_future(item):
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {"secid": item["code"], "fields": "f43,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                if data and data.get("f43"):
                    return {"name": item["name"], "type": item["type"], "price": data.get("f43", 0) / item["div"], "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0}
            except:
                pass
            return {"name": item["name"], "type": item["type"], "price": 0, "change_pct": 0}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = list(executor.map(fetch_future, em_futures))
        return futures
    
    def get_forex_data(self):
        """获取外汇数据"""
        forex = []
        try:
            codes = [("USDCNY", "美元/人民币"), ("EURCNY", "欧元/人民币"), ("JPYCNY", "日元/人民币"), ("GBPCNY", "英镑/人民币"), ("HKDCNY", "港币/人民币")]
            code_str = ",".join([f"fx_s{c[0]}" for c in codes])
            url = f"https://hq.sinajs.cn/list={code_str}"
            resp = self.session.get(url, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=8)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '"' in line:
                    data_str = line.split('"')[1]
                    if data_str:
                        parts = data_str.split(',')
                        if len(parts) >= 8:
                            for code, name in codes:
                                if code in line:
                                    curr = float(parts[1]) if parts[1] else 0
                                    prev = float(parts[3]) if parts[3] else curr
                                    forex.append({"name": name, "price": curr, "change_pct": ((curr - prev) / prev * 100) if prev else 0})
                                    break
        except:
            pass
        return forex

# ==================== 国际资讯模块 ====================

class InternationalNews:
    """国际资讯聚合器 - Reddit / Hacker News / 金十数据"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_reddit_hot_posts(self):
        """Reddit 财经热帖 (r/wallstreetbets, r/stocks, r/investing)"""
        posts = []
        subreddits = ["wallstreetbets", "stocks", "investing"]
        
        for sub in subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                resp = self.session.get(url, timeout=10)
                data = resp.json()
                
                if data.get("data", {}).get("children"):
                    for post in data["data"]["children"][:5]:
                        post_data = post.get("data", {})
                        if post_data.get("stickied"):
                            continue
                        
                        title = post_data.get("title", "")
                        score = post_data.get("score", 0)
                        comments = post_data.get("num_comments", 0)
                        created = post_data.get("created_utc", 0)
                        
                        # 只取24小时内的帖子
                        if created and (time.time() - created) < 86400:
                            hours_ago = int((time.time() - created) / 3600)
                            posts.append({
                                "title": title[:80] + "..." if len(title) > 80 else title,
                                "subreddit": f"r/{sub}",
                                "score": score,
                                "comments": comments,
                                "time": f"{hours_ago}小时前" if hours_ago > 0 else "刚刚",
                                "url": f"https://reddit.com{post_data.get('permalink', '')}"
                            })
            except:
                pass
        
        # 按热度排序
        posts.sort(key=lambda x: x["score"], reverse=True)
        return posts[:10]
    
    def get_hackernews_hot(self):
        """Hacker News 科技热帖"""
        posts = []
        
        try:
            # 获取热门帖子ID
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            resp = self.session.get(url, timeout=10)
            story_ids = resp.json()[:20]
            
            def fetch_story(story_id):
                try:
                    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    resp = self.session.get(url, timeout=5)
                    return resp.json()
                except:
                    return None
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                stories = list(executor.map(fetch_story, story_ids))
            
            for story in stories:
                if story and story.get("title"):
                    created = story.get("time", 0)
                    # 24小时内
                    if created and (time.time() - created) < 86400:
                        hours_ago = int((time.time() - created) / 3600)
                        posts.append({
                            "title": story.get("title", "")[:80],
                            "score": story.get("score", 0),
                            "comments": story.get("descendants", 0),
                            "time": f"{hours_ago}小时前" if hours_ago > 0 else "刚刚",
                            "url": story.get("url", f"https://news.ycombinator.com/item?id={story.get('id')}")
                        })
            
            posts.sort(key=lambda x: x["score"], reverse=True)
        except:
            pass
        
        return posts[:10]
    
    def get_jin10_flash(self):
        """金十数据 7x24 快讯"""
        flash_news = []
        
        try:
            # 金十数据快讯接口
            url = "https://flash-api.jin10.com/get_flash_list"
            params = {
                "channel": "-8200",
                "vip": 1,
                "t": int(time.time() * 1000)
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.jin10.com/',
                'x-app-id': 'bVBF4FyRTn5NJF5n',
                'x-version': '1.0.0'
            }
            
            resp = self.session.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            
            if data.get("data"):
                for item in data["data"][:15]:
                    content = item.get("data", {})
                    if isinstance(content, dict):
                        text = content.get("content", "")
                    else:
                        text = str(content)
                    
                    # 清理HTML标签
                    text = re.sub(r'<[^>]+>', '', text)
                    
                    if text and len(text) > 10:
                        time_str = item.get("time", "")
                        if time_str:
                            try:
                                time_str = time_str.split(" ")[1][:5] if " " in time_str else time_str[:5]
                            except:
                                time_str = ""
                        
                        # 判断重要性
                        is_important = item.get("important", 0) == 1 or "【" in text
                        
                        flash_news.append({
                            "content": text[:120] + "..." if len(text) > 120 else text,
                            "time": time_str,
                            "important": is_important
                        })
        except Exception as e:
            pass
        
        # 备用：如果金十接口失败，使用东方财富快讯
        if not flash_news:
            flash_news = self.get_eastmoney_flash()
        
        return flash_news[:12]
    
    def get_eastmoney_flash(self):
        """东方财富快讯（备用）"""
        flash_news = []
        try:
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            params = {"columns": "102", "pageSize": 15, "pageIndex": 0, "type": 1}
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("data"):
                for item in data["data"][:12]:
                    flash_news.append({
                        "content": item.get("title", "")[:120],
                        "time": item.get("showTime", "")[-5:] if item.get("showTime") else "",
                        "important": False
                    })
        except:
            pass
        return flash_news

# ==================== 新闻数据模块 ====================

class NewsAggregator:
    """国内新闻聚合器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_news_from_eastmoney(self):
        news = {"politics": [], "economy": [], "tech": []}
        try:
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            for col_id, category in [("350", "economy"), ("345", "politics"), ("351", "tech")]:
                params = {"columns": col_id, "pageSize": 15, "pageIndex": 0, "type": 1}
                resp = self.session.get(url, params=params, timeout=10)
                data = resp.json()
                if data.get("data"):
                    for item in data["data"][:15]:
                        news[category].append({
                            "title": item.get("title", ""),
                            "time": item.get("showTime", ""),
                            "source": item.get("mediaName", "东方财富")
                        })
        except:
            pass
        return news
    
    def get_news_from_sina(self):
        news = {"politics": [], "economy": [], "tech": []}
        try:
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {"pageid": "153", "lid": "2516", "num": 50, "page": 1}
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("result", {}).get("data"):
                for item in data["result"]["data"]:
                    title = item.get("title", "")
                    news_item = {
                        "title": title,
                        "time": datetime.fromtimestamp(int(item.get("ctime", 0))).strftime("%H:%M") if item.get("ctime") else "",
                        "source": item.get("media_name", "新浪财经")
                    }
                    
                    if any(kw in title for kw in ["政策", "央行", "两会", "国务院", "政府", "关税", "制裁"]):
                        if len(news["politics"]) < 15:
                            news["politics"].append(news_item)
                    elif any(kw in title for kw in ["AI", "人工智能", "芯片", "机器人", "科技", "算力", "大模型"]):
                        if len(news["tech"]) < 15:
                            news["tech"].append(news_item)
                    else:
                        if len(news["economy"]) < 15:
                            news["economy"].append(news_item)
        except:
            pass
        return news
    
    def get_all_news(self):
        all_news = {"politics": [], "economy": [], "tech": []}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(self.get_news_from_eastmoney), executor.submit(self.get_news_from_sina)]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    for cat in ["politics", "economy", "tech"]:
                        all_news[cat].extend(result.get(cat, []))
                except:
                    pass
        
        for cat in all_news:
            seen = set()
            unique = []
            for item in all_news[cat]:
                key = item["title"][:20]
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            all_news[cat] = unique[:10]
        
        return all_news

# ==================== A股数据模块 ====================

class AStockData:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    @st.cache_data(ttl=60)
    def get_stock_list(_self):
        stocks = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            for fs in ["m:1+t:2,m:1+t:23", "m:0+t:6,m:0+t:80"]:
                market = "sh" if "m:1" in fs else "sz"
                params = {"pn": 1, "pz": 3000, "fs": fs, "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = _self.session.get(url, params=params, timeout=10)
                for item in resp.json().get("data", {}).get("diff", []):
                    stocks.append({"code": item["f12"], "name": item["f14"], "market": market})
        except:
            pass
        return stocks
    
    def get_stock_realtime(self, code, market):
        try:
            secid = f"1.{code}" if market == "sh" else f"0.{code}"
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {"secid": secid, "fields": "f43,f44,f45,f46,f47,f48,f50,f58,f60,f169,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
            resp = self.session.get(url, params=params, timeout=5)
            data = resp.json().get("data", {})
            if data:
                return {
                    "code": code, "name": data.get("f58", ""),
                    "price": data.get("f43", 0) / 100 if data.get("f43") else 0,
                    "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                    "change_amt": data.get("f169", 0) / 100 if data.get("f169") else 0,
                    "volume": data.get("f47", 0) / 10000 if data.get("f47") else 0,
                    "amount": data.get("f48", 0) / 100000000 if data.get("f48") else 0,
                    "turnover": data.get("f50", 0) / 100 if data.get("f50") else 0,
                    "high": data.get("f44", 0) / 100 if data.get("f44") else 0,
                    "low": data.get("f45", 0) / 100 if data.get("f45") else 0,
                }
        except:
            pass
        return None

# ==================== 数据缓存 ====================

@st.cache_data(ttl=120)
def fetch_global_indices():
    return GlobalMarketData().get_all_indices()

@st.cache_data(ttl=120)
def fetch_futures_data():
    return GlobalMarketData().get_futures_data()

@st.cache_data(ttl=120)
def fetch_forex_data():
    return GlobalMarketData().get_forex_data()

@st.cache_data(ttl=300)
def fetch_news_data():
    return NewsAggregator().get_all_news()

@st.cache_data(ttl=180)
def fetch_reddit_posts():
    return InternationalNews().get_reddit_hot_posts()

@st.cache_data(ttl=180)
def fetch_hackernews_posts():
    return InternationalNews().get_hackernews_hot()

@st.cache_data(ttl=60)
def fetch_jin10_flash():
    return InternationalNews().get_jin10_flash()

@st.cache_data(ttl=60)
def fetch_stock_list():
    return AStockData().get_stock_list()

def get_stock_data(code, market):
    return AStockData().get_stock_realtime(code, market)

# ==================== 会话状态 ====================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}
if "alerts" not in st.session_state:
    st.session_state.alerts = {}
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "global"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0;'>
        <div style='font-size: 24px; font-weight: 700; color: #f5f5f7;'>📊 股市观察</div>
        <div style='font-size: 13px; color: #86868b; margin-top: 4px;'>全球行情与资讯 v3.8</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 10px 0;'></div>", unsafe_allow_html=True)
    
    tab = st.radio("功能模块", ["🌍 全球行情", "📈 A股监控"], label_visibility="collapsed")
    st.session_state.current_tab = "global" if "全球" in tab else "a_stock"
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.session_state.current_tab == "a_stock":
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 12px;'>搜索股票</div>", unsafe_allow_html=True)
        search = st.text_input("", placeholder="输入代码或名称", label_visibility="collapsed")
        
        if search:
            stocks = fetch_stock_list()
            results = [s for s in stocks if search.lower() in s["code"].lower() or search in s["name"]][:8]
            for stock in results:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<div style='color: #f5f5f7; font-size: 14px;'>{stock['name']} <span style='color: #86868b;'>{stock['code']}</span></div>", unsafe_allow_html=True)
                with col2:
                    if st.button("＋", key=f"add_{stock['code']}"):
                        st.session_state.watchlist[stock["code"]] = {"name": stock["name"], "market": stock["market"]}
                        st.rerun()
        
        st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 12px;'>监控列表</div>", unsafe_allow_html=True)
        
        if st.session_state.watchlist:
            for code, info in list(st.session_state.watchlist.items()):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<div style='color: #f5f5f7; font-size: 14px;'>{info['name']}</div>", unsafe_allow_html=True)
                with col2:
                    if st.button("✕", key=f"del_{code}"):
                        del st.session_state.watchlist[code]
                        st.rerun()
        else:
            st.markdown("<div style='color: #86868b; font-size: 13px;'>暂无监控</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown(f"<div style='color: #48484a; font-size: 11px; margin-top: 20px; text-align: center;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)

# ==================== 主界面 ====================

if st.session_state.current_tab == "global":
    st.markdown("""
    <div class='main-title'>股市观察</div>
    <div class='sub-title'>全球市场实时行情 · 国际财经资讯</div>
    """, unsafe_allow_html=True)
    
    # 获取数据
    with st.spinner("正在获取全球行情数据..."):
        indices = fetch_global_indices()
        futures = fetch_futures_data()
        forex = fetch_forex_data()
        news = fetch_news_data()
        reddit_posts = fetch_reddit_posts()
        hn_posts = fetch_hackernews_posts()
        jin10_flash = fetch_jin10_flash()
    
    # ========== 全球股指 ==========
    st.markdown("<div class='section-header'>🌍 全球股指</div>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    for i, idx in enumerate(indices[:15]):
        with cols[i % 5]:
            change_class = "up" if idx["change_pct"] > 0 else ("down" if idx["change_pct"] < 0 else "neutral")
            change_symbol = "+" if idx["change_pct"] > 0 else ""
            st.markdown(f"""
            <div class='index-card'>
                <div class='index-region'>{idx['region']}</div>
                <div class='index-name'>{idx['name']}</div>
                <div class='index-price'>{idx['price']:,.2f}</div>
                <div class='index-change {change_class}'>{change_symbol}{idx['change_pct']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== 期货 & 外汇 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='section-header'>📈 期货行情</div>", unsafe_allow_html=True)
        fut_cols = st.columns(4)
        for i, fut in enumerate(futures[:8]):
            with fut_cols[i % 4]:
                change_class = "up" if fut["change_pct"] > 0 else ("down" if fut["change_pct"] < 0 else "neutral")
                change_symbol = "+" if fut["change_pct"] > 0 else ""
                st.markdown(f"""
                <div class='futures-card'>
                    <div class='futures-name'>{fut['name']}</div>
                    <div class='futures-price'>{fut['price']:,.2f}</div>
                    <div class='futures-change {change_class}'>{change_symbol}{fut['change_pct']:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='section-header'>💱 外汇牌价</div>", unsafe_allow_html=True)
        if forex:
            fx_cols = st.columns(3)
            for i, fx in enumerate(forex[:6]):
                with fx_cols[i % 3]:
                    change_class = "up" if fx["change_pct"] > 0 else ("down" if fx["change_pct"] < 0 else "neutral")
                    change_symbol = "+" if fx["change_pct"] > 0 else ""
                    st.markdown(f"""
                    <div class='futures-card'>
                        <div class='futures-name'>{fx['name']}</div>
                        <div class='futures-price'>{fx['price']:.4f}</div>
                        <div class='futures-change {change_class}'>{change_symbol}{fx['change_pct']:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ========== 7x24快讯 ==========
    st.markdown("<div class='section-header'>⚡ 7×24 实时快讯</div>", unsafe_allow_html=True)
    
    flash_cols = st.columns(2)
    for i, flash in enumerate(jin10_flash[:10]):
        with flash_cols[i % 2]:
            importance_style = "border-left-color: #ff3b30;" if flash.get("important") else ""
            st.markdown(f"""
            <div class='flash-news' style='{importance_style}'>
                <span class='flash-time'>{'🔴 ' if flash.get('important') else ''}{flash.get('time', '')}</span>
                <div class='flash-content'>{flash.get('content', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ========== 国际社区热帖 ==========
    st.markdown("<div class='section-header'>🌐 国际社区热帖</div>", unsafe_allow_html=True)
    
    intl_cols = st.columns(2)
    
    # Reddit
    with intl_cols[0]:
        st.markdown("<div class='news-section-title'>🔥 Reddit 财经热帖</div>", unsafe_allow_html=True)
        if reddit_posts:
            for post in reddit_posts[:8]:
                st.markdown(f"""
                <div class='intl-card'>
                    <div class='intl-title'>{post['title']}</div>
                    <div class='intl-meta'>
                        <span class='tag tag-reddit'>{post['subreddit']}</span>
                        {post['time']}
                    </div>
                    <div class='intl-stats'>👍 {post['score']:,} · 💬 {post['comments']:,}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #86868b; padding: 20px;'>暂无数据</div>", unsafe_allow_html=True)
    
    # Hacker News
    with intl_cols[1]:
        st.markdown("<div class='news-section-title'>🧡 Hacker News 科技热帖</div>", unsafe_allow_html=True)
        if hn_posts:
            for post in hn_posts[:8]:
                st.markdown(f"""
                <div class='intl-card'>
                    <div class='intl-title'>{post['title']}</div>
                    <div class='intl-meta'>
                        <span class='tag tag-hn'>HN</span>
                        {post['time']}
                    </div>
                    <div class='intl-stats'>👍 {post['score']:,} · 💬 {post['comments']:,}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #86868b; padding: 20px;'>暂无数据</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ========== 国内财经资讯 ==========
    st.markdown("<div class='section-header'>📰 国内财经资讯</div>", unsafe_allow_html=True)
    
    news_cols = st.columns(3)
    categories = [("politics", "🏛️ 政治要闻", "tag-politics"), ("economy", "💰 经济要闻", "tag-economy"), ("tech", "🔬 科技要闻", "tag-tech")]
    
    for col, (cat_key, cat_name, tag_class) in zip(news_cols, categories):
        with col:
            st.markdown(f"<div class='news-section-title'>{cat_name}</div>", unsafe_allow_html=True)
            for i, item in enumerate(news.get(cat_key, [])[:10], 1):
                title = item['title'][:40] + '...' if len(item['title']) > 40 else item['title']
                st.markdown(f"""
                <div class='news-card'>
                    <div class='news-number'>{i:02d}</div>
                    <div class='news-title'>{title}</div>
                    <div class='news-meta'>{item.get('time', '')} · {item.get('source', '')}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='footer-info'>
        数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        数据来源: 新浪财经 / 东方财富 / 金十数据 / Reddit / Hacker News
    </div>
    """, unsafe_allow_html=True)

else:
    # A股监控页面
    st.markdown("""
    <div class='main-title'>股市观察</div>
    <div class='sub-title'>A股实时监控 · 智能预警</div>
    """, unsafe_allow_html=True)
    
    now = datetime.now()
    is_trading = now.weekday() < 5 and ((9 <= now.hour < 11) or (now.hour == 11 and now.minute <= 30) or (13 <= now.hour < 15))
    
    if not is_trading:
        st.markdown("""
        <div style='background: rgba(255, 159, 10, 0.1); border: 1px solid rgba(255, 159, 10, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 24px;'>
            <span style='color: #ff9f0a; font-size: 14px;'>⏰ 非交易时段，显示最近收盘数据</span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.watchlist:
        cols = st.columns(3)
        for i, (code, info) in enumerate(st.session_state.watchlist.items()):
            data = get_stock_data(code, info["market"])
            if data:
                with cols[i % 3]:
                    change_class = "up" if data["change_pct"] > 0 else ("down" if data["change_pct"] < 0 else "neutral")
                    change_symbol = "+" if data["change_pct"] > 0 else ""
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display: flex; justify-content: space-between;'>
                            <div class='stock-name'>{data['name']}</div>
                            <div class='stock-code'>{data['code']}</div>
                        </div>
                        <div class='stock-price {change_class}'>¥{data['price']:.2f}</div>
                        <div class='index-change {change_class}' style='margin-bottom: 16px;'>
                            {change_symbol}{data['change_amt']:.2f} ({change_symbol}{data['change_pct']:.2f}%)
                        </div>
                        <div class='stock-detail'><span class='detail-label'>成交量</span><span class='detail-value'>{data['volume']:.2f} 万手</span></div>
                        <div class='stock-detail'><span class='detail-label'>成交额</span><span class='detail-value'>{data['amount']:.2f} 亿</span></div>
                        <div class='stock-detail'><span class='detail-label'>换手率</span><span class='detail-value'>{data['turnover']:.2f}%</span></div>
                        <div class='stock-detail'><span class='detail-label'>最高/最低</span><span class='detail-value'>{data['high']:.2f} / {data['low']:.2f}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("报警设置"):
                        if code not in st.session_state.alerts:
                            st.session_state.alerts[code] = {"price_low": 0, "price_high": 0}
                        alert = st.session_state.alerts[code]
                        c1, c2 = st.columns(2)
                        with c1:
                            alert["price_low"] = st.number_input("价格下限", value=alert["price_low"], step=0.1, key=f"pl_{code}")
                        with c2:
                            alert["price_high"] = st.number_input("价格上限", value=alert["price_high"], step=0.1, key=f"ph_{code}")
    else:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-state-icon'>📈</div>
            <div class='empty-state-text'>在左侧搜索添加股票开始监控</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>热门股票</div>", unsafe_allow_html=True)
        hot_stocks = [
            {"code": "301165", "name": "锐捷网络", "market": "sz"},
            {"code": "300750", "name": "宁德时代", "market": "sz"},
            {"code": "600519", "name": "贵州茅台", "market": "sh"},
            {"code": "002475", "name": "立讯精密", "market": "sz"},
            {"code": "300059", "name": "东方财富", "market": "sz"},
            {"code": "000858", "name": "五粮液", "market": "sz"},
        ]
        cols = st.columns(3)
        for i, stock in enumerate(hot_stocks):
            with cols[i % 3]:
                if st.button(f"＋ {stock['name']}", key=f"hot_{stock['code']}", use_container_width=True):
                    st.session_state.watchlist[stock["code"]] = {"name": stock["name"], "market": stock["market"]}
                    st.rerun()
    
    st.markdown(f"<div class='timestamp'>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)
