"""
逻辑指挥官 - 算力基建监控哨兵 v3.1
支持全A股搜索、完整报警配置、微信推送
"""

import streamlit as st
import requests
import json
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
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

# 自定义CSS
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


# ==================== 全A股列表获取 ====================
@st.cache_data(ttl=86400)
def get_all_stocks():
    """获取全部A股列表"""
    try:
        stocks = {}
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
        
        # 沪市
        for page in range(1, 60):
            params = {'page': page, 'num': 100, 'sort': 'symbol', 'asc': 1, 'node': 'sh_a', 'symbol': ''}
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                data = resp.json()
                if not data:
                    break
                for item in data:
                    code = item.get('symbol', '')
                    name = item.get('name', '')
                    if code and name:
                        stocks[code] = {'name': name, 'market': 'sh', 'code': code}
            except:
                break
        
        # 深市
        for page in range(1, 100):
            params = {'page': page, 'num': 100, 'sort': 'symbol', 'asc': 1, 'node': 'sz_a', 'symbol': ''}
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                data = resp.json()
                if not data:
                    break
                for item in data:
                    code = item.get('symbol', '')
                    name = item.get('name', '')
                    if code and name:
                        stocks[code] = {'name': name, 'market': 'sz', 'code': code}
            except:
                break
        
        return stocks
    except:
        return {}


def search_stocks(keyword, all_stocks):
    """搜索股票"""
    if not keyword or len(keyword) < 1:
        return []
    
    keyword_upper = keyword.upper()
    results = []
    
    for code, info in all_stocks.items():
        name = info['name']
        if keyword_upper in code or keyword in name:
            results.append({
                'code': code,
                'name': name,
                'market': info['market'],
                'display': f"{name} ({code})"
            })
    
    results.sort(key=lambda x: (keyword_upper not in x['code'], x['code']))
    return results[:15]


# ==================== 数据获取 ====================
def get_realtime_quote(stock_code, market="sz"):
    """获取实时行情"""
    try:
        sina_code = f"{market}{stock_code}"
        url = f"http://hq.sinajs.cn/list={sina_code}"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        match = re.search(r'"(.+)"', response.text)
        if not match:
            return None
        
        data = match.group(1).split(',')
        if len(data) < 32 or data[0] == '':
            return None
        
        current_price = float(data[3]) if data[3] else 0
        pre_close = float(data[2]) if data[2] else 0
        
        if current_price <= 0:
            return None
        
        change_amount = current_price - pre_close
        change_pct = (change_amount / pre_close * 100) if pre_close > 0 else 0
        volume = float(data[8]) if data[8] else 0
        amount = float(data[9]) if data[9] else 0
        
        # 获取换手率
        turnover_rate = get_turnover_rate(stock_code, market)
        
        return {
            'name': data[0],
            'code': stock_code,
            'price': current_price,
            'change_pct': round(change_pct, 2),
            'change_amount': round(change_amount, 2),
            'volume': volume / 100,
            'amount': amount,
            'turnover_rate': turnover_rate,
            'high': float(data[4]) if data[4] else 0,
            'low': float(data[5]) if data[5] else 0,
            'open': float(data[1]) if data[1] else 0,
            'pre_close': pre_close,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except:
        return None


def get_turnover_rate(stock_code, market):
    """获取换手率"""
    try:
        sina_code = f"{market}{stock_code}"
        url = f"http://qt.gtimg.cn/q={sina_code}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        resp.encoding = 'gbk'
        parts = resp.text.split('~')
        if len(parts) > 38 and parts[38]:
            return float(parts[38])
        return 0
    except:
        return 0


def get_historical_data(stock_code, market="sz", days=90):
    """获取历史数据"""
    try:
        sina_code = f"{market}{stock_code}"
        url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_data/KC_MarketDataService.getKLineData"
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
        df = df.rename(columns={'day': '日期', 'open': '开盘', 'high': '最高', 'low': '最低', 'close': '收盘', 'volume': '成交量'})
        
        for col in ['开盘', '最高', '最低', '收盘', '成交量']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except:
        return None


# ==================== 推送 ====================
def send_pushplus(token, title, content):
    """微信推送"""
    if not token:
        return False, "未配置Token"
    try:
        url = "http://www.pushplus.plus/send"
        data = {"token": token, "title": title, "content": content, "template": "html"}
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        if result.get('code') == 200:
            return True, "成功"
        return False, result.get('msg', '失败')
    except Exception as e:
        return False, str(e)


# ==================== 报警检查 ====================
def check_alerts(quote, config):
    """多维度报警"""
    alerts = []
    if not quote or quote.get('price', 0) <= 0:
        return alerts
    
    name = quote['name']
    price = quote['price']
    volume = quote['volume']
    amount = quote['amount']
    turnover = quote.get('turnover_rate', 0)
    change_pct = quote['change_pct']
    
    # 价格
    if config.get('price_alert_enabled'):
        if config.get('price_min', 0) > 0 and price <= config['price_min']:
            alerts.append({'level': 'error', 'message': f"⚠️ {name} 股价 ¥{price:.2f} 跌破下限 ¥{config['price_min']:.2f}"})
        if config.get('price_max', 0) > 0 and price >= config['price_max']:
            alerts.append({'level': 'success', 'message': f"🎉 {name} 股价 ¥{price:.2f} 突破上限 ¥{config['price_max']:.2f}"})
    
    # 涨跌幅
    if config.get('change_alert_enabled'):
        if change_pct <= config.get('change_min', -10):
            alerts.append({'level': 'error', 'message': f"📉 {name} 跌幅 {change_pct:.2f}% 超过阈值 {config['change_min']}%"})
        if change_pct >= config.get('change_max', 10):
            alerts.append({'level': 'success', 'message': f"📈 {name} 涨幅 {change_pct:.2f}% 超过阈值 {config['change_max']}%"})
    
    # 成交量
    if config.get('volume_alert_enabled'):
        threshold = config.get('volume_threshold', 0) * 10000
        if threshold > 0 and volume >= threshold:
            alerts.append({'level': 'warning', 'message': f"📊 {name} 成交量 {volume/10000:.2f}万手 超阈值"})
    
    # 成交额
    if config.get('amount_alert_enabled'):
        threshold = config.get('amount_threshold', 0) * 100000000
        if threshold > 0 and amount >= threshold:
            alerts.append({'level': 'warning', 'message': f"💰 {name} 成交额 {amount/100000000:.2f}亿 超阈值"})
    
    # 换手率
    if config.get('turnover_alert_enabled'):
        threshold = config.get('turnover_threshold', 0)
        if threshold > 0 and turnover >= threshold:
            alerts.append({'level': 'warning', 'message': f"🔄 {name} 换手率 {turnover:.2f}% 超阈值 {threshold}%"})
    
    return alerts


# ==================== 图表 ====================
def create_chart(df, name, code, price_min=None, price_max=None, current=None):
    """创建图表"""
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
    
    fig.update_layout(height=450, template='plotly_white', showlegend=False,
                     title=f'{name} ({code}) 走势')
    return fig


def format_volume(v):
    return f"{v/10000:.2f}万手" if v >= 10000 else f"{v:.0f}手"

def format_amount(a):
    if a >= 100000000:
        return f"{a/100000000:.2f}亿"
    elif a >= 10000:
        return f"{a/10000:.2f}万"
    return f"{a:.2f}"


# ==================== 主程序 ====================
def main():
    # 初始化
    if 'monitored_stocks' not in st.session_state:
        st.session_state.monitored_stocks = {}
    if 'stock_configs' not in st.session_state:
        st.session_state.stock_configs = {}
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = []
    if 'pushplus_token' not in st.session_state:
        st.session_state.pushplus_token = ""
    
    st.markdown('<h1 class="main-header">🛡️ 逻辑指挥官 v3.1</h1>', unsafe_allow_html=True)
    
    # 加载股票列表
    with st.spinner("加载A股列表..."):
        all_stocks = get_all_stocks()
    
    # ===== 侧边栏 =====
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 搜索
        st.subheader("🔍 搜索股票")
        keyword = st.text_input("代码或名称", placeholder="301165 或 锐捷")
        
        if keyword:
            results = search_stocks(keyword, all_stocks)
            if results:
                for r in results:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"{r['name']} ({r['code']})")
                    with col2:
                        if st.button("➕", key=f"add_{r['code']}"):
                            st.session_state.monitored_stocks[r['code']] = {'name': r['name'], 'market': r['market']}
                            st.rerun()
            else:
                st.warning("未找到")
        
        # 已监控
        st.markdown("---")
        st.subheader(f"📌 监控列表 ({len(st.session_state.monitored_stocks)})")
        
        for code, info in list(st.session_state.monitored_stocks.items()):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"{info['name']} ({code})")
            with col2:
                if st.button("❌", key=f"del_{code}"):
                    del st.session_state.monitored_stocks[code]
                    st.rerun()
        
        if not st.session_state.monitored_stocks:
            if st.button("➕ 添加锐捷网络示例"):
                st.session_state.monitored_stocks['301165'] = {'name': '锐捷网络', 'market': 'sz'}
                st.rerun()
        
        # 热门
        with st.expander("🔥 热门股票"):
            hots = [("301165", "锐捷网络", "sz"), ("000063", "中兴通讯", "sz"),
                   ("002415", "海康威视", "sz"), ("600519", "贵州茅台", "sh"),
                   ("300750", "宁德时代", "sz"), ("002594", "比亚迪", "sz")]
            for code, name, market in hots:
                if code not in st.session_state.monitored_stocks:
                    if st.button(f"{name}", key=f"hot_{code}", use_container_width=True):
                        st.session_state.monitored_stocks[code] = {'name': name, 'market': market}
                        st.rerun()
        
        # 推送
        st.markdown("---")
        st.subheader("📱 微信推送")
        token = st.text_input("PushPlus Token", value=st.session_state.pushplus_token, type="password")
        st.session_state.pushplus_token = token
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔔 测试"):
                if token:
                    ok, msg = send_pushplus(token, "测试", "<h3>成功!</h3>")
                    st.success("✅") if ok else st.error(f"❌{msg}")
        with col_b:
            enable_push = st.checkbox("启用", value=True)
        
        st.markdown("---")
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
        st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 共{len(all_stocks)}只")
    
    # ===== 主内容 =====
    if not st.session_state.monitored_stocks:
        st.info("👈 搜索添加股票开始监控")
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
                    avg = float(hist['收盘'].mean())
                    lo, hi = float(hist['最低'].min()), float(hist['最高'].max())
                else:
                    avg, lo, hi = 50, 30, 70
                
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
                        cfg['change_min'] = st.number_input("跌幅阈值(%)", -20.0, 0.0, float(cfg['change_min']), 0.5, key=f"cmin_{code}")
                        cfg['change_max'] = st.number_input("涨幅阈值(%)", 0.0, 20.0, float(cfg['change_max']), 0.5, key=f"cmax_{code}")
                
                with c2:
                    st.markdown("**📦 成交量**")
                    cfg['volume_alert_enabled'] = st.checkbox("启用", value=cfg['volume_alert_enabled'], key=f"ven_{code}")
                    if cfg['volume_alert_enabled']:
                        cfg['volume_threshold'] = st.number_input("阈值(万手)", 0.1, 1000.0, float(cfg['volume_threshold']), 1.0, key=f"vth_{code}")
                    
                    st.markdown("**💵 成交额**")
                    cfg['amount_alert_enabled'] = st.checkbox("启用", value=cfg['amount_alert_enabled'], key=f"aen_{code}")
                    if cfg['amount_alert_enabled']:
                        cfg['amount_threshold'] = st.number_input("阈值(亿元)", 0.1, 500.0, float(cfg['amount_threshold']), 0.5, key=f"ath_{code}")
                
                with c3:
                    st.markdown("**🔄 换手率**")
                    cfg['turnover_alert_enabled'] = st.checkbox("启用", value=cfg['turnover_alert_enabled'], key=f"ten_{code}")
                    if cfg['turnover_alert_enabled']:
                        cfg['turnover_threshold'] = st.number_input("阈值(%)", 0.1, 50.0, float(cfg['turnover_threshold']), 0.5, key=f"tth_{code}")
            
            # 行情
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
                cols[2].metric("📦 成交量", format_volume(quote['volume']))
                cols[3].metric("💵 成交额", format_amount(quote['amount']))
                cols[4].metric("🔄 换手率", f"{quote.get('turnover_rate', 0):.2f}%")
                cols[5].metric("⏰ 更新", quote['timestamp'].split()[1])
            else:
                st.warning(f"⏳ {name} 暂无数据")
            
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
            send_pushplus(token, "🛡️ 监控报警", content)
            st.session_state.alert_history.append(h)
            st.session_state.alert_history = st.session_state.alert_history[-50:]
    
    st.markdown("---")
    st.caption("📌 数据来源: 新浪财经 | 仅供参考 | 🛡️ 逻辑指挥官 v3.1")
    
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
