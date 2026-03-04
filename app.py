"""
📊 股市观察 v4.2
专业级AI智能选股系统
- 顶部导航（移动端适配）
- 自选股监控
- 多维度数据源
- 智能推荐引擎
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
    initial_sidebar_state="collapsed"  # 默认收起侧边栏
)

# ==================== 专业级CSS（移动端适配） ====================
st.markdown("""
<style>
/* 全局样式 */
.stApp { background: #000000; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
* { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', sans-serif; }

/* 隐藏侧边栏 */
[data-testid="stSidebar"] { display: none; }

/* 顶部导航 */
.top-nav {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(20px);
    padding: 12px 0;
    border-bottom: 1px solid #2c2c2e;
    margin-bottom: 20px;
}

.nav-container {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    padding: 0 16px;
}

.nav-btn {
    padding: 10px 20px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    text-decoration: none;
}

.nav-active {
    background: linear-gradient(135deg, #0a84ff, #5e5ce6);
    color: white;
}

.nav-inactive {
    background: rgba(255, 255, 255, 0.1);
    color: #86868b;
}

.nav-inactive:hover {
    background: rgba(255, 255, 255, 0.15);
    color: #f5f5f7;
}

/* 标题 */
.main-title {
    font-size: 36px;
    font-weight: 700;
    color: #f5f5f7;
    text-align: center;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}

.sub-title {
    font-size: 15px;
    font-weight: 400;
    color: #86868b;
    text-align: center;
    margin-bottom: 30px;
}

.section-header {
    font-size: 24px;
    font-weight: 600;
    color: #f5f5f7;
    margin: 30px 0 16px 0;
    padding-left: 12px;
    border-left: 4px solid #0a84ff;
}

/* 卡片样式 */
.index-card {
    background: rgba(28, 28, 30, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}

.index-card:hover {
    transform: translateY(-2px);
    border-color: rgba(10, 132, 255, 0.3);
}

.index-region {
    font-size: 11px;
    font-weight: 500;
    color: #86868b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.index-name {
    font-size: 14px;
    font-weight: 600;
    color: #f5f5f7;
    margin: 4px 0;
}

.index-price {
    font-size: 22px;
    font-weight: 700;
    color: #f5f5f7;
}

.index-change {
    font-size: 14px;
    font-weight: 600;
    margin-top: 4px;
}

.up { color: #34c759; }
.down { color: #ff3b30; }
.neutral { color: #86868b; }

/* AI推荐区 */
.ai-section {
    background: linear-gradient(135deg, rgba(10, 132, 255, 0.08), rgba(94, 92, 230, 0.08));
    border: 1px solid rgba(10, 132, 255, 0.2);
    border-radius: 20px;
    padding: 24px;
    margin: 20px 0;
}

.ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.ai-icon { font-size: 28px; }
.ai-title { font-size: 20px; font-weight: 700; color: #f5f5f7; }
.ai-subtitle { font-size: 12px; color: #86868b; }

/* 推荐股票卡片 */
.stock-card {
    background: rgba(28, 28, 30, 0.9);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
}

.stock-card:hover {
    border-color: rgba(10, 132, 255, 0.4);
    transform: translateY(-2px);
}

.stock-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}

.stock-name {
    font-size: 16px;
    font-weight: 700;
    color: #f5f5f7;
}

.stock-code {
    font-size: 12px;
    color: #86868b;
}

.stock-price {
    font-size: 20px;
    font-weight: 700;
    text-align: right;
}

.stock-change {
    font-size: 13px;
    text-align: right;
}

.stock-reason {
    background: rgba(10, 132, 255, 0.1);
    border-radius: 8px;
    padding: 10px;
    margin-top: 10px;
}

.reason-label {
    font-size: 11px;
    font-weight: 600;
    color: #0a84ff;
    margin-bottom: 4px;
}

.reason-text {
    font-size: 12px;
    color: #f5f5f7;
    line-height: 1.5;
}

/* 信号标签 */
.signal-tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    margin-right: 4px;
    margin-top: 6px;
}

.tag-fund { background: rgba(52, 199, 89, 0.2); color: #34c759; }
.tag-hot { background: rgba(255, 59, 48, 0.2); color: #ff453a; }
.tag-news { background: rgba(255, 159, 10, 0.2); color: #ff9f0a; }
.tag-tech { background: rgba(10, 132, 255, 0.2); color: #0a84ff; }

/* 板块资金 */
.sector-card {
    background: rgba(28, 28, 30, 0.6);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.sector-name {
    font-size: 13px;
    font-weight: 600;
    color: #f5f5f7;
}

.sector-change {
    font-size: 12px;
    margin-top: 2px;
}

.sector-flow {
    font-size: 14px;
    font-weight: 700;
    margin-top: 4px;
}

/* 快讯 */
.flash-card {
    background: rgba(232, 65, 66, 0.06);
    border-left: 3px solid #e84142;
    padding: 10px 14px;
    margin-bottom: 6px;
    border-radius: 0 10px 10px 0;
}

.flash-time {
    font-size: 11px;
    font-weight: 600;
    color: #e84142;
}

.flash-content {
    font-size: 12px;
    color: #f5f5f7;
    margin-top: 4px;
    line-height: 1.5;
}

/* 新闻卡片 */
.news-card {
    background: rgba(28, 28, 30, 0.5);
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 6px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.news-num {
    font-size: 11px;
    font-weight: 700;
    color: #0a84ff;
}

.news-title {
    font-size: 13px;
    color: #f5f5f7;
    margin-top: 4px;
    line-height: 1.4;
}

.news-meta {
    font-size: 11px;
    color: #86868b;
    margin-top: 6px;
}

/* 自选股详情 */
.watchlist-card {
    background: rgba(28, 28, 30, 0.9);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.watchlist-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.watchlist-name {
    font-size: 18px;
    font-weight: 700;
    color: #f5f5f7;
}

.watchlist-code {
    font-size: 13px;
    color: #86868b;
}

.watchlist-price {
    font-size: 28px;
    font-weight: 700;
    margin: 12px 0;
}

.watchlist-detail {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #2c2c2e;
}

.watchlist-detail:last-child {
    border-bottom: none;
}

.detail-label {
    font-size: 13px;
    color: #86868b;
}

.detail-value {
    font-size: 13px;
    color: #f5f5f7;
    font-weight: 500;
}

/* 搜索框 */
.search-box {
    background: rgba(28, 28, 30, 0.8);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 国际社区 */
.intl-card {
    background: rgba(28, 28, 30, 0.5);
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 6px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.intl-title {
    font-size: 12px;
    color: #f5f5f7;
    line-height: 1.4;
}

.intl-stats {
    font-size: 11px;
    color: #0a84ff;
    margin-top: 6px;
}

/* 风险提示 */
.risk-box {
    background: rgba(255, 59, 48, 0.08);
    border: 1px solid rgba(255, 59, 48, 0.2);
    border-radius: 12px;
    padding: 14px;
    margin-top: 16px;
}

.risk-title {
    font-size: 13px;
    font-weight: 600;
    color: #ff453a;
    margin-bottom: 6px;
}

.risk-text {
    font-size: 11px;
    color: #86868b;
    line-height: 1.5;
}

/* 分割线 */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3a3a3c, transparent);
    margin: 30px 0;
}

/* 底部 */
.footer {
    text-align: center;
    color: #48484a;
    font-size: 11px;
    padding: 30px 0 20px 0;
}

/* Streamlit组件样式 */
.stButton > button {
    background: rgba(10, 132, 255, 0.15) !important;
    color: #0a84ff !important;
    border: 1px solid rgba(10, 132, 255, 0.3) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}

.stButton > button:hover {
    background: rgba(10, 132, 255, 0.25) !important;
}

.stTextInput > div > div > input {
    background: #1c1c1e !important;
    color: #f5f5f7 !important;
    border: 1px solid #3a3a3c !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}

.stSelectbox > div > div {
    background: #1c1c1e !important;
    border-radius: 8px !important;
}

/* 移动端适配 */
@media (max-width: 768px) {
    .main-title { font-size: 28px; }
    .sub-title { font-size: 13px; }
    .section-header { font-size: 20px; }
    .index-price { font-size: 18px; }
    .stock-price { font-size: 18px; }
    .nav-btn { padding: 8px 14px; font-size: 12px; }
}
</style>
""", unsafe_allow_html=True)

# ==================== 数据获取模块 ====================

class MarketDataEngine:
    """市场数据引擎 - 多源聚合"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Referer': 'https://quote.eastmoney.com/',
        })
    
    def get_global_indices(self):
        """全球股指"""
        indices = []
        codes = [
            {"code": "1.000001", "name": "上证指数", "region": "中国"},
            {"code": "0.399001", "name": "深证成指", "region": "中国"},
            {"code": "0.399006", "name": "创业板指", "region": "中国"},
            {"code": "100.HSI", "name": "恒生指数", "region": "香港"},
            {"code": "100.HSTECH", "name": "恒生科技", "region": "香港"},
            {"code": "100.DJIA", "name": "道琼斯", "region": "美国"},
            {"code": "100.NDX", "name": "纳斯达克", "region": "美国"},
            {"code": "100.SPX", "name": "标普500", "region": "美国"},
            {"code": "100.N225", "name": "日经225", "region": "日本"},
            {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
        ]
        
        for item in codes:
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {"secid": item["code"], "fields": "f43,f169,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                if data and data.get("f43"):
                    indices.append({
                        "name": item["name"], "region": item["region"],
                        "price": data["f43"] / 100,
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                    })
                else:
                    indices.append({"name": item["name"], "region": item["region"], "price": 0, "change_pct": 0})
            except:
                indices.append({"name": item["name"], "region": item["region"], "price": 0, "change_pct": 0})
        return indices
    
    def get_futures(self):
        """期货数据"""
        futures = []
        codes = [
            {"code": "113.IH00", "name": "上证50", "div": 100},
            {"code": "113.IF00", "name": "沪深300", "div": 100},
            {"code": "113.IC00", "name": "中证500", "div": 100},
            {"code": "113.AU0", "name": "黄金", "div": 1},
            {"code": "113.AG0", "name": "白银", "div": 1},
            {"code": "113.SC0", "name": "原油", "div": 1},
        ]
        
        for item in codes:
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {"secid": item["code"], "fields": "f43,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                if data and data.get("f43"):
                    futures.append({
                        "name": item["name"],
                        "price": data["f43"] / item["div"],
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0
                    })
            except:
                pass
        return futures
    
    def get_sector_flow(self):
        """板块资金流向"""
        sectors = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1, "pz": 30, "fs": "m:90+t:2",
                "fields": "f12,f14,f3,f62,f184,f66",
                "fid": "f62", "po": 1,
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=8)
            data = resp.json().get("data", {}).get("diff", [])
            
            for item in data[:20]:
                sectors.append({
                    "name": item.get("f14", ""),
                    "code": item.get("f12", ""),
                    "change_pct": item.get("f3", 0) / 100 if item.get("f3") else 0,
                    "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,
                    "main_pct": item.get("f184", 0) / 100 if item.get("f184") else 0,
                })
        except:
            pass
        return sectors
    
    def get_north_flow(self):
        """北向资金"""
        try:
            url = "https://push2.eastmoney.com/api/qt/kamt.rtmin/get"
            params = {"fields1": "f1,f2,f3,f4", "fields2": "f51,f52,f53,f54,f55,f56"}
            resp = self.session.get(url, params=params, timeout=8)
            data = resp.json().get("data", {})
            
            if data:
                s2n = data.get("s2n", [])
                if s2n:
                    latest = s2n[-1].split(",") if isinstance(s2n[-1], str) else []
                    if len(latest) >= 2 and latest[1] != "-":
                        return {"total": float(latest[1]) / 10000}
        except:
            pass
        return {"total": 0}
    
    def get_hot_stocks(self):
        """热门股票 - 多维度"""
        stocks = []
        
        # 涨幅榜
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1, "pz": 30,
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f62,f184,f225,f115",
                "fid": "f3", "po": 1,
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json().get("data", {}).get("diff", [])
            
            for item in data[:20]:
                code = item.get("f12", "")
                if not code:
                    continue
                
                def safe_float(val, divisor=1):
                    if val and val != "-" and val is not None:
                        try:
                            return float(val) / divisor
                        except:
                            pass
                    return 0
                
                stocks.append({
                    "code": code,
                    "name": item.get("f14", ""),
                    "market": "sh" if code.startswith("6") else "sz",
                    "price": safe_float(item.get("f2"), 100),
                    "change_pct": safe_float(item.get("f3"), 100),
                    "change_amt": safe_float(item.get("f4"), 100),
                    "volume": safe_float(item.get("f5"), 1),  # 手
                    "amount": safe_float(item.get("f6"), 100000000),  # 亿
                    "turnover": safe_float(item.get("f8"), 100),  # 换手率
                    "pe": safe_float(item.get("f9"), 100),  # PE
                    "main_net": safe_float(item.get("f62"), 100000000),  # 主力净流入
                    "main_pct": safe_float(item.get("f184"), 100),  # 主力净占比
                    "high": safe_float(item.get("f15"), 100),
                    "low": safe_float(item.get("f16"), 100),
                    "open": safe_float(item.get("f17"), 100),
                    "source": "涨幅榜"
                })
        except:
            pass
        
        # 资金流入榜补充
        try:
            params["fid"] = "f62"
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json().get("data", {}).get("diff", [])
            
            existing = {s["code"] for s in stocks}
            for item in data[:15]:
                code = item.get("f12", "")
                if code and code not in existing:
                    def safe_float(val, divisor=1):
                        if val and val != "-" and val is not None:
                            try:
                                return float(val) / divisor
                            except:
                                pass
                        return 0
                    
                    stocks.append({
                        "code": code,
                        "name": item.get("f14", ""),
                        "market": "sh" if code.startswith("6") else "sz",
                        "price": safe_float(item.get("f2"), 100),
                        "change_pct": safe_float(item.get("f3"), 100),
                        "turnover": safe_float(item.get("f8"), 100),
                        "amount": safe_float(item.get("f6"), 100000000),
                        "main_net": safe_float(item.get("f62"), 100000000),
                        "source": "资金榜"
                    })
        except:
            pass
        
        return stocks
    
    def get_stock_list(self):
        """A股完整列表"""
        stocks = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            for fs in ["m:1+t:2,m:1+t:23", "m:0+t:6,m:0+t:80"]:
                params = {"pn": 1, "pz": 5000, "fs": fs, "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
                resp = self.session.get(url, params=params, timeout=15)
                for item in resp.json().get("data", {}).get("diff", []):
                    code = item.get("f12", "")
                    stocks.append({
                        "code": code,
                        "name": item.get("f14", ""),
                        "market": "sh" if code.startswith("6") else "sz"
                    })
        except:
            pass
        return stocks
    
    def get_stock_realtime(self, code, market):
        """单只股票实时数据"""
        try:
            secid = f"1.{code}" if market == "sh" else f"0.{code}"
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f169,f170,f171,f62,f184",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=5)
            data = resp.json().get("data", {})
            
            if data:
                def sf(val, div=1):
                    if val and val != "-":
                        try:
                            return float(val) / div
                        except:
                            pass
                    return 0
                
                return {
                    "code": code,
                    "name": data.get("f58", ""),
                    "price": sf(data.get("f43"), 100),
                    "change_pct": sf(data.get("f170"), 100),
                    "change_amt": sf(data.get("f169"), 100),
                    "volume": sf(data.get("f47"), 10000),  # 万手
                    "amount": sf(data.get("f48"), 100000000),  # 亿
                    "turnover": sf(data.get("f50"), 100),
                    "high": sf(data.get("f44"), 100),
                    "low": sf(data.get("f45"), 100),
                    "open": sf(data.get("f46"), 100),
                    "prev_close": sf(data.get("f60"), 100),
                    "main_net": sf(data.get("f62"), 100000000),
                }
        except:
            pass
        return None


class NewsEngine:
    """新闻引擎"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def get_news(self):
        """获取分类新闻"""
        news = {"politics": [], "economy": [], "tech": []}
        try:
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            for col, cat in [("345", "politics"), ("350", "economy"), ("351", "tech")]:
                params = {"columns": col, "pageSize": 12, "pageIndex": 0, "type": 1}
                resp = self.session.get(url, params=params, timeout=8)
                for item in resp.json().get("data", [])[:10]:
                    news[cat].append({
                        "title": item.get("title", ""),
                        "time": item.get("showTime", "")[-8:],
                        "source": item.get("mediaName", "")
                    })
        except:
            pass
        return news
    
    def get_keywords(self, news):
        """提取热点关键词"""
        patterns = [
            ("AI", ["AI", "人工智能", "大模型", "DeepSeek", "算力", "ChatGPT"]),
            ("芯片", ["芯片", "半导体", "光刻", "英伟达", "台积电"]),
            ("机器人", ["机器人", "人形", "具身智能"]),
            ("新能源", ["新能源", "光伏", "储能", "风电"]),
            ("锂电", ["锂电", "电池", "宁德", "比亚迪"]),
            ("医药", ["医药", "创新药", "生物"]),
            ("军工", ["军工", "国防", "航空航天"]),
            ("消费", ["消费", "白酒", "零售"]),
        ]
        
        text = " ".join([i["title"] for cat in news.values() for i in cat])
        keywords = [kw for kw, ps in patterns if any(p in text for p in ps)]
        return keywords if keywords else ["AI"]
    
    def get_jin10(self):
        """金十快讯"""
        flash = []
        try:
            url = "https://flash-api.jin10.com/get_flash_list"
            params = {"channel": "-8200", "vip": 1, "t": int(time.time() * 1000)}
            headers = {'Referer': 'https://www.jin10.com/', 'x-app-id': 'bVBF4FyRTn5NJF5n'}
            resp = self.session.get(url, params=params, headers=headers, timeout=8)
            
            for item in resp.json().get("data", [])[:15]:
                content = item.get("data", {})
                text = content.get("content", "") if isinstance(content, dict) else str(content)
                text = re.sub(r'<[^>]+>', '', text)
                if text and len(text) > 10:
                    flash.append({
                        "content": text[:100],
                        "time": item.get("time", "")[-8:-3],
                        "important": item.get("important", 0) == 1
                    })
        except:
            pass
        return flash
    
    def get_reddit(self):
        """Reddit热帖"""
        posts = []
        try:
            for sub in ["wallstreetbets", "stocks"]:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                resp = self.session.get(url, timeout=10)
                for p in resp.json().get("data", {}).get("children", [])[:5]:
                    d = p.get("data", {})
                    if not d.get("stickied"):
                        posts.append({
                            "title": d.get("title", "")[:70],
                            "sub": f"r/{sub}",
                            "score": d.get("score", 0),
                            "comments": d.get("num_comments", 0)
                        })
        except:
            pass
        return sorted(posts, key=lambda x: x.get("score", 0), reverse=True)[:8]
    
    def get_hn(self):
        """Hacker News"""
        posts = []
        try:
            ids = self.session.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8).json()[:12]
            for sid in ids:
                try:
                    s = self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=3).json()
                    if s and s.get("title"):
                        posts.append({
                            "title": s["title"][:70],
                            "score": s.get("score", 0),
                            "comments": s.get("descendants", 0)
                        })
                except:
                    pass
        except:
            pass
        return posts[:8]


class AIRecommender:
    """AI推荐引擎"""
    
    def recommend(self, indices, sectors, north_flow, hot_stocks, keywords):
        """生成推荐"""
        signals = []
        
        # 全球信号
        us = [i for i in indices if i.get("region") == "美国"]
        us_avg = sum(i.get("change_pct", 0) for i in us) / len(us) if us else 0
        if abs(us_avg) > 0.3:
            signals.append(f"美股{'上涨' if us_avg > 0 else '下跌'}{abs(us_avg):.1f}%")
        
        # 北向资金
        nf = north_flow.get("total", 0)
        if abs(nf) > 10:
            signals.append(f"北向{'净流入' if nf > 0 else '净流出'}{abs(nf):.0f}亿")
        
        # 热点
        if keywords:
            signals.append(f"热点: {', '.join(keywords[:2])}")
        
        # 评分推荐
        scored = []
        for s in hot_stocks:
            if not s.get("price") or s["price"] <= 0:
                continue
            
            score = 0
            tags = []
            reasons = []
            
            # 涨幅
            chg = s.get("change_pct", 0)
            if 1 <= chg <= 5:
                score += 20
                tags.append("涨幅适中")
            elif 5 < chg <= 8:
                score += 15
                tags.append("强势")
            elif chg > 8:
                score += 5
            elif chg > 0:
                score += 10
            
            # 资金
            mn = s.get("main_net", 0)
            if mn > 3:
                score += 25
                tags.append("主力大买")
                reasons.append(f"主力净流入{mn:.1f}亿")
            elif mn > 1:
                score += 18
                tags.append("资金流入")
                reasons.append(f"主力净流入{mn:.1f}亿")
            elif mn > 0:
                score += 10
            
            # 换手
            tr = s.get("turnover", 0)
            if 5 <= tr <= 15:
                score += 12
                tags.append("换手活跃")
            elif tr > 15:
                score += 5
            
            # 成交额
            amt = s.get("amount", 0)
            if amt > 10:
                score += 10
                reasons.append(f"成交额{amt:.1f}亿")
            elif amt > 5:
                score += 5
            
            # 来源加分
            if s.get("source") == "资金榜":
                score += 8
            
            s["score"] = score
            s["tags"] = tags[:3]
            s["reasons"] = reasons
            scored.append(s)
        
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # 生成推荐理由
        recommendations = []
        for s in scored[:10]:
            reason_parts = []
            if s.get("tags"):
                reason_parts.extend(s["tags"])
            if s.get("reasons"):
                reason_parts.extend(s["reasons"])
            
            s["reason"] = "、".join(reason_parts[:4]) if reason_parts else "综合评分领先"
            recommendations.append(s)
        
        return recommendations, signals


# ==================== 缓存 ====================

@st.cache_data(ttl=90)
def get_indices():
    return MarketDataEngine().get_global_indices()

@st.cache_data(ttl=90)
def get_futures():
    return MarketDataEngine().get_futures()

@st.cache_data(ttl=90)
def get_sectors():
    return MarketDataEngine().get_sector_flow()

@st.cache_data(ttl=60)
def get_north():
    return MarketDataEngine().get_north_flow()

@st.cache_data(ttl=60)
def get_hot():
    return MarketDataEngine().get_hot_stocks()

@st.cache_data(ttl=60)
def get_stock_list():
    return MarketDataEngine().get_stock_list()

def get_stock(code, market):
    return MarketDataEngine().get_stock_realtime(code, market)

@st.cache_data(ttl=180)
def get_news():
    return NewsEngine().get_news()

@st.cache_data(ttl=180)
def get_keywords_cached(news_json):
    return NewsEngine().get_keywords(json.loads(news_json))

@st.cache_data(ttl=60)
def get_jin10():
    return NewsEngine().get_jin10()

@st.cache_data(ttl=180)
def get_reddit():
    return NewsEngine().get_reddit()

@st.cache_data(ttl=180)
def get_hn():
    return NewsEngine().get_hn()


# ==================== 会话状态 ====================
if "tab" not in st.session_state:
    st.session_state.tab = "ai"
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}

# ==================== 顶部导航 ====================
st.markdown("""
<div class='top-nav'>
    <div style='text-align: center; margin-bottom: 8px;'>
        <span style='font-size: 20px; font-weight: 700; color: #f5f5f7;'>📊 股市观察</span>
        <span style='font-size: 12px; color: #86868b; margin-left: 8px;'>v4.2</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 导航按钮
nav_cols = st.columns(4)
with nav_cols[0]:
    if st.button("🤖 AI选股", use_container_width=True, type="primary" if st.session_state.tab == "ai" else "secondary"):
        st.session_state.tab = "ai"
        st.rerun()
with nav_cols[1]:
    if st.button("🌍 全球行情", use_container_width=True, type="primary" if st.session_state.tab == "global" else "secondary"):
        st.session_state.tab = "global"
        st.rerun()
with nav_cols[2]:
    if st.button("⭐ 自选股", use_container_width=True, type="primary" if st.session_state.tab == "watch" else "secondary"):
        st.session_state.tab = "watch"
        st.rerun()
with nav_cols[3]:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ==================== AI智能选股 ====================
if st.session_state.tab == "ai":
    st.markdown("<div class='main-title'>AI智能选股</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>多维度信号聚合 · 智能推荐</div>", unsafe_allow_html=True)
    
    # 获取数据
    indices = get_indices()
    sectors = get_sectors()
    north = get_north()
    hot = get_hot()
    news = get_news()
    keywords = get_keywords_cached(json.dumps(news))
    
    # 生成推荐
    recs, signals = AIRecommender().recommend(indices, sectors, north, hot, keywords)
    
    # 市场信号
    st.markdown("<div class='section-header'>市场信号</div>", unsafe_allow_html=True)
    sig_cols = st.columns(4)
    
    with sig_cols[0]:
        us = [i for i in indices if i.get("region") == "美国"]
        us_avg = sum(i.get("change_pct", 0) for i in us) / len(us) if us else 0
        cls = "up" if us_avg > 0 else "down"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>🇺🇸 美股</div>
            <div class='index-name'>隔夜表现</div>
            <div class='index-change {cls}' style='font-size: 22px;'>{'+' if us_avg > 0 else ''}{us_avg:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with sig_cols[1]:
        nf = north.get("total", 0)
        cls = "up" if nf > 0 else ("down" if nf < 0 else "neutral")
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>💰 北向资金</div>
            <div class='index-name'>今日净流入</div>
            <div class='index-change {cls}' style='font-size: 22px;'>{'+' if nf > 0 else ''}{nf:.1f}亿</div>
        </div>
        """, unsafe_allow_html=True)
    
    with sig_cols[2]:
        top = sectors[0] if sectors else {"name": "-", "change_pct": 0}
        cls = "up" if top.get("change_pct", 0) > 0 else "down"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>🔥 领涨板块</div>
            <div class='index-name'>{top.get('name', '-')}</div>
            <div class='index-change {cls}' style='font-size: 22px;'>+{top.get('change_pct', 0):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with sig_cols[3]:
        kw = keywords[0] if keywords else "-"
        st.markdown(f"""
        <div class='index-card'>
            <div class='index-region'>📰 新闻热点</div>
            <div class='index-name'>关键词</div>
            <div style='font-size: 18px; color: #0a84ff; font-weight: 600; margin-top: 4px;'>{kw}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # AI推荐
    st.markdown("""
    <div class='ai-section'>
        <div class='ai-header'>
            <span class='ai-icon'>🤖</span>
            <div>
                <div class='ai-title'>AI智能推荐</div>
                <div class='ai-subtitle'>基于资金流向、涨幅、换手率综合评分</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if recs:
        rec_cols = st.columns(2)
        for i, s in enumerate(recs[:8]):
            with rec_cols[i % 2]:
                cls = "up" if s.get("change_pct", 0) > 0 else "down"
                sym = "+" if s.get("change_pct", 0) > 0 else ""
                
                tags_html = ""
                for t in s.get("tags", [])[:3]:
                    if "资金" in t or "主力" in t:
                        tags_html += f"<span class='signal-tag tag-fund'>💰 {t}</span>"
                    elif "涨" in t or "强" in t:
                        tags_html += f"<span class='signal-tag tag-hot'>🔥 {t}</span>"
                    else:
                        tags_html += f"<span class='signal-tag tag-tech'>📊 {t}</span>"
                
                # 添加到自选按钮
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div class='stock-header'>
                            <div>
                                <div class='stock-name'>{s.get('name', '')}</div>
                                <div class='stock-code'>{s.get('code', '')}</div>
                            </div>
                            <div>
                                <div class='stock-price {cls}'>¥{s.get('price', 0):.2f}</div>
                                <div class='stock-change {cls}'>{sym}{s.get('change_pct', 0):.2f}%</div>
                            </div>
                        </div>
                        <div>{tags_html}</div>
                        <div class='stock-reason'>
                            <div class='reason-label'>推荐理由</div>
                            <div class='reason-text'>{s.get('reason', '')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("⭐", key=f"add_{s['code']}", help="加入自选"):
                        st.session_state.watchlist[s["code"]] = {"name": s["name"], "market": s.get("market", "sz")}
                        st.toast(f"已添加 {s['name']}")
    else:
        st.info("正在获取数据，请稍后刷新...")
    
    st.markdown("""
        <div class='risk-box'>
            <div class='risk-title'>⚠️ 风险提示</div>
            <div class='risk-text'>本推荐基于公开数据的量化分析，不构成投资建议。股市有风险，投资需谨慎。</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 板块资金
    if sectors:
        st.markdown("<div class='section-header'>板块资金流向</div>", unsafe_allow_html=True)
        sec_cols = st.columns(5)
        for i, sec in enumerate(sectors[:10]):
            with sec_cols[i % 5]:
                chg_cls = "up" if sec.get("change_pct", 0) > 0 else "down"
                flow_cls = "up" if sec.get("main_net", 0) > 0 else "down"
                st.markdown(f"""
                <div class='sector-card'>
                    <div class='sector-name'>{sec.get('name', '')}</div>
                    <div class='sector-change {chg_cls}'>{'+' if sec.get('change_pct', 0) > 0 else ''}{sec.get('change_pct', 0):.2f}%</div>
                    <div class='sector-flow {flow_cls}'>{'+' if sec.get('main_net', 0) > 0 else ''}{sec.get('main_net', 0):.1f}亿</div>
                </div>
                """, unsafe_allow_html=True)
    
    # 快讯
    jin10 = get_jin10()
    if jin10:
        st.markdown("<div class='section-header'>实时快讯</div>", unsafe_allow_html=True)
        flash_cols = st.columns(2)
        for i, f in enumerate(jin10[:8]):
            with flash_cols[i % 2]:
                st.markdown(f"""
                <div class='flash-card'>
                    <span class='flash-time'>{'🔴 ' if f.get('important') else ''}{f.get('time', '')}</span>
                    <div class='flash-content'>{f.get('content', '')}</div>
                </div>
                """, unsafe_allow_html=True)

# ==================== 全球行情 ====================
elif st.session_state.tab == "global":
    st.markdown("<div class='main-title'>全球行情</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>实时追踪全球市场动态</div>", unsafe_allow_html=True)
    
    indices = get_indices()
    futures = get_futures()
    news = get_news()
    jin10 = get_jin10()
    reddit = get_reddit()
    hn = get_hn()
    
    # 股指
    st.markdown("<div class='section-header'>全球股指</div>", unsafe_allow_html=True)
    idx_cols = st.columns(5)
    for i, idx in enumerate(indices[:10]):
        with idx_cols[i % 5]:
            cls = "up" if idx.get("change_pct", 0) > 0 else ("down" if idx.get("change_pct", 0) < 0 else "neutral")
            st.markdown(f"""
            <div class='index-card'>
                <div class='index-region'>{idx.get('region', '')}</div>
                <div class='index-name'>{idx.get('name', '')}</div>
                <div class='index-price'>{idx.get('price', 0):,.2f}</div>
                <div class='index-change {cls}'>{'+' if idx.get('change_pct', 0) > 0 else ''}{idx.get('change_pct', 0):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 期货
    st.markdown("<div class='section-header'>期货行情</div>", unsafe_allow_html=True)
    fut_cols = st.columns(6)
    for i, f in enumerate(futures[:6]):
        with fut_cols[i]:
            cls = "up" if f.get("change_pct", 0) > 0 else "down"
            st.markdown(f"""
            <div class='sector-card'>
                <div class='sector-name'>{f.get('name', '')}</div>
                <div style='font-size: 16px; font-weight: 700; color: #f5f5f7; margin: 4px 0;'>{f.get('price', 0):,.2f}</div>
                <div class='sector-change {cls}'>{'+' if f.get('change_pct', 0) > 0 else ''}{f.get('change_pct', 0):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 快讯
    if jin10:
        st.markdown("<div class='section-header'>实时快讯</div>", unsafe_allow_html=True)
        flash_cols = st.columns(2)
        for i, f in enumerate(jin10[:10]):
            with flash_cols[i % 2]:
                st.markdown(f"""
                <div class='flash-card'>
                    <span class='flash-time'>{'🔴 ' if f.get('important') else ''}{f.get('time', '')}</span>
                    <div class='flash-content'>{f.get('content', '')}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 国际社区
    st.markdown("<div class='section-header'>国际社区</div>", unsafe_allow_html=True)
    intl_cols = st.columns(2)
    
    with intl_cols[0]:
        st.markdown("<div class='news-section-title' style='font-size: 18px; color: #ff4500;'>🔥 Reddit</div>", unsafe_allow_html=True)
        for p in reddit[:6]:
            st.markdown(f"""
            <div class='intl-card'>
                <div class='intl-title'>{p.get('title', '')}</div>
                <div class='intl-stats'>👍 {p.get('score', 0):,} · 💬 {p.get('comments', 0):,} · {p.get('sub', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with intl_cols[1]:
        st.markdown("<div class='news-section-title' style='font-size: 18px; color: #ff6600;'>🧡 Hacker News</div>", unsafe_allow_html=True)
        for p in hn[:6]:
            st.markdown(f"""
            <div class='intl-card'>
                <div class='intl-title'>{p.get('title', '')}</div>
                <div class='intl-stats'>👍 {p.get('score', 0):,} · 💬 {p.get('comments', 0):,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 国内新闻
    st.markdown("<div class='section-header'>国内财经</div>", unsafe_allow_html=True)
    news_cols = st.columns(3)
    cats = [("politics", "🏛️ 政治"), ("economy", "💰 经济"), ("tech", "🔬 科技")]
    
    for col, (key, name) in zip(news_cols, cats):
        with col:
            st.markdown(f"<div style='font-size: 16px; font-weight: 600; color: #f5f5f7; margin-bottom: 12px;'>{name}</div>", unsafe_allow_html=True)
            for i, n in enumerate(news.get(key, [])[:8], 1):
                title = n.get('title', '')[:32] + '...' if len(n.get('title', '')) > 32 else n.get('title', '')
                st.markdown(f"""
                <div class='news-card'>
                    <div class='news-num'>{i:02d}</div>
                    <div class='news-title'>{title}</div>
                    <div class='news-meta'>{n.get('time', '')}</div>
                </div>
                """, unsafe_allow_html=True)

# ==================== 自选股 ====================
elif st.session_state.tab == "watch":
    st.markdown("<div class='main-title'>自选股</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>实时跟踪您关注的股票</div>", unsafe_allow_html=True)
    
    # 搜索添加
    st.markdown("<div class='section-header'>搜索添加</div>", unsafe_allow_html=True)
    
    search = st.text_input("输入股票代码或名称", placeholder="如: 600519 或 贵州茅台", label_visibility="collapsed")
    
    if search:
        all_stocks = get_stock_list()
        results = [s for s in all_stocks if search.lower() in s.get("code", "").lower() or search in s.get("name", "")][:8]
        
        if results:
            for s in results:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{s['name']}** ({s['code']})")
                with col2:
                    if st.button("➕", key=f"search_add_{s['code']}"):
                        st.session_state.watchlist[s["code"]] = {"name": s["name"], "market": s["market"]}
                        st.toast(f"已添加 {s['name']}")
                        st.rerun()
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # 自选列表
    if st.session_state.watchlist:
        st.markdown(f"<div class='section-header'>我的自选 ({len(st.session_state.watchlist)}只)</div>", unsafe_allow_html=True)
        
        watch_cols = st.columns(2)
        for i, (code, info) in enumerate(list(st.session_state.watchlist.items())):
            data = get_stock(code, info["market"])
            
            with watch_cols[i % 2]:
                if data:
                    cls = "up" if data.get("change_pct", 0) > 0 else ("down" if data.get("change_pct", 0) < 0 else "neutral")
                    sym = "+" if data.get("change_pct", 0) > 0 else ""
                    
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.markdown(f"""
                        <div class='watchlist-card'>
                            <div class='watchlist-header'>
                                <div>
                                    <div class='watchlist-name'>{data.get('name', info['name'])}</div>
                                    <div class='watchlist-code'>{code}</div>
                                </div>
                            </div>
                            <div class='watchlist-price {cls}'>¥{data.get('price', 0):.2f}</div>
                            <div class='index-change {cls}' style='margin-bottom: 12px;'>{sym}{data.get('change_amt', 0):.2f} ({sym}{data.get('change_pct', 0):.2f}%)</div>
                            <div class='watchlist-detail'>
                                <span class='detail-label'>成交量</span>
                                <span class='detail-value'>{data.get('volume', 0):.2f}万手</span>
                            </div>
                            <div class='watchlist-detail'>
                                <span class='detail-label'>成交额</span>
                                <span class='detail-value'>{data.get('amount', 0):.2f}亿</span>
                            </div>
                            <div class='watchlist-detail'>
                                <span class='detail-label'>换手率</span>
                                <span class='detail-value'>{data.get('turnover', 0):.2f}%</span>
                            </div>
                            <div class='watchlist-detail'>
                                <span class='detail-label'>最高/最低</span>
                                <span class='detail-value'>{data.get('high', 0):.2f} / {data.get('low', 0):.2f}</span>
                            </div>
                            <div class='watchlist-detail'>
                                <span class='detail-label'>主力净流入</span>
                                <span class='detail-value {cls}'>{data.get('main_net', 0):.2f}亿</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("🗑️", key=f"del_{code}", help="移除"):
                            del st.session_state.watchlist[code]
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div class='watchlist-card'>
                        <div class='watchlist-name'>{info['name']}</div>
                        <div class='watchlist-code'>{code}</div>
                        <div style='color: #86868b; margin-top: 10px;'>数据加载中...</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 60px 20px; color: #86868b;'>
            <div style='font-size: 48px; margin-bottom: 16px;'>⭐</div>
            <div style='font-size: 16px;'>暂无自选股</div>
            <div style='font-size: 13px; margin-top: 8px;'>在上方搜索添加，或从AI推荐中添加</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 热门推荐
        st.markdown("<div class='section-header'>热门股票</div>", unsafe_allow_html=True)
        hots = [
            {"code": "600519", "name": "贵州茅台", "market": "sh"},
            {"code": "300750", "name": "宁德时代", "market": "sz"},
            {"code": "000858", "name": "五粮液", "market": "sz"},
            {"code": "601318", "name": "中国平安", "market": "sh"},
            {"code": "002475", "name": "立讯精密", "market": "sz"},
            {"code": "300059", "name": "东方财富", "market": "sz"},
        ]
        
        hot_cols = st.columns(3)
        for i, h in enumerate(hots):
            with hot_cols[i % 3]:
                if st.button(f"➕ {h['name']}", key=f"hot_{h['code']}", use_container_width=True):
                    st.session_state.watchlist[h["code"]] = {"name": h["name"], "market": h["market"]}
                    st.rerun()

# ==================== 底部 ====================
st.markdown(f"""
<div class='footer'>
    数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    数据来源: 东方财富 / 金十数据 / Reddit / Hacker News<br>
    ⚠️ 本工具仅供参考，不构成投资建议
</div>
""", unsafe_allow_html=True)
