"""
股市观察 v6.0 - 稳定版
使用 akshare 作为主要数据源，确保实时性和稳定性
"""

import streamlit as st
import akshare as ak
import pandas as pd
import time
from datetime import datetime
import pickle
import os

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="股市观察 v6.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 样式 ====================
st.markdown("""
<style>
    .stApp { background: #0a0a0a; color: #e0e0e0; }
    .stButton>button { background: #1e90ff; color: white; border: none; }
    .stButton>button:hover { background: #00bfff; }
    .metric-box { background: #1a1a1a; padding: 10px; border-radius: 8px; text-align: center; }
    .hot-item { background: #2a2a2a; padding: 8px; margin: 5px; border-radius: 6px; }
    .footer { text-align: center; color: #888; font-size: 0.8em; margin-top: 20px; }
    .error-box { background: #ff4444; color: white; padding: 10px; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ==================== 数据缓存与重试 ====================
@st.cache_data(ttl=15, show_spinner="加载实时行情...")
def get_stock_quote(code):
    """使用 akshare 获取个股实时行情"""
    for attempt in range(3):
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if not stock.empty:
                stock = stock.iloc[0]
                return {
                    "名称": stock['名称'],
                    "最新价": stock['最新价'],
                    "涨跌幅": stock['涨跌幅'],
                    "成交量": stock['成交量'],
                    "成交额": stock['成交额'],
                    "换手率": stock['换手率'],
                    "时间": datetime.now().strftime("%H:%M:%S")
                }
        except Exception as e:
            time.sleep(2)
    return None

@st.cache_data(ttl=60)
def get_hot_stocks():
    """获取当日热点个股（涨幅前20）"""
    try:
        df = ak.stock_zh_a_spot_em()
        df = df[df['涨跌幅'] > 3].sort_values('涨跌幅', ascending=False).head(20)
        return df[['代码', '名称', '最新价', '涨跌幅', '成交额']].to_dict('records')
    except:
        return []

# ==================== 自选股持久化 ====================
WATCHLIST_FILE = "watchlist.pkl"

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "wb") as f:
        pickle.dump(watchlist, f)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# ==================== AI 简单选股示例 ====================
def simple_ai_recommend():
    try:
        df = ak.stock_zh_a_spot_em()
        # 简单规则：涨幅>5%、成交额>10亿、换手率>5%
        df = df[(df['涨跌幅'] > 5) & (df['成交额'] > 1000000000) & (df['换手率'] > 5)]
        df = df.sort_values('涨跌幅', ascending=False).head(5)
        return df[['代码', '名称', '最新价', '涨跌幅', '换手率', '成交额']].to_dict('records')
    except:
        return []

# ==================== 主界面 ====================
st.title("📊 股市观察 v6.0")
st.caption("数据来源：akshare | 仅供参考，非投资建议")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("自选股管理")
    
    # 显示当前自选股
    if st.session_state.watchlist:
        for code, info in list(st.session_state.watchlist.items()):
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{info['name']} ({code})")
            with col2:
                if st.button("×", key=f"del_{code}", help="删除"):
                    del st.session_state.watchlist[code]
                    save_watchlist(st.session_state.watchlist)
                    st.rerun()
    else:
        st.info("暂无自选股")

    # 手动添加自选股
    st.subheader("添加自选股")
    code_input = st.text_input("输入股票代码（如 600519）")
    if st.button("添加"):
        if code_input:
            try:
                df = ak.stock_individual_info_em(symbol=code_input)
                if not df.empty:
                    name = df[df['item'] == '股票简称']['value'].iloc[0]
                    market = "sh" if code_input.startswith("6") else "sz"
                    st.session_state.watchlist[code_input] = {"name": name, "market": market}
                    save_watchlist(st.session_state.watchlist)
                    st.success(f"已添加 {name} ({code_input})")
                    st.rerun()
                else:
                    st.error("未找到该股票")
            except:
                st.error("添加失败，请检查代码")

# ==================== 主内容区 ====================
tab1, tab2, tab3 = st.tabs(["📈 自选股行情", "🔥 热点个股", "🤖 AI推荐"])

with tab1:
    if st.session_state.watchlist:
        st.subheader("自选股实时行情")
        cols = st.columns(3)
        for idx, (code, info) in enumerate(st.session_state.watchlist.items()):
            data = get_stock_quote(code)
            with cols[idx % 3]:
                if data:
                    delta = data['涨跌幅']
                    st.metric(
                        label=f"{info['name']} ({code})",
                        value=f"{data['最新价']:.2f}",
                        delta=f"{delta:+.2f}%",
                        delta_color="normal" if delta >= 0 else "inverse"
                    )
                    st.caption(f"成交量: {data['成交量']/10000:.1f}万手 | 更新: {data['时间']}")
                else:
                    st.error(f"{info['name']} 数据加载失败")
    else:
        st.info("请在侧边栏添加自选股")

with tab2:
    st.subheader("当日热点个股（涨幅前20）")
    if st.button("刷新热点"):
        st.rerun()
    
    hots = get_hot_stocks()
    if hots:
        cols = st.columns(3)
        for i, item in enumerate(hots):
            with cols[i % 3]:
                delta = item['涨跌幅']
                st.metric(
                    label=f"{item['名称']} ({item['代码']})",
                    value=f"{item['最新价']:.2f}",
                    delta=f"{delta:+.2f}%"
                )
                st.caption(f"成交额: {item['成交额']/1e8:.1f}亿")
    else:
        st.warning("热点数据加载失败，请稍后重试")

with tab3:
    st.subheader("AI 简单选股推荐")
    if st.button("生成今日推荐"):
        with st.spinner("AI 正在选股..."):
            recommends = simple_ai_recommend()
            if recommends:
                for rec in recommends:
                    delta = rec['涨跌幅']
                    st.metric(
                        label=f"{rec['名称']} ({rec['代码']})",
                        value=f"{rec['最新价']:.2f}",
                        delta=f"{delta:+.2f}%"
                    )
                    st.caption(f"换手率: {rec['换手率']}% | 成交额: {rec['成交额']/1e8:.1f}亿")
            else:
                st.error("选股失败，请检查网络或稍后重试")

# ==================== 底部 ====================
st.markdown(
    f"<div class='footer'>数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    f"来源: akshare | 仅供学习参考，非投资建议</div>",
    unsafe_allow_html=True
)
