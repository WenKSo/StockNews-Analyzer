import os
import sys

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从config导入常量
from config.config import ARK_API_KEY
from volcenginesdkarkruntime import Ark

# 配置 DeepSeek
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,
)

def analyze_technical_indicators(stock_code, period="daily", lookback_days=60):
    """
    分析股票的技术指标，包括：
    1. 趋势分析（均线、MACD等）
    2. 成交量分析
    3. 支撑位和压力位
    4. 技术形态
    """
    import akshare as ak
    from datetime import datetime, timedelta
    
    # 计算开始日期（当前日期往前推lookback_days天）
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y%m%d')
    
    try:
        # 获取历史行情数据
        print(f"[Debug] Fetching hist data for {stock_code} from {start_date} to {end_date}") # Debug print
        hist_data = ak.stock_zh_a_hist(symbol=stock_code, period=period, 
                                     start_date=start_date, end_date=end_date, adjust="qfq") # Changed adjust to "qfq"
        
        print(f"[Debug] Fetched hist_data shape: {hist_data.shape}") # Debug print
        print("[Debug] Fetched hist_data head:") # Debug print
        print(hist_data.head()) # Debug print
        print("[Debug] Fetched hist_data tail:") # Debug print
        print(hist_data.tail()) # Debug print

        if hist_data.empty or len(hist_data) < 20: # Added check for minimum length for indicators
            print("[Debug] Fetched data is empty or too short for indicator calculation.") # Debug print
            return {
                "status": "error",
                "message": f"无法获取足够 ({len(hist_data)} rows) 的历史行情数据进行分析"
            }
        
        # 计算技术指标
        # 1. 计算均线
        hist_data['MA5'] = hist_data['收盘'].rolling(window=5).mean()
        hist_data['MA10'] = hist_data['收盘'].rolling(window=10).mean()
        hist_data['MA20'] = hist_data['收盘'].rolling(window=20).mean()
        
        # 2. 计算MACD
        hist_data['EMA12'] = hist_data['收盘'].ewm(span=12, adjust=False).mean()
        hist_data['EMA26'] = hist_data['收盘'].ewm(span=26, adjust=False).mean()
        hist_data['MACD'] = hist_data['EMA12'] - hist_data['EMA26']
        hist_data['Signal'] = hist_data['MACD'].ewm(span=9, adjust=False).mean()
        
        # 3. 计算RSI
        delta = hist_data['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist_data['RSI'] = 100 - (100 / (1 + rs))
        
        print("[Debug] hist_data after indicator calculation (tail):") # Debug print
        print(hist_data.tail()[[col for col in ['日期', '收盘', 'MA5', 'MA20', 'MACD', 'Signal', 'RSI'] if col in hist_data.columns]]) # Debug print
        
        # 准备技术分析提示
        latest = hist_data.iloc[-1]
        prev = hist_data.iloc[-2]
        
        # 生成技术分析提示
        technical_analysis = {
            "trend": {
                "short_term": "上涨" if latest['MA5'] > prev['MA5'] else "下跌",
                "medium_term": "上涨" if latest['MA20'] > prev['MA20'] else "下跌",
                "macd_signal": "金叉" if latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal'] else 
                              "死叉" if latest['MACD'] < latest['Signal'] and prev['MACD'] >= prev['Signal'] else 
                              "维持"
            },
            "volume": {
                "recent_avg": hist_data['成交量'].tail(5).mean(),
                "latest": latest['成交量'],
                "trend": "放量" if latest['成交量'] > hist_data['成交量'].tail(5).mean() else "缩量"
            },
            "momentum": {
                "rsi": latest['RSI'],
                "overbought": latest['RSI'] > 70,
                "oversold": latest['RSI'] < 30
            },
            "support_resistance": {
                "support": hist_data['最低'].tail(20).min(),
                "resistance": hist_data['最高'].tail(20).max()
            }
        }
        
        return {
            "status": "success",
            "data": technical_analysis,
            "hist_data": hist_data  # Return the full DataFrame
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"技术分析出错: {str(e)}"
        }

def analyze_stock(news_text, stock_data):
    """
    综合分析股票的消息面、基本面和技术面，给出投资建议
    """
<<<<<<< HEAD
    # 提取技术分析数据
    technical_data = stock_data.get('technical_analysis', {})
    support_levels = technical_data.get('support_resistance', {}).get('支撑位', [])
    resistance_levels = technical_data.get('support_resistance', {}).get('压力位', [])
    
    # 将支撑位和压力位格式化为字符串
    support_str = "、".join([str(level) for level in support_levels]) if support_levels else "未识别到明确支撑位"
    resistance_str = "、".join([str(level) for level in resistance_levels]) if resistance_levels else "未识别到明确压力位"
    
=======
    # 1. 获取技术面分析
    stock_code = stock_data.get('basic', {}).get('ts_code', '').split('.')[0]  # 提取纯数字代码
    technical_analysis = analyze_technical_indicators(stock_code)
    
    # 2. 准备分析提示
>>>>>>> efd69ca1f46d29b8676683fe716bee9b5bf1c37f
    prompt = f"""
    请基于以下三个维度的信息，综合分析该股票的投资价值：

    一、消息面分析（新闻内容）：
    {news_text}

    二、基本面分析：
    1. 公司基本信息：
    代码：{stock_data.get('basic', {}).get('ts_code', '未知')}
    名称：{stock_data.get('basic', {}).get('name', '未知')}
    行业：{stock_data.get('basic', {}).get('industry', '未知')}
    
    2. 当前估值：
    最新收盘价：{stock_data.get('price', {}).get('close', '未知')}
    市盈率(PE)：{stock_data.get('price', {}).get('pe', '未知')}
    市净率(PB)：{stock_data.get('price', {}).get('pb', '未知')}
    
    3. 财务指标：
    每股收益(EPS)：{stock_data.get('financial_indicator', {}).get('eps', '未知')}
    净资产收益率(ROE)：{stock_data.get('financial_indicator', {}).get('roe', '未知')}
    毛利率：{stock_data.get('financial_indicator', {}).get('gross_profit_margin', '未知')}%
    资产负债率：{stock_data.get('financial_indicator', {}).get('debt_to_assets', '未知')}%
<<<<<<< HEAD
    
    5. 资产负债情况（简要参考）：
    总资产：{stock_data.get('balance_sheet', {}).get('total_assets', '未知')}
    总负债：{stock_data.get('balance_sheet', {}).get('total_liab', '未知')}
    
    6. 技术分析数据（作为参考）：
    主要支撑位：{support_str}
    主要压力位：{resistance_str}
    当前价格：{stock_data.get('price', {}).get('close', '未知')}
    
    请给出详细分析和明确的投资建议，必须按照以下结构呈现：
    
    ### 一、新闻分析（占分析内容的50%左右）
    [深入分析这条新闻对公司的具体影响，这是最核心的部分]
    - 新闻传递的核心信息是什么？
    - 对公司业务、收入和利润的可能影响
    - 对行业竞争格局的影响
    - 对公司市场地位的影响
    - 新闻可能导致的市场反应
    
    ### 二、基本面简要分析（占分析内容的20%左右）
    [简要分析公司当前基本面状况，仅作为辅助参考]
    - 公司当前估值是否合理
    - 财务状况是否健康
    - 盈利能力如何
    
    ### 三、技术面分析（占分析内容的15%左右）
    [分析股票当前技术形态和价格走势]
    - 价格所处位置（支撑位/压力位附近？突破还是回调？）
    - 价格趋势研判（上升趋势？下降趋势？震荡区间？）
    - 短期可能的价格目标位
    - 较强的支撑位和压力位分析
    
    ### 四、综合判断与投资建议（占分析内容的15%左右）
    [结合新闻、基本面和技术面，给出明确的投资建议]
    1. 整体判断：这条新闻是否足以影响投资决策
    2. 投资决策：必须明确给出以下三种结论之一
       - "建议买入"：如果综合判断积极
       - "不建议买入"：如果综合判断负面
       - "建议观望"：如果影响不明确或需要进一步观察
=======

    三、技术面分析：
    {technical_analysis.get('data', {}) if technical_analysis.get('status') == 'success' else '技术分析数据获取失败'}

    请给出详细分析和明确的投资建议，必须按照以下结构呈现：

    ### 一、消息面分析（30%权重）
    [分析新闻对公司的影响，判断是利好、利空还是中性]

    ### 二、基本面分析（30%权重）
    [分析公司当前的基本面状况，包括估值、财务状况等]

    ### 三、技术面分析（40%权重）
    [分析技术指标，判断当前趋势和买卖信号]

    ### 四、综合判断与投资建议
    1. 整体判断：[综合三个维度的分析，给出总体判断]
    2. 投资决策：必须明确给出以下三种结论之一
       - "建议买入"：如果三个维度都支持买入
       - "不建议买入"：如果任一维度显示明显风险
       - "建议观望"：如果信号不明确或需要进一步观察
>>>>>>> efd69ca1f46d29b8676683fe716bee9b5bf1c37f
    3. 如果建议买入：
       - 建议配置的仓位比例（占总投资的百分比）
       - 预期持有时间（短期、中期或长期）
<<<<<<< HEAD
       - 建议的买入价位区间
       - 止损位建议
    4. 投资理由（优势）和风险提示
    
    注意：重点分析新闻内容对该股票的直接影响，这是决策的核心依据。基本面和技术面数据作为辅助参考，需要综合考虑。
=======
    4. 投资理由和风险提示
>>>>>>> efd69ca1f46d29b8676683fe716bee9b5bf1c37f
    """
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content