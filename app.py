"""
📊 股市观察 v3.6
Apple风格简约设计 - 全球行情与资讯中心
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

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
/* 全局背景 - Apple深色模式 */
.stApp {
    background: #000000;
}

/* 隐藏Streamlit默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header {visibility: hidden;}

/* 苹果风格字体 */
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');

* {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
}

/* 侧边栏 */
[data-testid="stSidebar"] {
    background: #1c1c1e;
    border-right: 1px solid #2c2c2e;
}

[data-testid="stSidebar"] * {
    color: #f5f5f7 !important;
}

/* 主标题 */
.main-title {
    font-size: 48px;
    font-weight: 700;
    color: #f5f5f7;
    text-align: center;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}

.sub-title {
    font-size: 17px;
    font-weight: 400;
    color: #86868b;
    text-align: center;
    margin-bottom: 40px;
}

/* 板块标题 */
.section-header {
    font-size: 28px;
    font-weight: 600;
    color: #f5f5f7;
    margin: 40px 0 20px 0;
    letter-spacing: -0.3px;
}

/* 指数卡片 - 玻璃拟态 */
.index-card {
    background: rgba(28, 28, 30, 0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.index-card:hover {
    transform: scale(1.02);
    background: rgba(44, 44, 46, 0.9);
}

.index-region {
    font-size: 13px;
    font-weight: 500;
    color: #86868b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.index-name {
    font-size: 15px;
    font-weight: 600;
    color: #f5f5f7;
    margin-bottom: 8px;
}

.index-price {
    font-size: 28px;
    font-weight: 700;
    color: #f5f5f7;
    letter-spacing: -0.5px;
}

.index-change {
    font-size: 15px;
    font-weight: 500;
    margin-top: 4px;
}

.up { color: #34c759; }
.down { color: #ff3b30; }
.neutral { color: #86868b; }

/* 期货卡片 */
.futures-card {
    background: rgba(28, 28, 30, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.futures-name {
    font-size: 13px;
    color: #86868b;
    margin-bottom: 4px;
}

.futures-price {
    font-size: 20px;
    font-weight: 600;
    color: #f5f5f7;
}

.futures-change {
    font-size: 13px;
    font-weight: 500;
}

/* 新闻板块标题 */
.news-section-title {
    font-size: 22px;
    font-weight: 600;
    color: #f5f5f7;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #2c2c2e;
}

/* 新闻卡片 */
.news-card {
    background: rgba(28, 28, 30, 0.5);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: all 0.2s ease;
}

.news-card:hover {
    background: rgba(44, 44, 46, 0.7);
}

.news-number {
    font-size: 12px;
    font-weight: 600;
    color: #0a84ff;
    margin-bottom: 6px;
}

.news-title {
    font-size: 14px;
    font-weight: 500;
    color: #f5f5f7;
    line-height: 1.5;
    margin-bottom: 8px;
}

.news-meta {
    font-size: 12px;
    color: #86868b;
}

/* 标签 */
.tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 8px;
}

.tag-politics { 
    background: rgba(255, 59, 48, 0.15); 
    color: #ff453a; 
}
.tag-economy { 
    background: rgba(255, 159, 10, 0.15); 
    color: #ff9f0a; 
}
.tag-tech { 
    background: rgba(10, 132, 255, 0.15); 
    color: #0a84ff; 
}

/* 分隔线 */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3a3a3c, transparent);
    margin: 40px 0;
}

/* 底部信息 */
.footer-info {
    text-align: center;
    color: #86868b;
    font-size: 12px;
    padding: 40px 0 20px 0;
}

/* 股票监控卡片 */
.stock-card {
    background: rgba(28, 28, 30, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stock-name {
    font-size: 17px;
    font-weight: 600;
    color: #f5f5f7;
}

.stock-code {
    font-size: 13px;
    color: #86868b;
}

.stock-price {
    font-size: 34px;
    font-weight: 700;
    letter-spacing: -1px;
    margin: 12px 0;
}

.stock-detail {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #2c2c2e;
}

.stock-detail:last-child {
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

/* 时间戳 */
.timestamp {
    font-size: 12px;
    color: #48484a;
    text-align: right;
    margin-top: 20px;
}

/* 空状态 */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #86868b;
}

.empty-state-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.empty-state-text {
    font-size: 17px;
    font-weight: 500;
}

/* 热门股票按钮 */
.hot-stock-btn {
    background: rgba(28, 28, 30, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 12px 16px;
    color: #f5f5f7;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.hot-stock-btn:hover {
    background: rgba(44, 44, 46, 0.9);
}

/* Streamlit 组件样式覆盖 */
.stButton > button {
    background: rgba(10, 132, 255, 0.1) !important;
    color: #0a84ff !important;
    border: 1px solid rgba(10, 132, 255, 0.3) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(10, 132, 255, 0.2) !important;
    border-color: #0a84ff !important;
}

.stTextInput > div > div > input {
    background: #1c1c1e !important;
    color: #f5f5f7 !important;
    border: 1px solid #3a3a3c !important;
    border-radius: 10px !important;
}

.stSelectbox > div > div {
    background: #1c1c1e !important;
    border-radius: 10px !important;
}

.stExpander {
    background: rgba(28, 28, 30, 0.5) !important;
    border: 1px solid #2c2c2e !important;
    border-radius: 12px !important;
}

.stRadio > div {
    background: transparent !important;
}

.stRadio label {
    color: #f5f5f7 !important;
}

/* 警告和信息框 */
.stAlert {
    background: rgba(28, 28, 30, 0.8) !important;
    border: 1px solid #3a3a3c !important;
    border-radius: 12px !important;
    color: #f5f5f7 !important;
}
</style>
""", unsafe_allow_html=True)

# ==================== 数据获取函数 ====================

@st.cache_data(ttl=300)
def fetch_global_indices():
    """获取全球主要股指数据"""
    indices = []
    
    index_list = [
        {"code": "1.000001", "name": "上证指数", "region": "中国大陆"},
        {"code": "0.399001", "name": "深证成指", "region": "中国大陆"},
        {"code": "0.399006", "name": "创业板指", "region": "中国大陆"},
        {"code": "100.HSI", "name": "恒生指数", "region": "中国香港"},
        {"code": "100.N225", "name": "日经225", "region": "日本"},
        {"code": "100.KS11", "name": "韩国综合", "region": "韩国"},
        {"code": "100.DJIA", "name": "道琼斯", "region": "美国"},
        {"code": "100.NDX", "name": "纳斯达克100", "region": "美国"},
        {"code": "100.SPX", "name": "标普500", "region": "美国"},
        {"code": "100.FTSE", "name": "富时100", "region": "英国"},
        {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
        {"code": "100.FCHI", "name": "法国CAC40", "region": "法国"},
    ]
    
    for idx in index_list:
        try:
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": idx["code"],
                "fields": "f43,f169,f170",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json().get("data", {})
            
            if data:
                price = data.get("f43", 0) / 100 if data.get("f43") else 0
                change_pct = data.get("f170", 0) / 100 if data.get("f170") else 0
                change_amt = data.get("f169", 0) / 100 if data.get("f169") else 0
                
                indices.append({
                    "name": idx["name"],
                    "region": idx["region"],
                    "price": price,
                    "change_pct": change_pct,
                    "change_amt": change_amt
                })
        except:
            indices.append({
                "name": idx["name"],
                "region": idx["region"],
                "price": 0,
                "change_pct": 0,
                "change_amt": 0
            })
    
    return indices

@st.cache_data(ttl=300)
def fetch_futures_data():
    """获取期货数据"""
    futures = []
    
    futures_list = [
        {"code": "113.IH00", "name": "上证50期货", "type": "股指"},
        {"code": "113.IF00", "name": "沪深300期货", "type": "股指"},
        {"code": "113.IC00", "name": "中证500期货", "type": "股指"},
        {"code": "113.AU0", "name": "黄金", "type": "贵金属"},
        {"code": "113.AG0", "name": "白银", "type": "贵金属"},
        {"code": "113.SC0", "name": "原油", "type": "能源"},
        {"code": "113.CU0", "name": "沪铜", "type": "有色"},
        {"code": "113.AL0", "name": "沪铝", "type": "有色"},
    ]
    
    for fut in futures_list:
        try:
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": fut["code"],
                "fields": "f43,f170",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json().get("data", {})
            
            if data:
                price = data.get("f43", 0)
                if fut["type"] == "股指":
                    price = price / 100 if price else 0
                change_pct = data.get("f170", 0) / 100 if data.get("f170") else 0
                
                futures.append({
                    "name": fut["name"],
                    "type": fut["type"],
                    "price": price,
                    "change_pct": change_pct
                })
        except:
            futures.append({
                "name": fut["name"],
                "type": fut["type"],
                "price": 0,
                "change_pct": 0
            })
    
    return futures

@st.cache_data(ttl=600)
def fetch_news_data():
    """获取财经新闻"""
    news_data = {"politics": [], "economy": [], "tech": []}
    
    try:
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
        
        # 政治新闻
        params = {"columns": "345", "pageSize": 10, "pageIndex": 0, "type": 1}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data"):
            for item in data["data"][:10]:
                news_data["politics"].append({
                    "title": item.get("title", ""),
                    "time": item.get("showTime", ""),
                    "source": item.get("mediaName", "东方财富")
                })
        
        # 经济新闻
        params["columns"] = "350"
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data"):
            for item in data["data"][:10]:
                news_data["economy"].append({
                    "title": item.get("title", ""),
                    "time": item.get("showTime", ""),
                    "source": item.get("mediaName", "东方财富")
                })
        
        # 科技新闻
        params["columns"] = "351"
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data"):
            for item in data["data"][:10]:
                news_data["tech"].append({
                    "title": item.get("title", ""),
                    "time": item.get("showTime", ""),
                    "source": item.get("mediaName", "东方财富")
                })
                
    except:
        news_data = fetch_backup_news()
    
    if not news_data["politics"]:
        news_data = fetch_backup_news()
    
    return news_data

def fetch_backup_news():
    """备用新闻源"""
    news_data = {"politics": [], "economy": [], "tech": []}
    
    try:
        url = "https://feed.mix.sina.com.cn/api/roll/get"
        params = {"pageid": "153", "lid": "2516", "num": 30, "page": 1}
        resp = requests.get(url, params=params, timeout=10)
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
                    if len(news_data["politics"]) < 10:
                        news_data["politics"].append(news_item)
                elif any(kw in title for kw in ["AI", "人工智能", "芯片", "机器人", "科技"]):
                    if len(news_data["tech"]) < 10:
                        news_data["tech"].append(news_item)
                else:
                    if len(news_data["economy"]) < 10:
                        news_data["economy"].append(news_item)
    except:
        pass
    
    return news_data

@st.cache_data(ttl=60)
def fetch_a_stock_list():
    """获取A股列表"""
    stocks = []
    try:
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        
        # 沪市
        params = {
            "pn": 1, "pz": 3000, "fs": "m:1+t:2,m:1+t:23",
            "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"
        }
        resp = requests.get(url, params=params, timeout=10)
        for item in resp.json().get("data", {}).get("diff", []):
            stocks.append({"code": item["f12"], "name": item["f14"], "market": "sh"})
        
        # 深市
        params["fs"] = "m:0+t:6,m:0+t:80"
        resp = requests.get(url, params=params, timeout=10)
        for item in resp.json().get("data", {}).get("diff", []):
            stocks.append({"code": item["f12"], "name": item["f14"], "market": "sz"})
    except:
        pass
    
    return stocks

def get_stock_data(code, market):
    """获取股票数据"""
    try:
        secid = f"1.{code}" if market == "sh" else f"0.{code}"
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": secid,
            "fields": "f43,f44,f45,f46,f47,f48,f50,f58,f60,f169,f170",
            "ut": "fa5fd1943c7b386f172d6893dbfba10b"
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json().get("data", {})
        
        if data:
            return {
                "code": code,
                "name": data.get("f58", ""),
                "price": data.get("f43", 0) / 100 if data.get("f43") else 0,
                "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                "change_amt": data.get("f169", 0) / 100 if data.get("f169") else 0,
                "volume": data.get("f47", 0) / 10000 if data.get("f47") else 0,
                "amount": data.get("f48", 0) / 100000000 if data.get("f48") else 0,
                "turnover": data.get("f50", 0) / 100 if data.get("f50") else 0,
                "high": data.get("f44", 0) / 100 if data.get("f44") else 0,
                "low": data.get("f45", 0) / 100 if data.get("f45") else 0,
                "open": data.get("f46", 0) / 100 if data.get("f46") else 0,
                "prev_close": data.get("f60", 0) / 100 if data.get("f60") else 0,
            }
    except:
        pass
    return None

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
        <div style='font-size: 13px; color: #86868b; margin-top: 4px;'>全球行情与资讯</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 10px 0;'></div>", unsafe_allow_html=True)
    
    # 功能切换
    tab = st.radio(
        "功能模块",
        ["🌍 全球行情", "📈 A股监控"],
        label_visibility="collapsed"
    )
    st.session_state.current_tab = "global" if "全球" in tab else "a_stock"
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.session_state.current_tab == "a_stock":
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 12px;'>搜索股票</div>", unsafe_allow_html=True)
        search = st.text_input("", placeholder="输入代码或名称", label_visibility="collapsed")
        
        if search:
            stocks = fetch_a_stock_list()
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
    
    if st.button("刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown(f"<div style='color: #48484a; font-size: 11px; margin-top: 20px; text-align: center;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)

# ==================== 主界面 ====================

if st.session_state.current_tab == "global":
    # 全球行情页面
    st.markdown("""
    <div class='main-title'>股市观察</div>
    <div class='sub-title'>全球市场实时行情 · 财经资讯一览</div>
    """, unsafe_allow_html=True)
    
    # 获取数据
    indices = fetch_global_indices()
    futures = fetch_futures_data()
    news = fetch_news_data()
    
    # ========== 全球股指 ==========
    st.markdown("<div class='section-header'>全球股指</div>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, idx in enumerate(indices):
        with cols[i % 4]:
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
    
    # ========== 期货行情 ==========
    st.markdown("<div class='section-header'>期货行情</div>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, fut in enumerate(futures):
        with cols[i % 4]:
            change_class = "up" if fut["change_pct"] > 0 else ("down" if fut["change_pct"] < 0 else "neutral")
            change_symbol = "+" if fut["change_pct"] > 0 else ""
            
            st.markdown(f"""
            <div class='futures-card'>
                <div class='futures-name'>{fut['name']}</div>
                <div class='futures-price'>{fut['price']:,.2f}</div>
                <div class='futures-change {change_class}'>{change_symbol}{fut['change_pct']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ========== 财经资讯 ==========
    st.markdown("<div class='section-header'>财经资讯</div>", unsafe_allow_html=True)
    
    news_cols = st.columns(3)
    
    # 政治新闻
    with news_cols[0]:
        st.markdown("<div class='news-section-title'>🏛️ 政治要闻</div>", unsafe_allow_html=True)
        for i, item in enumerate(news["politics"][:10], 1):
            title = item['title'][:45] + '...' if len(item['title']) > 45 else item['title']
            st.markdown(f"""
            <div class='news-card'>
                <div class='news-number'>0{i if i < 10 else i}</div>
                <div class='news-title'>{title}</div>
                <div class='news-meta'>
                    <span class='tag tag-politics'>政治</span>
                    {item.get('time', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 经济新闻
    with news_cols[1]:
        st.markdown("<div class='news-section-title'>💰 经济要闻</div>", unsafe_allow_html=True)
        for i, item in enumerate(news["economy"][:10], 1):
            title = item['title'][:45] + '...' if len(item['title']) > 45 else item['title']
            st.markdown(f"""
            <div class='news-card'>
                <div class='news-number'>0{i if i < 10 else i}</div>
                <div class='news-title'>{title}</div>
                <div class='news-meta'>
                    <span class='tag tag-economy'>经济</span>
                    {item.get('time', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 科技新闻
    with news_cols[2]:
        st.markdown("<div class='news-section-title'>🔬 科技要闻</div>", unsafe_allow_html=True)
        for i, item in enumerate(news["tech"][:10], 1):
            title = item['title'][:45] + '...' if len(item['title']) > 45 else item['title']
            st.markdown(f"""
            <div class='news-card'>
                <div class='news-number'>0{i if i < 10 else i}</div>
                <div class='news-title'>{title}</div>
                <div class='news-meta'>
                    <span class='tag tag-tech'>科技</span>
                    {item.get('time', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 底部
    st.markdown(f"""
    <div class='footer-info'>
        数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        数据来源: 东方财富 / 新浪财经 · 仅供参考
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
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div class='stock-name'>{data['name']}</div>
                            <div class='stock-code'>{data['code']}</div>
                        </div>
                        <div class='stock-price {change_class}'>¥{data['price']:.2f}</div>
                        <div class='index-change {change_class}' style='margin-bottom: 16px;'>
                            {change_symbol}{data['change_amt']:.2f} ({change_symbol}{data['change_pct']:.2f}%)
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>成交量</span>
                            <span class='detail-value'>{data['volume']:.2f} 万手</span>
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>成交额</span>
                            <span class='detail-value'>{data['amount']:.2f} 亿</span>
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>换手率</span>
                            <span class='detail-value'>{data['turnover']:.2f}%</span>
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>最高 / 最低</span>
                            <span class='detail-value'>{data['high']:.2f} / {data['low']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("报警设置"):
                        if code not in st.session_state.alerts:
                            st.session_state.alerts[code] = {"price_low": 0, "price_high": 0, "change_low": -10, "change_high": 10}
                        
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
            {"code": "000858", "name": "五粮液", "market": "sz"},
            {"code": "002475", "name": "立讯精密", "market": "sz"},
            {"code": "300059", "name": "东方财富", "market": "sz"},
        ]
        
        cols = st.columns(3)
        for i, stock in enumerate(hot_stocks):
            with cols[i % 3]:
                if st.button(f"＋ {stock['name']}", key=f"hot_{stock['code']}", use_container_width=True):
                    st.session_state.watchlist[stock["code"]] = {"name": stock["name"], "market": stock["market"]}
                    st.rerun()
    
    st.markdown(f"""
    <div class='timestamp'>
        更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)
