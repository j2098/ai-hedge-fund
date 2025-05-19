from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseTradingPlatform(ABC):
    """
    交易平台API的基类。
    定义了所有交易平台API必须实现的方法。
    """
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账户信息
        
        Returns:
            包含账户信息的字典
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """
        获取持仓信息
        
        Returns:
            包含持仓信息的字典，格式为：
            {
                "AAPL": {
                    "quantity": 10,
                    "cost_price": 150.0,
                    "current_price": 160.0,
                    "market_value": 1600.0,
                    "profit_loss": 100.0,
                    "profit_loss_ratio": 0.0667,
                    "today_profit_loss": 20.0,
                    "position_ratio": 0.1
                },
                ...
            }
        """
        pass
    
    @abstractmethod
    def get_portfolio_tickers(self) -> List[str]:
        """
        获取投资组合中的股票代码列表
        
        Returns:
            股票代码列表
        """
        pass
    
    @abstractmethod
    def place_order(self, ticker: str, quantity: int, price: Optional[float] = None, order_type: str = "market", side: str = "buy") -> Dict[str, Any]:
        """
        下单
        
        Args:
            ticker: 股票代码
            quantity: 数量
            price: 价格（限价单需要）
            order_type: 订单类型（market或limit）
            side: 买卖方向（buy或sell）
            
        Returns:
            包含订单信息的字典
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否成功取消
        """
        pass
    
    @abstractmethod
    def get_orders(self) -> List[Dict[str, Any]]:
        """
        获取订单列表
        
        Returns:
            包含订单信息的列表
        """
        pass
