import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import numpy as np
import random
import sys
from datetime import datetime
import akshare as ak

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入自定义模块
from news_analyzer import analyze_news
from stock_data import get_stock_data, get_stock_history_data, calculate_chip_distribution, calculate_support_resistance, calculate_technical_indicators
from stock_analyzer import analyze_stock
from dingtalk_bot import DingTalkBot
from config.config import DINGTALK_WEBHOOK, DINGTALK_SECRET

# 初始化钉钉机器人
dingtalk_bot = DingTalkBot(DINGTALK_WEBHOOK, DINGTALK_SECRET)

# 设置页面标题和配置
st.set_page_config(
    page_title="股票新闻分析系统", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# 股票新闻分析与投资建议系统\n 基于AI的股票分析工具"
    }
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #43A047;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #43A047;
        padding-bottom: 0.5rem;
    }
    .news-container {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .stock-info-card {
        background-color: #F1F8E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #43A047;
        margin-bottom: 1rem;
    }
    .analysis-result {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFB300;
        margin-top: 1rem;
    }
    .buy-recommendation {
        color: #2E7D32;
        font-weight: bold;
        font-size: 1.2rem;
        background-color: #C8E6C9;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .sell-recommendation {
        color: #C62828;
        font-weight: bold;
        font-size: 1.2rem;
        background-color: #FFCDD2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .hold-recommendation {
        color: #F57C00;
        font-weight: bold;
        font-size: 1.2rem;
        background-color: #FFE0B2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #ECEFF1;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
    .tech-analysis-card {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 1rem;
    }
    .support-level {
        color: #2E7D32;
        font-weight: bold;
    }
    .resistance-level {
        color: #C62828;
        font-weight: bold;
    }
    .chip-distribution-card {
        background-color: #E0F7FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #00BCD4;
        margin-bottom: 1rem;
    }
    .profit-ratio {
        color: #2E7D32;
        font-weight: bold;
    }
    .loss-ratio {
        color: #C62828;
        font-weight: bold;
    }
    .history-chart-container {
        background-color: #FAFAFA;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #EEEEEE;
        margin: 1rem 0;
    }
    .index-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 8px;
        margin-bottom: 8px;
        border-left: 3px solid #1E88E5;
    }
    .index-value {
        font-size: 16px;
        font-weight: bold;
    }
    .index-change-positive {
        color: #2E7D32;
        font-weight: bold;
    }
    .index-change-negative {
        color: #C62828;
        font-weight: bold;
    }
    .index-change-neutral {
        color: #757575;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">📊 股票新闻分析与投资建议系统</h1>', unsafe_allow_html=True)

# 侧边栏
st.sidebar.image("https://img.freepik.com/free-vector/stock-market-concept_23-2148604937.jpg?w=826&t=st=1709574372~exp=1709574972~hmac=e254d49c8c5d7a6e9f86f5e3d7d5f5c6a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", use_container_width=True)
st.sidebar.header("🛠️ 操作面板")
option = st.sidebar.selectbox(
    "选择操作",
    ["分析新闻数据", "手动输入新闻"],
    index=1  # 设置默认选项为 "手动输入新闻"
)

# 添加一些装饰性元素
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 市场概览")

# 替换随机生成的市场数据为实时数据
@st.cache_data(ttl=300)  # 缓存5分钟
def get_market_indices():
    """获取主要市场指数的实时数据"""
    try:
        # 创建结果字典
        indices = {}
        
        # 获取上证系列指数
        try:
            sh_indices = ak.stock_zh_index_spot_em(symbol="上证系列指数")
            # 提取上证指数数据
            sh_index = sh_indices[sh_indices['名称'] == '上证指数']
            if not sh_index.empty:
                indices["上证指数"] = {
                    "value": float(sh_index['最新价'].values[0]),
                    "change": float(sh_index['涨跌幅'].values[0])
                }
            
            # 提取科创50数据
            kc50_index = sh_indices[sh_indices['名称'] == '科创50']
            if not kc50_index.empty:
                indices["科创50"] = {
                    "value": float(kc50_index['最新价'].values[0]),
                    "change": float(kc50_index['涨跌幅'].values[0])
                }
        except Exception as e:
            print(f"获取上证系列指数出错: {e}")
        
        # 获取深证系列指数
        try:
            sz_indices = ak.stock_zh_index_spot_em(symbol="深证系列指数")
            # 提取深证成指数据
            sz_index = sz_indices[sz_indices['名称'] == '深证成指']
            if not sz_index.empty:
                indices["深证成指"] = {
                    "value": float(sz_index['最新价'].values[0]),
                    "change": float(sz_index['涨跌幅'].values[0])
                }
            
            # 提取创业板指数据
            cyb_index = sz_indices[sz_indices['名称'] == '创业板指']
            if not cyb_index.empty:
                indices["创业板指"] = {
                    "value": float(cyb_index['最新价'].values[0]),
                    "change": float(cyb_index['涨跌幅'].values[0])
                }
        except Exception as e:
            print(f"获取深证系列指数出错: {e}")
        
        # 检查是否所有指数都已获取，如果没有则提供默认值
        required_indices = ['上证指数', '深证成指', '创业板指', '科创50']
        default_values = {
            '上证指数': 3000,
            '深证成指': 10000,
            '创业板指': 2000,
            '科创50': 1000
        }
        
        for index_name in required_indices:
            if index_name not in indices:
                indices[index_name] = {
                    "value": default_values.get(index_name, 0),
                    "change": 0.0
                }
        
        return indices
    except Exception as e:
        print(f"获取市场指数数据出错: {e}")
        import traceback
        traceback.print_exc()
        
        # 提供默认值避免错误
        return {
            "上证指数": {"value": 3000, "change": 0},
            "深证成指": {"value": 10000, "change": 0},
            "创业板指": {"value": 2000, "change": 0},
            "科创50": {"value": 1000, "change": 0}
        }

# 获取市场指数数据
market_indices = get_market_indices()

# 添加刷新按钮
if st.sidebar.button("🔄 刷新市场数据"):
    # 使用st.cache_data的clear方法清除缓存，强制重新获取数据
    get_market_indices.clear()
    st.sidebar.success("✅ 数据已刷新")
    # 使用st.rerun替代已废弃的st.experimental_rerun
    st.rerun()

# 布局优化：添加指数显示的样式
st.sidebar.markdown("""
<style>
.index-card {
    background-color: #f8f9fa;
    border-radius: 5px;
    padding: 8px;
    margin-bottom: 8px;
    border-left: 3px solid #1E88E5;
}
.index-value {
    font-size: 16px;
    font-weight: bold;
}
.index-change-positive {
    color: #2E7D32;
    font-weight: bold;
}
.index-change-negative {
    color: #C62828;
    font-weight: bold;
}
.index-change-neutral {
    color: #757575;
}
</style>
""", unsafe_allow_html=True)

# 按两列显示市场指数
index_cols = st.sidebar.columns(2)
col_idx = 0

# 显示市场指数
for index, data in market_indices.items():
    value = data["value"]
    change = data["change"]
    
    # 确定涨跌样式
    change_class = "index-change-positive" if change > 0 else "index-change-negative" if change < 0 else "index-change-neutral"
    change_sign = "+" if change > 0 else ""
    
    # 使用HTML为每个指数创建卡片
    index_html = f"""
    <div class="index-card">
        <div>{index}</div>
        <div class="index-value">{value:.2f}</div>
        <div class="{change_class}">{change_sign}{change:.2f}%</div>
    </div>
    """
    
    # 在对应列显示指数卡片
    with index_cols[col_idx]:
        st.markdown(index_html, unsafe_allow_html=True)
    
    # 切换列
    col_idx = (col_idx + 1) % 2

# 添加最后更新时间
st.sidebar.markdown(f"<small>最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)

# 辅助函数：处理可能包含百分号的值
def format_value(value):
    if isinstance(value, str) and '%' in value:
        return value  # 保持字符串格式，包含百分号
    elif isinstance(value, float) and np.isnan(value):
        return '未知'  # 处理 NaN 值
    elif isinstance(value, (int, float)):
        return value  # 保持数值格式
    else:
        return str(value)  # 其他情况转为字符串

# 根据选择显示不同的内容
if option == "分析新闻数据":
    st.markdown('<h2 class="sub-header">📰 分析已爬取的新闻数据</h2>', unsafe_allow_html=True)
    
    # 获取新闻数据文件路径
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, '..', 'data', 'news_data.json')
    
    # 加载新闻数据
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # 显示新闻列表
        st.markdown(f"### 已加载 {len(news_data)} 条新闻")
        
        # 创建新闻选择器
        news_titles = [news.get('title', f"新闻 {i+1}") for i, news in enumerate(news_data)]
        selected_news_index = st.selectbox("选择要分析的新闻", range(len(news_titles)), format_func=lambda x: news_titles[x])
        
        # 显示选中的新闻内容
        selected_news = news_data[selected_news_index]
        st.markdown("### 新闻内容")
        st.markdown(f'<div class="news-container">{selected_news.get("content", "无内容")}</div>', unsafe_allow_html=True)
        
        # 分析按钮
        if st.button("🔍 分析该新闻"):
            with st.spinner("🔄 正在分析新闻并提取相关股票..."):
                news_text = selected_news.get('content', '')
                result = analyze_news(news_text)
                
                if not result["analyze"]:
                    st.warning(f"⚠️ 新闻重要性等级为{result['importance_level']}（{result['importance_category']}），不进行分析")
                elif result["stock_code"] == "无相关上市公司":
                    st.warning("⚠️ 该新闻没有相关的已上市公司")
                    # 显示行业信息
                    if result["industry_info"]:
                        st.info(f"📊 所属行业: {result['industry_info']['main_category']} - {result['industry_info']['sub_category']} (相关度: {result['industry_info']['relevance_score']})")
                else:
                    # 显示分析结果
                    importance_level = result["importance_level"]
                    importance_category = result["importance_category"]
                    industry_info = result["industry_info"]
                    stock_code = result["stock_code"]
                    
                    st.success(f"✅ 找到相关股票代码: {stock_code}")
                    st.info(f"📊 新闻重要性: {importance_level}级 ({importance_category})")
                    st.info(f"📊 所属行业: {industry_info['main_category']} - {industry_info['sub_category']} (相关度: {industry_info['relevance_score']})")
                    
                    with st.spinner(f"🔄 正在获取股票 {stock_code} 的数据..."):
                        stock_data = get_stock_data(stock_code)
                        
                        if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                            st.error(f"❌ 未能获取到股票 {stock_code} 的有效数据")
                        else:
                            # 显示股票基本信息
                            st.markdown(f'<h3 class="sub-header">🏢 股票信息: {stock_data["basic"]["name"]} ({stock_code})</h3>', unsafe_allow_html=True)
                            
                            # 创建两列布局
                            col1, col2 = st.columns(2)
                            
                            # 基本信息表格
                            with col1:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📋 基本信息**")
                                basic_df = pd.DataFrame({
                                    "项目": ["股票代码", "股票名称", "所属行业", "上市日期"],
                                    "数值": [
                                        stock_data['basic']['ts_code'],
                                        stock_data['basic']['name'],
                                        stock_data['basic']['industry'],
                                        stock_data['basic']['list_date']
                                    ]
                                })
                                st.table(basic_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 实时市场数据区域
                            st.markdown("### 📈 实时市场数据")
                            col2, col3, col4 = st.columns(3)
                            
                            # 价格信息合并到实时市场数据
                            with col2:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**💰 价格信息**")
                                # 处理百分号问题
                                pct_chg = stock_data['price']['pct_chg']
                                if isinstance(pct_chg, (int, float)):
                                    pct_chg_str = f"{pct_chg}%"
                                else:
                                    pct_chg_str = pct_chg
                                
                                price_df = pd.DataFrame({
                                    "项目": ["最新价", "涨跌额", "涨跌幅", "今日开盘", "最高价", "最低价"],
                                    "数值": [
                                        format_value(stock_data['price']['close']),
                                        format_value(stock_data['price']['change']),
                                        pct_chg_str,
                                        format_value(stock_data['price']['open']),
                                        format_value(stock_data['price']['high']),
                                        format_value(stock_data['price']['low'])
                                    ]
                                })
                                st.table(price_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**🔍 市场表现**")
                                market_df = pd.DataFrame({
                                    "项目": ["成交量", "成交额", "市盈率(TTM)", "市净率", "市值/资产净值", "流通值"],
                                    "数值": [
                                        format_value(stock_data['price'].get('成交量', '未知')),
                                        format_value(stock_data['price'].get('成交额', '未知')),
                                        format_value(stock_data['price']['pe']),
                                        format_value(stock_data['price']['pb']),
                                        format_value(stock_data['price']['total_mv']),
                                        format_value(stock_data['price']['circ_mv'])
                                    ]
                                })
                                st.table(market_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col4:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📅 52周表现**")
                                performance_df = pd.DataFrame({
                                    "项目": ["52周最高", "52周最低", "今年以来涨幅", "振幅", "昨收", "周转率"],
                                    "数值": [
                                        format_value(stock_data['price'].get('52周最高', '未知')),
                                        format_value(stock_data['price'].get('52周最低', '未知')),
                                        format_value(stock_data['price'].get('今年以来涨幅', '未知')),
                                        format_value(stock_data['price'].get('振幅', '未知')),
                                        format_value(stock_data['price'].get('昨收', '未知')),
                                        format_value(stock_data['price'].get('周转率', '未知'))
                                    ]
                                })
                                st.table(performance_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 获取历史数据并计算技术指标
                            with st.spinner("获取历史行情数据..."):
                                history_period = st.selectbox("选择历史数据时间跨度", ["90", "180", "365", "730", "1095"], index=2)
                                history_data = get_stock_history_data(stock_code, period=history_period)
                                
                                if not history_data.empty:
                                    # 规范化列名
                                    column_map = {
                                        'date': '日期', '日期': '日期',
                                        'open': '开盘', '开盘': '开盘',
                                        'high': '最高', '最高': '最高',
                                        'low': '最低', '最低': '最低',
                                        'close': '收盘', '收盘': '收盘',
                                        'volume': '成交量', '成交量': '成交量'
                                    }
                                    
                                    # 重命名列，确保标准化
                                    for old_col, new_col in column_map.items():
                                        if old_col in history_data.columns:
                                            history_data = history_data.rename(columns={old_col: new_col})
                                    
                                    # 确保日期列为datetime类型
                                    if '日期' in history_data.columns:
                                        history_data['日期'] = pd.to_datetime(history_data['日期'])
                                    
                                    # 计算技术指标
                                    history_data_with_indicators = calculate_technical_indicators(history_data)
                                    
                                    # 获取支撑位和压力位
                                    support_resistance = calculate_support_resistance(history_data)
                                    
                                    # 创建一个带有多个子图的图表
                                    fig = make_subplots(
                                        rows=4, 
                                        cols=1, 
                                        shared_xaxes=True, 
                                        vertical_spacing=0.05, 
                                        row_heights=[0.5, 0.15, 0.15, 0.15],
                                        subplot_titles=("K线图 (带支撑位和压力位)", "成交量", "MACD", "RSI")
                                    )
                                    
                                    # 添加K线图
                                    fig.add_trace(
                                        go.Candlestick(
                                            x=history_data['日期'],
                                            open=history_data['开盘'],
                                            high=history_data['最高'],
                                            low=history_data['最低'],
                                            close=history_data['收盘'],
                                            name="K线"
                                        ),
                                        row=1, col=1
                                    )
                                    
                                    # 添加支撑位水平线
                                    for i, support in enumerate(support_resistance["支撑位"]):
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=support,
                                            y1=support,
                                            line=dict(
                                                color="green",
                                                width=2,
                                                dash="dash",
                                            ),
                                            row=1, col=1
                                        )
                                        # 添加支撑位标签
                                        fig.add_annotation(
                                            x=history_data['日期'].iloc[-1],
                                            y=support,
                                            text=f"S{i+1}: {support}",
                                            showarrow=False,
                                            yshift=10,
                                            xshift=50,
                                            bgcolor="green",
                                            font=dict(color="white"),
                                            row=1, col=1
                                        )
                                    
                                    # 添加压力位水平线
                                    for i, resistance in enumerate(support_resistance["压力位"]):
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=resistance,
                                            y1=resistance,
                                            line=dict(
                                                color="red",
                                                width=2,
                                                dash="dash",
                                            ),
                                            row=1, col=1
                                        )
                                        # 添加压力位标签
                                        fig.add_annotation(
                                            x=history_data['日期'].iloc[-1],
                                            y=resistance,
                                            text=f"R{i+1}: {resistance}",
                                            showarrow=False,
                                            yshift=-10,
                                            xshift=50,
                                            bgcolor="red",
                                            font=dict(color="white"),
                                            row=1, col=1
                                        )
                                    
                                    # 添加移动平均线
                                    ma_periods = [5, 10, 20, 60]
                                    ma_colors = ['blue', 'orange', 'purple', 'brown']
                                    for i, period in enumerate(ma_periods):
                                        ma_name = f"MA{period}"
                                        history_data[ma_name] = history_data['收盘'].rolling(window=period).mean()
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data[ma_name],
                                                mode='lines',
                                                line=dict(
                                                    color=ma_colors[i],
                                                    width=1
                                                ),
                                                name=ma_name
                                            ),
                                            row=1, col=1
                                        )
                                    
                                    # 添加成交量柱状图
                                    colors = ['red' if row['收盘'] >= row['开盘'] else 'green' for _, row in history_data.iterrows()]
                                    fig.add_trace(
                                        go.Bar(
                                            x=history_data['日期'],
                                            y=history_data['成交量'],
                                            marker_color=colors,
                                            name="成交量"
                                        ),
                                        row=2, col=1
                                    )
                                    
                                    # 添加MACD图表
                                    if 'MACD' in history_data_with_indicators.columns:
                                        # MACD线
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['MACD'],
                                                mode='lines',
                                                line=dict(color='blue'),
                                                name="MACD"
                                            ),
                                            row=3, col=1
                                        )
                                        # 信号线
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['MACD_Signal'],
                                                mode='lines',
                                                line=dict(color='orange'),
                                                name="MACD信号线"
                                            ),
                                            row=3, col=1
                                        )
                                        # MACD柱状图
                                        histogram_colors = [
                                            'red' if val >= 0 else 'green' 
                                            for val in history_data_with_indicators['MACD_Histogram']
                                        ]
                                        fig.add_trace(
                                            go.Bar(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['MACD_Histogram'],
                                                marker_color=histogram_colors,
                                                name="MACD柱状图"
                                            ),
                                            row=3, col=1
                                        )
                                        # 添加零线
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=0,
                                            y1=0,
                                            line=dict(color="gray", width=1),
                                            row=3, col=1
                                        )
                                    
                                    # 添加RSI图表
                                    if 'RSI' in history_data_with_indicators.columns:
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['RSI'],
                                                mode='lines',
                                                line=dict(color='purple'),
                                                name="RSI(14)"
                                            ),
                                            row=4, col=1
                                        )
                                        # 添加超买线（70）
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=70,
                                            y1=70,
                                            line=dict(color="red", width=1, dash="dash"),
                                            row=4, col=1
                                        )
                                        # 添加超卖线（30）
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=30,
                                            y1=30,
                                            line=dict(color="green", width=1, dash="dash"),
                                            row=4, col=1
                                        )
                                        # 添加中间线（50）
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=50,
                                            y1=50,
                                            line=dict(color="gray", width=1, dash="dot"),
                                            row=4, col=1
                                        )
                                    
                                    # 更新图表布局
                                    fig.update_layout(
                                        title=f"{stock_data['basic']['name']} ({stock_code}) 技术分析图",
                                        xaxis_title="日期",
                                        height=800,  # 增加图表高度以适应多个子图
                                        xaxis_rangeslider_visible=False,
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        ),
                                        hovermode="x unified"
                                    )
                                    
                                    # 更新Y轴标题
                                    fig.update_yaxes(title_text="价格", row=1, col=1)
                                    fig.update_yaxes(title_text="成交量", row=2, col=1)
                                    fig.update_yaxes(title_text="MACD", row=3, col=1)
                                    fig.update_yaxes(title_text="RSI", row=4, col=1)
                                    
                                    # 显示图表
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # 显示技术指标分析结果
                                    st.markdown("### 📊 技术指标分析")
                                    tech_cols = st.columns(2)
                                    
                                    with tech_cols[0]:
                                        st.markdown('<div class="tech-analysis-card">', unsafe_allow_html=True)
                                        st.markdown("**MACD分析**")
                                        
                                        # 获取最新的MACD值
                                        last_macd = history_data_with_indicators['MACD'].iloc[-1]
                                        last_signal = history_data_with_indicators['MACD_Signal'].iloc[-1]
                                        last_hist = history_data_with_indicators['MACD_Histogram'].iloc[-1]
                                        
                                        # 前一个交易日的值
                                        prev_hist = history_data_with_indicators['MACD_Histogram'].iloc[-2]
                                        
                                        # 判断MACD金叉/死叉信号
                                        macd_signal = "中性"
                                        if last_macd > last_signal and history_data_with_indicators['MACD'].iloc[-2] <= history_data_with_indicators['MACD_Signal'].iloc[-2]:
                                            macd_signal = "<span style='color:red;font-weight:bold;'>金叉(买入信号)</span>"
                                        elif last_macd < last_signal and history_data_with_indicators['MACD'].iloc[-2] >= history_data_with_indicators['MACD_Signal'].iloc[-2]:
                                            macd_signal = "<span style='color:green;font-weight:bold;'>死叉(卖出信号)</span>"
                                        
                                        # 判断柱状图趋势
                                        hist_trend = "持平"
                                        if last_hist > prev_hist:
                                            hist_trend = "<span style='color:red;'>上升趋势增强</span>"
                                        elif last_hist < prev_hist:
                                            hist_trend = "<span style='color:green;'>下降趋势增强</span>"
                                        
                                        st.markdown(f"""
                                        **最新值:**
                                        - MACD值: {last_macd:.4f}
                                        - 信号线: {last_signal:.4f}
                                        - 柱状图: {last_hist:.4f}
                                        
                                        **信号:**
                                        - MACD信号: {macd_signal}
                                        - 柱状图趋势: {hist_trend}
                                        """, unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    with tech_cols[1]:
                                        st.markdown('<div class="tech-analysis-card">', unsafe_allow_html=True)
                                        st.markdown("**RSI分析**")
                                        
                                        # 获取最新的RSI值
                                        last_rsi = history_data_with_indicators['RSI'].iloc[-1]
                                        
                                        # 判断RSI超买/超卖状态
                                        rsi_signal = "中性区间"
                                        rsi_color = "black"
                                        if last_rsi >= 70:
                                            rsi_signal = "超买区域(可能回调)"
                                            rsi_color = "red"
                                        elif last_rsi <= 30:
                                            rsi_signal = "超卖区域(可能反弹)"
                                            rsi_color = "green"
                                        
                                        st.markdown(f"""
                                        **最新值:**
                                        - RSI(14): <span style='color:{rsi_color};font-weight:bold;'>{last_rsi:.2f}</span>
                                        
                                        **信号:**
                                        - RSI状态: <span style='color:{rsi_color};font-weight:bold;'>{rsi_signal}</span>
                                        
                                        **参考标准:**
                                        - RSI > 70: 超买区域，可能存在回调风险
                                        - RSI < 30: 超卖区域，可能存在反弹机会
                                        - 50左右: 多空平衡
                                        """, unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # KDJ指标分析
                                    st.markdown('<div class="tech-analysis-card">', unsafe_allow_html=True)
                                    st.markdown("**KDJ指标分析**")
                                    
                                    # 获取最新的KDJ值
                                    last_k = history_data_with_indicators['K'].iloc[-1]
                                    last_d = history_data_with_indicators['D'].iloc[-1]
                                    last_j = history_data_with_indicators['J'].iloc[-1]
                                    
                                    # 判断KDJ金叉/死叉信号
                                    kdj_signal = "中性"
                                    if last_k > last_d and history_data_with_indicators['K'].iloc[-2] <= history_data_with_indicators['D'].iloc[-2]:
                                        kdj_signal = "<span style='color:red;font-weight:bold;'>金叉(买入信号)</span>"
                                    elif last_k < last_d and history_data_with_indicators['K'].iloc[-2] >= history_data_with_indicators['D'].iloc[-2]:
                                        kdj_signal = "<span style='color:green;font-weight:bold;'>死叉(卖出信号)</span>"
                                    
                                    # 判断超买/超卖状态
                                    kdj_status = "中性区间"
                                    if last_j > 100:
                                        kdj_status = "<span style='color:red;font-weight:bold;'>严重超买</span>"
                                    elif last_j > 80:
                                        kdj_status = "<span style='color:orange;font-weight:bold;'>超买</span>"
                                    elif last_j < 0:
                                        kdj_status = "<span style='color:green;font-weight:bold;'>严重超卖</span>"
                                    elif last_j < 20:
                                        kdj_status = "<span style='color:lightgreen;font-weight:bold;'>超卖</span>"
                                    
                                    kdj_cols = st.columns(3)
                                    
                                    with kdj_cols[0]:
                                        st.metric("K值", f"{last_k:.2f}")
                                    
                                    with kdj_cols[1]:
                                        st.metric("D值", f"{last_d:.2f}")
                                    
                                    with kdj_cols[2]:
                                        st.metric("J值", f"{last_j:.2f}")
                                    
                                    st.markdown(f"""
                                    **信号:**
                                    - KDJ信号: {kdj_signal}
                                    - KDJ状态: {kdj_status}
                                    """, unsafe_allow_html=True)
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # 计算并显示支撑位和压力位
                                    # support_resistance = calculate_support_resistance(history_data)
                                    
                                    # 创建支撑位和压力位的数据框
                                    sr_cols = st.columns(2)
                                    with sr_cols[0]:
                                        st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                        st.markdown("**🔽 支撑位**")
                                        if support_resistance["支撑位"]:
                                            support_df = pd.DataFrame({
                                                "支撑位": [f"支撑位 {i+1}" for i in range(len(support_resistance["支撑位"]))],
                                                "价格": support_resistance["支撑位"]
                                            })
                                            st.table(support_df.set_index('支撑位'))
                                        else:
                                            st.info("未找到明显的支撑位")
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    with sr_cols[1]:
                                        st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                        st.markdown("**🔼 压力位**")
                                        if support_resistance["压力位"]:
                                            resistance_df = pd.DataFrame({
                                                "压力位": [f"压力位 {i+1}" for i in range(len(support_resistance["压力位"]))],
                                                "价格": support_resistance["压力位"]
                                            })
                                            st.table(resistance_df.set_index('压力位'))
                                        else:
                                            st.info("未找到明显的压力位")
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # 计算并显示筹码分布
                                    st.markdown("### 📊 筹码分布")
                                    chip_data = calculate_chip_distribution(history_data)
                                    
                                    if not chip_data.empty:
                                        # 创建筹码分布图
                                        fig = go.Figure()
                                        
                                        # 添加筹码密度分布
                                        fig.add_trace(
                                            go.Bar(
                                                x=chip_data['价格'],
                                                y=chip_data['筹码密度_归一化'],
                                                name="筹码密度",
                                                marker_color='rgba(58, 71, 80, 0.6)'
                                            )
                                        )
                                        
                                        # 添加当前价格线
                                        current_price = history_data['收盘'].iloc[-1]
                                        fig.add_vline(
                                            x=current_price,
                                            line_width=2,
                                            line_dash="dash",
                                            line_color="red",
                                            annotation_text="当前价格",
                                            annotation_position="top right"
                                        )
                                        
                                        # 添加支撑位和压力位的垂直线
                                        for support in support_resistance["支撑位"]:
                                            fig.add_vline(
                                                x=support,
                                                line_width=1,
                                                line_dash="dot",
                                                line_color="green",
                                                annotation_text=f"支撑位 {support}",
                                                annotation_position="bottom left"
                                            )
                                        
                                        for resistance in support_resistance["压力位"]:
                                            fig.add_vline(
                                                x=resistance,
                                                line_width=1,
                                                line_dash="dot",
                                                line_color="red",
                                                annotation_text=f"压力位 {resistance}",
                                                annotation_position="top right"
                                            )
                                        
                                        # 更新图表布局
                                        fig.update_layout(
                                            title=f"{stock_data['basic']['name']} ({stock_code}) 筹码分布",
                                            xaxis_title="价格",
                                            yaxis_title="筹码密度 (%)",
                                            height=400,
                                            bargap=0,
                                            bargroupgap=0
                                        )
                                        
                                        # 显示图表
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # 筹码集中区域分析
                                        st.markdown("#### 筹码集中区域分析")
                                        
                                        # 找出筹码密度最大的几个区域
                                        top_chip_areas = chip_data.sort_values('筹码密度_归一化', ascending=False).head(3)
                                        
                                        # 计算获利盘/套牢盘比例
                                        profit_ratio = chip_data[chip_data['价格'] <= current_price]['筹码密度_归一化'].sum()
                                        loss_ratio = chip_data[chip_data['价格'] > current_price]['筹码密度_归一化'].sum()
                                        
                                        # 创建三列布局显示筹码分析
                                        chip_cols = st.columns(3)
                                        
                                        with chip_cols[0]:
                                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                            st.metric("获利盘比例", f"{profit_ratio:.2f}%")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        with chip_cols[1]:
                                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                            st.metric("套牢盘比例", f"{loss_ratio:.2f}%")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        with chip_cols[2]:
                                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                            if len(top_chip_areas) > 0:
                                                highest_density_price = top_chip_areas.iloc[0]['价格']
                                                st.metric("筹码最集中价位", f"{highest_density_price:.2f}")
                                            else:
                                                st.metric("筹码最集中价位", "未知")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        # 筹码分布表格
                                        st.markdown("#### 筹码密度最高的价格区间")
                                        if not top_chip_areas.empty:
                                            top_areas_df = pd.DataFrame({
                                                "排名": [f"Top {i+1}" for i in range(len(top_chip_areas))],
                                                "价格": [f"{row['价格']:.2f}" for _, row in top_chip_areas.iterrows()],
                                                "筹码密度(%)": [f"{row['筹码密度_归一化']:.2f}%" for _, row in top_chip_areas.iterrows()]
                                            })
                                            st.table(top_areas_df.set_index('排名'))
                                    else:
                                        st.warning("无法计算筹码分布，请检查历史数据是否完整")
                                else:
                                    st.warning("未能获取到历史数据，无法展示K线图和技术分析")
                            
                            # 财务指标可视化
                            st.markdown("### 📊 关键财务指标")
                            
                            # 创建财务指标数据
                            financial_data = {
                                "指标": [
                                    "每股收益(EPS)", 
                                    "净资产收益率(ROE)", 
                                    "毛利率", 
                                    "净利率", 
                                    "资产负债率",
                                    "每股净资产",
                                    "营业收入增长率",
                                    "净利润增长率",
                                    "流动比率",
                                    "速动比率"
                                ],
                                "数值": [
                                    format_value(stock_data['financial_indicator'].get('eps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('roe', '未知')),
                                    format_value(stock_data['financial_indicator'].get('gross_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('debt_to_assets', '未知')),
                                    format_value(stock_data['financial_indicator'].get('bps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('revenue_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('profit_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('current_ratio', '未知')),
                                    format_value(stock_data['financial_indicator'].get('quick_ratio', '未知'))
                                ]
                            }
                            
                            # 检查是否为金融企业（存在金融特有指标）
                            if stock_data['financial_indicator'].get('capital_adequacy', '未知') != '未知' or \
                               stock_data['financial_indicator'].get('net_interest_margin', '未知') != '未知':
                                financial_data["指标"].extend(["资本充足率", "净息差"])
                                financial_data["数值"].extend([
                                    format_value(stock_data['financial_indicator'].get('capital_adequacy', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_interest_margin', '未知'))
                                ])
                            
                            # 使用表格直接显示财务指标
                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                            financial_df = pd.DataFrame(financial_data)
                            st.table(financial_df.set_index('指标'))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 分析结果
                            with st.spinner("🧠 正在分析股票投资价值..."):
                                analysis_result = analyze_stock(news_text, stock_data)
                                st.markdown('<h3 class="sub-header">💡 投资分析结果</h3>', unsafe_allow_html=True)
                                st.markdown(f'<div class="analysis-result">{analysis_result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                                
                                # 提取投资建议关键词
                                if "建议买入" in analysis_result:
                                    st.markdown('<div class="buy-recommendation">✅ 建议买入</div>', unsafe_allow_html=True)
                                elif "不建议买入" in analysis_result:
                                    st.markdown('<div class="sell-recommendation">❌ 不建议买入</div>', unsafe_allow_html=True)
                                elif "建议观望" in analysis_result:
                                    st.markdown('<div class="hold-recommendation">⚠️ 建议观望</div>', unsafe_allow_html=True)
                                
                                # 发送到钉钉机器人
                                title = f"股票分析报告 - {stock_data['basic']['name']}({stock_code})"
                                # 先处理换行符
                                formatted_analysis = analysis_result.replace('\n', '\n\n')
                                content = f'''### {title}
                                
#### 新闻内容
{news_text[:200]}...

#### 基本信息
- 股票代码：{stock_code}
- 股票名称：{stock_data['basic']['name']}
- 所属行业：{stock_data['basic'].get('industry', '未知')}
- 上市日期：{stock_data['basic'].get('list_date', '未知')}

#### 价格信息
- 最新价格：{stock_data['price'].get('close', '未知')}
- 涨跌额：{stock_data['price'].get('change', '未知')}
- 涨跌幅：{stock_data['price'].get('pct_chg', '未知')}%
- 今日开盘：{stock_data['price'].get('open', '未知')}
- 最高价：{stock_data['price'].get('high', '未知')}
- 最低价：{stock_data['price'].get('low', '未知')}
- 市盈率(TTM)：{stock_data['price'].get('pe', '未知')}
- 市净率：{stock_data['price'].get('pb', '未知')}

#### 市场表现
- 成交量：{stock_data['price'].get('成交量', '未知')}
- 成交额：{stock_data['price'].get('成交额', '未知')}
- 市值：{stock_data['price'].get('total_mv', '未知')}
- 52周最高：{stock_data['price'].get('52周最高', '未知')}
- 52周最低：{stock_data['price'].get('52周最低', '未知')}
- 今年以来涨幅：{stock_data['price'].get('今年以来涨幅', '未知')}

#### 投资分析结果
{formatted_analysis}
'''
                                # 发送消息
                                if dingtalk_bot.send_markdown(title, content):
                                    st.success("✅ 分析报告已发送到钉钉群")
                                else:
                                    st.error("❌ 发送到钉钉群失败，请检查配置")
    except Exception as e:
        st.error(f"加载新闻数据出错: {e}")
        import traceback
        st.error(traceback.format_exc())

else:  # 手动输入新闻
    st.markdown('<h2 class="sub-header">✍️ 手动输入新闻进行分析</h2>', unsafe_allow_html=True)
    
    # 文本输入区
    news_text = st.text_area("请输入新闻内容", height=200)
    
    # 分析按钮
    if st.button("🔍 分析新闻"):
        if not news_text:
            st.warning("⚠️ 请输入新闻内容")
        else:
            with st.spinner("🔄 正在分析新闻并提取相关股票..."):
                result = analyze_news(news_text)
                
                if not result["analyze"]:
                    st.warning(f"⚠️ 新闻重要性等级为{result['importance_level']}（{result['importance_category']}），不进行分析")
                elif result["stock_code"] == "无相关上市公司":
                    st.warning("⚠️ 该新闻没有相关的已上市公司")
                    # 显示行业信息
                    if result["industry_info"]:
                        st.info(f"📊 所属行业: {result['industry_info']['main_category']} - {result['industry_info']['sub_category']} (相关度: {result['industry_info']['relevance_score']})")
                else:
                    # 显示分析结果
                    importance_level = result["importance_level"]
                    importance_category = result["importance_category"]
                    industry_info = result["industry_info"]
                    stock_code = result["stock_code"]
                    
                    st.success(f"✅ 找到相关股票代码: {stock_code}")
                    st.info(f"📊 新闻重要性: {importance_level}级 ({importance_category})")
                    st.info(f"📊 所属行业: {industry_info['main_category']} - {industry_info['sub_category']} (相关度: {industry_info['relevance_score']})")
                    
                    with st.spinner(f"🔄 正在获取股票 {stock_code} 的数据..."):
                        stock_data = get_stock_data(stock_code)
                        
                        if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                            st.error(f"❌ 未能获取到股票 {stock_code} 的有效数据")
                        else:
                            # 显示股票基本信息
                            st.markdown(f'<h3 class="sub-header">🏢 股票信息: {stock_data["basic"]["name"]} ({stock_code})</h3>', unsafe_allow_html=True)
                            
                            # 创建两列布局
                            col1, col2 = st.columns(2)
                            
                            # 基本信息表格
                            with col1:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📋 基本信息**")
                                basic_df = pd.DataFrame({
                                    "项目": ["股票代码", "股票名称", "所属行业", "上市日期"],
                                    "数值": [
                                        stock_data['basic']['ts_code'],
                                        stock_data['basic']['name'],
                                        stock_data['basic']['industry'],
                                        stock_data['basic']['list_date']
                                    ]
                                })
                                st.table(basic_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 实时市场数据区域
                            st.markdown("### 📈 实时市场数据")
                            col2, col3, col4 = st.columns(3)
                            
                            # 价格信息合并到实时市场数据
                            with col2:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**💰 价格信息**")
                                # 处理百分号问题
                                pct_chg = stock_data['price']['pct_chg']
                                if isinstance(pct_chg, (int, float)):
                                    pct_chg_str = f"{pct_chg}%"
                                else:
                                    pct_chg_str = pct_chg
                                
                                price_df = pd.DataFrame({
                                    "项目": ["最新价", "涨跌额", "涨跌幅", "今日开盘", "最高价", "最低价"],
                                    "数值": [
                                        format_value(stock_data['price']['close']),
                                        format_value(stock_data['price']['change']),
                                        pct_chg_str,
                                        format_value(stock_data['price']['open']),
                                        format_value(stock_data['price']['high']),
                                        format_value(stock_data['price']['low'])
                                    ]
                                })
                                st.table(price_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**🔍 市场表现**")
                                market_df = pd.DataFrame({
                                    "项目": ["成交量", "成交额", "市盈率(TTM)", "市净率", "市值/资产净值", "流通值"],
                                    "数值": [
                                        format_value(stock_data['price'].get('成交量', '未知')),
                                        format_value(stock_data['price'].get('成交额', '未知')),
                                        format_value(stock_data['price']['pe']),
                                        format_value(stock_data['price']['pb']),
                                        format_value(stock_data['price']['total_mv']),
                                        format_value(stock_data['price']['circ_mv'])
                                    ]
                                })
                                st.table(market_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col4:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📅 52周表现**")
                                performance_df = pd.DataFrame({
                                    "项目": ["52周最高", "52周最低", "今年以来涨幅", "振幅", "昨收", "周转率"],
                                    "数值": [
                                        format_value(stock_data['price'].get('52周最高', '未知')),
                                        format_value(stock_data['price'].get('52周最低', '未知')),
                                        format_value(stock_data['price'].get('今年以来涨幅', '未知')),
                                        format_value(stock_data['price'].get('振幅', '未知')),
                                        format_value(stock_data['price'].get('昨收', '未知')),
                                        format_value(stock_data['price'].get('周转率', '未知'))
                                    ]
                                })
                                st.table(performance_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 获取历史数据并计算技术指标
                            with st.spinner("获取历史行情数据..."):
                                history_period = st.selectbox("选择历史数据时间跨度", ["90", "180", "365", "730", "1095"], index=2)
                                history_data = get_stock_history_data(stock_code, period=history_period)
                                
                                if not history_data.empty:
                                    # 规范化列名
                                    column_map = {
                                        'date': '日期', '日期': '日期',
                                        'open': '开盘', '开盘': '开盘',
                                        'high': '最高', '最高': '最高',
                                        'low': '最低', '最低': '最低',
                                        'close': '收盘', '收盘': '收盘',
                                        'volume': '成交量', '成交量': '成交量'
                                    }
                                    
                                    # 重命名列，确保标准化
                                    for old_col, new_col in column_map.items():
                                        if old_col in history_data.columns:
                                            history_data = history_data.rename(columns={old_col: new_col})
                                    
                                    # 确保日期列为datetime类型
                                    if '日期' in history_data.columns:
                                        history_data['日期'] = pd.to_datetime(history_data['日期'])
                                    
                                    # 计算技术指标
                                    history_data_with_indicators = calculate_technical_indicators(history_data)
                                    
                                    # 获取支撑位和压力位
                                    support_resistance = calculate_support_resistance(history_data)
                                    
                                    # 创建一个带有多个子图的图表
                                    fig = make_subplots(
                                        rows=4, 
                                        cols=1, 
                                        shared_xaxes=True, 
                                        vertical_spacing=0.05, 
                                        row_heights=[0.5, 0.15, 0.15, 0.15],
                                        subplot_titles=("K线图 (带支撑位和压力位)", "成交量", "MACD", "RSI")
                                    )
                                    
                                    # 添加K线图
                                    fig.add_trace(
                                        go.Candlestick(
                                            x=history_data['日期'],
                                            open=history_data['开盘'],
                                            high=history_data['最高'],
                                            low=history_data['最低'],
                                            close=history_data['收盘'],
                                            name="K线"
                                        ),
                                        row=1, col=1
                                    )
                                    
                                    # 添加支撑位水平线
                                    for i, support in enumerate(support_resistance["支撑位"]):
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=support,
                                            y1=support,
                                            line=dict(
                                                color="green",
                                                width=2,
                                                dash="dash",
                                            ),
                                            row=1, col=1
                                        )
                                        # 添加支撑位标签
                                        fig.add_annotation(
                                            x=history_data['日期'].iloc[-1],
                                            y=support,
                                            text=f"S{i+1}: {support}",
                                            showarrow=False,
                                            yshift=10,
                                            xshift=50,
                                            bgcolor="green",
                                            font=dict(color="white"),
                                            row=1, col=1
                                        )
                                    
                                    # 添加压力位水平线
                                    for i, resistance in enumerate(support_resistance["压力位"]):
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=resistance,
                                            y1=resistance,
                                            line=dict(
                                                color="red",
                                                width=2,
                                                dash="dash",
                                            ),
                                            row=1, col=1
                                        )
                                        # 添加压力位标签
                                        fig.add_annotation(
                                            x=history_data['日期'].iloc[-1],
                                            y=resistance,
                                            text=f"R{i+1}: {resistance}",
                                            showarrow=False,
                                            yshift=-10,
                                            xshift=50,
                                            bgcolor="red",
                                            font=dict(color="white"),
                                            row=1, col=1
                                        )
                                    
                                    # 添加移动平均线
                                    ma_periods = [5, 10, 20, 60]
                                    ma_colors = ['blue', 'orange', 'purple', 'brown']
                                    for i, period in enumerate(ma_periods):
                                        ma_name = f"MA{period}"
                                        history_data[ma_name] = history_data['收盘'].rolling(window=period).mean()
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data[ma_name],
                                                mode='lines',
                                                line=dict(
                                                    color=ma_colors[i],
                                                    width=1
                                                ),
                                                name=ma_name
                                            ),
                                            row=1, col=1
                                        )
                                    
                                    # 添加成交量柱状图
                                    colors = ['red' if row['收盘'] >= row['开盘'] else 'green' for _, row in history_data.iterrows()]
                                    fig.add_trace(
                                        go.Bar(
                                            x=history_data['日期'],
                                            y=history_data['成交量'],
                                            marker_color=colors,
                                            name="成交量"
                                        ),
                                        row=2, col=1
                                    )
                                    
                                    # 添加MACD图表
                                    if 'MACD' in history_data_with_indicators.columns:
                                        # MACD线
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['MACD'],
                                                mode='lines',
                                                line=dict(color='blue'),
                                                name="MACD"
                                            ),
                                            row=3, col=1
                                        )
                                        # 信号线
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['MACD_Signal'],
                                                mode='lines',
                                                line=dict(color='orange'),
                                                name="MACD信号线"
                                            ),
                                            row=3, col=1
                                        )
                                        # MACD柱状图
                                        histogram_colors = [
                                            'red' if val >= 0 else 'green' 
                                            for val in history_data_with_indicators['MACD_Histogram']
                                        ]
                                        fig.add_trace(
                                            go.Bar(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['MACD_Histogram'],
                                                marker_color=histogram_colors,
                                                name="MACD柱状图"
                                            ),
                                            row=3, col=1
                                        )
                                        # 添加零线
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=0,
                                            y1=0,
                                            line=dict(color="gray", width=1),
                                            row=3, col=1
                                        )
                                    
                                    # 添加RSI图表
                                    if 'RSI' in history_data_with_indicators.columns:
                                        fig.add_trace(
                                            go.Scatter(
                                                x=history_data['日期'],
                                                y=history_data_with_indicators['RSI'],
                                                mode='lines',
                                                line=dict(color='purple'),
                                                name="RSI(14)"
                                            ),
                                            row=4, col=1
                                        )
                                        # 添加超买线（70）
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=70,
                                            y1=70,
                                            line=dict(color="red", width=1, dash="dash"),
                                            row=4, col=1
                                        )
                                        # 添加超卖线（30）
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=30,
                                            y1=30,
                                            line=dict(color="green", width=1, dash="dash"),
                                            row=4, col=1
                                        )
                                        # 添加中间线（50）
                                        fig.add_shape(
                                            type="line",
                                            x0=history_data['日期'].iloc[0],
                                            x1=history_data['日期'].iloc[-1],
                                            y0=50,
                                            y1=50,
                                            line=dict(color="gray", width=1, dash="dot"),
                                            row=4, col=1
                                        )
                                    
                                    # 更新图表布局
                                    fig.update_layout(
                                        title=f"{stock_data['basic']['name']} ({stock_code}) 技术分析图",
                                        xaxis_title="日期",
                                        height=800,  # 增加图表高度以适应多个子图
                                        xaxis_rangeslider_visible=False,
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        ),
                                        hovermode="x unified"
                                    )
                                    
                                    # 更新Y轴标题
                                    fig.update_yaxes(title_text="价格", row=1, col=1)
                                    fig.update_yaxes(title_text="成交量", row=2, col=1)
                                    fig.update_yaxes(title_text="MACD", row=3, col=1)
                                    fig.update_yaxes(title_text="RSI", row=4, col=1)
                                    
                                    # 显示图表
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # 显示技术指标分析结果
                                    st.markdown("### 📊 技术指标分析")
                                    tech_cols = st.columns(2)
                                    
                                    with tech_cols[0]:
                                        st.markdown('<div class="tech-analysis-card">', unsafe_allow_html=True)
                                        st.markdown("**MACD分析**")
                                        
                                        # 获取最新的MACD值
                                        last_macd = history_data_with_indicators['MACD'].iloc[-1]
                                        last_signal = history_data_with_indicators['MACD_Signal'].iloc[-1]
                                        last_hist = history_data_with_indicators['MACD_Histogram'].iloc[-1]
                                        
                                        # 前一个交易日的值
                                        prev_hist = history_data_with_indicators['MACD_Histogram'].iloc[-2]
                                        
                                        # 判断MACD金叉/死叉信号
                                        macd_signal = "中性"
                                        if last_macd > last_signal and history_data_with_indicators['MACD'].iloc[-2] <= history_data_with_indicators['MACD_Signal'].iloc[-2]:
                                            macd_signal = "<span style='color:red;font-weight:bold;'>金叉(买入信号)</span>"
                                        elif last_macd < last_signal and history_data_with_indicators['MACD'].iloc[-2] >= history_data_with_indicators['MACD_Signal'].iloc[-2]:
                                            macd_signal = "<span style='color:green;font-weight:bold;'>死叉(卖出信号)</span>"
                                        
                                        # 判断柱状图趋势
                                        hist_trend = "持平"
                                        if last_hist > prev_hist:
                                            hist_trend = "<span style='color:red;'>上升趋势增强</span>"
                                        elif last_hist < prev_hist:
                                            hist_trend = "<span style='color:green;'>下降趋势增强</span>"
                                        
                                        st.markdown(f"""
                                        **最新值:**
                                        - MACD值: {last_macd:.4f}
                                        - 信号线: {last_signal:.4f}
                                        - 柱状图: {last_hist:.4f}
                                        
                                        **信号:**
                                        - MACD信号: {macd_signal}
                                        - 柱状图趋势: {hist_trend}
                                        """, unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    with tech_cols[1]:
                                        st.markdown('<div class="tech-analysis-card">', unsafe_allow_html=True)
                                        st.markdown("**RSI分析**")
                                        
                                        # 获取最新的RSI值
                                        last_rsi = history_data_with_indicators['RSI'].iloc[-1]
                                        
                                        # 判断RSI超买/超卖状态
                                        rsi_signal = "中性区间"
                                        rsi_color = "black"
                                        if last_rsi >= 70:
                                            rsi_signal = "超买区域(可能回调)"
                                            rsi_color = "red"
                                        elif last_rsi <= 30:
                                            rsi_signal = "超卖区域(可能反弹)"
                                            rsi_color = "green"
                                        
                                        st.markdown(f"""
                                        **最新值:**
                                        - RSI(14): <span style='color:{rsi_color};font-weight:bold;'>{last_rsi:.2f}</span>
                                        
                                        **信号:**
                                        - RSI状态: <span style='color:{rsi_color};font-weight:bold;'>{rsi_signal}</span>
                                        
                                        **参考标准:**
                                        - RSI > 70: 超买区域，可能存在回调风险
                                        - RSI < 30: 超卖区域，可能存在反弹机会
                                        - 50左右: 多空平衡
                                        """, unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # KDJ指标分析
                                    st.markdown('<div class="tech-analysis-card">', unsafe_allow_html=True)
                                    st.markdown("**KDJ指标分析**")
                                    
                                    # 获取最新的KDJ值
                                    last_k = history_data_with_indicators['K'].iloc[-1]
                                    last_d = history_data_with_indicators['D'].iloc[-1]
                                    last_j = history_data_with_indicators['J'].iloc[-1]
                                    
                                    # 判断KDJ金叉/死叉信号
                                    kdj_signal = "中性"
                                    if last_k > last_d and history_data_with_indicators['K'].iloc[-2] <= history_data_with_indicators['D'].iloc[-2]:
                                        kdj_signal = "<span style='color:red;font-weight:bold;'>金叉(买入信号)</span>"
                                    elif last_k < last_d and history_data_with_indicators['K'].iloc[-2] >= history_data_with_indicators['D'].iloc[-2]:
                                        kdj_signal = "<span style='color:green;font-weight:bold;'>死叉(卖出信号)</span>"
                                    
                                    # 判断超买/超卖状态
                                    kdj_status = "中性区间"
                                    if last_j > 100:
                                        kdj_status = "<span style='color:red;font-weight:bold;'>严重超买</span>"
                                    elif last_j > 80:
                                        kdj_status = "<span style='color:orange;font-weight:bold;'>超买</span>"
                                    elif last_j < 0:
                                        kdj_status = "<span style='color:green;font-weight:bold;'>严重超卖</span>"
                                    elif last_j < 20:
                                        kdj_status = "<span style='color:lightgreen;font-weight:bold;'>超卖</span>"
                                    
                                    kdj_cols = st.columns(3)
                                    
                                    with kdj_cols[0]:
                                        st.metric("K值", f"{last_k:.2f}")
                                    
                                    with kdj_cols[1]:
                                        st.metric("D值", f"{last_d:.2f}")
                                    
                                    with kdj_cols[2]:
                                        st.metric("J值", f"{last_j:.2f}")
                                    
                                    st.markdown(f"""
                                    **信号:**
                                    - KDJ信号: {kdj_signal}
                                    - KDJ状态: {kdj_status}
                                    """, unsafe_allow_html=True)
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # 计算并显示支撑位和压力位
                                    # support_resistance = calculate_support_resistance(history_data)
                                    
                                    # 创建支撑位和压力位的数据框
                                    sr_cols = st.columns(2)
                                    with sr_cols[0]:
                                        st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                        st.markdown("**🔽 支撑位**")
                                        if support_resistance["支撑位"]:
                                            support_df = pd.DataFrame({
                                                "支撑位": [f"支撑位 {i+1}" for i in range(len(support_resistance["支撑位"]))],
                                                "价格": support_resistance["支撑位"]
                                            })
                                            st.table(support_df.set_index('支撑位'))
                                        else:
                                            st.info("未找到明显的支撑位")
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    with sr_cols[1]:
                                        st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                        st.markdown("**🔼 压力位**")
                                        if support_resistance["压力位"]:
                                            resistance_df = pd.DataFrame({
                                                "压力位": [f"压力位 {i+1}" for i in range(len(support_resistance["压力位"]))],
                                                "价格": support_resistance["压力位"]
                                            })
                                            st.table(resistance_df.set_index('压力位'))
                                        else:
                                            st.info("未找到明显的压力位")
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # 计算并显示筹码分布
                                    st.markdown("### 📊 筹码分布")
                                    chip_data = calculate_chip_distribution(history_data)
                                    
                                    if not chip_data.empty:
                                        # 创建筹码分布图
                                        fig = go.Figure()
                                        
                                        # 添加筹码密度分布
                                        fig.add_trace(
                                            go.Bar(
                                                x=chip_data['价格'],
                                                y=chip_data['筹码密度_归一化'],
                                                name="筹码密度",
                                                marker_color='rgba(58, 71, 80, 0.6)'
                                            )
                                        )
                                        
                                        # 添加当前价格线
                                        current_price = history_data['收盘'].iloc[-1]
                                        fig.add_vline(
                                            x=current_price,
                                            line_width=2,
                                            line_dash="dash",
                                            line_color="red",
                                            annotation_text="当前价格",
                                            annotation_position="top right"
                                        )
                                        
                                        # 添加支撑位和压力位的垂直线
                                        for support in support_resistance["支撑位"]:
                                            fig.add_vline(
                                                x=support,
                                                line_width=1,
                                                line_dash="dot",
                                                line_color="green",
                                                annotation_text=f"支撑位 {support}",
                                                annotation_position="bottom left"
                                            )
                                        
                                        for resistance in support_resistance["压力位"]:
                                            fig.add_vline(
                                                x=resistance,
                                                line_width=1,
                                                line_dash="dot",
                                                line_color="red",
                                                annotation_text=f"压力位 {resistance}",
                                                annotation_position="top right"
                                            )
                                        
                                        # 更新图表布局
                                        fig.update_layout(
                                            title=f"{stock_data['basic']['name']} ({stock_code}) 筹码分布",
                                            xaxis_title="价格",
                                            yaxis_title="筹码密度 (%)",
                                            height=400,
                                            bargap=0,
                                            bargroupgap=0
                                        )
                                        
                                        # 显示图表
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # 筹码集中区域分析
                                        st.markdown("#### 筹码集中区域分析")
                                        
                                        # 找出筹码密度最大的几个区域
                                        top_chip_areas = chip_data.sort_values('筹码密度_归一化', ascending=False).head(3)
                                        
                                        # 计算获利盘/套牢盘比例
                                        profit_ratio = chip_data[chip_data['价格'] <= current_price]['筹码密度_归一化'].sum()
                                        loss_ratio = chip_data[chip_data['价格'] > current_price]['筹码密度_归一化'].sum()
                                        
                                        # 创建三列布局显示筹码分析
                                        chip_cols = st.columns(3)
                                        
                                        with chip_cols[0]:
                                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                            st.metric("获利盘比例", f"{profit_ratio:.2f}%")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        with chip_cols[1]:
                                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                            st.metric("套牢盘比例", f"{loss_ratio:.2f}%")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        with chip_cols[2]:
                                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                            if len(top_chip_areas) > 0:
                                                highest_density_price = top_chip_areas.iloc[0]['价格']
                                                st.metric("筹码最集中价位", f"{highest_density_price:.2f}")
                                            else:
                                                st.metric("筹码最集中价位", "未知")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        # 筹码分布表格
                                        st.markdown("#### 筹码密度最高的价格区间")
                                        if not top_chip_areas.empty:
                                            top_areas_df = pd.DataFrame({
                                                "排名": [f"Top {i+1}" for i in range(len(top_chip_areas))],
                                                "价格": [f"{row['价格']:.2f}" for _, row in top_chip_areas.iterrows()],
                                                "筹码密度(%)": [f"{row['筹码密度_归一化']:.2f}%" for _, row in top_chip_areas.iterrows()]
                                            })
                                            st.table(top_areas_df.set_index('排名'))
                                    else:
                                        st.warning("无法计算筹码分布，请检查历史数据是否完整")
                                else:
                                    st.warning("未能获取到历史数据，无法展示K线图和技术分析")
                            
                            # 财务指标可视化
                            st.markdown("### 📊 关键财务指标")
                            
                            # 创建财务指标数据
                            financial_data = {
                                "指标": [
                                    "每股收益(EPS)", 
                                    "净资产收益率(ROE)", 
                                    "毛利率", 
                                    "净利率", 
                                    "资产负债率",
                                    "每股净资产",
                                    "营业收入增长率",
                                    "净利润增长率",
                                    "流动比率",
                                    "速动比率"
                                ],
                                "数值": [
                                    format_value(stock_data['financial_indicator'].get('eps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('roe', '未知')),
                                    format_value(stock_data['financial_indicator'].get('gross_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('debt_to_assets', '未知')),
                                    format_value(stock_data['financial_indicator'].get('bps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('revenue_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('profit_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('current_ratio', '未知')),
                                    format_value(stock_data['financial_indicator'].get('quick_ratio', '未知'))
                                ]
                            }
                            
                            # 检查是否为金融企业（存在金融特有指标）
                            if stock_data['financial_indicator'].get('capital_adequacy', '未知') != '未知' or \
                               stock_data['financial_indicator'].get('net_interest_margin', '未知') != '未知':
                                financial_data["指标"].extend(["资本充足率", "净息差"])
                                financial_data["数值"].extend([
                                    format_value(stock_data['financial_indicator'].get('capital_adequacy', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_interest_margin', '未知'))
                                ])
                            
                            # 使用表格直接显示财务指标
                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                            financial_df = pd.DataFrame(financial_data)
                            st.table(financial_df.set_index('指标'))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 分析结果
                            with st.spinner("🧠 正在分析股票投资价值..."):
                                analysis_result = analyze_stock(news_text, stock_data)
                                st.markdown('<h3 class="sub-header">💡 投资分析结果</h3>', unsafe_allow_html=True)
                                st.markdown(f'<div class="analysis-result">{analysis_result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                                
                                # 提取投资建议关键词
                                if "建议买入" in analysis_result:
                                    st.markdown('<div class="buy-recommendation">✅ 建议买入</div>', unsafe_allow_html=True)
                                elif "不建议买入" in analysis_result:
                                    st.markdown('<div class="sell-recommendation">❌ 不建议买入</div>', unsafe_allow_html=True)
                                elif "建议观望" in analysis_result:
                                    st.markdown('<div class="hold-recommendation">⚠️ 建议观望</div>', unsafe_allow_html=True)
                                
                                # 发送到钉钉机器人
                                title = f"股票分析报告 - {stock_data['basic']['name']}({stock_code})"
                                # 先处理换行符
                                formatted_analysis = analysis_result.replace('\n', '\n\n')
                                content = f'''### {title}
                                
#### 新闻内容
{news_text[:200]}...

#### 基本信息
- 股票代码：{stock_code}
- 股票名称：{stock_data['basic']['name']}
- 所属行业：{stock_data['basic'].get('industry', '未知')}
- 上市日期：{stock_data['basic'].get('list_date', '未知')}

#### 价格信息
- 最新价格：{stock_data['price'].get('close', '未知')}
- 涨跌额：{stock_data['price'].get('change', '未知')}
- 涨跌幅：{stock_data['price'].get('pct_chg', '未知')}%
- 今日开盘：{stock_data['price'].get('open', '未知')}
- 最高价：{stock_data['price'].get('high', '未知')}
- 最低价：{stock_data['price'].get('low', '未知')}
- 市盈率(TTM)：{stock_data['price'].get('pe', '未知')}
- 市净率：{stock_data['price'].get('pb', '未知')}

#### 市场表现
- 成交量：{stock_data['price'].get('成交量', '未知')}
- 成交额：{stock_data['price'].get('成交额', '未知')}
- 市值：{stock_data['price'].get('total_mv', '未知')}
- 52周最高：{stock_data['price'].get('52周最高', '未知')}
- 52周最低：{stock_data['price'].get('52周最低', '未知')}
- 今年以来涨幅：{stock_data['price'].get('今年以来涨幅', '未知')}

#### 投资分析结果
{formatted_analysis}
'''
                                # 发送消息
                                if dingtalk_bot.send_markdown(title, content):
                                    st.success("✅ 分析报告已发送到钉钉群")
                                else:
                                    st.error("❌ 发送到钉钉群失败，请检查配置")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>© 2024 股票新闻分析与投资建议系统 | 基于AI的智能投资分析工具</p>
</div>
""", unsafe_allow_html=True) 