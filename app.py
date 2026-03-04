"""
🛡️ 逻辑指挥官 - 算力基建监控哨兵 v3.5
新增: 全球行情 + 财经新闻资讯中心
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
import re

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="逻辑指挥官 v3.5 - 全球行情与资讯",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义CSS样式 ====================
st.markdown("""
<style>
/* 全局样式 */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
}

/* 卡片样式 */
.metric-card {
    background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(99,102,241,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-bottom: 15px;
}

/* 新闻卡片 */
.news-card {
    background: linear-gradient(145deg, rgba(30,41,59,0.85), rgba(15,23,42,0.9));
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
    border-left: 4px solid #6366f1;
    transition: all 0.3s ease;
}
.news-card:hover {
    transform: translateX(5px);
    border-left-color: #22d3ee;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3);
}
.news-card.politics { border-left-color: #ef4444; }
.news-card.economy { border-left-color: #f59e0b; }
.news-card.tech { border-left-color: #22d3ee; }

.news-title {
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
    line-height: 1.4;
}
.news-meta {
    color: #64748b;
    font-size: 12px;
}
.news-source {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 5px;
}

/* 指数卡片 */
.index-card {
    background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    border: 1px solid rgba(99,102,241,0.2);
    margin-bottom: 10px;
}
.index-name {
    color: #94a3b8;
    font-size: 12px;
    margin-bottom: 5px;
}
.index-value {
    color: #f1f5f9;
    font-size: 20px;
    font-weight: bold;
}
.index-change {
    font-size: 14px;
    font-weight: 600;
    margin-top: 5px;
}
.index-up { color: #22c55e; }
.index-down { color: #ef4444; }

/* 板块标题 */
.section-title {
    color: #e2e8f0;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(99,102,241,0.5);
    display: flex;
    align-items: center;
    gap: 10px;
}

/* 标签样式 */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 5px;
}
.tag-politics { background: rgba(239,68,68,0.2); color: #ef4444; }
.tag-economy { background: rgba(245,158,11,0.2); color: #f59e0b; }
.tag-tech { background: rgba(34,211,238,0.2); color: #22d3ee; }

/* 期货卡片 */
.futures-card {
    background: linear-gradient(145deg, rgba(30,41,59,0.85), rgba(15,23,42,0.9));
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 8px;
    border: 1px solid rgba(99,102,241,0.15);
}
.futures-name {
    color: #94a3b8;
    font-size: 11px;
}
.futures-price {
    color: #f1f5f9;
    font-size: 16px;
    font-weight: bold;
}

/* 更新时间 */
.update-time {
    color: #64748b;
    font-size: 11px;
    text-align: right;
    margin-top: 10px;
}

/* 隐藏Streamlit默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ==================== 数据获取函数 ====================

@st.cache_data(ttl=300)
def fetch_global_indices():
    """获取全球主要股指数据"""
    indices = []
    
    # 全球主要指数列表 (使用东方财富接口)
    index_list = [
        # 亚太
        {"code": "1.000001", "name": "上证指数", "region": "中国"},
        {"code": "0.399001", "name": "深证成指", "region": "中国"},
        {"code": "0.399006", "name": "创业板指", "region": "中国"},
        {"code": "100.HSI", "name": "恒生指数", "region": "香港"},
        {"code": "100.N225", "name": "日经225", "region": "日本"},
        {"code": "100.KS11", "name": "韩国综合", "region": "韩国"},
        # 美洲
        {"code": "100.DJIA", "name": "道琼斯", "region": "美国"},
        {"code": "100.NDX", "name": "纳斯达克100", "region": "美国"},
        {"code": "100.SPX", "name": "标普500", "region": "美国"},
        # 欧洲
        {"code": "100.FTSE", "name": "富时100", "region": "英国"},
        {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
        {"code": "100.FCHI", "name": "法国CAC40", "region": "法国"},
    ]
    
    for idx in index_list:
        try:
            # 东方财富行情接口
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": idx["code"],
                "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f169,f170",
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
        except Exception as e:
            # 使用模拟数据作为备用
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
                "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f169,f170",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json().get("data", {})
            
            if data:
                price = data.get("f43", 0)
                # 期货价格可能不需要除100
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
    """获取财经新闻数据"""
    news_data = {
        "politics": [],
        "economy": [],
        "tech": []
    }
    
    try:
        # 东方财富财经新闻接口
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
        
        # 政治新闻 (时政要闻)
        params_politics = {
            "columns": "345",
            "pageSize": 10,
            "pageIndex": 0,
            "type": 1
        }
        resp = requests.get(url, params=params_politics, timeout=10)
        data = resp.json()
        if data.get("data"):
            for item in data["data"][:10]:
                news_data["politics"].append({
                    "title": item.get("title", ""),
                    "time": item.get("showTime", ""),
                    "source": item.get("mediaName", "东方财富"),
                    "url": item.get("url", "")
                })
        
        # 经济新闻 (财经要闻)
        params_economy = {
            "columns": "350",
            "pageSize": 10,
            "pageIndex": 0,
            "type": 1
        }
        resp = requests.get(url, params=params_economy, timeout=10)
        data = resp.json()
        if data.get("data"):
            for item in data["data"][:10]:
                news_data["economy"].append({
                    "title": item.get("title", ""),
                    "time": item.get("showTime", ""),
                    "source": item.get("mediaName", "东方财富"),
                    "url": item.get("url", "")
                })
        
        # 科技新闻 (科技要闻)
        params_tech = {
            "columns": "351",
            "pageSize": 10,
            "pageIndex": 0,
            "type": 1
        }
        resp = requests.get(url, params=params_tech, timeout=10)
        data = resp.json()
        if data.get("data"):
            for item in data["data"][:10]:
                news_data["tech"].append({
                    "title": item.get("title", ""),
                    "time": item.get("showTime", ""),
                    "source": item.get("mediaName", "东方财富"),
                    "url": item.get("url", "")
                })
                
    except Exception as e:
        st.warning(f"新闻数据获取异常: {str(e)}")
    
    # 如果获取失败，使用备用新闻源
    if not news_data["politics"]:
        news_data = fetch_backup_news()
    
    return news_data

def fetch_backup_news():
    """备用新闻源 - 新浪财经"""
    news_data = {
        "politics": [],
        "economy": [],
        "tech": []
    }
    
    try:
        # 新浪财经滚动新闻
        url = "https://feed.mix.sina.com.cn/api/roll/get"
        
        # 财经要闻
        params = {
            "pageid": "153",
            "lid": "2516",
            "num": 30,
            "page": 1
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get("result", {}).get("data"):
            items = data["result"]["data"]
            
            # 分类新闻
            for item in items:
                title = item.get("title", "")
                news_item = {
                    "title": title,
                    "time": datetime.fromtimestamp(int(item.get("ctime", 0))).strftime("%H:%M") if item.get("ctime") else "",
                    "source": item.get("media_name", "新浪财经"),
                    "url": item.get("url", "")
                }
                
                # 简单分类逻辑
                if any(kw in title for kw in ["政策", "央行", "两会", "国务院", "发改委", "总书记", "习近平", "政府", "制裁", "关税"]):
                    if len(news_data["politics"]) < 10:
                        news_data["politics"].append(news_item)
                elif any(kw in title for kw in ["AI", "人工智能", "芯片", "半导体", "机器人", "DeepSeek", "英伟达", "科技", "技术"]):
                    if len(news_data["tech"]) < 10:
                        news_data["tech"].append(news_item)
                else:
                    if len(news_data["economy"]) < 10:
                        news_data["economy"].append(news_item)
                        
    except Exception as e:
        pass
    
    return news_data

@st.cache_data(ttl=60)
def fetch_a_stock_list():
    """获取A股列表"""
    stocks = []
    try:
        # 沪市
        url_sh = "https://push2.eastmoney.com/api/qt/clist/get"
        params_sh = {
            "pn": 1, "pz": 3000, "fs": "m:1+t:2,m:1+t:23",
            "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"
        }
        resp_sh = requests.get(url_sh, params=params_sh, timeout=10)
        data_sh = resp_sh.json().get("data", {}).get("diff", [])
        for item in data_sh:
            stocks.append({"code": item["f12"], "name": item["f14"], "market": "sh"})
        
        # 深市
        params_sz = {
            "pn": 1, "pz": 3000, "fs": "m:0+t:6,m:0+t:80",
            "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"
        }
        resp_sz = requests.get(url_sh, params=params_sz, timeout=10)
        data_sz = resp_sz.json().get("data", {}).get("diff", [])
        for item in data_sz:
            stocks.append({"code": item["f12"], "name": item["f14"], "market": "sz"})
            
    except Exception as e:
        st.error(f"获取股票列表失败: {str(e)}")
    
    return stocks

def get_stock_data(code, market):
    """获取单只股票实时数据"""
    try:
        secid = f"1.{code}" if market == "sh" else f"0.{code}"
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": secid,
            "fields": "f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f169,f170,f171",
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
                "volume": data.get("f47", 0) / 10000 if data.get("f47") else 0,  # 万手
                "amount": data.get("f48", 0) / 100000000 if data.get("f48") else 0,  # 亿元
                "turnover": data.get("f50", 0) / 100 if data.get("f50") else 0,  # 换手率
                "high": data.get("f44", 0) / 100 if data.get("f44") else 0,
                "low": data.get("f45", 0) / 100 if data.get("f45") else 0,
                "open": data.get("f46", 0) / 100 if data.get("f46") else 0,
                "prev_close": data.get("f60", 0) / 100 if data.get("f60") else 0,
            }
    except:
        pass
    return None

# ==================== 会话状态初始化 ====================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}
if "alerts" not in st.session_state:
    st.session_state.alerts = {}
if "pushplus_token" not in st.session_state:
    st.session_state.pushplus_token = ""
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "global"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## 🌍 逻辑指挥官 v3.5")
    st.markdown("**全球行情与资讯中心**")
    st.markdown("---")
    
    # 功能切换
    tab_selection = st.radio(
        "📊 功能模块",
        ["🌍 全球行情资讯", "📈 A股监控"],
        index=0 if st.session_state.current_tab == "global" else 1,
        label_visibility="collapsed"
    )
    st.session_state.current_tab = "global" if "全球" in tab_selection else "a_stock"
    
    st.markdown("---")
    
    if st.session_state.current_tab == "a_stock":
        # A股搜索
        st.markdown("### 🔍 A股搜索")
        search_query = st.text_input("输入代码或名称", placeholder="如: 301165 或 锐捷")
        
        if search_query:
            all_stocks = fetch_a_stock_list()
            results = [s for s in all_stocks if search_query.lower() in s["code"].lower() or search_query in s["name"]][:10]
            
            if results:
                st.markdown("**搜索结果:**")
                for stock in results:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{stock['name']}** ({stock['code']})")
                    with col2:
                        if st.button("➕", key=f"add_{stock['code']}"):
                            st.session_state.watchlist[stock["code"]] = {
                                "name": stock["name"],
                                "market": stock["market"]
                            }
                            st.success(f"已添加 {stock['name']}")
                            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 监控列表")
        
        if st.session_state.watchlist:
            for code in list(st.session_state.watchlist.keys()):
                stock = st.session_state.watchlist[code]
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{stock['name']}** ({code})")
                with col2:
                    if st.button("🗑️", key=f"del_{code}"):
                        del st.session_state.watchlist[code]
                        st.rerun()
        else:
            st.info("暂无监控股票")
    
    st.markdown("---")
    
    # 推送设置
    with st.expander("🔔 推送设置"):
        token = st.text_input("PushPlus Token", type="password", value=st.session_state.pushplus_token)
        if token != st.session_state.pushplus_token:
            st.session_state.pushplus_token = token
        st.caption("[获取Token](https://www.pushplus.plus/)")
    
    # 刷新按钮
    if st.button("🔄 刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ==================== 主界面 ====================

if st.session_state.current_tab == "global":
    # ==================== 全球行情资讯页面 ====================
    
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #e2e8f0; font-size: 32px; margin-bottom: 5px;'>
            🌍 全球行情与资讯中心
        </h1>
        <p style='color: #64748b; font-size: 14px;'>
            实时追踪全球市场动态 · 政治经济科技资讯一网打尽
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取数据
    with st.spinner("正在加载全球行情数据..."):
        indices = fetch_global_indices()
        futures = fetch_futures_data()
        news = fetch_news_data()
    
    # ==================== 全球股指行情 ====================
    st.markdown("""
    <div class='section-title'>
        📊 全球主要股指
    </div>
    """, unsafe_allow_html=True)
    
    # 分区域显示
    regions = {
        "🇨🇳 中国大陆": ["上证指数", "深证成指", "创业板指"],
        "🇭🇰 港股": ["恒生指数"],
        "🇯🇵🇰🇷 日韩": ["日经225", "韩国综合"],
        "🇺🇸 美股": ["道琼斯", "纳斯达克100", "标普500"],
        "🇪🇺 欧洲": ["富时100", "德国DAX", "法国CAC40"]
    }
    
    cols = st.columns(5)
    for i, (region_name, idx_names) in enumerate(regions.items()):
        with cols[i]:
            st.markdown(f"**{region_name}**")
            for idx_name in idx_names:
                idx_data = next((x for x in indices if x["name"] == idx_name), None)
                if idx_data:
                    change_class = "index-up" if idx_data["change_pct"] >= 0 else "index-down"
                    change_symbol = "▲" if idx_data["change_pct"] >= 0 else "▼"
                    
                    st.markdown(f"""
                    <div class='index-card'>
                        <div class='index-name'>{idx_data['name']}</div>
                        <div class='index-value'>{idx_data['price']:,.2f}</div>
                        <div class='index-change {change_class}'>
                            {change_symbol} {abs(idx_data['change_pct']):.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== 期货行情 ====================
    st.markdown("""
    <div class='section-title'>
        📈 主要期货行情
    </div>
    """, unsafe_allow_html=True)
    
    fut_cols = st.columns(4)
    fut_types = ["股指", "贵金属", "能源", "有色"]
    
    for i, fut_type in enumerate(fut_types):
        with fut_cols[i]:
            st.markdown(f"**{fut_type}期货**")
            type_futures = [f for f in futures if f["type"] == fut_type]
            for fut in type_futures:
                change_class = "index-up" if fut["change_pct"] >= 0 else "index-down"
                change_symbol = "+" if fut["change_pct"] >= 0 else ""
                
                st.markdown(f"""
                <div class='futures-card'>
                    <div class='futures-name'>{fut['name']}</div>
                    <div class='futures-price'>{fut['price']:,.2f}</div>
                    <span class='{change_class}'>{change_symbol}{fut['change_pct']:.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== 新闻资讯 ====================
    st.markdown("""
    <div class='section-title'>
        📰 今日财经资讯
    </div>
    """, unsafe_allow_html=True)
    
    news_cols = st.columns(3)
    
    # 政治新闻
    with news_cols[0]:
        st.markdown("""
        <div style='background: rgba(239,68,68,0.1); padding: 10px 15px; border-radius: 10px; margin-bottom: 15px;'>
            <span style='color: #ef4444; font-weight: 700; font-size: 16px;'>🏛️ 政治要闻 TOP 10</span>
        </div>
        """, unsafe_allow_html=True)
        
        if news["politics"]:
            for i, item in enumerate(news["politics"][:10], 1):
                st.markdown(f"""
                <div class='news-card politics'>
                    <div class='news-title'>{i}. {item['title'][:50]}{'...' if len(item['title']) > 50 else ''}</div>
                    <div class='news-meta'>
                        <span class='tag tag-politics'>政治</span>
                        {item.get('time', '')}
                    </div>
                    <div class='news-source'>来源: {item.get('source', '财经媒体')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无政治新闻")
    
    # 经济新闻
    with news_cols[1]:
        st.markdown("""
        <div style='background: rgba(245,158,11,0.1); padding: 10px 15px; border-radius: 10px; margin-bottom: 15px;'>
            <span style='color: #f59e0b; font-weight: 700; font-size: 16px;'>💰 经济要闻 TOP 10</span>
        </div>
        """, unsafe_allow_html=True)
        
        if news["economy"]:
            for i, item in enumerate(news["economy"][:10], 1):
                st.markdown(f"""
                <div class='news-card economy'>
                    <div class='news-title'>{i}. {item['title'][:50]}{'...' if len(item['title']) > 50 else ''}</div>
                    <div class='news-meta'>
                        <span class='tag tag-economy'>经济</span>
                        {item.get('time', '')}
                    </div>
                    <div class='news-source'>来源: {item.get('source', '财经媒体')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无经济新闻")
    
    # 科技新闻
    with news_cols[2]:
        st.markdown("""
        <div style='background: rgba(34,211,238,0.1); padding: 10px 15px; border-radius: 10px; margin-bottom: 15px;'>
            <span style='color: #22d3ee; font-weight: 700; font-size: 16px;'>🔬 科技要闻 TOP 10</span>
        </div>
        """, unsafe_allow_html=True)
        
        if news["tech"]:
            for i, item in enumerate(news["tech"][:10], 1):
                st.markdown(f"""
                <div class='news-card tech'>
                    <div class='news-title'>{i}. {item['title'][:50]}{'...' if len(item['title']) > 50 else ''}</div>
                    <div class='news-meta'>
                        <span class='tag tag-tech'>科技</span>
                        {item.get('time', '')}
                    </div>
                    <div class='news-source'>来源: {item.get('source', '财经媒体')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无科技新闻")
    
    # 更新时间
    st.markdown(f"""
    <div class='update-time'>
        数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源: 东方财富/新浪财经
    </div>
    """, unsafe_allow_html=True)

else:
    # ==================== A股监控页面 ====================
    
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #e2e8f0; font-size: 32px; margin-bottom: 5px;'>
            📈 A股实时监控
        </h1>
        <p style='color: #64748b; font-size: 14px;'>
            自选股实时行情 · 智能报警推送
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 判断是否交易时间
    now = datetime.now()
    is_trading_time = (
        now.weekday() < 5 and
        ((9 <= now.hour < 11) or (now.hour == 11 and now.minute <= 30) or
         (13 <= now.hour < 15))
    )
    
    if not is_trading_time:
        st.warning("⏰ 当前为非交易时段，显示最近收盘数据")
    
    if st.session_state.watchlist:
        # 获取所有股票数据
        stock_data_list = []
        for code, info in st.session_state.watchlist.items():
            data = get_stock_data(code, info["market"])
            if data:
                data["name"] = info["name"]
                stock_data_list.append(data)
        
        if stock_data_list:
            # 创建数据表格
            cols = st.columns(3)
            
            for i, stock in enumerate(stock_data_list):
                with cols[i % 3]:
                    change_color = "#22c55e" if stock["change_pct"] >= 0 else "#ef4444"
                    change_symbol = "▲" if stock["change_pct"] >= 0 else "▼"
                    
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                            <span style='color: #e2e8f0; font-size: 16px; font-weight: 700;'>{stock['name']}</span>
                            <span style='color: #64748b; font-size: 12px;'>{stock['code']}</span>
                        </div>
                        <div style='font-size: 28px; font-weight: 700; color: {change_color};'>
                            ¥{stock['price']:.2f}
                        </div>
                        <div style='color: {change_color}; font-size: 14px; margin-top: 5px;'>
                            {change_symbol} {stock['change_amt']:.2f} ({stock['change_pct']:.2f}%)
                        </div>
                        <div style='margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                            <div>
                                <span style='color: #64748b; font-size: 11px;'>成交量</span>
                                <div style='color: #94a3b8; font-size: 13px;'>{stock['volume']:.2f}万手</div>
                            </div>
                            <div>
                                <span style='color: #64748b; font-size: 11px;'>成交额</span>
                                <div style='color: #94a3b8; font-size: 13px;'>{stock['amount']:.2f}亿</div>
                            </div>
                            <div>
                                <span style='color: #64748b; font-size: 11px;'>换手率</span>
                                <div style='color: #94a3b8; font-size: 13px;'>{stock['turnover']:.2f}%</div>
                            </div>
                            <div>
                                <span style='color: #64748b; font-size: 11px;'>最高/最低</span>
                                <div style='color: #94a3b8; font-size: 13px;'>{stock['high']:.2f}/{stock['low']:.2f}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 报警设置
                    with st.expander(f"⚙️ {stock['name']} 报警设置"):
                        alert_key = stock["code"]
                        if alert_key not in st.session_state.alerts:
                            st.session_state.alerts[alert_key] = {
                                "price_low": 0, "price_high": 0,
                                "change_low": -10, "change_high": 10,
                                "volume": 0, "amount": 0, "turnover": 0
                            }
                        
                        alert = st.session_state.alerts[alert_key]
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            alert["price_low"] = st.number_input(
                                "价格下限", value=alert["price_low"], 
                                step=0.1, key=f"pl_{alert_key}"
                            )
                        with c2:
                            alert["price_high"] = st.number_input(
                                "价格上限", value=alert["price_high"],
                                step=0.1, key=f"ph_{alert_key}"
                            )
                        
                        c3, c4 = st.columns(2)
                        with c3:
                            alert["change_low"] = st.number_input(
                                "跌幅报警(%)", value=alert["change_low"],
                                step=0.5, key=f"cl_{alert_key}"
                            )
                        with c4:
                            alert["change_high"] = st.number_input(
                                "涨幅报警(%)", value=alert["change_high"],
                                step=0.5, key=f"ch_{alert_key}"
                            )
                        
                        alert["volume"] = st.number_input(
                            "成交量报警(万手)", value=alert["volume"],
                            step=100.0, key=f"vol_{alert_key}"
                        )
        else:
            st.warning("无法获取股票数据，请稍后重试")
    else:
        st.info("👈 请在左侧搜索并添加股票到监控列表")
        
        # 快速添加热门股票
        st.markdown("### 🔥 热门股票快速添加")
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
                if st.button(f"➕ {stock['name']}", key=f"hot_{stock['code']}", use_container_width=True):
                    st.session_state.watchlist[stock["code"]] = {
                        "name": stock["name"],
                        "market": stock["market"]
                    }
                    st.rerun()

# ==================== 页脚 ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 12px; padding: 20px;'>
    🛡️ 逻辑指挥官 v3.5 | 全球行情与资讯中心<br>
    数据来源: 东方财富 / 新浪财经 | 仅供参考，不构成投资建议
</div>
""", unsafe_allow_html=True)
