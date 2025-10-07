# 个股资金流分析应用

这是一个基于Streamlit开发的个股资金流分析应用，作为一个资深的个股资金流专家，可以从个股不同规模的资金流中，分析出资金流的流向、大小、速度等特征，分析出个股主力资金的状态，如潜伏，抽逃，无主力资金关注等。

## ✨ 功能特性

- 🔍 **智能识别**: 自动识别股票代码对应的交易市场（沪深北）
- 📊 **数据获取**: 获取最近100个交易日的资金流数据（东方财富网）
- 📈 **技术分析**: 自动计算MA3、MA5、MA10移动平均线
- 🤖 **AI分析**: 基于LLM的专业资金流分析
- 💰 **单位优化**: 自动将金额从\"元\"转换为\"亿元\"显示
- 📋 **多格式展示**: 支持表格和Markdown格式数据展示
- 🔄 **流式显示**: LLM分析结果实时流式输出

## 🏗️ 项目结构

```
stock-fund-analysis/
├── src/                    # 源代码目录
│   ├── __init__.py        # 包初始化文件
│   ├── config.py          # 配置管理模块
│   ├── logger.py          # 日志模块
│   ├── data_fetcher.py    # 数据获取模块
│   ├── data_processor.py  # 数据处理模块
│   └── llm_client.py      # LLM集成模块
├── main.py                # Streamlit主应用
├── run.py                 # 启动脚本
├── pyproject.toml         # Poetry配置文件
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- Poetry（推荐）或 pip

### 2. 安装依赖

#### 使用Poetry（推荐）
```bash
# 安装Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 激活虚拟环境
poetry shell
```

#### 使用pip
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，配置LLM相关参数
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-3.5-turbo
```

### 4. 启动应用

```bash
# 方式1：使用启动脚本
python run.py

# 方式2：直接使用streamlit
streamlit run main.py

# 方式3：使用Poetry
poetry run streamlit run main.py
```

应用将在 http://localhost:8501 启动

## 📊 数据说明

### 数据来源
- **接口**: AKShare - stock_individual_fund_flow
- **数据源**: 东方财富网-数据中心-个股资金流向
- **更新频率**: 实时获取最新数据
- **数据量**: 近100个交易日

### 数据字段
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 日期 | datetime | 交易日期 |
| 收盘价 | float | 当日收盘价（元） |
| 涨跌幅 | float | 涨跌幅（%） |
| 主力净流入-净额 | float | 主力资金净流入金额（亿元） |
| 主力净流入-净占比 | float | 主力资金净流入占比（%） |
| 超大单净流入-净额 | float | 超大单净流入金额（亿元） |
| 超大单净流入-净占比 | float | 超大单净流入占比（%） |
| 大单净流入-净额 | float | 大单净流入金额（亿元） |
| 大单净流入-净占比 | float | 大单净流入占比（%） |
| 中单净流入-净额 | float | 中单净流入金额（亿元） |
| 中单净流入-净占比 | float | 中单净流入占比（%） |
| 小单净流入-净额 | float | 小单净流入金额（亿元） |
| 小单净流入-净占比 | float | 小单净流入占比（%） |

### 技术指标
每个净额字段都会自动计算以下移动平均线：
- **MA3**: 3日移动平均线
- **MA5**: 5日移动平均线  
- **MA10**: 10日移动平均线

## 🎯 使用方法

1. **输入股票代码**: 在左侧输入6位股票代码（如：000001、600519、300750）
2. **选择分析天数**: 调整要分析的最近交易日天数（10-50天）
3. **开始分析**: 点击"开始分析"按钮
4. **查看结果**: 
   - 数据表格展示
   - AI专业分析报告
   - Markdown格式原始数据

## 🔧 配置说明

### 环境变量配置（.env文件）

```bash
# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# 应用配置
APP_TITLE=个股资金流分析专家
LOG_LEVEL=INFO
MAX_TRADING_DAYS=30
```

### 支持的股票代码格式
- **上海证券交易所**: 60xxxx, 68xxxx, 90xxxx
- **深圳证券交易所**: 00xxxx, 30xxxx, 20xxxx  
- **北京证券交易所**: 43xxxx, 83xxxx, 87xxxx, 88xxxx

## 📝 开发说明

### 技术栈
- **前端框架**: Streamlit
- **数据获取**: AKShare
- **数据处理**: Pandas, Numpy
- **AI分析**: OpenAI API
- **日志系统**: Loguru
- **依赖管理**: Poetry
- **Python版本**: 3.11+

### 模块说明
- **config.py**: 配置管理，处理环境变量和应用配置
- **logger.py**: 日志系统配置，支持控制台和文件日志
- **data_fetcher.py**: 数据获取模块，封装AKShare API调用
- **data_processor.py**: 数据处理模块，实现均线计算和格式化
- **llm_client.py**: LLM集成模块，处理AI分析和流式输出
- **main.py**: Streamlit主应用，实现用户界面

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请提交 Issue 或联系开发者。
