from typing import Dict, Any, List, Optional

from src.trading_platforms.platform_factory import TradingPlatformFactory, TradingPlatform


def get_trading_platform_handler(platform: Optional[TradingPlatform] = None):
    """
    获取交易平台处理程序
    
    Args:
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        交易平台处理程序
    """
    return TradingPlatformFactory.get_handler(platform)


def get_account_info(platform: Optional[TradingPlatform] = None) -> Dict[str, Any]:
    """
    获取账户信息
    
    Args:
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        包含账户信息的字典
    """
    try:
        handler = get_trading_platform_handler(platform)
        return handler.get_account_info()
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to get account info: {e}")
        return {}


def get_positions(platform: Optional[TradingPlatform] = None) -> Dict[str, Any]:
    """
    获取持仓信息
    
    Args:
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        包含持仓信息的字典
    """
    try:
        handler = get_trading_platform_handler(platform)
        return handler.get_positions()
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to get positions: {e}")
        return {}


def get_portfolio_tickers(platform: Optional[TradingPlatform] = None) -> List[str]:
    """
    获取投资组合中的股票代码列表
    
    Args:
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        股票代码列表
    """
    try:
        handler = get_trading_platform_handler(platform)
        return handler.get_portfolio_tickers()
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to get portfolio tickers: {e}")
        return []


def place_order(ticker: str, quantity: int, price: Optional[float] = None, order_type: str = "market", side: str = "buy", platform: Optional[TradingPlatform] = None) -> Dict[str, Any]:
    """
    下单
    
    Args:
        ticker: 股票代码
        quantity: 数量
        price: 价格（限价单需要）
        order_type: 订单类型（market或limit）
        side: 买卖方向（buy或sell）
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        包含订单信息的字典
    """
    try:
        handler = get_trading_platform_handler(platform)
        return handler.place_order(ticker, quantity, price, order_type, side)
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to place order: {e}")
        return {"success": False, "error": str(e)}


def cancel_order(order_id: str, platform: Optional[TradingPlatform] = None) -> bool:
    """
    取消订单
    
    Args:
        order_id: 订单ID
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        是否成功取消
    """
    try:
        handler = get_trading_platform_handler(platform)
        return handler.cancel_order(order_id)
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to cancel order: {e}")
        return False


def get_orders(platform: Optional[TradingPlatform] = None) -> List[Dict[str, Any]]:
    """
    获取订单列表
    
    Args:
        platform: 交易平台枚举值，如果为None则使用默认平台
        
    Returns:
        包含订单信息的列表
    """
    try:
        handler = get_trading_platform_handler(platform)
        return handler.get_orders()
    except Exception as e:
        print(f"\033[91mERROR\033[0m: Failed to get orders: {e}")
        return []
