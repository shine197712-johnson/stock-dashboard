"""
📊 股市观察 v4.0
AI智能选股系统 - 全球联动分析 + Claude AI推荐
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

/* AI推荐卡片 - 特殊样式 */
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

.ai-icon {
    font-size: 32px;
}

.ai-title {
    font-size: 24px;
    font-weight: 700;
    color: #f5f5f7;
}

.ai-subtitle {
    font-size: 13px;
    color: #86868b;
}

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

.stock-recommend-name {
    font-size: 18px;
    font-weight: 700;
    color: #f5f5f7;
}

.stock-recommend-code {
    font-size: 13px;
    color: #86868b;
}

.stock-recommend-price {
    font-size: 24px;
    font-weight: 700;
}

.stock-recommend-reason {
    background: rgba(10, 132, 255, 0.1);
    border-radius: 10px;
    padding: 12px;
    margin-top: 12px;
}

.reason-title {
    font-size: 12px;
    font-weight: 600;
    color: #0a84ff;
    margin-bottom: 6px;
}

.reason-content {
    font-size: 13px;
    color: #f5f5f7;
    line-height: 1.6;
}

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

/* 资金流向 */
.fund-flow-card {
    background: rgba(28, 28, 30, 0.6);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.fund-name { font-size: 14px; font-weight: 600; color: #f5f5f7; }
.fund-amount { font-size: 18px; font-weight: 700; margin-top: 4px; }

/* 快讯 */
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

.stButton > button { background: rgba(10, 132, 255, 0.1) !important; color: #0a84ff !important; border: 1px solid rgba(10, 132, 255, 0.3) !important; border-radius: 10px !important; }
.stButton > button:hover { background: rgba(10, 132, 255, 0.2) !important; }
.stTextInput > div > div > input { background: #1c1c1e !important; color: #f5f5f7 !important; border: 1px solid #3a3a3c !important; border-radius: 10px !important; }
.stExpander { background: rgba(28, 28, 30, 0.5) !important; border: 1px solid #2c2c2e !important; border-radius: 12px !important; }

/* AI分析中动画 */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.analyzing { animation: pulse 1.5s ease-in-out infinite; }

/* 风险提示 */
.risk-warning {
    background: rgba(255, 59, 48, 0.1);
    border: 1px solid rgba(255, 59, 48, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin-top: 20px;
}
.risk-title { color: #ff453a; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.risk-content { color: #86868b; font-size: 12px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ==================== 数据获取模块 ====================

class GlobalMarketData:
    """全球市场数据"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 8
    
    def get_all_indices(self):
        """获取全球股指"""
        indices = {}
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
            {"code": "100.FTSE", "name": "富时100", "region": "英国"},
            {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
            {"code": "100.FCHI", "name": "法国CAC40", "region": "法国"},
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
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                        "source": "东财"
                    }
            except:
                pass
            return {"name": item["name"], "region": item["region"], "price": 0, "change_pct": 0, "source": "-"}
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_single, em_codes))
        return results
    
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
                    futures.append({"name": item["name"], "price": data.get("f43", 0) / item["div"], "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0})
                else:
                    futures.append({"name": item["name"], "price": 0, "change_pct": 0})
            except:
                futures.append({"name": item["name"], "price": 0, "change_pct": 0})
        return futures

class AStockAnalyzer:
    """A股分析器 - 板块、资金流向、热点"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_sector_flow(self):
        """获取板块资金流向"""
        sectors = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1, "pz": 20, "fs": "m:90+t:2",
                "fields": "f12,f14,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87",
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
                    "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,  # 主力净流入(亿)
                    "main_pct": item.get("f184", 0) / 100 if item.get("f184") else 0,  # 主力净占比
                })
        except:
            pass
        return sectors
    
    def get_north_flow(self):
        """获取北向资金"""
        try:
            url = "https://push2.eastmoney.com/api/qt/kamt.rtmin/get"
            params = {"fields1": "f1,f2,f3,f4", "fields2": "f51,f52,f53,f54,f55,f56", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json().get("data", {})
            
            if data:
                # 解析实时数据
                s2n = data.get("s2n", [])  # 沪股通+深股通
                if s2n:
                    latest = s2n[-1].split(",") if s2n[-1] else []
                    if len(latest) >= 2:
                        return {
                            "total": float(latest[1]) / 10000 if latest[1] != "-" else 0,  # 亿
                            "hgt": float(data.get("hzjlj", 0)) / 10000,  # 沪股通累计
                            "sgt": float(data.get("szjlj", 0)) / 10000,  # 深股通累计
                        }
        except:
            pass
        return {"total": 0, "hgt": 0, "sgt": 0}
    
    def get_hot_stocks(self):
        """获取热门股票（涨幅榜+换手榜+资金流入榜）"""
        hot_stocks = []
        
        try:
            # 涨幅榜
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1, "pz": 10, "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17,f18,f62,f184",
                "fid": "f3", "po": 1,
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json().get("data", {}).get("diff", [])
            
            for item in data[:10]:
                code = item.get("f12", "")
                market = "sh" if code.startswith("6") else "sz"
                hot_stocks.append({
                    "code": code,
                    "name": item.get("f14", ""),
                    "market": market,
                    "price": item.get("f2", 0) / 100 if item.get("f2") else 0,
                    "change_pct": item.get("f3", 0) / 100 if item.get("f3") else 0,
                    "turnover": item.get("f7", 0) / 100 if item.get("f7") else 0,
                    "amount": item.get("f6", 0) / 100000000 if item.get("f6") else 0,
                    "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,
                    "source": "涨幅榜"
                })
        except:
            pass
        
        try:
            # 资金流入榜
            params["fid"] = "f62"
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json().get("data", {}).get("diff", [])
            
            existing_codes = {s["code"] for s in hot_stocks}
            for item in data[:10]:
                code = item.get("f12", "")
                if code not in existing_codes:
                    market = "sh" if code.startswith("6") else "sz"
                    hot_stocks.append({
                        "code": code,
                        "name": item.get("f14", ""),
                        "market": market,
                        "price": item.get("f2", 0) / 100 if item.get("f2") else 0,
                        "change_pct": item.get("f3", 0) / 100 if item.get("f3") else 0,
                        "turnover": item.get("f7", 0) / 100 if item.get("f7") else 0,
                        "amount": item.get("f6", 0) / 100000000 if item.get("f6") else 0,
                        "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,
                        "source": "资金榜"
                    })
        except:
            pass
        
        return hot_stocks
    
    def get_concept_stocks(self, concept_keywords):
        """根据概念关键词获取相关股票"""
        concept_stocks = []
        
        # 概念板块代码映射
        concept_map = {
            "AI": "BK0800", "人工智能": "BK0800", "算力": "BK0891",
            "芯片": "BK0493", "半导体": "BK0493", "光刻机": "BK0717",
            "机器人": "BK0747", "人形机器人": "BK0747",
            "新能源": "BK0478", "光伏": "BK0478", "储能": "BK1038",
            "锂电池": "BK0574", "宁德时代": "BK0574",
            "医药": "BK0465", "创新药": "BK0465",
            "军工": "BK0477", "国防": "BK0477",
            "消费": "BK0438", "白酒": "BK0477",
            "金融": "BK0475", "券商": "BK0707", "银行": "BK0475",
            "房地产": "BK0451", "地产": "BK0451",
            "稀土": "BK0482", "有色": "BK0478",
            "DeepSeek": "BK0800", "大模型": "BK0800",
        }
        
        # 找到匹配的概念
        matched_concepts = []
        for keyword in concept_keywords:
            for key, code in concept_map.items():
                if key in keyword or keyword in key:
                    if code not in [c[1] for c in matched_concepts]:
                        matched_concepts.append((key, code))
        
        # 获取概念板块成分股
        for concept_name, concept_code in matched_concepts[:3]:
            try:
                url = "https://push2.eastmoney.com/api/qt/clist/get"
                params = {
                    "pn": 1, "pz": 5, "fs": f"b:{concept_code}",
                    "fields": "f12,f14,f2,f3,f62,f184",
                    "fid": "f3", "po": 1,
                    "ut": "fa5fd1943c7b386f172d6893dbfba10b"
                }
                resp = self.session.get(url, params=params, timeout=10)
                data = resp.json().get("data", {}).get("diff", [])
                
                for item in data[:5]:
                    code = item.get("f12", "")
                    market = "sh" if code.startswith("6") else "sz"
                    concept_stocks.append({
                        "code": code,
                        "name": item.get("f14", ""),
                        "market": market,
                        "price": item.get("f2", 0) / 100 if item.get("f2") else 0,
                        "change_pct": item.get("f3", 0) / 100 if item.get("f3") else 0,
                        "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,
                        "concept": concept_name,
                    })
            except:
                pass
        
        return concept_stocks

class NewsAggregator:
    """新闻聚合器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_all_news(self):
        """获取所有新闻"""
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
        """从新闻中提取关键词"""
        keywords = []
        
        # 关键词映射
        keyword_patterns = [
            ("AI", ["AI", "人工智能", "大模型", "ChatGPT", "DeepSeek", "算力", "智能"]),
            ("芯片", ["芯片", "半导体", "光刻", "晶圆", "封装", "英伟达", "台积电"]),
            ("机器人", ["机器人", "人形", "具身智能", "自动化"]),
            ("新能源", ["新能源", "光伏", "风电", "储能", "氢能", "碳中和"]),
            ("锂电池", ["锂电", "电池", "宁德", "比亚迪", "充电"]),
            ("稀土", ["稀土", "永磁", "钕铁硼"]),
            ("消费", ["消费", "零售", "电商", "白酒"]),
            ("医药", ["医药", "创新药", "生物", "疫苗"]),
            ("金融", ["金融", "银行", "券商", "保险"]),
            ("军工", ["军工", "国防", "航空", "航天"]),
        ]
        
        all_titles = []
        for category in news_data.values():
            for item in category:
                all_titles.append(item.get("title", ""))
        
        full_text = " ".join(all_titles)
        
        for keyword, patterns in keyword_patterns:
            count = sum(1 for p in patterns if p in full_text)
            if count >= 2:
                keywords.append(keyword)
        
        return keywords

class InternationalNews:
    """国际资讯"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_reddit_hot(self):
        posts = []
        for sub in ["wallstreetbets", "stocks"]:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                resp = self.session.get(url, timeout=10)
                for post in resp.json().get("data", {}).get("children", [])[:5]:
                    pd = post.get("data", {})
                    if not pd.get("stickied") and (time.time() - pd.get("created_utc", 0)) < 86400:
                        posts.append({
                            "title": pd.get("title", "")[:80],
                            "subreddit": f"r/{sub}",
                            "score": pd.get("score", 0),
                            "comments": pd.get("num_comments", 0),
                        })
            except:
                pass
        posts.sort(key=lambda x: x["score"], reverse=True)
        return posts[:8]
    
    def get_hackernews_hot(self):
        posts = []
        try:
            resp = self.session.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
            story_ids = resp.json()[:15]
            
            def fetch(sid):
                try:
                    r = self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
                    return r.json()
                except:
                    return None
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                stories = list(executor.map(fetch, story_ids))
            
            for s in stories:
                if s and s.get("title") and (time.time() - s.get("time", 0)) < 86400:
                    posts.append({
                        "title": s.get("title", "")[:80],
                        "score": s.get("score", 0),
                        "comments": s.get("descendants", 0),
                    })
        except:
            pass
        posts.sort(key=lambda x: x["score"], reverse=True)
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

# ==================== AI选股引擎 ====================

class AIStockRecommender:
    """AI智能选股引擎"""
    
    def __init__(self):
        self.analyzer = AStockAnalyzer()
    
    def analyze_global_signals(self, indices):
        """分析全球信号"""
        signals = []
        
        # 美股信号
        us_indices = [i for i in indices if i["region"] == "美国"]
        us_avg_change = sum(i["change_pct"] for i in us_indices) / len(us_indices) if us_indices else 0
        
        if us_avg_change > 1:
            signals.append({"type": "global", "signal": "美股大涨", "impact": "利好科技、消费", "keywords": ["AI", "芯片", "消费"]})
        elif us_avg_change < -1:
            signals.append({"type": "global", "signal": "美股大跌", "impact": "避险资金流入", "keywords": ["军工", "金融"]})
        
        # 纳斯达克单独分析
        nasdaq = next((i for i in indices if "纳斯达克" in i["name"]), None)
        if nasdaq and nasdaq["change_pct"] > 1.5:
            signals.append({"type": "global", "signal": "纳斯达克领涨", "impact": "科技股活跃", "keywords": ["AI", "芯片", "机器人"]})
        
        # 港股信号
        hk_indices = [i for i in indices if "香港" in i["region"]]
        hk_tech = next((i for i in hk_indices if "科技" in i["name"]), None)
        if hk_tech and hk_tech["change_pct"] > 2:
            signals.append({"type": "global", "signal": "恒生科技大涨", "impact": "互联网、科技回暖", "keywords": ["AI", "消费"]})
        
        return signals
    
    def analyze_fund_signals(self, sectors, north_flow):
        """分析资金信号"""
        signals = []
        
        # 北向资金
        if north_flow["total"] > 50:
            signals.append({"type": "fund", "signal": f"北向资金净流入{north_flow['total']:.1f}亿", "impact": "外资看好A股", "keywords": ["金融", "消费"]})
        elif north_flow["total"] < -50:
            signals.append({"type": "fund", "signal": f"北向资金净流出{abs(north_flow['total']):.1f}亿", "impact": "外资避险", "keywords": ["军工"]})
        
        # 板块资金流向
        top_sectors = [s for s in sectors if s["main_net"] > 5][:3]
        for sector in top_sectors:
            signals.append({
                "type": "fund", 
                "signal": f"{sector['name']}主力净流入{sector['main_net']:.1f}亿",
                "impact": f"{sector['name']}板块活跃",
                "keywords": [sector['name']]
            })
        
        return signals
    
    def analyze_news_signals(self, news_keywords):
        """分析新闻信号"""
        signals = []
        
        keyword_impact = {
            "AI": "人工智能、算力相关标的",
            "芯片": "半导体、设备材料",
            "机器人": "自动化、传感器",
            "新能源": "光伏、风电、储能",
            "稀土": "永磁材料、有色金属",
        }
        
        for kw in news_keywords[:3]:
            if kw in keyword_impact:
                signals.append({
                    "type": "news",
                    "signal": f"新闻热点: {kw}",
                    "impact": keyword_impact[kw],
                    "keywords": [kw]
                })
        
        return signals
    
    def generate_recommendations(self, indices, futures, sectors, north_flow, hot_stocks, news_keywords):
        """生成推荐股票"""
        recommendations = []
        
        # 收集所有信号
        all_signals = []
        all_signals.extend(self.analyze_global_signals(indices))
        all_signals.extend(self.analyze_fund_signals(sectors, north_flow))
        all_signals.extend(self.analyze_news_signals(news_keywords))
        
        # 收集所有关键词
        all_keywords = []
        for signal in all_signals:
            all_keywords.extend(signal.get("keywords", []))
        
        # 获取概念相关股票
        concept_stocks = self.analyzer.get_concept_stocks(all_keywords)
        
        # 合并热门股票和概念股票
        candidate_stocks = {}
        
        # 热门股票
        for stock in hot_stocks:
            code = stock["code"]
            if code not in candidate_stocks:
                candidate_stocks[code] = {
                    **stock,
                    "signals": [stock["source"]],
                    "score": 10 if stock["source"] == "资金榜" else 5
                }
            else:
                candidate_stocks[code]["signals"].append(stock["source"])
                candidate_stocks[code]["score"] += 5
        
        # 概念股票
        for stock in concept_stocks:
            code = stock["code"]
            if code not in candidate_stocks:
                candidate_stocks[code] = {
                    **stock,
                    "signals": [f"概念:{stock['concept']}"],
                    "score": 8
                }
            else:
                candidate_stocks[code]["signals"].append(f"概念:{stock['concept']}")
                candidate_stocks[code]["score"] += 8
        
        # 评分排序
        for code, stock in candidate_stocks.items():
            # 资金流入加分
            if stock.get("main_net", 0) > 1:
                stock["score"] += 10
            elif stock.get("main_net", 0) > 0:
                stock["score"] += 5
            
            # 涨幅适中加分（3-7%最佳）
            change = stock.get("change_pct", 0)
            if 3 <= change <= 7:
                stock["score"] += 5
            elif change > 9:
                stock["score"] -= 5  # 追高风险
        
        # 排序取TOP
        sorted_stocks = sorted(candidate_stocks.values(), key=lambda x: x["score"], reverse=True)
        
        # 生成推荐理由
        for stock in sorted_stocks[:8]:
            reasons = []
            
            # 根据信号生成理由
            for signal in stock.get("signals", []):
                if "资金" in signal:
                    reasons.append("主力资金流入")
                elif "涨幅" in signal:
                    reasons.append("涨幅领先")
                elif "概念" in signal:
                    concept = signal.split(":")[1] if ":" in signal else ""
                    reasons.append(f"{concept}概念龙头")
            
            # 资金面
            if stock.get("main_net", 0) > 1:
                reasons.append(f"主力净流入{stock['main_net']:.1f}亿")
            
            # 换手率
            if stock.get("turnover", 0) > 10:
                reasons.append("换手活跃")
            
            stock["reason"] = "、".join(reasons[:3]) if reasons else "综合评分领先"
            stock["related_signals"] = [s for s in all_signals if any(kw in stock.get("concept", "") or kw in stock.get("name", "") for kw in s.get("keywords", []))][:2]
            
            recommendations.append(stock)
        
        return recommendations, all_signals

# ==================== 缓存函数 ====================

@st.cache_data(ttl=120)
def fetch_global_indices():
    return GlobalMarketData().get_all_indices()

@st.cache_data(ttl=120)
def fetch_futures_data():
    return GlobalMarketData().get_futures_data()

@st.cache_data(ttl=180)
def fetch_sector_flow():
    return AStockAnalyzer().get_sector_flow()

@st.cache_data(ttl=60)
def fetch_north_flow():
    return AStockAnalyzer().get_north_flow()

@st.cache_data(ttl=120)
def fetch_hot_stocks():
    return AStockAnalyzer().get_hot_stocks()

@st.cache_data(ttl=300)
def fetch_news_data():
    return NewsAggregator().get_all_news()

@st.cache_data(ttl=300)
def fetch_news_keywords(news_data):
    return NewsAggregator().extract_keywords(news_data)

@st.cache_data(ttl=180)
def fetch_reddit_posts():
    return InternationalNews().get_reddit_hot()

@st.cache_data(ttl=180)
def fetch_hn_posts():
    return InternationalNews().get_hackernews_hot()

@st.cache_data(ttl=60)
def fetch_jin10_flash():
    return InternationalNews().get_jin10_flash()

@st.cache_data(ttl=120)
def generate_ai_recommendations(indices_json, futures_json, sectors_json, north_flow_json, hot_stocks_json, keywords_json):
    """生成AI推荐（使用JSON序列化参数以支持缓存）"""
    indices = json.loads(indices_json)
    futures = json.loads(futures_json)
    sectors = json.loads(sectors_json)
    north_flow = json.loads(north_flow_json)
    hot_stocks = json.loads(hot_stocks_json)
    keywords = json.loads(keywords_json)
    
    recommender = AIStockRecommender()
    return recommender.generate_recommendations(indices, futures, sectors, north_flow, hot_stocks, keywords)

# ==================== 会话状态 ====================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "ai"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0;'>
        <div style='font-size: 24px; font-weight: 700; color: #f5f5f7;'>📊 股市观察</div>
        <div style='font-size: 13px; color: #86868b; margin-top: 4px;'>AI智能选股 v4.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 10px 0;'></div>", unsafe_allow_html=True)
    
    tab = st.radio("功能模块", ["🤖 AI智能选股", "🌍 全球行情", "📈 自选监控"], label_visibility="collapsed")
    
    if "AI" in tab:
        st.session_state.current_tab = "ai"
    elif "全球" in tab:
        st.session_state.current_tab = "global"
    else:
        st.session_state.current_tab = "watchlist"
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown(f"<div style='color: #48484a; font-size: 11px; margin-top: 20px; text-align: center;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)

# ==================== 主界面 ====================

if st.session_state.current_tab == "ai":
    # AI智能选股页面
    st.markdown("""
    <div class='main-title'>AI智能选股</div>
    <div class='sub-title'>全球联动分析 · 多维度信号聚合 · 智能推荐</div>
    """, unsafe_allow_html=True)
    
    # 获取所有数据
    with st.spinner("正在分析全球市场数据..."):
        indices = fetch_global_indices()
        futures = fetch_futures_data()
        sectors = fetch_sector_flow()
        north_flow = fetch_north_flow()
        hot_stocks = fetch_hot_stocks()
        news = fetch_news_data()
        news_keywords = fetch_news_keywords(news)
        
        # 生成推荐
        recommendations, signals = generate_ai_recommendations(
            json.dumps(indices),
            json.dumps(futures),
            json.dumps(sectors),
            json.dumps(north_flow),
            json.dumps(hot_stocks),
            json.dumps(news_keywords)
        )
    
    # ========== 市场信号概览 ==========
    st.markdown("<div class='section-header'>📡 市场信号</div>", unsafe_allow_html=True)
    
    signal_cols = st.columns(4)
    
    # 美股信号
    with signal_cols[0]:
        us_indices = [i for i in indices if i["region"] == "美国"]
        us_avg = sum(i["change_pct"] for i in us_indices) / len(us_indices) if us_indices else 0
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
        nf = north_flow["total"]
        change_class = "up" if nf > 0 else "down"
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
        change_class = "up" if top_sector["change_pct"] > 0 else "down"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>🔥 领涨板块</div>
            <div class='index-name'>{top_sector['name']}</div>
            <div class='index-change {change_class}' style='font-size: 24px;'>+{top_sector['change_pct']:.2f}%</div>
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
                for sig in stock.get("signals", [])[:3]:
                    if "资金" in sig:
                        signal_tags += "<span class='signal-tag signal-fund'>💰 资金流入</span>"
                    elif "涨幅" in sig:
                        signal_tags += "<span class='signal-tag signal-hot'>🔥 涨幅领先</span>"
                    elif "概念" in sig:
                        concept = sig.split(":")[1] if ":" in sig else "热点"
                        signal_tags += f"<span class='signal-tag signal-news'>📰 {concept}</span>"
                
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
        st.markdown("<div style='color: #86868b; text-align: center; padding: 40px;'>暂无推荐数据</div>", unsafe_allow_html=True)
    
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
    st.markdown("<div class='section-header'>💰 板块资金流向 TOP10</div>", unsafe_allow_html=True)
    
    sector_cols = st.columns(5)
    for i, sector in enumerate(sectors[:10]):
        with sector_cols[i % 5]:
            change_class = "up" if sector["change_pct"] > 0 else "down"
            fund_class = "up" if sector["main_net"] > 0 else "down"
            st.markdown(f"""
            <div class='fund-flow-card'>
                <div class='fund-name'>{sector['name']}</div>
                <div class='index-change {change_class}'>{'+' if sector['change_pct'] > 0 else ''}{sector['change_pct']:.2f}%</div>
                <div class='fund-amount {fund_class}'>{'+' if sector['main_net'] > 0 else ''}{sector['main_net']:.1f}亿</div>
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

elif st.session_state.current_tab == "global":
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
    cols = st.columns(4)
    for i, idx in enumerate(indices[:12]):
        with cols[i % 4]:
            change_class = "up" if idx["change_pct"] > 0 else ("down" if idx["change_pct"] < 0 else "neutral")
            st.markdown(f"""
            <div class='index-card'>
                <div class='index-region'>{idx['region']}</div>
                <div class='index-name'>{idx['name']}</div>
                <div class='index-price'>{idx['price']:,.2f}</div>
                <div class='index-change {change_class}'>{'+' if idx['change_pct'] > 0 else ''}{idx['change_pct']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 期货
    st.markdown("<div class='section-header'>📈 期货行情</div>", unsafe_allow_html=True)
    fut_cols = st.columns(6)
    for i, fut in enumerate(futures[:6]):
        with fut_cols[i]:
            change_class = "up" if fut["change_pct"] > 0 else "down"
            st.markdown(f"""
            <div class='futures-card'>
                <div class='futures-name'>{fut['name']}</div>
                <div class='futures-price'>{fut['price']:,.2f}</div>
                <div class='futures-change {change_class}'>{'+' if fut['change_pct'] > 0 else ''}{fut['change_pct']:.2f}%</div>
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
        for post in reddit[:6]:
            st.markdown(f"""
            <div class='intl-card'>
                <div class='intl-title'>{post['title']}</div>
                <div class='intl-meta'><span class='tag tag-reddit'>{post['subreddit']}</span></div>
                <div class='intl-stats'>👍 {post['score']:,} · 💬 {post['comments']:,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with intl_cols[1]:
        st.markdown("<div class='news-section-title'>🧡 Hacker News</div>", unsafe_allow_html=True)
        for post in hn[:6]:
            st.markdown(f"""
            <div class='intl-card'>
                <div class='intl-title'>{post['title']}</div>
                <div class='intl-meta'><span class='tag tag-hn'>HN</span></div>
                <div class='intl-stats'>👍 {post['score']:,} · 💬 {post['comments']:,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 国内新闻
    st.markdown("<div class='section-header'>📰 国内财经</div>", unsafe_allow_html=True)
    news_cols = st.columns(3)
    categories = [("politics", "🏛️ 政治"), ("economy", "💰 经济"), ("tech", "🔬 科技")]
    
    for col, (cat_key, cat_name) in zip(news_cols, categories):
        with col:
            st.markdown(f"<div class='news-section-title'>{cat_name}</div>", unsafe_allow_html=True)
            for i, item in enumerate(news.get(cat_key, [])[:8], 1):
                title = item['title'][:35] + '...' if len(item['title']) > 35 else item['title']
                st.markdown(f"""
                <div class='news-card'>
                    <div class='news-number'>{i:02d}</div>
                    <div class='news-title'>{title}</div>
                    <div class='news-meta'>{item.get('time', '')}</div>
                </div>
                """, unsafe_allow_html=True)

else:
    # 自选监控页面
    st.markdown("""
    <div class='main-title'>自选监控</div>
    <div class='sub-title'>实时跟踪您关注的股票</div>
    """, unsafe_allow_html=True)
    
    st.info("🔧 自选监控功能开发中，敬请期待...")

# Footer
st.markdown(f"""
<div class='footer-info'>
    数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    数据来源: 东方财富 / 新浪财经 / 金十数据 / Reddit / Hacker News<br>
    ⚠️ 本工具仅供参考，不构成投资建议
</div>
""", unsafe_allow_html=True)
