"""
📊 股市观察 v5.0
稳定版 - 确保数据显示
"""

import streamlit as st
import requests
import json
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="股市观察",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 样式 ====================
st.markdown("""
<style>
.stApp { background: #0a0a0a; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
* { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; }
[data-testid="stSidebar"] { display: none; }

.title { font-size: 32px; font-weight: 700; color: #f5f5f7; text-align: center; margin-bottom: 6px; }
.subtitle { font-size: 14px; color: #86868b; text-align: center; margin-bottom: 20px; }
.header { font-size: 20px; font-weight: 600; color: #f5f5f7; margin: 24px 0 12px 0; padding-left: 10px; border-left: 3px solid #0a84ff; }

.card { background: rgba(30,30,32,0.9); border-radius: 12px; padding: 14px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.06); }
.card:hover { border-color: rgba(10,132,255,0.3); }

.region { font-size: 10px; color: #86868b; text-transform: uppercase; }
.name { font-size: 13px; font-weight: 600; color: #f5f5f7; margin: 2px 0; }
.price { font-size: 18px; font-weight: 700; color: #f5f5f7; }
.change { font-size: 12px; font-weight: 600; }

.up { color: #34c759; }
.down { color: #ff3b30; }
.flat { color: #86868b; }

.ai-box { background: linear-gradient(135deg, rgba(10,132,255,0.1), rgba(94,92,230,0.1)); border: 1px solid rgba(10,132,255,0.25); border-radius: 16px; padding: 18px; margin: 16px 0; }
.ai-title { font-size: 18px; font-weight: 700; color: #f5f5f7; margin-bottom: 4px; }
.ai-sub { font-size: 11px; color: #86868b; margin-bottom: 14px; }

.stock-card { background: rgba(30,30,32,0.95); border-radius: 10px; padding: 12px; margin-bottom: 6px; border: 1px solid rgba(255,255,255,0.05); }
.stock-name { font-size: 14px; font-weight: 700; color: #f5f5f7; }
.stock-code { font-size: 10px; color: #86868b; }
.stock-price { font-size: 16px; font-weight: 700; }
.stock-info { font-size: 11px; color: #86868b; margin-top: 6px; }

.tag { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 600; margin-right: 3px; }
.tag-up { background: rgba(52,199,89,0.2); color: #34c759; }
.tag-fund { background: rgba(10,132,255,0.2); color: #0a84ff; }
.tag-hot { background: rgba(255,59,48,0.2); color: #ff453a; }

.sector { background: rgba(30,30,32,0.8); border-radius: 8px; padding: 10px; margin-bottom: 5px; }
.sector-name { font-size: 11px; font-weight: 600; color: #f5f5f7; }
.sector-val { font-size: 13px; font-weight: 700; margin-top: 2px; }

.flash { background: rgba(232,65,66,0.08); border-left: 2px solid #e84142; padding: 8px 10px; margin-bottom: 4px; border-radius: 0 6px 6px 0; }
.flash-time { font-size: 9px; color: #e84142; font-weight: 600; }
.flash-text { font-size: 11px; color: #f5f5f7; margin-top: 2px; line-height: 1.4; }

.news { background: rgba(30,30,32,0.6); border-radius: 6px; padding: 8px; margin-bottom: 4px; }
.news-title { font-size: 11px; color: #f5f5f7; line-height: 1.4; }
.news-meta { font-size: 9px; color: #86868b; margin-top: 4px; }

.intl { background: rgba(30,30,32,0.6); border-radius: 6px; padding: 8px; margin-bottom: 4px; }
.intl-title { font-size: 10px; color: #f5f5f7; line-height: 1.3; }
.intl-stats { font-size: 9px; color: #0a84ff; margin-top: 3px; }

.watch-card { background: rgba(30,30,32,0.95); border-radius: 12px; padding: 14px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.08); }
.watch-name { font-size: 15px; font-weight: 700; color: #f5f5f7; }
.watch-price { font-size: 22px; font-weight: 700; margin: 8px 0; }
.watch-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #222; font-size: 11px; }
.watch-label { color: #86868b; }
.watch-value { color: #f5f5f7; }

.risk { background: rgba(255,59,48,0.08); border: 1px solid rgba(255,59,48,0.2); border-radius: 8px; padding: 10px; margin-top: 12px; font-size: 10px; color: #86868b; }

.footer { text-align: center; color: #48484a; font-size: 10px; padding: 20px 0; }

.stButton > button { background: rgba(10,132,255,0.15) !important; color: #0a84ff !important; border: 1px solid rgba(10,132,255,0.3) !important; border-radius: 6px !important; font-size: 12px !important; padding: 6px 12px !important; }
.stTextInput input { background: #1a1a1c !important; color: #f5f5f7 !important; border: 1px solid #333 !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== 数据获取 ====================

class DataFetcher:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
    
    def get(self, url, params=None, headers=None, timeout=8):
        try:
            r = self.s.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r
        except:
            pass
        return None
    
    # 全球指数
    def fetch_indices(self):
        indices = []
        items = [
            ("1.000001", "上证指数", "🇨🇳 中国"),
            ("0.399001", "深证成指", "🇨🇳 中国"),
            ("0.399006", "创业板指", "🇨🇳 中国"),
            ("100.HSI", "恒生指数", "🇭🇰 香港"),
            ("100.HSTECH", "恒生科技", "🇭🇰 香港"),
            ("100.HSCEI", "国企指数", "🇭🇰 香港"),
            ("100.DJIA", "道琼斯", "🇺🇸 美国"),
            ("100.NDX", "纳斯达克100", "🇺🇸 美国"),
            ("100.SPX", "标普500", "🇺🇸 美国"),
            ("100.N225", "日经225", "🇯🇵 日本"),
            ("100.KS11", "韩国综合", "🇰🇷 韩国"),
            ("100.TWII", "台湾加权", "🇹🇼 台湾"),
            ("100.FTSE", "富时100", "🇬🇧 英国"),
            ("100.GDAXI", "德国DAX", "🇩🇪 德国"),
            ("100.FCHI", "法国CAC40", "🇫🇷 法国"),
        ]
        
        for code, name, region in items:
            try:
                r = self.get(
                    "https://push2.eastmoney.com/api/qt/stock/get",
                    {"secid": code, "fields": "f43,f169,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    timeout=5
                )
                if r:
                    d = r.json().get("data", {})
                    if d and d.get("f43"):
                        indices.append({
                            "name": name, "region": region,
                            "price": d["f43"] / 100,
                            "change_pct": d.get("f170", 0) / 100 if d.get("f170") else 0,
                        })
            except:
                pass
        return indices
    
    # 期货
    def fetch_futures(self):
        futures = []
        items = [
            ("113.IH00", "上证50", 100), ("113.IF00", "沪深300", 100), ("113.IC00", "中证500", 100),
            ("113.AU0", "沪金", 1), ("113.AG0", "沪银", 1), ("113.SC0", "原油", 1),
            ("113.CU0", "沪铜", 1), ("113.AL0", "沪铝", 1), ("113.RB0", "螺纹钢", 1),
        ]
        
        for code, name, div in items:
            try:
                r = self.get(
                    "https://push2.eastmoney.com/api/qt/stock/get",
                    {"secid": code, "fields": "f43,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    timeout=5
                )
                if r:
                    d = r.json().get("data", {})
                    if d and d.get("f43"):
                        futures.append({
                            "name": name,
                            "price": d["f43"] / div,
                            "change_pct": d.get("f170", 0) / 100 if d.get("f170") else 0,
                        })
            except:
                pass
        return futures
    
    # 外汇
    def fetch_forex(self):
        forex = []
        try:
            r = self.get(
                "https://hq.sinajs.cn/list=fx_sUSDCNY,fx_sEURCNY,fx_sGBPCNY,fx_sJPYCNY,fx_sHKDCNY",
                headers={'Referer': 'https://finance.sina.com.cn'}
            )
            if r:
                r.encoding = 'gbk'
                names = {"USDCNY": "美元/人民币", "EURCNY": "欧元/人民币", "GBPCNY": "英镑/人民币", "JPYCNY": "日元/人民币", "HKDCNY": "港币/人民币"}
                for line in r.text.strip().split('\n'):
                    for code, name in names.items():
                        if code in line and '"' in line:
                            parts = line.split('"')[1].split(',')
                            if len(parts) >= 4:
                                curr = float(parts[1]) if parts[1] else 0
                                prev = float(parts[3]) if parts[3] else curr
                                chg = ((curr - prev) / prev * 100) if prev else 0
                                forex.append({"name": name, "price": curr, "change_pct": chg})
                            break
        except:
            pass
        return forex
    
    # 板块
    def fetch_sectors(self):
        sectors = []
        try:
            r = self.get(
                "https://push2.eastmoney.com/api/qt/clist/get",
                {"pn": 1, "pz": 20, "fs": "m:90+t:2", "fields": "f14,f3,f62,f184", "fid": "f62", "po": 1, "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
            )
            if r:
                for item in r.json().get("data", {}).get("diff", [])[:15]:
                    sectors.append({
                        "name": item.get("f14", ""),
                        "change_pct": item.get("f3", 0) / 100 if item.get("f3") else 0,
                        "main_net": item.get("f62", 0) / 100000000 if item.get("f62") else 0,
                    })
        except:
            pass
        return sectors
    
    # 北向资金
    def fetch_north(self):
        try:
            r = self.get("https://push2.eastmoney.com/api/qt/kamt.rtmin/get", {"fields1": "f1,f2,f3,f4", "fields2": "f51,f52,f53,f54,f55,f56"})
            if r:
                d = r.json().get("data", {})
                s2n = d.get("s2n", [])
                if s2n:
                    parts = s2n[-1].split(",") if isinstance(s2n[-1], str) else []
                    if len(parts) >= 2 and parts[1] != "-":
                        return {"total": float(parts[1]) / 10000}
        except:
            pass
        return {"total": 0}
    
    # 热门股票
    def fetch_hot_stocks(self):
        stocks = []
        try:
            # 涨幅榜
            r = self.get(
                "https://push2.eastmoney.com/api/qt/clist/get",
                {"pn": 1, "pz": 30, "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23", "fields": "f2,f3,f6,f8,f12,f14,f62", "fid": "f3", "po": 1, "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
            )
            if r:
                for item in r.json().get("data", {}).get("diff", [])[:25]:
                    code = item.get("f12", "")
                    if not code:
                        continue
                    
                    def sf(v, d=1):
                        try:
                            if v and v != "-":
                                return float(v) / d
                        except:
                            pass
                        return 0
                    
                    stocks.append({
                        "code": code,
                        "name": item.get("f14", ""),
                        "market": "sh" if code.startswith("6") else "sz",
                        "price": sf(item.get("f2"), 100),
                        "change_pct": sf(item.get("f3"), 100),
                        "amount": sf(item.get("f6"), 100000000),
                        "turnover": sf(item.get("f8"), 100),
                        "main_net": sf(item.get("f62"), 100000000),
                        "source": "涨幅榜"
                    })
            
            # 资金榜
            codes = {s["code"] for s in stocks}
            r = self.get(
                "https://push2.eastmoney.com/api/qt/clist/get",
                {"pn": 1, "pz": 20, "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23", "fields": "f2,f3,f6,f8,f12,f14,f62", "fid": "f62", "po": 1, "ut": "fa5fd1943c7b386f172d6893dbfba10b"}
            )
            if r:
                for item in r.json().get("data", {}).get("diff", [])[:15]:
                    code = item.get("f12", "")
                    if code and code not in codes:
                        def sf(v, d=1):
                            try:
                                if v and v != "-":
                                    return float(v) / d
                            except:
                                pass
                            return 0
                        
                        stocks.append({
                            "code": code,
                            "name": item.get("f14", ""),
                            "market": "sh" if code.startswith("6") else "sz",
                            "price": sf(item.get("f2"), 100),
                            "change_pct": sf(item.get("f3"), 100),
                            "amount": sf(item.get("f6"), 100000000),
                            "turnover": sf(item.get("f8"), 100),
                            "main_net": sf(item.get("f62"), 100000000),
                            "source": "资金榜"
                        })
        except:
            pass
        return stocks
    
    # 新闻
    def fetch_news(self):
        news = {"politics": [], "economy": [], "tech": []}
        try:
            for col, cat in [("345", "politics"), ("350", "economy"), ("351", "tech")]:
                r = self.get("https://np-listapi.eastmoney.com/comm/web/getNewsByColumns", {"columns": col, "pageSize": 12, "pageIndex": 0, "type": 1})
                if r:
                    for item in r.json().get("data", [])[:10]:
                        news[cat].append({
                            "title": item.get("title", ""),
                            "time": item.get("showTime", "")[-8:],
                        })
        except:
            pass
        return news
    
    # 金十快讯
    def fetch_jin10(self):
        flash = []
        try:
            r = self.get(
                "https://flash-api.jin10.com/get_flash_list",
                {"channel": "-8200", "vip": 1, "t": int(time.time() * 1000)},
                headers={'Referer': 'https://www.jin10.com/', 'x-app-id': 'bVBF4FyRTn5NJF5n'}
            )
            if r:
                for item in r.json().get("data", [])[:12]:
                    content = item.get("data", {})
                    text = content.get("content", "") if isinstance(content, dict) else str(content)
                    text = re.sub(r'<[^>]+>', '', text)
                    if text and len(text) > 5:
                        flash.append({
                            "text": text[:100],
                            "time": item.get("time", "")[-8:-3] if item.get("time") else "",
                            "important": item.get("important", 0) == 1
                        })
        except:
            pass
        return flash
    
    # Reddit
    def fetch_reddit(self):
        posts = []
        try:
            for sub in ["wallstreetbets", "stocks"]:
                r = self.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=5", timeout=10)
                if r:
                    for p in r.json().get("data", {}).get("children", [])[:5]:
                        d = p.get("data", {})
                        if not d.get("stickied"):
                            posts.append({
                                "title": d.get("title", "")[:60],
                                "sub": f"r/{sub}",
                                "score": d.get("score", 0),
                            })
        except:
            pass
        return sorted(posts, key=lambda x: x.get("score", 0), reverse=True)[:6]
    
    # HN
    def fetch_hn(self):
        posts = []
        try:
            r = self.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8)
            if r:
                for sid in r.json()[:8]:
                    try:
                        sr = self.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=3)
                        if sr:
                            s = sr.json()
                            if s and s.get("title"):
                                posts.append({"title": s["title"][:60], "score": s.get("score", 0)})
                    except:
                        pass
        except:
            pass
        return posts[:6]
    
    # 股票列表
    def fetch_stock_list(self):
        stocks = []
        try:
            for fs in ["m:1+t:2,m:1+t:23", "m:0+t:6,m:0+t:80"]:
                r = self.get(
                    "https://push2.eastmoney.com/api/qt/clist/get",
                    {"pn": 1, "pz": 5000, "fs": fs, "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    timeout=15
                )
                if r:
                    for item in r.json().get("data", {}).get("diff", []):
                        code = item.get("f12", "")
                        stocks.append({"code": code, "name": item.get("f14", ""), "market": "sh" if code.startswith("6") else "sz"})
        except:
            pass
        return stocks
    
    # 单股实时
    def fetch_stock(self, code, market):
        try:
            secid = f"1.{code}" if market == "sh" else f"0.{code}"
            r = self.get(
                "https://push2.eastmoney.com/api/qt/stock/get",
                {"secid": secid, "fields": "f43,f44,f45,f46,f47,f48,f50,f58,f60,f62,f169,f170", "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                timeout=5
            )
            if r:
                d = r.json().get("data", {})
                if d:
                    def sf(v, div=1):
                        try:
                            if v and v != "-":
                                return float(v) / div
                        except:
                            pass
                        return 0
                    
                    return {
                        "name": d.get("f58", ""),
                        "price": sf(d.get("f43"), 100),
                        "change": sf(d.get("f169"), 100),
                        "change_pct": sf(d.get("f170"), 100),
                        "volume": sf(d.get("f47"), 10000),
                        "amount": sf(d.get("f48"), 100000000),
                        "turnover": sf(d.get("f50"), 100),
                        "high": sf(d.get("f44"), 100),
                        "low": sf(d.get("f45"), 100),
                        "open": sf(d.get("f46"), 100),
                        "prev_close": sf(d.get("f60"), 100),
                        "main_net": sf(d.get("f62"), 100000000),
                    }
        except:
            pass
        return None


# AI推荐
def generate_recommendations(stocks, sectors, north):
    if not stocks:
        return []
    
    scored = []
    for s in stocks:
        if not s.get("price") or s["price"] <= 0:
            continue
        
        score = 0
        tags = []
        reasons = []
        
        chg = s.get("change_pct", 0)
        if 1 <= chg <= 5:
            score += 20
            tags.append(("涨幅适中", "up"))
        elif 5 < chg <= 9:
            score += 12
            tags.append(("强势", "hot"))
        elif chg > 0:
            score += 8
        
        mn = s.get("main_net", 0)
        if mn > 2:
            score += 25
            tags.append(("主力大买", "fund"))
            reasons.append(f"主力净流入{mn:.1f}亿")
        elif mn > 0.5:
            score += 15
            tags.append(("资金流入", "fund"))
            reasons.append(f"主力净流入{mn:.1f}亿")
        elif mn > 0:
            score += 5
        
        tr = s.get("turnover", 0)
        if 5 <= tr <= 15:
            score += 10
            reasons.append(f"换手{tr:.1f}%")
        
        amt = s.get("amount", 0)
        if amt > 10:
            score += 8
            reasons.append(f"成交{amt:.1f}亿")
        
        if s.get("source") == "资金榜":
            score += 5
        
        s["score"] = score
        s["tags"] = tags[:3]
        s["reason"] = "、".join(reasons[:3]) if reasons else "综合评分领先"
        scored.append(s)
    
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored[:10]


# ==================== 缓存 ====================
fetcher = DataFetcher()

@st.cache_data(ttl=90)
def get_indices():
    return fetcher.fetch_indices()

@st.cache_data(ttl=90)
def get_futures():
    return fetcher.fetch_futures()

@st.cache_data(ttl=120)
def get_forex():
    return fetcher.fetch_forex()

@st.cache_data(ttl=60)
def get_sectors():
    return fetcher.fetch_sectors()

@st.cache_data(ttl=45)
def get_north():
    return fetcher.fetch_north()

@st.cache_data(ttl=45)
def get_hot_stocks():
    return fetcher.fetch_hot_stocks()

@st.cache_data(ttl=180)
def get_news():
    return fetcher.fetch_news()

@st.cache_data(ttl=60)
def get_jin10():
    return fetcher.fetch_jin10()

@st.cache_data(ttl=180)
def get_reddit():
    return fetcher.fetch_reddit()

@st.cache_data(ttl=180)
def get_hn():
    return fetcher.fetch_hn()

@st.cache_data(ttl=300)
def get_stock_list():
    return fetcher.fetch_stock_list()

def get_stock(code, market):
    return fetcher.fetch_stock(code, market)


# ==================== 会话 ====================
if "tab" not in st.session_state:
    st.session_state.tab = "ai"
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}

# ==================== 顶部导航 ====================
st.markdown("<div class='title'>📊 股市观察</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>全球行情 · AI智能选股 · 实时资讯</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🤖 AI选股", use_container_width=True):
        st.session_state.tab = "ai"
        st.rerun()
with c2:
    if st.button("🌍 全球行情", use_container_width=True):
        st.session_state.tab = "global"
        st.rerun()
with c3:
    if st.button("⭐ 自选股", use_container_width=True):
        st.session_state.tab = "watch"
        st.rerun()
with c4:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ==================== AI选股 ====================
if st.session_state.tab == "ai":
    indices = get_indices()
    sectors = get_sectors()
    north = get_north()
    hot = get_hot_stocks()
    jin10 = get_jin10()
    
    # 市场信号
    st.markdown("<div class='header'>📡 市场信号</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        us = [i for i in indices if "美国" in i.get("region", "")]
        us_avg = sum(i.get("change_pct", 0) for i in us) / len(us) if us else 0
        cls = "up" if us_avg > 0 else "down"
        st.markdown(f"<div class='card'><div class='region'>🇺🇸 美股</div><div class='name'>隔夜表现</div><div class='change {cls}' style='font-size:18px;'>{'+' if us_avg > 0 else ''}{us_avg:.2f}%</div></div>", unsafe_allow_html=True)
    
    with c2:
        nf = north.get("total", 0)
        cls = "up" if nf > 0 else ("down" if nf < 0 else "flat")
        st.markdown(f"<div class='card'><div class='region'>💰 北向资金</div><div class='name'>今日净流入</div><div class='change {cls}' style='font-size:18px;'>{'+' if nf > 0 else ''}{nf:.1f}亿</div></div>", unsafe_allow_html=True)
    
    with c3:
        top = sectors[0] if sectors else {"name": "-", "change_pct": 0}
        cls = "up" if top.get("change_pct", 0) > 0 else "down"
        st.markdown(f"<div class='card'><div class='region'>🔥 领涨板块</div><div class='name'>{top.get('name', '-')}</div><div class='change {cls}' style='font-size:18px;'>+{top.get('change_pct', 0):.2f}%</div></div>", unsafe_allow_html=True)
    
    with c4:
        a_idx = [i for i in indices if "中国" in i.get("region", "")]
        sh = next((i for i in a_idx if "上证" in i.get("name", "")), {"price": 0, "change_pct": 0})
        cls = "up" if sh.get("change_pct", 0) > 0 else "down"
        st.markdown(f"<div class='card'><div class='region'>🇨🇳 A股</div><div class='name'>上证指数</div><div class='change {cls}' style='font-size:18px;'>{'+' if sh.get('change_pct', 0) > 0 else ''}{sh.get('change_pct', 0):.2f}%</div></div>", unsafe_allow_html=True)
    
    # AI推荐
    recs = generate_recommendations(hot, sectors, north)
    
    st.markdown("""
    <div class='ai-box'>
        <div class='ai-title'>🤖 AI智能推荐</div>
        <div class='ai-sub'>基于资金流向、涨幅、换手率综合评分 | 点击⭐加入自选</div>
    </div>
    """, unsafe_allow_html=True)
    
    if recs:
        cols = st.columns(2)
        for i, s in enumerate(recs[:8]):
            with cols[i % 2]:
                cls = "up" if s.get("change_pct", 0) > 0 else "down"
                tags_html = "".join([f"<span class='tag tag-{t[1]}'>{t[0]}</span>" for t in s.get("tags", [])])
                
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex;justify-content:space-between;'>
                            <div><div class='stock-name'>{s.get('name','')}</div><div class='stock-code'>{s.get('code','')}</div></div>
                            <div style='text-align:right;'><div class='stock-price {cls}'>¥{s.get('price',0):.2f}</div><div class='change {cls}'>{'+' if s.get('change_pct',0) > 0 else ''}{s.get('change_pct',0):.2f}%</div></div>
                        </div>
                        <div style='margin-top:6px;'>{tags_html}</div>
                        <div class='stock-info'>💡 {s.get('reason','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("⭐", key=f"add_{s['code']}"):
                        st.session_state.watchlist[s["code"]] = {"name": s["name"], "market": s.get("market", "sz")}
                        st.toast(f"已添加 {s['name']}")
    else:
        st.info("正在获取数据...")
    
    st.markdown("<div class='risk'>⚠️ 风险提示：本推荐基于公开数据分析，不构成投资建议。股市有风险，投资需谨慎。</div>", unsafe_allow_html=True)
    
    # 板块资金
    if sectors:
        st.markdown("<div class='header'>💰 板块资金流向</div>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i, sec in enumerate(sectors[:10]):
            with cols[i % 5]:
                chg_cls = "up" if sec.get("change_pct", 0) > 0 else "down"
                flow_cls = "up" if sec.get("main_net", 0) > 0 else "down"
                st.markdown(f"<div class='sector'><div class='sector-name'>{sec.get('name','')}</div><div class='change {chg_cls}'>{'+' if sec.get('change_pct',0) > 0 else ''}{sec.get('change_pct',0):.2f}%</div><div class='sector-val {flow_cls}'>{'+' if sec.get('main_net',0) > 0 else ''}{sec.get('main_net',0):.1f}亿</div></div>", unsafe_allow_html=True)
    
    # 快讯
    if jin10:
        st.markdown("<div class='header'>⚡ 实时快讯</div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, f in enumerate(jin10[:8]):
            with cols[i % 2]:
                st.markdown(f"<div class='flash'><span class='flash-time'>{'🔴 ' if f.get('important') else ''}{f.get('time','')}</span><div class='flash-text'>{f.get('text','')}</div></div>", unsafe_allow_html=True)

# ==================== 全球行情 ====================
elif st.session_state.tab == "global":
    indices = get_indices()
    futures = get_futures()
    forex = get_forex()
    news = get_news()
    jin10 = get_jin10()
    reddit = get_reddit()
    hn = get_hn()
    
    # 股指
    st.markdown("<div class='header'>🌍 全球股指</div>", unsafe_allow_html=True)
    if indices:
        cols = st.columns(5)
        for i, idx in enumerate(indices[:15]):
            with cols[i % 5]:
                cls = "up" if idx.get("change_pct", 0) > 0 else ("down" if idx.get("change_pct", 0) < 0 else "flat")
                st.markdown(f"<div class='card'><div class='region'>{idx.get('region','')}</div><div class='name'>{idx.get('name','')}</div><div class='price'>{idx.get('price',0):,.2f}</div><div class='change {cls}'>{'+' if idx.get('change_pct',0) > 0 else ''}{idx.get('change_pct',0):.2f}%</div></div>", unsafe_allow_html=True)
    else:
        st.info("正在加载全球股指...")
    
    # 期货
    st.markdown("<div class='header'>📈 期货行情</div>", unsafe_allow_html=True)
    if futures:
        cols = st.columns(6)
        for i, f in enumerate(futures[:9]):
            with cols[i % 6]:
                cls = "up" if f.get("change_pct", 0) > 0 else "down"
                st.markdown(f"<div class='sector'><div class='sector-name'>{f.get('name','')}</div><div style='font-size:14px;font-weight:700;color:#f5f5f7;margin:3px 0;'>{f.get('price',0):,.2f}</div><div class='change {cls}'>{'+' if f.get('change_pct',0) > 0 else ''}{f.get('change_pct',0):.2f}%</div></div>", unsafe_allow_html=True)
    
    # 外汇
    st.markdown("<div class='header'>💱 外汇牌价</div>", unsafe_allow_html=True)
    if forex:
        cols = st.columns(5)
        for i, fx in enumerate(forex[:5]):
            with cols[i]:
                cls = "up" if fx.get("change_pct", 0) > 0 else "down"
                st.markdown(f"<div class='sector'><div class='sector-name'>{fx.get('name','')}</div><div style='font-size:14px;font-weight:700;color:#f5f5f7;margin:3px 0;'>{fx.get('price',0):.4f}</div><div class='change {cls}'>{'+' if fx.get('change_pct',0) > 0 else ''}{fx.get('change_pct',0):.3f}%</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 快讯
    if jin10:
        st.markdown("<div class='header'>⚡ 实时快讯</div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, f in enumerate(jin10[:10]):
            with cols[i % 2]:
                st.markdown(f"<div class='flash'><span class='flash-time'>{'🔴 ' if f.get('important') else ''}{f.get('time','')}</span><div class='flash-text'>{f.get('text','')}</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 国际社区
    st.markdown("<div class='header'>🌐 国际社区</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<div style='font-size:14px;font-weight:600;color:#ff4500;margin-bottom:8px;'>🔥 Reddit</div>", unsafe_allow_html=True)
        for p in reddit[:5]:
            st.markdown(f"<div class='intl'><div class='intl-title'>{p.get('title','')}</div><div class='intl-stats'>👍 {p.get('score',0):,} · {p.get('sub','')}</div></div>", unsafe_allow_html=True)
    
    with c2:
        st.markdown("<div style='font-size:14px;font-weight:600;color:#ff6600;margin-bottom:8px;'>🧡 Hacker News</div>", unsafe_allow_html=True)
        for p in hn[:5]:
            st.markdown(f"<div class='intl'><div class='intl-title'>{p.get('title','')}</div><div class='intl-stats'>👍 {p.get('score',0):,}</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 新闻
    st.markdown("<div class='header'>📰 国内财经</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cats = [("politics", "🏛️ 政治", c1), ("economy", "💰 经济", c2), ("tech", "🔬 科技", c3)]
    for key, name, col in cats:
        with col:
            st.markdown(f"<div style='font-size:13px;font-weight:600;color:#f5f5f7;margin-bottom:8px;'>{name}</div>", unsafe_allow_html=True)
            for n in news.get(key, [])[:6]:
                title = n.get('title', '')[:28] + '...' if len(n.get('title', '')) > 28 else n.get('title', '')
                st.markdown(f"<div class='news'><div class='news-title'>{title}</div><div class='news-meta'>{n.get('time','')}</div></div>", unsafe_allow_html=True)

# ==================== 自选股 ====================
elif st.session_state.tab == "watch":
    st.markdown("<div class='header'>🔍 搜索添加</div>", unsafe_allow_html=True)
    search = st.text_input("输入股票代码或名称", placeholder="如: 600519 或 贵州茅台", label_visibility="collapsed")
    
    if search:
        all_stocks = get_stock_list()
        results = [s for s in all_stocks if search.lower() in s.get("code", "").lower() or search in s.get("name", "")][:6]
        if results:
            for s in results:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.write(f"**{s['name']}** ({s['code']})")
                with c2:
                    if st.button("➕", key=f"s_{s['code']}"):
                        st.session_state.watchlist[s["code"]] = {"name": s["name"], "market": s["market"]}
                        st.toast(f"已添加 {s['name']}")
                        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.watchlist:
        st.markdown(f"<div class='header'>⭐ 我的自选 ({len(st.session_state.watchlist)})</div>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for i, (code, info) in enumerate(list(st.session_state.watchlist.items())):
            data = get_stock(code, info["market"])
            
            with cols[i % 2]:
                if data:
                    cls = "up" if data.get("change_pct", 0) > 0 else ("down" if data.get("change_pct", 0) < 0 else "flat")
                    sym = "+" if data.get("change_pct", 0) > 0 else ""
                    
                    c1, c2 = st.columns([6, 1])
                    with c1:
                        st.markdown(f"""
                        <div class='watch-card'>
                            <div class='watch-name'>{data.get('name', info['name'])}</div>
                            <div style='font-size:11px;color:#86868b;'>{code}</div>
                            <div class='watch-price {cls}'>¥{data.get('price',0):.2f}</div>
                            <div class='change {cls}'>{sym}{data.get('change',0):.2f} ({sym}{data.get('change_pct',0):.2f}%)</div>
                            <div style='margin-top:10px;'>
                                <div class='watch-row'><span class='watch-label'>成交量</span><span class='watch-value'>{data.get('volume',0):.2f}万手</span></div>
                                <div class='watch-row'><span class='watch-label'>成交额</span><span class='watch-value'>{data.get('amount',0):.2f}亿</span></div>
                                <div class='watch-row'><span class='watch-label'>换手率</span><span class='watch-value'>{data.get('turnover',0):.2f}%</span></div>
                                <div class='watch-row'><span class='watch-label'>最高/最低</span><span class='watch-value'>{data.get('high',0):.2f} / {data.get('low',0):.2f}</span></div>
                                <div class='watch-row'><span class='watch-label'>主力净流入</span><span class='watch-value {cls}'>{data.get('main_net',0):.2f}亿</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        if st.button("🗑️", key=f"d_{code}"):
                            del st.session_state.watchlist[code]
                            st.rerun()
                else:
                    st.markdown(f"<div class='watch-card'><div class='watch-name'>{info['name']}</div><div style='color:#86868b;'>加载中...</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:40px;color:#86868b;'>
            <div style='font-size:36px;'>⭐</div>
            <div style='margin-top:12px;'>暂无自选股</div>
            <div style='font-size:12px;margin-top:6px;'>搜索添加，或从AI推荐中点击⭐添加</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='header'>🔥 热门股票</div>", unsafe_allow_html=True)
        hots = [
            ("600519", "贵州茅台", "sh"), ("300750", "宁德时代", "sz"),
            ("000858", "五粮液", "sz"), ("601318", "中国平安", "sh"),
            ("002475", "立讯精密", "sz"), ("300059", "东方财富", "sz"),
        ]
        cols = st.columns(3)
        for i, (code, name, market) in enumerate(hots):
            with cols[i % 3]:
                if st.button(f"➕ {name}", key=f"h_{code}", use_container_width=True):
                    st.session_state.watchlist[code] = {"name": name, "market": market}
                    st.rerun()

# ==================== 底部 ====================
st.markdown(f"<div class='footer'>数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源: 东方财富/新浪/金十/Reddit/HN | ⚠️ 仅供参考</div>", unsafe_allow_html=True)
