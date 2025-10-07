"""
个股资金流分析应用 - Streamlit主程序
"""

import streamlit as st
import pandas as pd
from typing import Optional

# 导入自定义模块
from src.config import config
from src.logger import get_logger
from src.data_fetcher import StockDataFetcher
from src.data_processor import DataProcessor
from src.llm_client import create_llm_client

# 设置页面配置
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 获取日志记录器
logger = get_logger(__name__)


def init_session_state():
    """初始化会话状态"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'current_stock' not in st.session_state:
        st.session_state.current_stock = None


def display_header():
    """显示页面头部"""
    st.title("📈 " + config.APP_TITLE)
    st.markdown("---")
    

def display_sidebar():
    """显示侧边栏"""
    st.sidebar.header("🔧 分析配置")
    
    # 股票代码输入
    stock_code = st.sidebar.text_input(
        "股票代码",
        placeholder="请输入股票代码，如：000001",
        help="支持6位数字股票代码，系统会自动识别交易市场"
    )
    
    # 分析天数选择
    days = st.sidebar.slider(
        "分析天数",
        min_value=10,
        max_value=50,
        value=config.MAX_TRADING_DAYS,
        help="选择要分析的最近交易日天数"
    )
    
    # 开始分析按钮
    analyze_button = st.sidebar.button(
        "🚀 开始分析",
        type="primary",
        use_container_width=True
    )
    
    # 配置状态显示
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 配置状态")
    
    # 检查LLM配置
    if config.validate():
        st.sidebar.success("✅ LLM配置正常")
    else:
        missing = config.get_missing_configs()
        st.sidebar.error(f"❌ 缺少配置: {', '.join(missing)}")
        st.sidebar.info("请在.env文件中配置相关参数")
    
    return stock_code, days, analyze_button


def fetch_and_process_data(stock_code: str, days: int) -> Optional[pd.DataFrame]:
    """获取并处理股票数据"""
    try:
        with st.spinner("🔄 正在获取股票数据..."):
            # 获取原始数据
            raw_data = StockDataFetcher.fetch_fund_flow(stock_code)
            
            # 处理数据
            processed_data = DataProcessor.process_fund_flow_data(raw_data, days)
            
            logger.info(f"成功获取并处理股票 {stock_code} 的数据，共 {len(processed_data)} 条记录")
            return processed_data
            
    except Exception as e:
        st.error(f"❌ 数据获取失败: {str(e)}")
        logger.error(f"数据获取失败: {str(e)}")
        return None


def display_data_charts(df: pd.DataFrame, stock_code: str):
    """显示数据图表"""
    st.subheader(f"📊 {stock_code} 资金流分析")
    
    # 数据统计概览
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("数据天数", len(df))
    
    with col2:
        if '主力净流入-净额' in df.columns:
            main_flow = df['主力净流入-净额'].sum()
            st.metric(
                "主力净流入总额", 
                f"{main_flow:.2f}亿元",
                delta=f"{main_flow:.2f}亿元" if main_flow != 0 else None
            )
    
    with col3:
        if '收盘价' in df.columns:
            latest_price = df['收盘价'].iloc[0] if len(df) > 0 else 0
            st.metric("最新收盘价", f"{latest_price:.2f}元")
    
    with col4:
        if '涨跌幅' in df.columns:
            latest_change = df['涨跌幅'].iloc[0] if len(df) > 0 else 0
            st.metric("最新涨跌幅", f"{latest_change:.2f}%")
    
    # 图表展示
    tab1, tab2, tab3 = st.tabs(["💰 主力资金趋势", "📈 资金流结构", "🔗 价格资金关联"])
    
    with tab1:
        # 主力资金流趋势图 + 收盘价格走势图
        if '主力净流入-净额' in df.columns and '日期' in df.columns:
            import plotly.express as px
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            # 创建双轴子图
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('收盘价格走势', '主力资金净流入趋势'),
                vertical_spacing=0.08,
                row_heights=[0.4, 0.6]
            )
            
            # 上图：收盘价格走势
            if '收盘价' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['日期'],
                        y=df['收盘价'],
                        mode='lines',
                        name='收盘价',
                        line=dict(color='#1f77b4', width=1.5)
                    ),
                    row=1, col=1
                )
            
            # 下图：主力净流入净额
            if '主力净流入-净额' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['日期'],
                        y=df['主力净流入-净额'],
                        mode='lines',
                        name='主力净流入',
                        line=dict(color='red', width=1.5)
                    ),
                    row=2, col=1
                )
            
            # MA3 趋势线
            if '主力净流入-净额-MA3' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['日期'],
                        y=df['主力净流入-净额-MA3'],
                        mode='lines',
                        name='MA3',
                        line=dict(color='orange', dash='dot', width=1.2)
                    ),
                    row=2, col=1
                )
            
            # MA5 趋势线
            if '主力净流入-净额-MA5' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['日期'],
                        y=df['主力净流入-净额-MA5'],
                        mode='lines',
                        name='MA5',
                        line=dict(color='blue', dash='dash', width=1.2)
                    ),
                    row=2, col=1
                )
            
            # 添加零轴线到下图
            fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=1)
            
            # 更新布局
            fig.update_layout(
                height=600,
                showlegend=True,
                title_text="价格与主力资金流关联分析"
            )
            
            # 更新y轴标签
            fig.update_yaxes(title_text="价格(元)", row=1, col=1)
            fig.update_yaxes(title_text="净流入金额(亿元)", row=2, col=1)
            fig.update_xaxes(title_text="日期", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无主力资金流数据")
    
    with tab2:
        # 资金流结构对比
        if all(col in df.columns for col in ['主力净流入-净占比', '超大单净流入-净占比', '大单净流入-净占比']):
            import plotly.express as px
            
            # 计算平均净占比
            avg_data = {
                '主力资金': df['主力净流入-净占比'].mean(),
                '超大单': df['超大单净流入-净占比'].mean(),
                '大单': df['大单净流入-净占比'].mean(),
                '中单': df['中单净流入-净占比'].mean() if '中单净流入-净占比' in df.columns else 0,
                '小单': df['小单净流入-净占比'].mean() if '小单净流入-净占比' in df.columns else 0
            }
            
            # 创建柱状图
            fig = px.bar(
                x=list(avg_data.keys()),
                y=list(avg_data.values()),
                title="各类资金平均净占比",
                labels={'x': '资金类型', 'y': '平均净占比(%)'},
                color=list(avg_data.values()),
                color_continuous_scale='RdYlBu_r'
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无净占比数据")
    
    with tab3:
        # 价格与资金流关联
        if all(col in df.columns for col in ['收盘价', '主力净流入-净额', '日期']):
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            # 创建双轴图
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('股价走势', '主力资金流'),
                vertical_spacing=0.1
            )
            
            # 添加股价
            fig.add_trace(
                go.Scatter(
                    x=df['日期'],
                    y=df['收盘价'],
                    mode='lines',
                    name='收盘价',
                    line=dict(color='black', width=2)
                ),
                row=1, col=1
            )
            
            # 添加主力资金流
            colors = ['red' if x > 0 else 'green' for x in df['主力净流入-净额']]
            fig.add_trace(
                go.Bar(
                    x=df['日期'],
                    y=df['主力净流入-净额'],
                    name='主力净流入',
                    marker_color=colors
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=500,
                title_text="股价与主力资金流关联分析",
                showlegend=True
            )
            
            fig.update_yaxes(title_text="价格(元)", row=1, col=1)
            fig.update_yaxes(title_text="净流入(亿元)", row=2, col=1)
            fig.update_xaxes(title_text="日期", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无价格或资金流数据")


def display_llm_analysis(stock_code: str, market: str, df: pd.DataFrame):
    """显示LLM分析结果"""
    st.subheader("🤖 AI资金流分析")
    
    # 创建LLM客户端
    llm_client = create_llm_client()
    
    if llm_client is None:
        st.error("❌ LLM配置错误，无法进行AI分析")
        return
    
    # 生成Markdown数据
    try:
        markdown_data = DataProcessor.generate_markdown_table(df)
        
        # 显示分析结果容器
        analysis_container = st.empty()
        
        # 流式显示分析结果
        with st.spinner("🧠 AI正在分析中..."):
            analysis_text = ""
            
            for chunk in llm_client.analyze_fund_flow(stock_code, market, markdown_data):
                analysis_text += chunk
                analysis_container.markdown(analysis_text + "▌")  # 添加光标效果
            
            # 移除光标，显示最终结果
            analysis_container.markdown(analysis_text)
            
        st.success("✅ AI分析完成")
        
    except Exception as e:
        st.error(f"❌ AI分析失败: {str(e)}")
        logger.error(f"AI分析失败: {str(e)}")


def display_raw_data_section(df: pd.DataFrame):
    """显示原始数据部分"""
    with st.expander("📋 查看Markdown格式数据", expanded=False):
        try:
            markdown_table = DataProcessor.generate_markdown_table(df)
            st.code(markdown_table, language="markdown")
        except Exception as e:
            st.error(f"生成Markdown数据失败: {str(e)}")


def main():
    """主函数"""
    # 初始化
    init_session_state()
    
    # 显示页面头部
    display_header()
    
    # 显示侧边栏并获取用户输入
    stock_code, days, analyze_button = display_sidebar()
    
    # 处理分析请求
    if analyze_button and stock_code:
        # 验证股票代码
        try:
            clean_code, market = StockDataFetcher.validate_stock_code(stock_code)
            st.session_state.current_stock = (clean_code, market)
            
            # 获取并处理数据
            processed_data = fetch_and_process_data(clean_code, days)
            
            if processed_data is not None:
                st.session_state.current_data = processed_data
                st.session_state.analysis_complete = True
                st.rerun()  # 重新运行以更新显示
                
        except Exception as e:
            st.error(f"❌ 股票代码验证失败: {str(e)}")
    
    # 显示分析结果
    if st.session_state.analysis_complete and st.session_state.current_data is not None:
        df = st.session_state.current_data
        clean_code, market = st.session_state.current_stock
        
        # 显示数据图表
        display_data_charts(df, clean_code)
        
        st.markdown("---")
        
        # 显示LLM分析
        display_llm_analysis(clean_code, market, df)
        
        st.markdown("---")
        
        # 显示原始数据
        display_raw_data_section(df)
    
    elif not st.session_state.analysis_complete:
        # 显示欢迎信息
        st.info("👈 请在左侧输入股票代码并点击\"开始分析\"按钮")
        
        # 显示示例
        st.markdown("### 📝 使用示例")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.code("000001", language="text")
            st.caption("平安银行（深交所）")
        
        with col2:
            st.code("600519", language="text")
            st.caption("贵州茅台（上交所）")
        
        with col3:
            st.code("300750", language="text")
            st.caption("宁德时代（深交所创业板）")


if __name__ == "__main__":
    main()