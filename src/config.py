"""
配置管理模块
处理环境变量和应用配置
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # LLM配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 应用配置
    APP_TITLE: str = os.getenv("APP_TITLE", "个股资金流分析专家")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_TRADING_DAYS: int = int(os.getenv("MAX_TRADING_DAYS", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置是否存在"""
        if not cls.OPENAI_API_KEY:
            return False
        return True
    
    @classmethod
    def get_missing_configs(cls) -> list[str]:
        """获取缺失的配置项"""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        return missing


# 全局配置实例
config = Config()