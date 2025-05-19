from typing import Dict, Any, List, Optional
import json
import os

# 导入交易平台工具
from src.tools.trading import get_positions, get_portfolio_tickers
from src.trading_platforms.platform_factory import TradingPlatform

# 初始化交易平台工厂
try:
    from src.trading_platforms.platform_factory import TradingPlatformFactory
    TradingPlatformFactory.initialize()

    # 检查Moomoo平台是否可用
    try:
        from src.trading_platforms.moomoo_platform import MOOMOO_AVAILABLE
    except ImportError:
        MOOMOO_AVAILABLE = False
except ImportError:
    MOOMOO_AVAILABLE = False
    print("\033[93mWARNING\033[0m: Trading platform factory not available.")


def get_portfolio_from_moomoo() -> Dict[str, float]:
    """
    从Moomoo账户获取投资组合权重

    Returns:
        字典，键为股票代码，值为投资组合权重（0-1之间的浮点数）
    """
    if not MOOMOO_AVAILABLE:
        print("\033[93mWARNING\033[0m: Moomoo API is not available. Cannot get portfolio from Moomoo.")
        return {}

    try:
        # 获取持仓信息
        positions = get_positions(TradingPlatform.MOOMOO)
        if not positions:
            return {}

        # 计算总市值
        total_market_value = sum(position["market_value"] for position in positions.values())
        if total_market_value <= 0:
            return {}

        # 计算每个股票的权重
        portfolio = {}
        for ticker, position in positions.items():
            weight = position["market_value"] / total_market_value
            portfolio[ticker] = weight

        return portfolio
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to get portfolio from Moomoo: {e}")
        return {}


def save_portfolio_to_file(portfolio: Dict[str, float], file_path: str) -> bool:
    """
    将投资组合保存到文件

    Args:
        portfolio: 投资组合字典，键为股票代码，值为权重
        file_path: 文件路径

    Returns:
        是否成功保存
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存到文件
        with open(file_path, "w") as f:
            json.dump(portfolio, f, indent=2)

        return True
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to save portfolio to file: {e}")
        return False


def load_portfolio_from_file(file_path: str) -> Dict[str, float]:
    """
    从文件加载投资组合

    Args:
        file_path: 文件路径

    Returns:
        投资组合字典，键为股票代码，值为权重
    """
    try:
        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r") as f:
            portfolio = json.load(f)

        return portfolio
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to load portfolio from file: {e}")
        return {}


def get_portfolio_tickers_from_moomoo() -> List[str]:
    """
    从Moomoo账户获取投资组合股票代码列表

    Returns:
        股票代码列表
    """
    if not MOOMOO_AVAILABLE:
        print("\033[93mWARNING\033[0m: Moomoo API is not available. Cannot get portfolio tickers from Moomoo.")
        return []

    try:
        return get_portfolio_tickers(TradingPlatform.MOOMOO)
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to get portfolio tickers from Moomoo: {e}")
        return []
