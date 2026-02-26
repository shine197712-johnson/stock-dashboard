"""
逻辑指挥官 - 算力基建监控哨兵 v3.3
使用东方财富接口，解决海外访问问题
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


# ==================== 东方财富接口 ====================
@st.cache_data(ttl=86400)
def get_all_stocks():
    """从东方财富获取全部A股列表"""
    stocks = {}
    
    try:
        # 东方财富A股列表接口
        url = "http://82.push2.eastmoney.com/api/qt/clist/get"
        
        # 沪深A股
        for fs in ["m:0+t:6,7,13", "m:1+t:2,23"]:  # 深市、沪市
            params = {
                'pn': 1,
                'pz': 5000,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': fs,
                'fields': 'f12,f14'
            }
            
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff']:
                    code = item.get('f12', '')
                    name = item.get('f14', '')
                    if code and name:
                        # 判断市场
                        if code.startswith('6'):
                            market = 'sh'
                        else:
                            market = 'sz'
                        stocks[code] = {'name': name, 'market': market}
    except Exception as e:
        st.error(f"获取股票列表失败: {e}")
    
    return stocks


def search_stocks(keyword, all_stocks):
    """搜索股票"""
    if not keyword:
        return []
    keyword_upper = keyword.upper()
    results = []
    for code, info in all_stocks.items():
        if keyword_upper in code or keyword in info['name']:
            results.append({'code': code, 'name': info['name'], 'market': info['market']})
    results.sort(key=lambda x: (keyword_upper not in x['code'], x['code']))
    return results[:15]


def get_eastmoney_secid(code, market):
    """生成东方财富的secid"""
    if market == 'sh':
        return f"1.{code}"
    else:
        return f"0.{code}"


def get_realtime_quote(stock_code, market="sz"):
    """从东方财富获取实时行情"""
    try:
        secid = get_eastmoney_secid(stock_code, market)
        
        url = "http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': secid,
            'fields': 'f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f116,f117,f168,f169,f170',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'invt': 2
        }
        
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if not data.get('data'):
            return None
        
        d = data['data']
        
        # 解析字段
        # f43:最新价(分) f44:最高(分) f45:最低(分) f46:今开(分) f47:成交量(手) f48:成交额(元)
        # f50:量比 f51:涨停价 f52:跌停价 f55:收益 f57:代码 f58:名称 f60:昨收(分)
        # f116:总市值 f117:流通市值 f168:换手率 f169:涨跌额(分) f170:涨跌幅
        
        current_price = d.get('f43', 0)
        if isinstance(current_price, str) and current_price == '-':
            current_price = 0
        current_price = float(current_price) / 100 if current_price else 0
        
        pre_close = float(d.get('f60', 0)) / 100 if d.get('f60') else 0
        high = float(d.get('f44', 0)) / 100 if d.get('f44') else 0
        low = float(d.get('f45', 0)) / 100 if d.get('f45') else 0
        open_price = float(d.get('f46', 0)) / 100 if d.get('f46') else 0
        volume = float(d.get('f47', 0)) if d.get('f47') else 0  # 手
        amount = float(d.get('f48', 0)) if d.get('f48') else 0  # 元
        turnover = float(d.get('f168', 0)) if d.get('f168') else 0  # 换手率
        change_pct = float(d.get('f170', 0)) / 100 if d.get('f170') else 0  # 涨跌幅
        change_amount = float(d.get('f169', 0)) / 100 if d.get('f169') else 0  # 涨跌额
        name = d.get('f58', '')
        
        # 非交易时段，当前价可能为0
        if current_price <= 0:
            current_price = pre_close
        
        if current_price <= 0:
            return None
        
        return {
            'name': name,
            'code': stock_code,
            'price': current_price,
            'change_pct': round(change_pct, 2),
            'change_amount': round(change_amount, 2),
            'volume': volume,
            'amount': amount,
            'turnover_rate': turnover,
            'high': high if high > 0 else current_price,
            'low': low if low > 0 else current_price,
            'open': open_price if open_price > 0 else current_price,
            'pre_close': pre_close,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return None


def get_historical_data(stock_code, market="sz", days=90):
    """从东方财富获取历史K线"""
    try:
        secid = get_eastmoney_secid(stock_code, market)
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            'secid': secid,
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57',
            'klt': 101,  # 日K
            'fqt': 1,    # 前复权
            'end': '20500101',
            'lmt': days,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }
        
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if not data.get('data') or not data['data'].get('klines'):
            return None
        
        klines = data['data']['klines']
        records = []
        
        for line in klines:
            parts = line.split(',')
            if len(parts) >= 7:
                records.append({
                    '日期': parts[0],
                    '开盘': float(parts[1]),
                    '收盘': float(parts[2]),
                    '最高': float(parts[3]),
                    '最低': float(parts[4]),
                    '成交量': float(parts[5]),
                    '成交额': float(parts[6])
                })
        
        df = pd.DataFrame(records)
        df['日期'] = pd.to_datetime(df['日期'])
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
    
    name, price, volume, amount = quote['name'], quote['price'], quote['volume'], quote['amount']
    turnover, change_pct = quote.get('turnover_rate', 0), quote['change_pct']
    
    if config.get('price_alert_enabled'):
        if config.get('price_min', 0) > 0 and price <= config['price_min']:
            alerts.append({'level': 'error', 'message': f"⚠️ {name} ¥{price:.2f} 跌破下限 ¥{config['price_min']:.2f}"})
        if config.get('price_max', 0) > 0 and price >= config['price_max']:
            alerts.append({'level': 'success', 'message': f"🎉 {name} ¥{price:.2f} 突破上限 ¥{config['price_max']:.2f}"})
    
    if config.get('change_alert_enabled'):
        if change_pct <= config.get('change_min', -10):
            alerts.append({'level': 'error', 'message': f"📉 {name} 跌幅 {change_pct:.2f}% 超阈值"})
        if change_pct >= config.get('change_max', 10):
            alerts.append({'level': 'success', 'message': f"📈 {name} 涨幅 {change_pct:.2f}% 超阈值"})
    
    if config.get('volume_alert_enabled'):
        th = config.get('volume_threshold', 0) * 10000
        if th > 0 and volume >= th:
            alerts.append({'level': 'warning', 'message': f"📊 {name} 成交量 {volume/10000:.2f}万手 超阈值"})
    
    if config.get('amount_alert_enabled'):
        th = config.get('amount_threshold', 0) * 100000000
        if th > 0 and amount >= th:
            alerts.append({'level': 'warning', 'message': f"💰 {name} 成交额 {amount/100000000:.2f}亿 超阈值"})
    
    if config.get('turnover_alert_enabled'):
        th = config.get('turnover_threshold', 0)
        if th > 0 and turnover >= th:
            alerts.append({'level': 'warning', 'message': f"🔄 {name} 换手率 {turnover:.2f}% 超阈值"})
    
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
    
    st.markdown('<h1 class="main-header">🛡️ 逻辑指挥官 v3.3</h1>', unsafe_allow_html=True)
    
    now = datetime.now()
    hour, minute, weekday = now.hour, now.minute, now.weekday()
    
    # 判断交易时段（北京时间）
    is_trading = weekday < 5 and (
        (hour == 9 and minute >= 30) or 
        (hour == 10) or 
        (hour == 11 and minute <= 30) or
        (hour >= 13 and hour < 15)
    )
    
    if not is_trading:
        st.info("💤 当前为非交易时段，显示最新收盘数据")
    
    with st.spinner("加载A股列表..."):
        all_stocks = get_all_stocks()
    
    if not all_stocks:
        st.error("⚠️ 无法加载股票列表，请稍后刷新")
        if st.button("🔄 重新加载"):
            st.cache_data.clear()
            st.rerun()
        return
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 配置")
        
        st.subheader("🔍 搜索股票")
        keyword = st.text_input("代码或名称", placeholder="300499 或 高澜")
        
        if keyword:
            results = search_stocks(keyword, all_stocks)
            if results:
                for r in results:
                    col1, col2 = st.columns([3, 1])
                    col1.caption(f"{r['name']} ({r['code']})")
                    if col2.button("➕", key=f"add_{r['code']}"):
                        st.session_state.monitored_stocks[r['code']] = {'name': r['name'], 'market': r['market']}
                        st.rerun()
            else:
                st.warning("未找到")
        
        st.markdown("---")
        st.subheader(f"📌 监控列表 ({len(st.session_state.monitored_stocks)})")
        
        for code, info in list(st.session_state.monitored_stocks.items()):
            col1, col2 = st.columns([3, 1])
            col1.caption(f"{info['name']} ({code})")
            if col2.button("❌", key=f"del_{code}"):
                del st.session_state.monitored_stocks[code]
                st.rerun()
        
        if not st.session_state.monitored_stocks:
            if st.button("➕ 添加示例股票"):
                st.session_state.monitored_stocks['301165'] = {'name': '锐捷网络', 'market': 'sz'}
                st.session_state.monitored_stocks['300499'] = {'name': '高澜股份', 'market': 'sz'}
                st.session_state.monitored_stocks['600487'] = {'name': '亨通光电', 'market': 'sh'}
                st.rerun()
        
        with st.expander("🔥 热门股票"):
            hots = [("301165", "锐捷网络", "sz"), ("300499", "高澜股份", "sz"),
                   ("600487", "亨通光电", "sh"), ("002415", "海康威视", "sz"),
                   ("300750", "宁德时代", "sz"), ("002594", "比亚迪", "sz"),
                   ("600519", "贵州茅台", "sh"), ("000063", "中兴通讯", "sz")]
            for code, name, market in hots:
                if code not in st.session_state.monitored_stocks:
                    if st.button(f"{name}", key=f"hot_{code}", use_container_width=True):
                        st.session_state.monitored_stocks[code] = {'name': name, 'market': market}
                        st.rerun()
        
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
        col_r1, col_r2 = st.columns(2)
        if col_r1.button("🔄 刷新", use_container_width=True):
            st.rerun()
        if col_r2.button("🗑️ 清缓存", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.caption(f"⏰ {now.strftime('%H:%M:%S')} | 共{len(all_stocks)}只")
    
    # 主内容
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
                st.warning(f"⏳ {name} ({code}) 数据获取失败")
                st.caption("可能原因: 停牌、退市或网络问题，请点击左侧「清缓存」后重试")
            
            # 图表
            if hist is not None and not hist.empty:
                pmin = cfg['price_min'] if cfg['price_alert_enabled'] else None
                pmax = cfg['price_max'] if cfg['price_alert_enabled'] else None
                cur = quote['price'] if quote else None
                st.plotly_chart(create_chart(hist, name, code, pmin, pmax, cur), use_container_width=True)
            else:
                st.info("📊 暂无历史K线数据")
    
    # 推送
    if all_alerts and token and enable_push:
        content = "<h3>🚨 报警</h3><ul>" + "".join(f"<li>{a['message']}</li>" for a in all_alerts) + "</ul>"
        h = hashlib.md5(content.encode()).hexdigest()
        if h not in st.session_state.alert_history:
            send_pushplus(token, "🛡️ 报警", content)
            st.session_state.alert_history.append(h)
            st.session_state.alert_history = st.session_state.alert_history[-50:]
    
    st.markdown("---")
    st.caption("📌 数据来源: 东方财富 | 🛡️ 逻辑指挥官 v3.3")
    
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
