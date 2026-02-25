"""
逻辑指挥官 - 算力基建监控哨兵
A股实时监控仪表盘 - 锐捷网络 (301165)
"""

import streamlit as st
import akshare as ak
import plotly.graph_objects as go
import plotly.express as px
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
    .stock-code {
        font-size: 1rem;
        color: #17a2b8;
        text-align: center;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 股票代码
STOCK_CODE = "301165"
STOCK_NAME = "锐捷网络"


@st.cache_data(ttl=60)  # 缓存60秒
def get_realtime_quote():
    """获取实时行情数据"""
    try:
        # 使用 akshare 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df['代码'] == STOCK_CODE]
        
        if stock_data.empty:
            return None
        
        row = stock_data.iloc[0]
        return {
            'name': row.get('名称', STOCK_NAME),
            'code': STOCK_CODE,
            'price': float(row.get('最新价', 0)),
            'change_pct': float(row.get('涨跌幅', 0)),
            'change_amount': float(row.get('涨跌额', 0)),
            'turnover_rate': float(row.get('换手率', 0)),
            'volume': float(row.get('成交量', 0)),
            'amount': float(row.get('成交额', 0)),
            'high': float(row.get('最高', 0)),
            'low': float(row.get('最低', 0)),
            'open': float(row.get('今开', 0)),
            'pre_close': float(row.get('昨收', 0)),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        st.error(f"获取实时数据出错: {str(e)}")
        return None


@st.cache_data(ttl=300)  # 缓存5分钟
def get_historical_data(days=90):
    """获取历史行情数据"""
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        # 获取日K线数据
        df = ak.stock_zh_a_hist(
            symbol=STOCK_CODE, 
            period="daily", 
            start_date=start_date, 
            end_date=end_date, 
            adjust="qfq"  # 前复权
        )
        
        if df.empty:
            return None
            
        df['日期'] = pd.to_datetime(df['日期'])
        return df
    except Exception as e:
        st.error(f"获取历史数据出错: {str(e)}")
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
    if current_price > 0:
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
        yaxis_title='成交量 (手)',
        template='plotly_white',
        height=250
    )
    
    return fig


def check_alerts(current_price, support_line, resistance_line):
    """检查报警条件"""
    alerts = []
    
    if current_price <= 0:
        return alerts
    
    # 检查支撑位
    if current_price <= support_line:
        alerts.append({
            'type': 'support',
            'message': f'⚠️ 警告：股价 ¥{current_price:.2f} 已跌破或触及支撑位 ¥{support_line:.2f}！',
            'level': 'error'
        })
    
    # 检查压力位
    if current_price >= resistance_line:
        alerts.append({
            'type': 'resistance',
            'message': f'🎉 提示：股价 ¥{current_price:.2f} 已突破或触及压力位 ¥{resistance_line:.2f}！',
            'level': 'success'
        })
    
    return alerts


def format_volume(vol):
    """格式化成交量显示"""
    if vol >= 100000000:
        return f"{vol/100000000:.2f}亿"
    elif vol >= 10000:
        return f"{vol/10000:.2f}万"
    else:
        return f"{vol:.0f}"


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
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 监控参数设置")
        st.markdown("---")
        
        # 获取历史数据以确定滑动条范围
        hist_data = get_historical_data(90)
        if hist_data is not None and not hist_data.empty:
            price_min = float(hist_data['最低'].min()) * 0.9
            price_max = float(hist_data['最高'].max()) * 1.1
            price_avg = float(hist_data['收盘'].mean())
        else:
            price_min = 30.0
            price_max = 80.0
            price_avg = 50.0
        
        # 支撑位滑动条
        support_line = st.slider(
            "🟢 支撑位报警线 (元)",
            min_value=price_min,
            max_value=price_max,
            value=price_avg * 0.95,
            step=0.1,
            help="当股价跌至或低于此价位时触发警报"
        )
        
        # 压力位滑动条
        resistance_line = st.slider(
            "🔴 压力位报警线 (元)",
            min_value=price_min,
            max_value=price_max,
            value=price_avg * 1.05,
            step=0.1,
            help="当股价涨至或高于此价位时触发提示"
        )
        
        st.markdown("---")
        st.info(f"支撑位: ¥{support_line:.2f}\n\n压力位: ¥{resistance_line:.2f}")
        
        # 刷新按钮
        st.markdown("---")
        if st.button("🔄 手动刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # 显示刷新时间
        st.markdown("---")
        st.caption(f"⏰ 自动刷新: 每60秒")
        st.caption(f"📅 更新时间: {datetime.now().strftime('%H:%M:%S')}")
    
    # 获取实时行情
    quote = get_realtime_quote()
    
    # 主内容区域
    if quote is None or quote['price'] <= 0:
        st.warning("⏳ 当前处于非交易时段或正在获取数据，请稍后重试...")
        st.info("💡 A股交易时间: 周一至周五 9:30-11:30, 13:00-15:00 (法定节假日除外)")
        
        # 即使没有实时数据，也显示历史图表
        if hist_data is not None and not hist_data.empty:
            st.markdown("### 📈 历史走势 (最近90天)")
            fig = create_price_chart(hist_data, support_line, resistance_line, 0)
            st.plotly_chart(fig, use_container_width=True)
    else:
        # 检查报警
        alerts = check_alerts(quote['price'], support_line, resistance_line)
        
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
                label="🔄 换手率",
                value=f"{quote['turnover_rate']:.2f}%",
                delta=None
            )
        
        with col4:
            st.metric(
                label="📦 成交量",
                value=format_volume(quote['volume']),
                delta=f"成交额: {format_amount(quote['amount'])}"
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
            fig = create_price_chart(hist_data, support_line, resistance_line, quote['price'])
            st.plotly_chart(fig, use_container_width=True)
            
            # 成交量图
            vol_fig = create_volume_chart(hist_data)
            st.plotly_chart(vol_fig, use_container_width=True)
        else:
            st.warning("暂无历史数据")
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
        <p>📌 数据来源: 东方财富 | 仅供参考,不构成投资建议</p>
        <p>🛡️ 逻辑指挥官 - 算力基建监控哨兵 v1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 自动刷新逻辑
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
