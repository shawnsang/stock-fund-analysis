"""
数据获取模块
封装AKShare API调用和市场参数自动识别
"""

import re
from typing import Optional, Tuple
import pandas as pd
import akshare as ak
from .logger import get_logger

logger = get_logger(__name__)


class StockDataFetcher:
    """股票数据获取器"""
    
    @staticmethod
    def detect_market(stock_code: str) -> str:
        """
        根据股票代码自动识别市场
        
        Args:
            stock_code: 股票代码
            
        Returns:
            市场代码: sh/sz/bj
        """
        # 清理股票代码，只保留数字
        clean_code = re.sub(r'[^\d]', '', stock_code)
        
        if not clean_code:
            raise ValueError(f"无效的股票代码: {stock_code}")
        
        # 根据代码规则判断市场
        if clean_code.startswith(('60', '68', '90')):
            return 'sh'  # 上海证券交易所
        elif clean_code.startswith(('00', '30', '20')):
            return 'sz'  # 深圳证券交易所
        elif clean_code.startswith(('43', '83', '87', '88')):
            return 'bj'  # 北京证券交易所
        else:
            # 默认根据代码长度和首位数字判断
            if len(clean_code) == 6:
                if clean_code[0] in ['6']:
                    return 'sh'
                elif clean_code[0] in ['0', '3']:
                    return 'sz'
            
            # 如果无法判断，默认为深圳
            logger.warning(f"无法自动识别股票代码 {stock_code} 的市场，默认使用深圳市场")
            return 'sz'
    
    @staticmethod
    def validate_stock_code(stock_code: str) -> Tuple[str, str]:
        """
        验证并标准化股票代码
        
        Args:
            stock_code: 原始股票代码
            
        Returns:
            (标准化的股票代码, 市场代码)
        """
        # 清理股票代码
        clean_code = re.sub(r'[^\d]', '', stock_code)
        
        if not clean_code:
            raise ValueError(f"无效的股票代码: {stock_code}")
        
        # 补齐到6位
        if len(clean_code) < 6:
            clean_code = clean_code.zfill(6)
        elif len(clean_code) > 6:
            clean_code = clean_code[:6]
        
        market = StockDataFetcher.detect_market(clean_code)
        
        logger.info(f"股票代码标准化: {stock_code} -> {clean_code}, 市场: {market}")
        
        return clean_code, market
    
    @staticmethod
    def fetch_fund_flow(stock_code: str, market: Optional[str] = None) -> pd.DataFrame:
        """
        获取个股资金流数据
        
        Args:
            stock_code: 股票代码
            market: 市场代码，如果不提供则自动识别
            
        Returns:
            资金流数据DataFrame
        """
        try:
            # 验证和标准化股票代码
            clean_code, auto_market = StockDataFetcher.validate_stock_code(stock_code)
            
            # 使用提供的市场代码或自动识别的市场代码
            final_market = market if market else auto_market
            
            logger.info(f"开始获取股票 {clean_code} ({final_market}) 的资金流数据")
            
            # 调用AKShare API
            df = ak.stock_individual_fund_flow(stock=clean_code, market=final_market)
            
            if df.empty:
                raise ValueError(f"未获取到股票 {clean_code} 的资金流数据")
            
            logger.info(f"成功获取 {len(df)} 条资金流数据")
            
            # 确保日期列为datetime类型
            if '日期' in df.columns:
                df['日期'] = pd.to_datetime(df['日期'])
                # 按日期排序，最新的在前
                df = df.sort_values('日期', ascending=False).reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"获取资金流数据失败: {str(e)}")
            raise
    
    @staticmethod
    def get_stock_info(stock_code: str) -> dict:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票基本信息字典
        """
        try:
            clean_code, market = StockDataFetcher.validate_stock_code(stock_code)
            
            # 这里可以扩展获取更多股票信息的逻辑
            # 目前返回基本信息
            return {
                'code': clean_code,
                'market': market,
                'full_code': f"{clean_code}.{market.upper()}"
            }
            
        except Exception as e:
            logger.error(f"获取股票信息失败: {str(e)}")
            raise