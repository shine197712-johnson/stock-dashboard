"""
📊 股市观察 v4.1
AI智能选股系统 - 修复数据获取，增强稳定性
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
    page_title="股市观察 - AI智能选股",
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
    background: rgba(28, 28, 30, 0.8); backdrop-filter: blur(20px); border-radius: 18px;
    padding: 20px; margin-bottom: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
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
    background: rgba(28, 28, 30, 0.6); backdrop-filter: blur(20px); border-radius: 14px;
    padding: 16px; margin-bottom: 10px; border: 1px solid rgba(255, 255, 255, 0.08);
}
.futures-name { font-size: 13px; color: #86868b; margin-bottom: 4px; }
.futures-price { font-size: 20px; font-weight: 600; color: #f5f5f7; }
.futures-change { font-size: 13px; font-weight: 500; }

.news-section-title { font-size: 22px; font-weight: 600; color: #f5f5f7; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #2c2c2e; }
.news-card { background: rgba(28, 28, 30, 0.5); border-radius: 12px; padding: 16px; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.06); }
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

.divider { height: 1px; background: linear-gradient(90deg, transparent, #3a3a3c, transparent); margin: 40px 0; }
.footer-info { text-align: center; color: #86868b; font-size: 12px; padding: 40px 0 20px 0; }

/* AI推荐卡片 */
.ai-section {
    background: linear-gradient(135deg, rgba(10, 132, 255, 0.1), rgba(94, 92, 230, 0.1));
    border: 1px solid rgba(10, 132, 255, 0.3);
    border-radius: 24px;
    padding: 30px;
    margin: 30px 0;
}

.ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.ai-icon { font-size: 32px; }
.ai-title { font-size: 24px; font-weight: 700; color: #f5f5f7; }
.ai-subtitle { font-size: 13px; color: #86868b; }

.stock-recommend-card {
    background: rgba(28, 28, 30, 0.9);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}

.stock-recommend-card:hover {
    border-color: rgba(10, 132, 255, 0.5);
    transform: translateY(-2px);
}

.stock-recommend-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.stock-recommend-name { font-size: 18px; font-weight: 700; color: #f5f5f7; }
.stock-recommend-code { font-size: 13px; color: #86868b; }
.stock-recommend-price { font-size: 24px; font-weight: 700; }

.stock-recommend-reason {
    background: rgba(10, 132, 255, 0.1);
    border-radius: 10px;
    padding: 12px;
    margin-top: 12px;
}

.reason-title { font-size: 12px; font-weight: 600; color: #0a84ff; margin-bottom: 6px; }
.reason-content { font-size: 13px; color: #f5f5f7; line-height: 1.6; }

.signal-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    margin-top: 8px;
}

.signal-hot { background: rgba(255, 59, 48, 0.2); color: #ff453a; }
.signal-fund { background: rgba(52, 199, 89, 0.2); color: #34c759; }
.signal-news { background: rgba(255, 159, 10, 0.2); color: #ff9f0a; }
.signal-global { background: rgba(94, 92, 230, 0.2); color: #5e5ce6; }

.fund-flow-card {
    background: rgba(28, 28, 30, 0.6);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.fund-name { font-size: 14px; font-weight: 600; color: #f5f5f7; }
.fund-amount { font-size: 18px; font-weight: 700; margin-top: 4px; }

.flash-news { 
    background: rgba(232, 65, 66, 0.08); 
    border-left: 3px solid #e84142;
    padding: 12px 16px;
    margin-bottom: 8px;
    border-radius: 0 12px 12px 0;
}
.flash-time { color: #e84142; font-size: 12px; font-weight: 600; }
.flash-content { color: #f5f5f7; font-size: 13px; margin-top: 4px; line-height: 1.5; }

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

.risk-warning {
    background: rgba(255, 59, 48, 0.1);
    border: 1px solid rgba(255, 59, 48, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin-top: 20px;
}
.risk-title { color: #ff453a; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.risk-content { color: #86868b; font-size: 12px; line-height: 1.6; }

.debug-info {
    background: rgba(255, 159, 10, 0.1);
    border: 1px solid rgba(255, 159, 10, 0.3);
    border-radius: 8px;
    padding: 10px;
    margin: 10px 0;
    font-size: 12px;
    color: #ff9f0a;
}

.stButton > button { background: rgba(10, 132, 255, 0.1) !important; color: #0a84ff !important; border: 1px solid rgba(10, 132, 255, 0.3) !important; border-radius: 10px !important; }
.stButton > button:hover { background: rgba(10, 132, 255, 0.2) !important; }
.stTextInput > div > div > input { background: #1c1c1e !important; color: #f5f5f7 !important; border: 1px solid #3a3a3c !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== 数据获取模块（增强稳定性） ====================

class GlobalMarketData:
    """全球市场数据 - 增强版"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
    
    def get_all_indices(self):
        """获取全球股指 - 多源尝试"""
        indices = []
        
        # 东方财富接口
        em_codes = [
            {"code": "1.000001", "name": "上证指数", "region": "中国大陆"},
            {"code": "0.399001", "name": "深证成指", "region": "中国大陆"},
            {"code": "0.399006", "name": "创业板指", "region": "中国大陆"},
            {"code": "100.HSI", "name": "恒生指数", "region": "中国香港"},
            {"code": "100.HSTECH", "name": "恒生科技", "region": "中国香港"},
            {"code": "100.DJIA", "name": "道琼斯", "region": "美国"},
            {"code": "100.NDX", "name": "纳斯达克", "region": "美国"},
            {"code": "100.SPX", "name": "标普500", "region": "美国"},
            {"code": "100.N225", "name": "日经225", "region": "日本"},
            {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
        ]
        
        for item in em_codes:
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {
                    "secid": item["code"],
                    "fields": "f43,f169,f170",
                    "ut": "fa5fd1943c7b386f172d6893dbfba10b"
                }
                resp = self.session.get(url, params=params, timeout=8)
                data = resp.json().get("data", {})
                
                if data and data.get("f43"):
                    indices.append({
                        "name": item["name"],
                        "region": item["region"],
                        "price": data.get("f43", 0) / 100,
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                    })
                else:
                    # 添加占位数据
                    indices.append({
                        "name": item["name"],
                        "region": item["region"],
                        "price": 0,
                        "change_pct": 0,
                    })
            except Exception as e:
                indices.append({
                    "name": item["name"],
                    "region": item["region"],
                    "price": 0,
                    "change_pct": 0,
                })
        
        return indices
    
    def get_futures_data(self):
        """获取期货数据"""
        futures = []
        em_futures = [
            {"code": "113.IH00", "name": "上证50期货", "div": 100},
            {"code": "113.IF00", "name": "沪深300期货", "div": 100},
            {"code": "113.AU0", "name": "沪金主力", "div": 1},
            {"code": "113.AG0", "name": "沪银主力", "div": 1},
            {"code": "113.SC0", "name": "原油主力", "div": 1},
            {"code": "113.CU0", "name": "沪铜主力", "div": 1},
        ]
        
        for item in em_futures:
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {"secid": item["code"], "fields": "f43,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                if data and data.get("f43"):
                    futures.append({
                        "name": item["name"],
                        "price": data.get("f43", 0) / item["div"],
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0
                    })
                else:
                    futures.append({"name": item["name"], "price": 0, "change_pct": 0})
            except:
                futures.append({"name": item["name"], "price": 0, "change_pct": 0})
        
        return futures

class AStockAnalyzer:
    """A股分析器 - 增强稳定性"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/',
        })
    
    def get_sector_flow(self):
        """获取板块资金流向"""
        sectors = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1, "pz": 20, "fs": "m:90+t:2",
                "fields": "f12,f14,f3,f62,f184",
                "fid": "f62", "po": 1,
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json().get("data", {}).get("diff", [])
            
            for item in data[:15]:
                sectors.append({
                    "name": item.get("f14", ""),
                    "code": item.get("f12", ""),
                    "change_pct": item.get("f3", 0) / 100 if item.get("f3") else 0,
                    "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,
                })
        except Exception as e:
            pass
        return sectors
    
    def get_north_flow(self):
        """获取北向资金 - 简化版"""
        try:
            # 使用更稳定的接口
            url = "https://push2.eastmoney.com/api/qt/kamtbs.rtmin/get"
            params = {"fields1": "f1,f2,f3,f4", "fields2": "f51,f52,f53,f54,f55,f56"}
            resp = self.session.get(url, params=params, timeout=8)
            data = resp.json().get("data", {})
            
            if data:
                # 尝试解析
                n2s = data.get("n2s", [])
                s2n = data.get("s2n", [])
                
                total = 0
                if s2n and len(s2n) > 0:
                    latest = s2n[-1].split(",") if isinstance(s2n[-1], str) else []
                    if len(latest) >= 2 and latest[1] != "-":
                        try:
                            total = float(latest[1]) / 10000  # 转亿
                        except:
                            pass
                
                return {"total": total}
        except:
            pass
        return {"total": 0}
    
    def get_hot_stocks_v2(self):
        """获取热门股票 - 增强版，确保有数据返回"""
        hot_stocks = []
        
        try:
            # 方法1: 涨幅榜
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1, "pz": 20,
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f2,f3,f4,f5,f6,f7,f12,f14,f15,f16,f17,f18,f62",
                "fid": "f3", "po": 1,
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=10)
            result = resp.json()
            
            if result.get("data", {}).get("diff"):
                data = result["data"]["diff"]
                for item in data[:15]:
                    code = item.get("f12", "")
                    if not code:
                        continue
                    
                    market = "sh" if code.startswith("6") else "sz"
                    price = item.get("f2")
                    if price and price != "-":
                        price = float(price) / 100
                    else:
                        price = 0
                    
                    change_pct = item.get("f3")
                    if change_pct and change_pct != "-":
                        change_pct = float(change_pct) / 100
                    else:
                        change_pct = 0
                    
                    main_net = item.get("f62")
                    if main_net and main_net != "-":
                        main_net = float(main_net) / 100000000
                    else:
                        main_net = 0
                    
                    turnover = item.get("f7")
                    if turnover and turnover != "-":
                        turnover = float(turnover) / 100
                    else:
                        turnover = 0
                    
                    amount = item.get("f6")
                    if amount and amount != "-":
                        amount = float(amount) / 100000000
                    else:
                        amount = 0
                    
                    hot_stocks.append({
                        "code": code,
                        "name": item.get("f14", ""),
                        "market": market,
                        "price": price,
                        "change_pct": change_pct,
                        "turnover": turnover,
                        "amount": amount,
                        "main_net": main_net,
                        "source": "涨幅榜"
                    })
        except Exception as e:
            pass
        
        # 方法2: 资金流入榜（补充）
        try:
            params["fid"] = "f62"
            resp = self.session.get(url, params=params, timeout=10)
            result = resp.json()
            
            if result.get("data", {}).get("diff"):
                existing_codes = {s["code"] for s in hot_stocks}
                for item in result["data"]["diff"][:10]:
                    code = item.get("f12", "")
                    if code and code not in existing_codes:
                        market = "sh" if code.startswith("6") else "sz"
                        
                        price = item.get("f2")
                        price = float(price) / 100 if price and price != "-" else 0
                        
                        change_pct = item.get("f3")
                        change_pct = float(change_pct) / 100 if change_pct and change_pct != "-" else 0
                        
                        main_net = item.get("f62")
                        main_net = float(main_net) / 100000000 if main_net and main_net != "-" else 0
                        
                        hot_stocks.append({
                            "code": code,
                            "name": item.get("f14", ""),
                            "market": market,
                            "price": price,
                            "change_pct": change_pct,
                            "turnover": 0,
                            "amount": 0,
                            "main_net": main_net,
                            "source": "资金流入榜"
                        })
        except:
            pass
        
        return hot_stocks

class NewsAggregator:
    """新闻聚合器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_all_news(self):
        news = {"politics": [], "economy": [], "tech": []}
        
        try:
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            for col_id, category in [("350", "economy"), ("345", "politics"), ("351", "tech")]:
                params = {"columns": col_id, "pageSize": 15, "pageIndex": 0, "type": 1}
                resp = self.session.get(url, params=params, timeout=10)
                data = resp.json()
                if data.get("data"):
                    for item in data["data"][:10]:
                        news[category].append({
                            "title": item.get("title", ""),
                            "time": item.get("showTime", ""),
                            "source": item.get("mediaName", "东方财富")
                        })
        except:
            pass
        
        return news
    
    def extract_keywords(self, news_data):
        keywords = []
        keyword_patterns = [
            ("AI", ["AI", "人工智能", "大模型", "ChatGPT", "DeepSeek", "算力", "智能"]),
            ("芯片", ["芯片", "半导体", "光刻", "晶圆", "英伟达"]),
            ("机器人", ["机器人", "人形", "具身智能", "自动化"]),
            ("新能源", ["新能源", "光伏", "风电", "储能", "氢能"]),
            ("锂电池", ["锂电", "电池", "宁德", "比亚迪"]),
            ("稀土", ["稀土", "永磁"]),
            ("消费", ["消费", "零售", "白酒"]),
            ("医药", ["医药", "创新药", "生物"]),
            ("金融", ["金融", "银行", "券商"]),
            ("军工", ["军工", "国防", "航空"]),
        ]
        
        all_titles = " ".join([item.get("title", "") for cat in news_data.values() for item in cat])
        
        for keyword, patterns in keyword_patterns:
            if any(p in all_titles for p in patterns):
                keywords.append(keyword)
        
        return keywords if keywords else ["AI", "消费"]  # 默认热点

class InternationalNews:
    """国际资讯"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_reddit_hot(self):
        posts = []
        try:
            for sub in ["wallstreetbets", "stocks"]:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                resp = self.session.get(url, timeout=10)
                for post in resp.json().get("data", {}).get("children", [])[:5]:
                    pd = post.get("data", {})
                    if not pd.get("stickied"):
                        posts.append({
                            "title": pd.get("title", "")[:80],
                            "subreddit": f"r/{sub}",
                            "score": pd.get("score", 0),
                            "comments": pd.get("num_comments", 0),
                        })
        except:
            pass
        posts.sort(key=lambda x: x.get("score", 0), reverse=True)
        return posts[:8]
    
    def get_hackernews_hot(self):
        posts = []
        try:
            resp = self.session.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
            story_ids = resp.json()[:10]
            
            for sid in story_ids:
                try:
                    r = self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
                    s = r.json()
                    if s and s.get("title"):
                        posts.append({
                            "title": s.get("title", "")[:80],
                            "score": s.get("score", 0),
                            "comments": s.get("descendants", 0),
                        })
                except:
                    pass
        except:
            pass
        return posts[:8]
    
    def get_jin10_flash(self):
        flash = []
        try:
            url = "https://flash-api.jin10.com/get_flash_list"
            params = {"channel": "-8200", "vip": 1, "t": int(time.time() * 1000)}
            headers = {'Referer': 'https://www.jin10.com/', 'x-app-id': 'bVBF4FyRTn5NJF5n'}
            resp = self.session.get(url, params=params, headers=headers, timeout=10)
            for item in resp.json().get("data", [])[:12]:
                content = item.get("data", {})
                text = content.get("content", "") if isinstance(content, dict) else str(content)
                text = re.sub(r'<[^>]+>', '', text)
                if text and len(text) > 10:
                    flash.append({
                        "content": text[:120],
                        "time": item.get("time", "")[-8:-3] if item.get("time") else "",
                        "important": item.get("important", 0) == 1
                    })
        except:
            pass
        return flash

# ==================== AI选股引擎（简化版，确保稳定） ====================

class AIStockRecommender:
    """AI智能选股引擎 - 简化稳定版"""
    
    def generate_recommendations(self, indices, sectors, north_flow, hot_stocks, news_keywords):
        """生成推荐股票"""
        recommendations = []
        signals = []
        
        # 1. 分析全球信号
        us_indices = [i for i in indices if i.get("region") == "美国"]
        us_avg = sum(i.get("change_pct", 0) for i in us_indices) / len(us_indices) if us_indices else 0
        
        if us_avg > 0.5:
            signals.append({"type": "global", "text": f"美股上涨{us_avg:.1f}%，利好科技股"})
        elif us_avg < -0.5:
            signals.append({"type": "global", "text": f"美股下跌{abs(us_avg):.1f}%，关注防御板块"})
        
        # 2. 分析北向资金
        nf_total = north_flow.get("total", 0)
        if nf_total > 20:
            signals.append({"type": "fund", "text": f"北向资金净流入{nf_total:.1f}亿"})
        elif nf_total < -20:
            signals.append({"type": "fund", "text": f"北向资金净流出{abs(nf_total):.1f}亿"})
        
        # 3. 分析新闻热点
        if news_keywords:
            signals.append({"type": "news", "text": f"新闻热点: {', '.join(news_keywords[:3])}"})
        
        # 4. 筛选推荐股票
        if hot_stocks:
            # 对热门股票进行评分
            scored_stocks = []
            for stock in hot_stocks:
                score = 0
                reasons = []
                
                # 涨幅评分（3-7%最佳）
                change = stock.get("change_pct", 0)
                if 2 <= change <= 5:
                    score += 15
                    reasons.append(f"涨幅适中({change:.1f}%)")
                elif 5 < change <= 8:
                    score += 10
                    reasons.append(f"强势上涨({change:.1f}%)")
                elif change > 8:
                    score += 5
                    reasons.append(f"涨幅较大({change:.1f}%)")
                elif change > 0:
                    score += 8
                
                # 资金流入评分
                main_net = stock.get("main_net", 0)
                if main_net > 2:
                    score += 20
                    reasons.append(f"主力净流入{main_net:.1f}亿")
                elif main_net > 0.5:
                    score += 10
                    reasons.append(f"主力小幅流入")
                elif main_net > 0:
                    score += 5
                
                # 换手率评分
                turnover = stock.get("turnover", 0)
                if 5 <= turnover <= 15:
                    score += 10
                    reasons.append("换手活跃")
                elif turnover > 15:
                    score += 5
                
                # 来源加分
                if stock.get("source") == "资金流入榜":
                    score += 10
                
                stock["score"] = score
                stock["reasons"] = reasons
                scored_stocks.append(stock)
            
            # 排序取TOP 8
            scored_stocks.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            for stock in scored_stocks[:8]:
                if stock.get("price", 0) > 0:  # 确保有价格数据
                    reason_text = "、".join(stock.get("reasons", [])[:3])
                    if not reason_text:
                        reason_text = "综合评分领先"
                    
                    recommendations.append({
                        "code": stock.get("code", ""),
                        "name": stock.get("name", ""),
                        "price": stock.get("price", 0),
                        "change_pct": stock.get("change_pct", 0),
                        "main_net": stock.get("main_net", 0),
                        "turnover": stock.get("turnover", 0),
                        "reason": reason_text,
                        "score": stock.get("score", 0),
                        "source": stock.get("source", "")
                    })
        
        return recommendations, signals

# ==================== 缓存函数 ====================

@st.cache_data(ttl=120)
def fetch_global_indices():
    return GlobalMarketData().get_all_indices()

@st.cache_data(ttl=120)
def fetch_futures_data():
    return GlobalMarketData().get_futures_data()

@st.cache_data(ttl=120)
def fetch_sector_flow():
    return AStockAnalyzer().get_sector_flow()

@st.cache_data(ttl=60)
def fetch_north_flow():
    return AStockAnalyzer().get_north_flow()

@st.cache_data(ttl=60)
def fetch_hot_stocks():
    return AStockAnalyzer().get_hot_stocks_v2()

@st.cache_data(ttl=300)
def fetch_news_data():
    return NewsAggregator().get_all_news()

@st.cache_data(ttl=300)
def extract_news_keywords(news_json):
    news = json.loads(news_json)
    return NewsAggregator().extract_keywords(news)

@st.cache_data(ttl=180)
def fetch_reddit_posts():
    return InternationalNews().get_reddit_hot()

@st.cache_data(ttl=180)
def fetch_hn_posts():
    return InternationalNews().get_hackernews_hot()

@st.cache_data(ttl=60)
def fetch_jin10_flash():
    return InternationalNews().get_jin10_flash()

# ==================== 会话状态 ====================
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "ai"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0;'>
        <div style='font-size: 24px; font-weight: 700; color: #f5f5f7;'>📊 股市观察</div>
        <div style='font-size: 13px; color: #86868b; margin-top: 4px;'>AI智能选股 v4.1</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 10px 0;'></div>", unsafe_allow_html=True)
    
    tab = st.radio("功能模块", ["🤖 AI智能选股", "🌍 全球行情"], label_visibility="collapsed")
    st.session_state.current_tab = "ai" if "AI" in tab else "global"
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown(f"<div style='color: #48484a; font-size: 11px; margin-top: 20px; text-align: center;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)

# ==================== 主界面 ====================

if st.session_state.current_tab == "ai":
    st.markdown("""
    <div class='main-title'>AI智能选股</div>
    <div class='sub-title'>全球联动分析 · 多维度信号聚合 · 智能推荐</div>
    """, unsafe_allow_html=True)
    
    # 获取数据
    with st.spinner("正在分析全球市场数据..."):
        indices = fetch_global_indices()
        futures = fetch_futures_data()
        sectors = fetch_sector_flow()
        north_flow = fetch_north_flow()
        hot_stocks = fetch_hot_stocks()
        news = fetch_news_data()
        news_keywords = extract_news_keywords(json.dumps(news))
    
    # 生成推荐
    recommender = AIStockRecommender()
    recommendations, signals = recommender.generate_recommendations(
        indices, sectors, north_flow, hot_stocks, news_keywords
    )
    
    # ========== 市场信号概览 ==========
    st.markdown("<div class='section-header'>📡 市场信号</div>", unsafe_allow_html=True)
    
    signal_cols = st.columns(4)
    
    # 美股信号
    with signal_cols[0]:
        us_indices = [i for i in indices if i.get("region") == "美国"]
        us_avg = sum(i.get("change_pct", 0) for i in us_indices) / len(us_indices) if us_indices else 0
        change_class = "up" if us_avg > 0 else "down"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>🇺🇸 美股</div>
            <div class='index-name'>隔夜表现</div>
            <div class='index-change {change_class}' style='font-size: 24px;'>{'+' if us_avg > 0 else ''}{us_avg:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 北向资金
    with signal_cols[1]:
        nf = north_flow.get("total", 0)
        change_class = "up" if nf > 0 else ("down" if nf < 0 else "neutral")
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>💰 北向资金</div>
            <div class='index-name'>今日净流入</div>
            <div class='index-change {change_class}' style='font-size: 24px;'>{'+' if nf > 0 else ''}{nf:.1f}亿</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 热点板块
    with signal_cols[2]:
        top_sector = sectors[0] if sectors else {"name": "-", "change_pct": 0}
        change_class = "up" if top_sector.get("change_pct", 0) > 0 else "down"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>🔥 领涨板块</div>
            <div class='index-name'>{top_sector.get('name', '-')}</div>
            <div class='index-change {change_class}' style='font-size: 24px;'>{'+' if top_sector.get('change_pct', 0) > 0 else ''}{top_sector.get('change_pct', 0):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 新闻热点
    with signal_cols[3]:
        hot_keyword = news_keywords[0] if news_keywords else "无"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>📰 新闻热点</div>
            <div class='index-name'>关键词</div>
            <div style='font-size: 20px; color: #0a84ff; font-weight: 600; margin-top: 4px;'>{hot_keyword}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== 数据状态提示 ==========
    data_status = []
    if hot_stocks:
        data_status.append(f"✅ 热门股票: {len(hot_stocks)}只")
    else:
        data_status.append("⚠️ 热门股票数据获取中...")
    
    if sectors:
        data_status.append(f"✅ 板块数据: {len(sectors)}个")
    
    st.markdown(f"<div class='debug-info'>数据状态: {' | '.join(data_status)}</div>", unsafe_allow_html=True)
    
    # ========== AI推荐股票 ==========
    st.markdown("""
    <div class='ai-section'>
        <div class='ai-header'>
            <span class='ai-icon'>🤖</span>
            <div>
                <div class='ai-title'>AI智能推荐</div>
                <div class='ai-subtitle'>基于全球联动、资金流向、新闻热点综合分析</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if recommendations:
        rec_cols = st.columns(2)
        
        for i, stock in enumerate(recommendations[:8]):
            with rec_cols[i % 2]:
                change_class = "up" if stock.get("change_pct", 0) > 0 else "down"
                change_symbol = "+" if stock.get("change_pct", 0) > 0 else ""
                
                # 信号标签
                signal_tags = ""
                if stock.get("main_net", 0) > 0.5:
                    signal_tags += "<span class='signal-tag signal-fund'>💰 资金流入</span>"
                if stock.get("source") == "涨幅榜":
                    signal_tags += "<span class='signal-tag signal-hot'>🔥 涨幅领先</span>"
                if stock.get("source") == "资金流入榜":
                    signal_tags += "<span class='signal-tag signal-fund'>💎 主力加仓</span>"
                if stock.get("turnover", 0) > 10:
                    signal_tags += "<span class='signal-tag signal-news'>📊 换手活跃</span>"
                
                st.markdown(f"""
                <div class='stock-recommend-card'>
                    <div class='stock-recommend-header'>
                        <div>
                            <div class='stock-recommend-name'>{stock.get('name', '')}</div>
                            <div class='stock-recommend-code'>{stock.get('code', '')}</div>
                        </div>
                        <div class='stock-recommend-price {change_class}'>
                            ¥{stock.get('price', 0):.2f}
                            <span style='font-size: 14px; margin-left: 8px;'>{change_symbol}{stock.get('change_pct', 0):.2f}%</span>
                        </div>
                    </div>
                    <div>{signal_tags}</div>
                    <div class='stock-recommend-reason'>
                        <div class='reason-title'>📊 推荐理由</div>
                        <div class='reason-content'>{stock.get('reason', '综合评分领先')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='color: #86868b; text-align: center; padding: 40px;'>
            <div style='font-size: 48px; margin-bottom: 16px;'>📊</div>
            <div>正在获取市场数据，请稍后刷新...</div>
            <div style='font-size: 12px; margin-top: 8px;'>如持续无数据，可能是非交易时段或网络延迟</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 风险提示
    st.markdown("""
        <div class='risk-warning'>
            <div class='risk-title'>⚠️ 风险提示</div>
            <div class='risk-content'>
                本推荐基于公开数据的量化分析，不构成投资建议。股市有风险，投资需谨慎。
                建议结合自身风险承受能力和投资目标，审慎决策。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== 板块资金流向 ==========
    if sectors:
        st.markdown("<div class='section-header'>💰 板块资金流向 TOP10</div>", unsafe_allow_html=True)
        
        sector_cols = st.columns(5)
        for i, sector in enumerate(sectors[:10]):
            with sector_cols[i % 5]:
                change_class = "up" if sector.get("change_pct", 0) > 0 else "down"
                fund_class = "up" if sector.get("main_net", 0) > 0 else "down"
                st.markdown(f"""
                <div class='fund-flow-card'>
                    <div class='fund-name'>{sector.get('name', '')}</div>
                    <div class='index-change {change_class}'>{'+' if sector.get('change_pct', 0) > 0 else ''}{sector.get('change_pct', 0):.2f}%</div>
                    <div class='fund-amount {fund_class}'>{'+' if sector.get('main_net', 0) > 0 else ''}{sector.get('main_net', 0):.1f}亿</div>
                </div>
                """, unsafe_allow_html=True)
    
    # ========== 快讯 ==========
    jin10 = fetch_jin10_flash()
    if jin10:
        st.markdown("<div class='section-header'>⚡ 实时快讯</div>", unsafe_allow_html=True)
        flash_cols = st.columns(2)
        for i, flash in enumerate(jin10[:8]):
            with flash_cols[i % 2]:
                st.markdown(f"""
                <div class='flash-news'>
                    <span class='flash-time'>{'🔴 ' if flash.get('important') else ''}{flash.get('time', '')}</span>
                    <div class='flash-content'>{flash.get('content', '')}</div>
                </div>
                """, unsafe_allow_html=True)

else:
    # 全球行情页面
    st.markdown("""
    <div class='main-title'>全球行情</div>
    <div class='sub-title'>实时追踪全球市场动态</div>
    """, unsafe_allow_html=True)
    
    indices = fetch_global_indices()
    futures = fetch_futures_data()
    news = fetch_news_data()
    reddit = fetch_reddit_posts()
    hn = fetch_hn_posts()
    jin10 = fetch_jin10_flash()
    
    # 全球股指
    st.markdown("<div class='section-header'>🌍 全球股指</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, idx in enumerate(indices[:10]):
        with cols[i % 5]:
            change_class = "up" if idx.get("change_pct", 0) > 0 else ("down" if idx.get("change_pct", 0) < 0 else "neutral")
            st.markdown(f"""
            <div class='index-card'>
                <div class='index-region'>{idx.get('region', '')}</div>
                <div class='index-name'>{idx.get('name', '')}</div>
                <div class='index-price'>{idx.get('price', 0):,.2f}</div>
                <div class='index-change {change_class}'>{'+' if idx.get('change_pct', 0) > 0 else ''}{idx.get('change_pct', 0):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 期货
    st.markdown("<div class='section-header'>📈 期货行情</div>", unsafe_allow_html=True)
    fut_cols = st.columns(6)
    for i, fut in enumerate(futures[:6]):
        with fut_cols[i]:
            change_class = "up" if fut.get("change_pct", 0) > 0 else "down"
            st.markdown(f"""
            <div class='futures-card'>
                <div class='futures-name'>{fut.get('name', '')}</div>
                <div class='futures-price'>{fut.get('price', 0):,.2f}</div>
                <div class='futures-change {change_class}'>{'+' if fut.get('change_pct', 0) > 0 else ''}{fut.get('change_pct', 0):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 快讯
    if jin10:
        st.markdown("<div class='section-header'>⚡ 实时快讯</div>", unsafe_allow_html=True)
        flash_cols = st.columns(2)
        for i, flash in enumerate(jin10[:10]):
            with flash_cols[i % 2]:
                st.markdown(f"""
                <div class='flash-news'>
                    <span class='flash-time'>{'🔴 ' if flash.get('important') else ''}{flash.get('time', '')}</span>
                    <div class='flash-content'>{flash.get('content', '')}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 国际社区
    st.markdown("<div class='section-header'>🌐 国际社区</div>", unsafe_allow_html=True)
    intl_cols = st.columns(2)
    
    with intl_cols[0]:
        st.markdown("<div class='news-section-title'>🔥 Reddit</div>", unsafe_allow_html=True)
        if reddit:
            for post in reddit[:6]:
                st.markdown(f"""
                <div class='intl-card'>
                    <div class='intl-title'>{post.get('title', '')}</div>
                    <div class='intl-meta'><span class='tag tag-reddit'>{post.get('subreddit', '')}</span></div>
                    <div class='intl-stats'>👍 {post.get('score', 0):,} · 💬 {post.get('comments', 0):,}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #86868b; padding: 20px;'>暂无数据</div>", unsafe_allow_html=True)
    
    with intl_cols[1]:
        st.markdown("<div class='news-section-title'>🧡 Hacker News</div>", unsafe_allow_html=True)
        if hn:
            for post in hn[:6]:
                st.markdown(f"""
                <div class='intl-card'>
                    <div class='intl-title'>{post.get('title', '')}</div>
                    <div class='intl-meta'><span class='tag tag-hn'>HN</span></div>
                    <div class='intl-stats'>👍 {post.get('score', 0):,} · 💬 {post.get('comments', 0):,}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #86868b; padding: 20px;'>暂无数据</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 国内新闻
    st.markdown("<div class='section-header'>📰 国内财经</div>", unsafe_allow_html=True)
    news_cols = st.columns(3)
    categories = [("politics", "🏛️ 政治"), ("economy", "💰 经济"), ("tech", "🔬 科技")]
    
    for col, (cat_key, cat_name) in zip(news_cols, categories):
        with col:
            st.markdown(f"<div class='news-section-title'>{cat_name}</div>", unsafe_allow_html=True)
            for i, item in enumerate(news.get(cat_key, [])[:8], 1):
                title = item.get('title', '')[:35] + '...' if len(item.get('title', '')) > 35 else item.get('title', '')
                st.markdown(f"""
                <div class='news-card'>
                    <div class='news-number'>{i:02d}</div>
                    <div class='news-title'>{title}</div>
                    <div class='news-meta'>{item.get('time', '')}</div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class='footer-info'>
    数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    数据来源: 东方财富 / 金十数据 / Reddit / Hacker News<br>
    ⚠️ 本工具仅供参考，不构成投资建议
</div>
""", unsafe_allow_html=True)
