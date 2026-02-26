"""
逻辑指挥官 - 算力基建监控哨兵
A股实时监控仪表盘 - 锐捷网络 (301165)
使用新浪财经API，海外服务器可稳定访问
"""

import streamlit as st
import requests
import json
import re
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import time

# 页面配置
st.set_page_config(
    page_title="逻辑指挥官 - 算力基建监控哨兵",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
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
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 股票代码配置
STOCK_CODE = "301165"
STOCK_NAME = "锐捷网络"
# 新浪接口需要的代码格式：深圳sz，上海sh
SINA_CODE = f"sz{STOCK_CODE}"


def get_realtime_quote_sina():
    """从新浪财经获取实时行情"""
    try:
        url = f"http://hq.sinajs.cn/list={SINA_CODE}"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        # 解析返回数据
        # 格式: var hq_str_sz301165="锐捷网络,49.800,49.550,50.200,..."
        content = response.text
        match = re.search(r'"(.+)"', content)
        
        if not match:
            return None
        
        data = match.group(1).split(',')
        
        if len(data) < 32 or data[0] == '':
            return None
        
        # 新浪数据字段说明
        # 0:名称 1:今开 2:昨收 3:当前价 4:最高 5:最低 
        # 8:成交量(股) 9:成交额(元)
        current_price = float(data[3]) if data[3] else 0
        pre_close = float(data[2]) if data[2] else 0
        
        if current_price <= 0:
            return None
        
        change_amount = current_price - pre_close
        change_pct = (change_amount / pre_close * 100) if pre_close > 0 else 0
        
        # 计算换手率需要总股本，这里用成交量近似显示
        volume = float(data[8]) if data[8] else 0  # 成交量(股)
        amount = float(data[9]) if data[9] else 0  # 成交额(元)
        
        return {
            'name': data[0],
            'code': STOCK_CODE,
            'price': current_price,
            'change_pct': round(change_pct, 2),
            'change_amount': round(change_amount, 2),
            'volume': volume / 100,  # 转换为手
            'amount': amount,
            'high': float(data[4]) if data[4] else 0,
            'low': float(data[5]) if data[5] else 0,
            'open': float(data[1]) if data[1] else 0,
            'pre_close': pre_close,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        st.error(f"新浪接口错误: {str(e)}")
        return None


def get_historical_data_sina(days=90):
    """从新浪获取历史K线数据"""
    try:
        # 使用新浪K线接口
        url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_sh000001/KC_MarketDataService.getKLineData"
        params = {
            'symbol': SINA_CODE,
            'scale': '240',  # 日K
            'ma': 'no',
            'datalen': days
        }
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # 解析JSONP响应
        content = response.text
        match = re.search(r'\((\[.+\])\)', content)
        
        if not match:
            return None
        
        data = json.loads(match.group(1))
        
        if not data:
            return None
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        df['day'] = pd.to_datetime(df['day'])
        df = df.rename(columns={
            'day': '日期',
            'open': '开盘',
            'high': '最高',
            'low': '最低',
            'close': '收盘',
            'volume': '成交量'
        })
        
        # 转换数据类型
        for col in ['开盘', '最高', '最低', '收盘']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"获取历史数据错误: {str(e)}")
        return None


def get_historical_data_backup():
    """备用方案：使用腾讯接口获取历史数据"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # 腾讯日K线接口
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        params = {
            '_var': 'kline_dayqfq',
            'param': f'{SINA_CODE},day,{start_date.strftime("%Y-%m-%d")},{end_date.strftime("%Y-%m-%d")},640,qfq',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        content = response.text
        
        # 解析返回的JS变量
        match = re.search(r'kline_dayqfq=(\{.+\})', content)
        if not match:
            return None
        
        data = json.loads(match.group(1))
        
        # 提取K线数据
        kline_data = data.get('data', {}).get(SINA_CODE, {})
        day_data = kline_data.get('qfqday', kline_data.get('day', []))
        
        if not day_data:
            return None
        
        # 转换为DataFrame
        df = pd.DataFrame(day_data, columns=['日期', '开盘', '收盘', '最高', '最低', '成交量'])
        df['日期'] = pd.to_datetime(df['日期'])
        
        for col in ['开盘', '最高', '最低', '收盘']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        return df
    except Exception as e:
        return None


def create_price_chart(df, support_line, resistance_line, current_price):
    """创建价格走势图"""
    fig = go.Figure()
    
    # 收盘价折线
    fig.add_trace(go.Scatter(
        x=df['日期'],
        y=df['收盘'],
        mode='lines',
        name='收盘价',
        line=dict(color='#667eea', width=2),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    # 支撑位线
    fig.add_hline(
        y=support_line, 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"支撑位: ¥{support_line:.2f}",
        annotation_position="right"
    )
    
    # 压力位线
    fig.add_hline(
        y=resistance_line, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"压力位: ¥{resistance_line:.2f}",
        annotation_position="right"
    )
    
    # 当前价格线
    if current_price and current_price > 0:
        fig.add_hline(
            y=current_price, 
            line_dash="dot", 
            line_color="orange",
            annotation_text=f"当前价: ¥{current_price:.2f}",
            annotation_position="left"
        )
    
    fig.update_layout(
        title=dict(
            text=f'{STOCK_NAME} ({STOCK_CODE}) 历史走势',
            font=dict(size=20)
        ),
        xaxis_title='日期',
        yaxis_title='价格 (元)',
        template='plotly_white',
        height=500,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_volume_chart(df):
    """创建成交量图"""
    colors = ['red' if row['收盘'] >= row['开盘'] else 'green' 
              for _, row in df.iterrows()]
    
    fig = go.Figure(data=[go.Bar(
        x=df['日期'],
        y=df['成交量'],
        marker_color=colors,
        name='成交量'
    )])
    
    fig.update_layout(
        title='成交量走势',
        xaxis_title='日期',
        yaxis_title='成交量',
        template='plotly_white',
        height=250
    )
    
    return fig


def check_alerts(current_price, support_line, resistance_line):
    """检查报警条件"""
    alerts = []
    
    if not current_price or current_price <= 0:
        return alerts
    
    if current_price <= support_line:
        alerts.append({
            'type': 'support',
            'message': f'⚠️ 警告：股价 ¥{current_price:.2f} 已跌破或触及支撑位 ¥{support_line:.2f}！',
            'level': 'error'
        })
    
    if current_price >= resistance_line:
        alerts.append({
            'type': 'resistance',
            'message': f'🎉 提示：股价 ¥{current_price:.2f} 已突破或触及压力位 ¥{resistance_line:.2f}！',
            'level': 'success'
        })
    
    return alerts


def format_volume(vol):
    """格式化成交量显示"""
    if vol >= 10000:
        return f"{vol/10000:.2f}万手"
    else:
        return f"{vol:.0f}手"


def format_amount(amt):
    """格式化成交额显示"""
    if amt >= 100000000:
        return f"{amt/100000000:.2f}亿"
    elif amt >= 10000:
        return f"{amt/10000:.2f}万"
    else:
        return f"{amt:.2f}"


def main():
    # 页面标题
    st.markdown('<h1 class="main-header">🛡️ 逻辑指挥官 - 算力基建监控哨兵</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">实时监控 | {STOCK_NAME} ({STOCK_CODE})</p>', unsafe_allow_html=True)
    
    # 获取历史数据（用于设置滑动条范围）
    hist_data = get_historical_data_sina(90)
    if hist_data is None or hist_data.empty:
        hist_data = get_historical_data_backup()
    
    # 设置价格范围
    if hist_data is not None and not hist_data.empty:
        price_min = float(hist_data['最低'].min()) * 0.9
        price_max = float(hist_data['最高'].max()) * 1.1
        price_avg = float(hist_data['收盘'].mean())
    else:
        price_min = 30.0
        price_max = 80.0
        price_avg = 50.0
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 监控参数设置")
        st.markdown("---")
        
        # 支撑位滑动条
        support_line = st.slider(
            "🟢 支撑位报警线 (元)",
            min_value=float(price_min),
            max_value=float(price_max),
            value=float(price_avg * 0.95),
            step=0.1,
            help="当股价跌至或低于此价位时触发警报"
        )
        
        # 压力位滑动条
        resistance_line = st.slider(
            "🔴 压力位报警线 (元)",
            min_value=float(price_min),
            max_value=float(price_max),
            value=float(price_avg * 1.05),
            step=0.1,
            help="当股价涨至或高于此价位时触发提示"
        )
        
        st.markdown("---")
        st.info(f"支撑位: ¥{support_line:.2f}\n\n压力位: ¥{resistance_line:.2f}")
        
        # 刷新按钮
        st.markdown("---")
        if st.button("🔄 手动刷新数据", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.caption(f"⏰ 自动刷新: 每60秒")
        st.caption(f"📅 更新时间: {datetime.now().strftime('%H:%M:%S')}")
        st.caption("📡 数据源: 新浪财经")
    
    # 获取实时行情
    quote = get_realtime_quote_sina()
    
    # 主内容区域
    if quote is None or quote.get('price', 0) <= 0:
        st.warning("⏳ 当前处于非交易时段或正在获取数据，请稍后重试...")
        st.info("💡 A股交易时间: 周一至周五 9:30-11:30, 13:00-15:00 (法定节假日除外)")
        current_price = 0
    else:
        # 检查报警
        current_price = quote['price']
        alerts = check_alerts(current_price, support_line, resistance_line)
        
        # 显示报警信息
        if alerts:
            for alert in alerts:
                if alert['level'] == 'error':
                    st.error(alert['message'])
                elif alert['level'] == 'success':
                    st.success(alert['message'])
        
        # 实时行情指标
        st.markdown("### 📊 实时行情")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_color = "normal" if quote['change_pct'] >= 0 else "inverse"
            st.metric(
                label="💰 最新价",
                value=f"¥{quote['price']:.2f}",
                delta=f"{quote['change_pct']:.2f}%",
                delta_color=delta_color
            )
        
        with col2:
            st.metric(
                label="📈 涨跌额",
                value=f"¥{quote['change_amount']:.2f}",
                delta=f"昨收: ¥{quote['pre_close']:.2f}"
            )
        
        with col3:
            st.metric(
                label="📦 成交量",
                value=format_volume(quote['volume']),
            )
        
        with col4:
            st.metric(
                label="💵 成交额",
                value=format_amount(quote['amount']),
            )
        
        # 额外信息
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(label="📍 今开", value=f"¥{quote['open']:.2f}")
        
        with col6:
            st.metric(label="⬆️ 最高", value=f"¥{quote['high']:.2f}")
        
        with col7:
            st.metric(label="⬇️ 最低", value=f"¥{quote['low']:.2f}")
        
        with col8:
            st.metric(label="🕐 更新时间", value=quote['timestamp'].split(' ')[1])
        
        st.markdown("---")
    
    # 历史走势图
    st.markdown("### 📈 历史走势 (最近90天)")
    
    if hist_data is not None and not hist_data.empty:
        fig = create_price_chart(hist_data, support_line, resistance_line, current_price)
        st.plotly_chart(fig, use_container_width=True)
        
        # 成交量图
        vol_fig = create_volume_chart(hist_data)
        st.plotly_chart(vol_fig, use_container_width=True)
    else:
        st.warning("暂无历史数据，请稍后刷新")
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
        <p>📌 数据来源: 新浪财经 | 仅供参考,不构成投资建议</p>
        <p>🛡️ 逻辑指挥官 - 算力基建监控哨兵 v2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 自动刷新
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
