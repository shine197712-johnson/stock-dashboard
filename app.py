"""
逻辑指挥官 - 算力基建监控哨兵 v3.0 专业版
支持多股票监控、多维度报警、消息推送
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
    .stock-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .alert-triggered {
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 预设股票列表 ====================
STOCK_PRESETS = {
    "301165": {"name": "锐捷网络", "market": "sz", "sector": "网络设备"},
    "000063": {"name": "中兴通讯", "market": "sz", "sector": "通信设备"},
    "600588": {"name": "用友网络", "market": "sh", "sector": "软件服务"},
    "002415": {"name": "海康威视", "market": "sz", "sector": "安防设备"},
    "300059": {"name": "东方财富", "market": "sz", "sector": "金融科技"},
    "600519": {"name": "贵州茅台", "market": "sh", "sector": "白酒"},
    "300750": {"name": "宁德时代", "market": "sz", "sector": "新能源"},
    "002594": {"name": "比亚迪", "market": "sz", "sector": "新能源汽车"},
}


# ==================== 数据获取函数 ====================
def get_realtime_quote(stock_code, market="sz"):
    """获取实时行情"""
    try:
        sina_code = f"{market}{stock_code}"
        url = f"http://hq.sinajs.cn/list={sina_code}"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        content = response.text
        match = re.search(r'"(.+)"', content)
        
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
        
        return {
            'name': data[0],
            'code': stock_code,
            'price': current_price,
            'change_pct': round(change_pct, 2),
            'change_amount': round(change_amount, 2),
            'volume': volume / 100,
            'amount': amount,
            'high': float(data[4]) if data[4] else 0,
            'low': float(data[5]) if data[5] else 0,
            'open': float(data[1]) if data[1] else 0,
            'pre_close': pre_close,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return None


def get_historical_data(stock_code, market="sz", days=90):
    """获取历史K线数据"""
    try:
        sina_code = f"{market}{stock_code}"
        url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_data/KC_MarketDataService.getKLineData"
        params = {
            'symbol': sina_code,
            'scale': '240',
            'ma': 'no',
            'datalen': days
        }
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        content = response.text
        match = re.search(r'\((\[.+\])\)', content)
        
        if not match:
            return None
        
        data = json.loads(match.group(1))
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df['day'] = pd.to_datetime(df['day'])
        df = df.rename(columns={
            'day': '日期', 'open': '开盘', 'high': '最高',
            'low': '最低', 'close': '收盘', 'volume': '成交量'
        })
        
        for col in ['开盘', '最高', '最低', '收盘', '成交量']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except:
        return None


def get_stock_news(stock_code, stock_name):
    """获取股票相关新闻 - 使用百度新闻搜索"""
    try:
        # 使用新浪财经股票新闻接口
        url = "https://feed.mix.sina.com.cn/api/roll/get"
        params = {
            'pageid': '155',
            'lid': '2516',
            'num': 5,
            'page': 1
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        news_list = []
        if data.get('result', {}).get('data'):
            for item in data['result']['data'][:5]:
                title = item.get('title', '')
                # 过滤包含股票名称的新闻
                if stock_name in title or stock_code in title or '算力' in title or '网络' in title:
                    news_list.append({
                        'title': title,
                        'time': item.get('ctime', ''),
                        'url': item.get('url', '#')
                    })
        
        # 如果没有找到相关新闻，返回通用财经新闻
        if not news_list and data.get('result', {}).get('data'):
            for item in data['result']['data'][:3]:
                news_list.append({
                    'title': item.get('title', ''),
                    'time': item.get('ctime', ''),
                    'url': item.get('url', '#')
                })
        
        return news_list
    except:
        return []


# ==================== 消息推送函数 ====================
def send_pushplus(token, title, content):
    """通过 PushPlus 发送微信推送"""
    if not token:
        return False, "未配置 PushPlus Token"
    
    try:
        url = "http://www.pushplus.plus/send"
        data = {
            "token": token,
            "title": title,
            "content": content,
            "template": "html"
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            return True, "推送成功"
        else:
            return False, result.get('msg', '推送失败')
    except Exception as e:
        return False, str(e)


def check_alerts_multi(quote, config):
    """多维度报警检查"""
    alerts = []
    
    if not quote or quote.get('price', 0) <= 0:
        return alerts
    
    price = quote['price']
    volume = quote['volume']
    change_pct = quote['change_pct']
    
    # 价格报警
    if config.get('price_alert_enabled', False):
        support = config.get('support_line', 0)
        resistance = config.get('resistance_line', 0)
        
        if support > 0 and price <= support:
            alerts.append({
                'type': 'price_support',
                'level': 'error',
                'message': f"⚠️ {quote['name']} 股价 ¥{price:.2f} 跌破支撑位 ¥{support:.2f}"
            })
        
        if resistance > 0 and price >= resistance:
            alerts.append({
                'type': 'price_resistance',
                'level': 'success',
                'message': f"🎉 {quote['name']} 股价 ¥{price:.2f} 突破压力位 ¥{resistance:.2f}"
            })
    
    # 涨跌幅报警
    if config.get('change_alert_enabled', False):
        change_threshold = config.get('change_threshold', 5)
        
        if abs(change_pct) >= change_threshold:
            if change_pct > 0:
                alerts.append({
                    'type': 'change_up',
                    'level': 'success',
                    'message': f"📈 {quote['name']} 涨幅达 {change_pct:.2f}%，超过阈值 {change_threshold}%"
                })
            else:
                alerts.append({
                    'type': 'change_down',
                    'level': 'error',
                    'message': f"📉 {quote['name']} 跌幅达 {change_pct:.2f}%，超过阈值 {change_threshold}%"
                })
    
    # 成交量报警
    if config.get('volume_alert_enabled', False):
        volume_threshold = config.get('volume_threshold', 10000)
        
        if volume >= volume_threshold:
            alerts.append({
                'type': 'volume',
                'level': 'warning',
                'message': f"📊 {quote['name']} 成交量 {volume/10000:.2f}万手，超过阈值 {volume_threshold/10000:.2f}万手"
            })
    
    return alerts


# ==================== 图表函数 ====================
def create_stock_chart(df, stock_name, stock_code, support=None, resistance=None, current_price=None):
    """创建股票走势图"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=[f'{stock_name} ({stock_code}) 价格走势', '成交量']
    )
    
    # 价格线
    fig.add_trace(go.Scatter(
        x=df['日期'], y=df['收盘'],
        mode='lines', name='收盘价',
        line=dict(color='#667eea', width=2),
        fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.1)'
    ), row=1, col=1)
    
    # 支撑位
    if support and support > 0:
        fig.add_hline(y=support, line_dash="dash", line_color="green",
                     annotation_text=f"支撑: ¥{support:.2f}", row=1, col=1)
    
    # 压力位
    if resistance and resistance > 0:
        fig.add_hline(y=resistance, line_dash="dash", line_color="red",
                     annotation_text=f"压力: ¥{resistance:.2f}", row=1, col=1)
    
    # 当前价
    if current_price and current_price > 0:
        fig.add_hline(y=current_price, line_dash="dot", line_color="orange",
                     annotation_text=f"现价: ¥{current_price:.2f}", row=1, col=1)
    
    # 成交量
    colors = ['red' if row['收盘'] >= row['开盘'] else 'green' for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df['日期'], y=df['成交量'], marker_color=colors, name='成交量'), row=2, col=1)
    
    fig.update_layout(height=500, template='plotly_white', showlegend=False)
    return fig


# ==================== 辅助函数 ====================
def format_volume(vol):
    if vol >= 10000:
        return f"{vol/10000:.2f}万手"
    return f"{vol:.0f}手"


def format_amount(amt):
    if amt >= 100000000:
        return f"{amt/100000000:.2f}亿"
    elif amt >= 10000:
        return f"{amt/10000:.2f}万"
    return f"{amt:.2f}"


# ==================== 主程序 ====================
def main():
    # 初始化 session state
    if 'monitored_stocks' not in st.session_state:
        st.session_state.monitored_stocks = ['301165']
    
    if 'stock_configs' not in st.session_state:
        st.session_state.stock_configs = {}
    
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = []
    
    if 'pushplus_token' not in st.session_state:
        st.session_state.pushplus_token = ""
    
    # 页面标题
    st.markdown('<h1 class="main-header">🛡️ 逻辑指挥官 - 算力基建监控哨兵 v3.0</h1>', unsafe_allow_html=True)
    
    # ==================== 侧边栏 ====================
    with st.sidebar:
        st.header("⚙️ 监控配置")
        
        # 股票选择
        st.subheader("📌 选择监控股票")
        
        available_stocks = list(STOCK_PRESETS.keys())
        
        selected_stocks = st.multiselect(
            "从预设列表选择",
            options=available_stocks,
            default=st.session_state.monitored_stocks,
            format_func=lambda x: f"{STOCK_PRESETS[x]['name']} ({x})"
        )
        
        # 自定义股票
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        with col1:
            custom_code = st.text_input("自定义代码", placeholder="600000")
        with col2:
            custom_market = st.selectbox("市场", ["sz", "sh"])
        
        if st.button("➕ 添加", use_container_width=True):
            if custom_code and len(custom_code) == 6:
                if custom_code not in STOCK_PRESETS:
                    STOCK_PRESETS[custom_code] = {
                        "name": f"自定义{custom_code}",
                        "market": custom_market,
                        "sector": "自定义"
                    }
                if custom_code not in selected_stocks:
                    selected_stocks.append(custom_code)
                st.success(f"已添加 {custom_code}")
                st.rerun()
        
        st.session_state.monitored_stocks = selected_stocks if selected_stocks else ['301165']
        
        # 消息推送
        st.markdown("---")
        st.subheader("📱 微信推送")
        
        pushplus_token = st.text_input(
            "PushPlus Token",
            value=st.session_state.pushplus_token,
            type="password",
            help="访问 pushplus.plus 微信扫码获取"
        )
        st.session_state.pushplus_token = pushplus_token
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔔 测试", use_container_width=True):
                if pushplus_token:
                    success, msg = send_pushplus(
                        pushplus_token,
                        "🛡️ 测试消息",
                        "<h3>推送测试成功！</h3><p>监控哨兵已就绪</p>"
                    )
                    if success:
                        st.success("✅ 成功")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("请输入Token")
        
        with col_b:
            enable_push = st.checkbox("启用推送", value=True)
        
        st.caption("💡 pushplus.plus 免费注册")
        
        # 刷新
        st.markdown("---")
        if st.button("🔄 刷新数据", use_container_width=True):
            st.rerun()
        
        st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    # ==================== 主内容 ====================
    all_alerts = []
    
    # 显示监控的股票数量
    st.info(f"📊 当前监控 {len(st.session_state.monitored_stocks)} 只股票")
    
    # 创建标签页
    if len(st.session_state.monitored_stocks) > 1:
        tabs = st.tabs([f"{STOCK_PRESETS.get(code, {}).get('name', code)}" for code in st.session_state.monitored_stocks])
    else:
        tabs = [st.container()]
    
    for idx, stock_code in enumerate(st.session_state.monitored_stocks):
        stock_info = STOCK_PRESETS.get(stock_code, {"name": stock_code, "market": "sz", "sector": "未知"})
        market = stock_info['market']
        stock_name = stock_info['name']
        
        with tabs[idx]:
            # 获取数据
            quote = get_realtime_quote(stock_code, market)
            hist_data = get_historical_data(stock_code, market, 90)
            
            # 初始化配置
            if stock_code not in st.session_state.stock_configs:
                if hist_data is not None and not hist_data.empty:
                    avg_price = float(hist_data['收盘'].mean())
                    avg_volume = float(hist_data['成交量'].mean())
                else:
                    avg_price = 50
                    avg_volume = 10000
                
                st.session_state.stock_configs[stock_code] = {
                    'price_alert_enabled': True,
                    'support_line': avg_price * 0.95,
                    'resistance_line': avg_price * 1.05,
                    'change_alert_enabled': True,
                    'change_threshold': 5.0,
                    'volume_alert_enabled': False,
                    'volume_threshold': avg_volume * 2
                }
            
            config = st.session_state.stock_configs[stock_code]
            
            # 报警设置
            with st.expander(f"⚙️ 报警设置 - {stock_name}", expanded=False):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown("**💰 价格报警**")
                    config['price_alert_enabled'] = st.checkbox(
                        "启用", value=config['price_alert_enabled'], key=f"price_en_{stock_code}"
                    )
                    if config['price_alert_enabled']:
                        if hist_data is not None and not hist_data.empty:
                            p_min = float(hist_data['最低'].min()) * 0.8
                            p_max = float(hist_data['最高'].max()) * 1.2
                        else:
                            p_min, p_max = 10.0, 200.0
                        
                        config['support_line'] = st.slider(
                            "支撑位", p_min, p_max, float(config['support_line']), 0.5, key=f"sup_{stock_code}"
                        )
                        config['resistance_line'] = st.slider(
                            "压力位", p_min, p_max, float(config['resistance_line']), 0.5, key=f"res_{stock_code}"
                        )
                
                with col_b:
                    st.markdown("**📊 涨跌幅报警**")
                    config['change_alert_enabled'] = st.checkbox(
                        "启用", value=config['change_alert_enabled'], key=f"chg_en_{stock_code}"
                    )
                    if config['change_alert_enabled']:
                        config['change_threshold'] = st.slider(
                            "阈值(%)", 1.0, 10.0, float(config['change_threshold']), 0.5, key=f"chg_{stock_code}"
                        )
                
                with col_c:
                    st.markdown("**📦 成交量报警**")
                    config['volume_alert_enabled'] = st.checkbox(
                        "启用", value=config['volume_alert_enabled'], key=f"vol_en_{stock_code}"
                    )
                    if config['volume_alert_enabled']:
                        config['volume_threshold'] = st.slider(
                            "阈值(万手)", 1.0, 100.0, float(config['volume_threshold']/10000), 1.0, key=f"vol_{stock_code}"
                        ) * 10000
            
            # 显示行情
            if quote:
                alerts = check_alerts_multi(quote, config)
                all_alerts.extend(alerts)
                
                # 报警显示
                for alert in alerts:
                    if alert['level'] == 'error':
                        st.error(alert['message'])
                    elif alert['level'] == 'success':
                        st.success(alert['message'])
                    else:
                        st.warning(alert['message'])
                
                # 指标卡片
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    delta_color = "normal" if quote['change_pct'] >= 0 else "inverse"
                    st.metric("💰 最新价", f"¥{quote['price']:.2f}", f"{quote['change_pct']:.2f}%", delta_color=delta_color)
                with col2:
                    st.metric("📈 涨跌额", f"¥{quote['change_amount']:.2f}")
                with col3:
                    st.metric("📦 成交量", format_volume(quote['volume']))
                with col4:
                    st.metric("💵 成交额", format_amount(quote['amount']))
                with col5:
                    st.metric("⏰ 更新", quote['timestamp'].split(' ')[1])
            else:
                st.warning(f"⏳ {stock_name} 暂无数据（非交易时段）")
            
            # 走势图
            if hist_data is not None and not hist_data.empty:
                current_price = quote['price'] if quote else None
                fig = create_stock_chart(
                    hist_data, stock_name, stock_code,
                    config.get('support_line') if config.get('price_alert_enabled') else None,
                    config.get('resistance_line') if config.get('price_alert_enabled') else None,
                    current_price
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 新闻
            with st.expander(f"📰 相关新闻", expanded=False):
                news = get_stock_news(stock_code, stock_name)
                if news:
                    for n in news:
                        st.markdown(f"• [{n['title']}]({n['url']})")
                else:
                    st.info("暂无相关新闻")
    
    # 推送通知
    if all_alerts and pushplus_token and enable_push:
        content = "<h3>🚨 监控报警</h3><ul>"
        for a in all_alerts:
            content += f"<li>{a['message']}</li>"
        content += f"</ul><p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        
        alert_hash = hashlib.md5(content.encode()).hexdigest()
        if alert_hash not in st.session_state.alert_history:
            send_pushplus(pushplus_token, "🛡️ 监控报警", content)
            st.session_state.alert_history.append(alert_hash)
            if len(st.session_state.alert_history) > 100:
                st.session_state.alert_history = st.session_state.alert_history[-50:]
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6c757d;'>
        <p>📌 数据来源: 新浪财经 | 仅供参考,不构成投资建议</p>
        <p>🛡️ 逻辑指挥官 v3.0 专业版</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 自动刷新
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
