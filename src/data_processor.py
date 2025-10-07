"""
数据处理模块
实现MA均线计算和数据格式化（元转亿元）
"""

from typing import List
import pandas as pd
import numpy as np
from .logger import get_logger
from .config import config

logger = get_logger(__name__)


class DataProcessor:
    """数据处理器"""
    
    # 需要处理的净额列
    AMOUNT_COLUMNS = [
        '主力净流入-净额',
        '超大单净流入-净额', 
        '大单净流入-净额',
        '中单净流入-净额',
        '小单净流入-净额'
    ]
    
    # 净占比列
    RATIO_COLUMNS = [
        '主力净流入-净占比',
        '超大单净流入-净占比',
        '大单净流入-净占比', 
        '中单净流入-净占比',
        '小单净流入-净占比'
    ]
    
    @staticmethod
    def yuan_to_yi(amount: float) -> float:
        """
        将金额从元转换为亿元
        
        Args:
            amount: 金额（元）
            
        Returns:
            金额（亿元），保留2位小数
        """
        if pd.isna(amount):
            return np.nan
        return round(amount / 100000000, 2)
    
    @staticmethod
    def calculate_ma(series: pd.Series, window: int) -> pd.Series:
        """
        计算移动平均线
        
        Args:
            series: 数据序列
            window: 窗口大小
            
        Returns:
            移动平均线序列
        """
        return series.rolling(window=window, min_periods=1).mean().round(2)
    
    @staticmethod
    def add_ma_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        为净额列添加MA3、MA5、MA10均线
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            添加均线后的DataFrame
        """
        logger.info("开始计算移动平均线")
        
        # 创建副本避免修改原数据
        result_df = df.copy()
        
        # 确保数据按日期升序排列（用于计算均线）
        if '日期' in result_df.columns:
            result_df = result_df.sort_values('日期', ascending=True)
        
        # 为每个净额列计算均线
        for col in DataProcessor.AMOUNT_COLUMNS:
            if col in result_df.columns:
                logger.debug(f"计算 {col} 的移动平均线")
                
                # 计算MA3、MA5、MA10
                result_df[f'{col}-MA3'] = DataProcessor.calculate_ma(result_df[col], 3)
                result_df[f'{col}-MA5'] = DataProcessor.calculate_ma(result_df[col], 5)
                result_df[f'{col}-MA10'] = DataProcessor.calculate_ma(result_df[col], 10)
        
        # 恢复按日期降序排列（最新的在前）
        if '日期' in result_df.columns:
            result_df = result_df.sort_values('日期', ascending=False)
        
        logger.info("移动平均线计算完成")
        return result_df
    
    @staticmethod
    def format_amounts(df: pd.DataFrame) -> pd.DataFrame:
        """
        格式化金额列，从元转换为亿元
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            格式化后的DataFrame
        """
        logger.info("开始格式化金额数据")
        
        # 创建副本避免修改原数据
        result_df = df.copy()
        
        # 获取所有需要转换的列（包括均线列）
        amount_cols_to_convert = []
        
        for col in result_df.columns:
            # 检查是否是净额列或其均线列
            if any(base_col in col for base_col in DataProcessor.AMOUNT_COLUMNS):
                if '净额' in col or 'MA' in col:
                    amount_cols_to_convert.append(col)
        
        # 转换金额单位
        for col in amount_cols_to_convert:
            if col in result_df.columns:
                logger.debug(f"转换 {col} 的单位：元 -> 亿元")
                result_df[col] = result_df[col].apply(DataProcessor.yuan_to_yi)
        
        logger.info(f"完成 {len(amount_cols_to_convert)} 个金额列的单位转换")
        return result_df
    
    @staticmethod
    def get_recent_data(df: pd.DataFrame, days: int = None) -> pd.DataFrame:
        """
        获取最近N个交易日的数据
        
        Args:
            df: 数据DataFrame
            days: 天数，默认使用配置中的MAX_TRADING_DAYS
            
        Returns:
            最近N天的数据
        """
        if days is None:
            days = config.MAX_TRADING_DAYS
        
        logger.info(f"获取最近 {days} 个交易日的数据")
        
        # 确保数据按日期降序排列
        if '日期' in df.columns:
            df = df.sort_values('日期', ascending=False)
        
        # 取前N条记录
        recent_df = df.head(days).copy()
        
        logger.info(f"返回 {len(recent_df)} 条最近交易日数据")
        return recent_df
    
    @staticmethod
    def process_fund_flow_data(df: pd.DataFrame, days: int = None) -> pd.DataFrame:
        """
        完整的数据处理流程
        
        Args:
            df: 原始资金流数据
            days: 返回最近N天的数据
            
        Returns:
            处理完成的数据
        """
        logger.info("开始完整数据处理流程")
        
        try:
            # 1. 添加移动平均线
            df_with_ma = DataProcessor.add_ma_columns(df)
            
            # 2. 格式化金额单位
            df_formatted = DataProcessor.format_amounts(df_with_ma)
            
            # 3. 获取最近N天数据
            df_recent = DataProcessor.get_recent_data(df_formatted, days)
            
            logger.info("数据处理流程完成")
            return df_recent
            
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}")
            raise
    
    @staticmethod
    def generate_markdown_table(df: pd.DataFrame) -> str:
        """
        生成Markdown格式的数据表格
        
        Args:
            df: 处理后的数据DataFrame
            
        Returns:
            Markdown格式的表格字符串
        """
        logger.info("生成Markdown表格")
        
        try:
            # 选择要显示的列
            display_columns = ['日期', '收盘价', '涨跌幅']
            
            # 添加净额列及其均线
            for base_col in DataProcessor.AMOUNT_COLUMNS:
                if base_col in df.columns:
                    display_columns.extend([
                        base_col,
                        f'{base_col}-MA3',
                        f'{base_col}-MA5', 
                        f'{base_col}-MA10'
                    ])
            
            # 添加净占比列
            for ratio_col in DataProcessor.RATIO_COLUMNS:
                if ratio_col in df.columns:
                    display_columns.append(ratio_col)
            
            # 过滤存在的列
            available_columns = [col for col in display_columns if col in df.columns]
            display_df = df[available_columns].copy()
            
            # 格式化日期
            if '日期' in display_df.columns:
                display_df['日期'] = display_df['日期'].dt.strftime('%Y-%m-%d')
            
            # 生成Markdown表格
            markdown_table = display_df.to_markdown(index=False, floatfmt='.2f')
            
            logger.info("Markdown表格生成完成")
            return markdown_table
            
        except Exception as e:
            logger.error(f"生成Markdown表格失败: {str(e)}")
            raise