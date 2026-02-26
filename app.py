"""
逻辑指挥官 - 算力基建监控哨兵 v3.4
内置股票列表 + 手动输入，避免海外网络问题
"""

import streamlit as st
import requests
import json
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pandas as pd
import time
import hashlib

# 页面配置
st.set_page_config(
    page_title="逻辑指挥官 - 算力基建监控哨兵",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 内置股票列表（300+常用股票）====================
BUILTIN_STOCKS = {
    # 算力/网络/通信
    "301165": ("锐捷网络", "sz"), "000063": ("中兴通讯", "sz"), "600487": ("亨通光电", "sh"),
    "002281": ("光迅科技", "sz"), "300502": ("新易盛", "sz"), "002396": ("星网锐捷", "sz"),
    "603019": ("中科曙光", "sh"), "000977": ("浪潮信息", "sz"), "688256": ("寒武纪", "sh"),
    
    # 新能源
    "300750": ("宁德时代", "sz"), "002594": ("比亚迪", "sz"), "601012": ("隆基绿能", "sh"),
    "300274": ("阳光电源", "sz"), "002459": ("晶澳科技", "sz"), "600438": ("通威股份", "sh"),
    "002129": ("TCL中环", "sz"), "601865": ("福莱特", "sh"), "300763": ("锦浪科技", "sz"),
    
    # 半导体/芯片
    "002371": ("北方华创", "sz"), "688981": ("中芯国际", "sh"), "603501": ("韦尔股份", "sh"),
    "002049": ("紫光国微", "sz"), "603986": ("兆易创新", "sh"), "300782": ("卓胜微", "sz"),
    "688012": ("中微公司", "sh"), "002185": ("华天科技", "sz"), "600584": ("长电科技", "sh"),
    
    # 消费/白酒
    "600519": ("贵州茅台", "sh"), "000858": ("五粮液", "sz"), "000568": ("泸州老窖", "sz"),
    "002304": ("洋河股份", "sz"), "600809": ("山西汾酒", "sh"), "000799": ("酒鬼酒", "sz"),
    "603369": ("今世缘", "sh"), "000596": ("古井贡酒", "sz"), "600779": ("水井坊", "sh"),
    
    # 医药
    "300760": ("迈瑞医疗", "sz"), "600276": ("恒瑞医药", "sh"), "000538": ("云南白药", "sz"),
    "300122": ("智飞生物", "sz"), "002007": ("华兰生物", "sz"), "300347": ("泰格医药", "sz"),
    "603259": ("药明康德", "sh"), "000661": ("长春高新", "sz"), "300015": ("爱尔眼科", "sz"),
    
    # 金融科技
    "300059": ("东方财富", "sz"), "600588": ("用友网络", "sh"), "002230": ("科大讯飞", "sz"),
    "688111": ("金山办公", "sh"), "300033": ("同花顺", "sz"), "002241": ("歌尔股份", "sz"),
    
    # 安防/智能制造
    "002415": ("海康威视", "sz"), "002236": ("大华股份", "sz"), "300124": ("汇川技术", "sz"),
    "601100": ("恒立液压", "sh"), "002008": ("大族激光", "sz"), "300285": ("国瓷材料", "sz"),
    
    # 互联网/平台
    "002024": ("苏宁易购", "sz"), "300413": ("芒果超媒", "sz"), "002555": ("三七互娱", "sz"),
    "002602": ("世纪华通", "sz"), "300418": ("昆仑万维", "sz"), "603444": ("吉比特", "sh"),
    
    # 汽车
    "600104": ("上汽集团", "sh"), "000625": ("长安汽车", "sz"), "601238": ("广汽集团", "sh"),
    "002920": ("德赛西威", "sz"), "603799": ("华友钴业", "sh"), "300450": ("先导智能", "sz"),
    
    # 银行/保险/券商
    "601398": ("工商银行", "sh"), "601288": ("农业银行", "sh"), "601939": ("建设银行", "sh"),
    "600036": ("招商银行", "sh"), "601318": ("中国平安", "sh"), "601628": ("中国人寿", "sh"),
    "600030": ("中信证券", "sh"), "601688": ("华泰证券", "sh"), "600837": ("海通证券", "sh"),
    
    # 地产/建材
    "000002": ("万科A", "sz"), "001979": ("招商蛇口", "sz"), "600048": ("保利发展", "sh"),
    "600585": ("海螺水泥", "sh"), "002271": ("东方雨虹", "sz"), "603392": ("万泰生物", "sh"),
    
    # 军工
    "600893": ("航发动力", "sh"), "000768": ("中航西飞", "sz"), "600760": ("中航沈飞", "sh"),
    "002179": ("中航光电", "sz"), "600118": ("中国卫星", "sh"), "000687": ("华讯方舟", "sz"),
    
    # 电力/能源
    "600900": ("长江电力", "sh"), "601985": ("中国核电", "sh"), "003816": ("中国广核", "sz"),
    "600023": ("浙能电力", "sh"), "600886": ("国投电力", "sh"), "601991": ("大唐发电", "sh"),
    
    # 其他热门
    "300499": ("高澜股份", "sz"), "600030": ("中信证券", "sh"), "601899": ("紫金矿业", "sh"),
    "603288": ("海天味业", "sh"), "000333": ("美的集团", "sz"), "000651": ("格力电器", "sz"),
    "600887": ("伊利股份", "sh"), "000895": ("双汇发展", "sz"), "600309": ("万华化学", "sh"),
}


def search_stocks(keyword):
    """搜索内置股票"""
    if not keyword:
        return []
    keyword = keyword.upper()
    results = []
    for code, (name, market) in BUILTIN_STOCKS.items():
        if keyword in code or keyword in name:
            results.append({'code': code, 'name': name, 'market': market})
    results.sort(key=lambda x: (keyword not in x['code'], x['code']))
    return results[:15]


def get_market_by_code(code):
    """根据代码判断市场"""
    if code.startswith('6'):
        return 'sh'
    elif code.startswith('0') or code.startswith('3'):
        return 'sz'
    else:
        return 'sz'


# ==================== 数据获取（多源重试）====================
def get_realtime_quote(stock_code, market="sz"):
    """获取实时行情 - 多数据源重试"""
    
    # 尝试方法1: 新浪财经
    quote = get_quote_sina(stock_code, market)
    if quote:
        return quote
    
    # 尝试方法2: 腾讯财经
    quote = get_quote_tencent(stock_code, market)
    if quote:
        return quote
    
    return None


def get_quote_sina(stock_code, market):
    """新浪财经接口"""
    try:
        sina_code = f"{market}{stock_code}"
        url = f"https://hq.sinajs.cn/list={sina_code}"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        match = re.search(r'"(.+)"', response.text)
        if not match:
            return None
        
        data = match.group(1).split(',')
        if len(data) < 32 or not data[0]:
            return None
        
        current_price = float(data[3]) if data[3] else 0
        pre_close = float(data[2]) if data[2] else 0
        
        if current_price <= 0:
            current_price = pre_close
        if current_price <= 0:
            return None
        
        change_amount = current_price - pre_close
        change_pct = (change_amount / pre_close * 100) if pre_close > 0 else 0
        
        return {
            'name': data[0],
            'code': stock_code,
            'price': current_price,
            'change_pct': round(change_pct, 2),
            'change_amount': round(change_amount, 2),
            'volume': float(data[8]) / 100 if data[8] else 0,
            'amount': float(data[9]) if data[9] else 0,
            'turnover_rate': 0,
            'high': float(data[4]) if data[4] else current_price,
            'low': float(data[5]) if data[5] else current_price,
            'open': float(data[1]) if data[1] else current_price,
            'pre_close': pre_close,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': '新浪'
        }
    except:
        return None


def get_quote_tencent(stock_code, market):
    """腾讯财经接口"""
    try:
        tc_code = f"{market}{stock_code}"
        url = f"https://qt.gtimg.cn/q={tc_code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        if '="' not in response.text:
            return None
        
        data_str = response.text.split('="')[1].rstrip('";')
        parts = data_str.split('~')
        
        if len(parts) < 40:
            return None
        
        name = parts[1]
        current_price = float(parts[3]) if parts[3] else 0
        pre_close = float(parts[4]) if parts[4] else 0
        
        if current_price <= 0:
            current_price = pre_close
        if current_price <= 0:
            return None
        
        change_amount = current_price - pre_close
        change_pct = (change_amount / pre_close * 100) if pre_close > 0 else 0
        
        return {
            'name': name,
            'code': stock_code,
            'price': current_price,
            'change_pct': round(change_pct, 2),
            'change_amount': round(change_amount, 2),
            'volume': float(parts[6]) if parts[6] else 0,
            'amount': float(parts[37]) * 10000 if len(parts) > 37 and parts[37] else 0,
            'turnover_rate': float(parts[38]) if len(parts) > 38 and parts[38] else 0,
            'high': float(parts[33]) if len(parts) > 33 and parts[33] else current_price,
            'low': float(parts[34]) if len(parts) > 34 and parts[34] else current_price,
            'open': float(parts[5]) if parts[5] else current_price,
            'pre_close': pre_close,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': '腾讯'
        }
    except:
        return None


def get_historical_data(stock_code, market="sz", days=90):
    """获取历史K线 - 新浪接口"""
    try:
        sina_code = f"{market}{stock_code}"
        url = "https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_data/KC_MarketDataService.getKLineData"
        params = {'symbol': sina_code, 'scale': '240', 'ma': 'no', 'datalen': days}
        headers = {'Referer': 'https://finance.sina.com.cn', 'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        match = re.search(r'\((\[.+\])\)', response.text)
        
        if not match:
            return None
        
        data = json.loads(match.group(1))
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df['day'] = pd.to_datetime(df['day'])
        df = df.rename(columns={'day': '日期', 'open': '开盘', 'high': '最高', 
                                'low': '最低', 'close': '收盘', 'volume': '成交量'})
        for col in ['开盘', '最高', '最低', '收盘', '成交量']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except:
        return None


# ==================== 推送 ====================
def send_pushplus(token, title, content):
    if not token:
        return False, "未配置"
    try:
        resp = requests.post("http://www.pushplus.plus/send", 
                           json={"token": token, "title": title, "content": content, "template": "html"},
                           timeout=10)
        result = resp.json()
        return (True, "成功") if result.get('code') == 200 else (False, result.get('msg', '失败'))
    except Exception as e:
        return False, str(e)


# ==================== 报警 ====================
def check_alerts(quote, config):
    alerts = []
    if not quote or quote.get('price', 0) <= 0:
        return alerts
    
    name, price = quote['name'], quote['price']
    volume, amount = quote['volume'], quote['amount']
    turnover, change_pct = quote.get('turnover_rate', 0), quote['change_pct']
    
    if config.get('price_alert_enabled'):
        if config.get('price_min', 0) > 0 and price <= config['price_min']:
            alerts.append({'level': 'error', 'message': f"⚠️ {name} ¥{price:.2f} 跌破下限 ¥{config['price_min']:.2f}"})
        if config.get('price_max', 0) > 0 and price >= config['price_max']:
            alerts.append({'level': 'success', 'message': f"🎉 {name} ¥{price:.2f} 突破上限 ¥{config['price_max']:.2f}"})
    
    if config.get('change_alert_enabled'):
        if change_pct <= config.get('change_min', -10):
            alerts.append({'level': 'error', 'message': f"📉 {name} 跌幅 {change_pct:.2f}%"})
        if change_pct >= config.get('change_max', 10):
            alerts.append({'level': 'success', 'message': f"📈 {name} 涨幅 {change_pct:.2f}%"})
    
    if config.get('volume_alert_enabled'):
        th = config.get('volume_threshold', 0) * 10000
        if th > 0 and volume >= th:
            alerts.append({'level': 'warning', 'message': f"📊 {name} 成交量 {volume/10000:.2f}万手"})
    
    if config.get('amount_alert_enabled'):
        th = config.get('amount_threshold', 0) * 100000000
        if th > 0 and amount >= th:
            alerts.append({'level': 'warning', 'message': f"💰 {name} 成交额 {amount/100000000:.2f}亿"})
    
    if config.get('turnover_alert_enabled'):
        th = config.get('turnover_threshold', 0)
        if th > 0 and turnover >= th:
            alerts.append({'level': 'warning', 'message': f"🔄 {name} 换手率 {turnover:.2f}%"})
    
    return alerts


# ==================== 图表 ====================
def create_chart(df, name, code, price_min=None, price_max=None, current=None):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Scatter(x=df['日期'], y=df['收盘'], mode='lines', name='收盘价',
                            line=dict(color='#667eea', width=2), fill='tozeroy',
                            fillcolor='rgba(102,126,234,0.1)'), row=1, col=1)
    
    if price_min and price_min > 0:
        fig.add_hline(y=price_min, line_dash="dash", line_color="green",
                     annotation_text=f"下限: ¥{price_min:.2f}", row=1, col=1)
    if price_max and price_max > 0:
        fig.add_hline(y=price_max, line_dash="dash", line_color="red",
                     annotation_text=f"上限: ¥{price_max:.2f}", row=1, col=1)
    if current and current > 0:
        fig.add_hline(y=current, line_dash="dot", line_color="orange",
                     annotation_text=f"现价: ¥{current:.2f}", row=1, col=1)
    
    colors = ['red' if r['收盘'] >= r['开盘'] else 'green' for _, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df['日期'], y=df['成交量'], marker_color=colors), row=2, col=1)
    
    fig.update_layout(height=450, template='plotly_white', showlegend=False, title=f'{name} ({code})')
    return fig


def fmt_vol(v):
    return f"{v/10000:.2f}万手" if v >= 10000 else f"{v:.0f}手"

def fmt_amt(a):
    return f"{a/100000000:.2f}亿" if a >= 100000000 else (f"{a/10000:.2f}万" if a >= 10000 else f"{a:.2f}")


# ==================== 主程序 ====================
def main():
    if 'monitored_stocks' not in st.session_state:
        st.session_state.monitored_stocks = {}
    if 'stock_configs' not in st.session_state:
        st.session_state.stock_configs = {}
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = []
    if 'pushplus_token' not in st.session_state:
        st.session_state.pushplus_token = ""
    
    st.markdown('<h1 class="main-header">🛡️ 逻辑指挥官 v3.4</h1>', unsafe_allow_html=True)
    
    now = datetime.now()
    hour, minute, weekday = now.hour, now.minute, now.weekday()
    is_trading = weekday < 5 and ((hour == 9 and minute >= 30) or (hour == 10) or 
                                   (hour == 11 and minute <= 30) or (13 <= hour < 15))
    
    if not is_trading:
        st.info("💤 当前为非交易时段，显示最新收盘数据")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 搜索内置股票
        st.subheader("🔍 搜索股票")
        keyword = st.text_input("代码或名称", placeholder="300499 或 高澜")
        
        if keyword:
            results = search_stocks(keyword)
            if results:
                for r in results:
                    col1, col2 = st.columns([3, 1])
                    col1.caption(f"{r['name']} ({r['code']})")
                    if col2.button("➕", key=f"add_{r['code']}"):
                        st.session_state.monitored_stocks[r['code']] = {'name': r['name'], 'market': r['market']}
                        st.rerun()
            else:
                st.caption("内置列表未找到，可手动输入添加👇")
        
        # 手动输入任意代码
        st.markdown("---")
        st.subheader("✏️ 手动添加")
        col_c, col_m = st.columns([2, 1])
        manual_code = col_c.text_input("股票代码", placeholder="300499", max_chars=6, label_visibility="collapsed")
        manual_market = col_m.selectbox("市场", ["sz", "sh"], label_visibility="collapsed")
        
        if st.button("➕ 添加此股票", use_container_width=True):
            if manual_code and len(manual_code) == 6:
                # 自动判断市场
                market = get_market_by_code(manual_code) if manual_market == "auto" else manual_market
                # 尝试获取股票名称
                quote = get_realtime_quote(manual_code, market)
                if quote:
                    st.session_state.monitored_stocks[manual_code] = {'name': quote['name'], 'market': market}
                    st.success(f"✅ 已添加 {quote['name']}")
                    st.rerun()
                else:
                    st.error("❌ 获取失败，请检查代码或稍后重试")
            else:
                st.warning("请输入6位股票代码")
        
        # 监控列表
        st.markdown("---")
        st.subheader(f"📌 监控列表 ({len(st.session_state.monitored_stocks)})")
        
        for code, info in list(st.session_state.monitored_stocks.items()):
            col1, col2 = st.columns([3, 1])
            col1.caption(f"{info['name']} ({code})")
            if col2.button("❌", key=f"del_{code}"):
                del st.session_state.monitored_stocks[code]
                st.rerun()
        
        if not st.session_state.monitored_stocks:
            if st.button("➕ 添加示例股票", use_container_width=True):
                st.session_state.monitored_stocks['301165'] = {'name': '锐捷网络', 'market': 'sz'}
                st.session_state.monitored_stocks['300499'] = {'name': '高澜股份', 'market': 'sz'}
                st.session_state.monitored_stocks['600487'] = {'name': '亨通光电', 'market': 'sh'}
                st.rerun()
        
        # 热门股票
        with st.expander("🔥 热门股票"):
            hots = [("301165", "锐捷网络", "sz"), ("300499", "高澜股份", "sz"),
                   ("600487", "亨通光电", "sh"), ("002415", "海康威视", "sz"),
                   ("300750", "宁德时代", "sz"), ("002594", "比亚迪", "sz"),
                   ("600519", "贵州茅台", "sh"), ("000063", ("中兴通讯", "sz"))]
            for item in hots:
                if len(item) == 3:
                    code, name, market = item
                else:
                    continue
                if code not in st.session_state.monitored_stocks:
                    if st.button(f"{name}", key=f"hot_{code}", use_container_width=True):
                        st.session_state.monitored_stocks[code] = {'name': name, 'market': market}
                        st.rerun()
        
        # 微信推送
        st.markdown("---")
        st.subheader("📱 微信推送")
        token = st.text_input("PushPlus Token", value=st.session_state.pushplus_token, type="password")
        st.session_state.pushplus_token = token
        
        col_a, col_b = st.columns(2)
        if col_a.button("🔔 测试"):
            if token:
                ok, msg = send_pushplus(token, "测试", "<h3>成功!</h3>")
                st.success("✅") if ok else st.error(f"❌{msg}")
        enable_push = col_b.checkbox("启用", value=True)
        
        st.markdown("---")
        if st.button("🔄 刷新数据", use_container_width=True):
            st.rerun()
        st.caption(f"⏰ {now.strftime('%H:%M:%S')} | 内置{len(BUILTIN_STOCKS)}只股票")
    
    # 主内容
    if not st.session_state.monitored_stocks:
        st.info("👈 搜索或手动输入股票代码添加监控")
        st.markdown("""
        ### 💡 使用说明
        1. **搜索添加**: 在左侧搜索框输入股票代码或名称
        2. **手动添加**: 输入6位股票代码，选择市场(sz深圳/sh上海)
        3. **快速添加**: 点击「热门股票」快速添加
        """)
        return
    
    all_alerts = []
    codes = list(st.session_state.monitored_stocks.keys())
    names = [st.session_state.monitored_stocks[c]['name'] for c in codes]
    tabs = st.tabs(names) if len(codes) > 1 else [st.container()]
    
    for idx, code in enumerate(codes):
        info = st.session_state.monitored_stocks[code]
        market, name = info['market'], info['name']
        
        with tabs[idx]:
            quote = get_realtime_quote(code, market)
            hist = get_historical_data(code, market, 90)
            
            # 初始化配置
            if code not in st.session_state.stock_configs:
                if hist is not None and not hist.empty:
                    lo, hi = float(hist['最低'].min()), float(hist['最高'].max())
                else:
                    lo, hi = 10, 100
                st.session_state.stock_configs[code] = {
                    'price_alert_enabled': True, 'price_min': round(lo*0.95, 2), 'price_max': round(hi*1.05, 2),
                    'change_alert_enabled': True, 'change_min': -5.0, 'change_max': 5.0,
                    'volume_alert_enabled': False, 'volume_threshold': 10.0,
                    'amount_alert_enabled': False, 'amount_threshold': 10.0,
                    'turnover_alert_enabled': False, 'turnover_threshold': 10.0,
                }
            
            cfg = st.session_state.stock_configs[code]
            
            # 报警设置
            with st.expander(f"⚙️ {name} 报警设置"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("**💰 价格区间**")
                    cfg['price_alert_enabled'] = st.checkbox("启用", value=cfg['price_alert_enabled'], key=f"pen_{code}")
                    if cfg['price_alert_enabled']:
                        cfg['price_min'] = st.number_input("下限(元)", 0.0, 9999.0, float(cfg['price_min']), 0.1, key=f"pmin_{code}")
                        cfg['price_max'] = st.number_input("上限(元)", 0.0, 9999.0, float(cfg['price_max']), 0.1, key=f"pmax_{code}")
                    
                    st.markdown("**📊 涨跌幅**")
                    cfg['change_alert_enabled'] = st.checkbox("启用", value=cfg['change_alert_enabled'], key=f"cen_{code}")
                    if cfg['change_alert_enabled']:
                        cfg['change_min'] = st.number_input("跌幅(%)", -20.0, 0.0, float(cfg['change_min']), 0.5, key=f"cmin_{code}")
                        cfg['change_max'] = st.number_input("涨幅(%)", 0.0, 20.0, float(cfg['change_max']), 0.5, key=f"cmax_{code}")
                
                with c2:
                    st.markdown("**📦 成交量**")
                    cfg['volume_alert_enabled'] = st.checkbox("启用", value=cfg['volume_alert_enabled'], key=f"ven_{code}")
                    if cfg['volume_alert_enabled']:
                        cfg['volume_threshold'] = st.number_input("阈值(万手)", 0.1, 1000.0, float(cfg['volume_threshold']), 1.0, key=f"vth_{code}")
                    
                    st.markdown("**💵 成交额**")
                    cfg['amount_alert_enabled'] = st.checkbox("启用", value=cfg['amount_alert_enabled'], key=f"aen_{code}")
                    if cfg['amount_alert_enabled']:
                        cfg['amount_threshold'] = st.number_input("阈值(亿)", 0.1, 500.0, float(cfg['amount_threshold']), 0.5, key=f"ath_{code}")
                
                with c3:
                    st.markdown("**🔄 换手率**")
                    cfg['turnover_alert_enabled'] = st.checkbox("启用", value=cfg['turnover_alert_enabled'], key=f"ten_{code}")
                    if cfg['turnover_alert_enabled']:
                        cfg['turnover_threshold'] = st.number_input("阈值(%)", 0.1, 50.0, float(cfg['turnover_threshold']), 0.5, key=f"tth_{code}")
            
            # 显示行情
            if quote:
                alerts = check_alerts(quote, cfg)
                all_alerts.extend(alerts)
                
                for a in alerts:
                    if a['level'] == 'error':
                        st.error(a['message'])
                    elif a['level'] == 'success':
                        st.success(a['message'])
                    else:
                        st.warning(a['message'])
                
                cols = st.columns(6)
                cols[0].metric("💰 最新价", f"¥{quote['price']:.2f}", f"{quote['change_pct']:.2f}%",
                              delta_color="normal" if quote['change_pct'] >= 0 else "inverse")
                cols[1].metric("📈 涨跌", f"¥{quote['change_amount']:.2f}")
                cols[2].metric("📦 成交量", fmt_vol(quote['volume']))
                cols[3].metric("💵 成交额", fmt_amt(quote['amount']))
                cols[4].metric("🔄 换手率", f"{quote.get('turnover_rate', 0):.2f}%")
                cols[5].metric("⏰ 更新", quote['timestamp'].split()[1])
                
                cols2 = st.columns(4)
                cols2[0].metric("📍 今开", f"¥{quote['open']:.2f}")
                cols2[1].metric("⬆️ 最高", f"¥{quote['high']:.2f}")
                cols2[2].metric("⬇️ 最低", f"¥{quote['low']:.2f}")
                cols2[3].metric("📊 昨收", f"¥{quote['pre_close']:.2f}")
            else:
                st.warning(f"⏳ {name} ({code}) 数据获取失败，请稍后刷新")
            
            # 图表
            if hist is not None and not hist.empty:
                pmin = cfg['price_min'] if cfg['price_alert_enabled'] else None
                pmax = cfg['price_max'] if cfg['price_alert_enabled'] else None
                cur = quote['price'] if quote else None
                st.plotly_chart(create_chart(hist, name, code, pmin, pmax, cur), use_container_width=True)
    
    # 推送
    if all_alerts and token and enable_push:
        content = "<h3>🚨 报警</h3><ul>" + "".join(f"<li>{a['message']}</li>" for a in all_alerts) + "</ul>"
        h = hashlib.md5(content.encode()).hexdigest()
        if h not in st.session_state.alert_history:
            send_pushplus(token, "🛡️ 报警", content)
            st.session_state.alert_history.append(h)
            st.session_state.alert_history = st.session_state.alert_history[-50:]
    
    st.markdown("---")
    st.caption("📌 数据来源: 新浪/腾讯财经 | 🛡️ 逻辑指挥官 v3.4")
    
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
