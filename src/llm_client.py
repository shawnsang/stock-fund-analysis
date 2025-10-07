"""
LLM集成模块
处理提示词生成和API调用
"""

from typing import Iterator, Optional
import openai
from .config import config
from .logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """LLM客户端"""
    
    def __init__(self):
        """初始化LLM客户端"""
        self.client = openai.OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = config.OPENAI_MODEL
        
    def generate_analysis_prompt(self, stock_code: str, market: str, markdown_data: str) -> str:
        """
        生成资金流分析提示词
        
        Args:
            stock_code: 股票代码
            market: 市场代码
            markdown_data: Markdown格式的数据表格
            
        Returns:
            完整的分析提示词
        """
        prompt = f"""
## 分析数据
以下是该股票{stock_code}({market.upper()})最近30个交易日的资金流数据，包含净额（亿元）和净占比（%）：

**重要说明：数据按日期降序排列，表格第一行为最新交易日数据，最后一行为最早交易日数据。**

{markdown_data}

## 分析要求
基于30日资金流数据，简要回答：

**投资建议**: 
🔴 买入/🟡 持有/🔵 观望/🟠 减仓/⚫ 卖出
【操作策略】：操作方向？重点观察指标？买入或卖出价位？
- 短期策略（1-3日）：
- 中期策略（1-2周）：
**趋势**: 主力资金流向？MA均线方向？
- 建仓/增仓/减仓/出货
**结构**: 机构vs散户主导？资金协同性？

【风险等级】：🔴高风险/🟠中高风险/🟡中等风险/🟢中低风险/🔵低风险

要求：数据支撑，结论简明，突出重点。"""


        return prompt
    
    def analyze_fund_flow(self, stock_code: str, market: str, markdown_data: str) -> Iterator[str]:
        """
        分析资金流数据并返回流式结果
        
        Args:
            stock_code: 股票代码
            market: 市场代码
            markdown_data: Markdown格式的数据表格
            
        Yields:
            分析结果的文本片段
        """
        try:
            # 生成提示词
            prompt = self.generate_analysis_prompt(stock_code, market, markdown_data)
            
            # 记录完整提示词到日志
            logger.info("=== LLM分析提示词 ===")
            logger.info(prompt)
            logger.info("=== 提示词结束 ===")
            
            # 调用LLM API
            logger.info(f"开始调用LLM分析股票 {stock_code} 的资金流数据")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """专业股票资金流分析师。分析要求：
1. **趋势**: 资金流向和MA均线方向
2. **结构**: 机构vs散户，协同vs背离  
3. **信号**: 买卖信号和风险点
4. **建议**: 具体操作和观察重点

输出要求：结论先行，数据支撑，简明扼要。"""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                stream=True,
                temperature=0.5,
                max_tokens=1500
            )
            
            # 流式返回结果
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield content
                    
        except Exception as e:
            error_msg = f"LLM分析失败: {str(e)}"
            logger.error(error_msg)
            yield f"❌ {error_msg}"
    
    def test_connection(self) -> bool:
        """
        测试LLM连接
        
        Returns:
            连接是否成功
        """
        try:
            logger.info("测试LLM连接")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            logger.info("LLM连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"LLM连接测试失败: {str(e)}")
            return False


def create_llm_client() -> Optional[LLMClient]:
    """
    创建LLM客户端实例
    
    Returns:
        LLM客户端实例，如果配置无效则返回None
    """
    if not config.validate():
        missing_configs = config.get_missing_configs()
        logger.error(f"LLM配置不完整，缺少: {', '.join(missing_configs)}")
        return None
    
    try:
        client = LLMClient()
        if client.test_connection():
            logger.info("LLM客户端创建成功")
            return client
        else:
            logger.error("LLM客户端连接失败")
            return None
            
    except Exception as e:
        logger.error(f"创建LLM客户端失败: {str(e)}")
        return None