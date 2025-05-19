import os
import sys
from typing import Dict, Any, List, Optional

from src.trading_platforms.base_platform import BaseTradingPlatform

# 添加本地Moomoo SDK路径
sdk_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'MMAPI4Python_9.2.5208')
if os.path.exists(sdk_path):
    sys.path.insert(0, sdk_path)

# 尝试导入moomoo API
try:
    # 尝试从本地SDK导入
    from moomoo import OpenQuoteContext, OpenHKTradeContext, OpenUSTradeContext, TrdEnv, TrdSide, OrderType
    MOOMOO_AVAILABLE = True
    print(f"Successfully imported moomoo SDK from {sdk_path}")
except ImportError:
    try:
        # 如果本地导入失败，尝试从已安装的包导入
        from futu import OpenQuoteContext, OpenHKTradeContext, OpenUSTradeContext, TrdEnv, TrdSide, OrderType
        MOOMOO_AVAILABLE = True
        print("Successfully imported moomoo SDK from installed futu package")
    except ImportError:
        MOOMOO_AVAILABLE = False
        print("\033[93mWARNING\033[0m: Moomoo SDK not found. Moomoo trading platform will not be available.")
        print("Please ensure the Moomoo SDK is properly installed or located at:", sdk_path)


class MoomooPlatform(BaseTradingPlatform):
    """
    Moomoo交易平台API处理程序。
    """

    def __init__(self):
        """初始化Moomoo交易平台处理程序"""
        if not MOOMOO_AVAILABLE:
            raise ImportError("Moomoo SDK is required for Moomoo trading platform. Please ensure it's properly installed.")

        # 从环境变量获取Moomoo API配置
        self._api_host = os.environ.get("MOOMOO_API_HOST", "127.0.0.1")
        self._api_port = int(os.environ.get("MOOMOO_API_PORT", "11111"))
        self._api_key = os.environ.get("MOOMOO_API_KEY", "")
        self._trade_env = os.environ.get("MOOMOO_TRADE_ENV", "SIMULATE")  # SIMULATE 或 REAL

        # 初始化连接
        self._quote_ctx = None
        self._trade_ctx_us = None
        self._connected = False

    def _ensure_connection(self):
        """确保与Moomoo API的连接已建立"""
        if not self._connected:
            try:
                # 创建行情上下文
                self._quote_ctx = OpenQuoteContext(host=self._api_host, port=self._api_port)

                # 创建美股交易上下文
                trd_env = TrdEnv.SIMULATE if self._trade_env == "SIMULATE" else TrdEnv.REAL
                self._trade_ctx_us = OpenUSTradeContext(host=self._api_host, port=self._api_port)

                # 检查API版本，适配不同版本的API
                if hasattr(self._trade_ctx_us, 'set_trade_env'):
                    # 旧版API
                    self._trade_ctx_us.set_trade_env(trd_env)
                else:
                    # 新版API可能在创建上下文时已经设置了交易环境
                    print(f"\033[92mINFO\033[0m: Using newer Moomoo API version that doesn't require set_trade_env")

                # 如果有API密钥，进行解锁
                if self._api_key:
                    ret, data = self._trade_ctx_us.unlock_trade(password_md5=self._api_key)
                    if ret != 0:
                        print(f"\033[91mMOOMOO ERROR\033[0m: Failed to unlock trade: {data}")

                self._connected = True
                print(f"\033[92mINFO\033[0m: Connected to Moomoo API at {self._api_host}:{self._api_port}")
            except Exception as e:
                print(f"\033[91mMOOMOO ERROR\033[0m: Failed to connect to Moomoo API: {e}")
                raise

    def _close_connection(self):
        """关闭与Moomoo API的连接"""
        if self._quote_ctx:
            self._quote_ctx.close()
        if self._trade_ctx_us:
            self._trade_ctx_us.close()
        self._connected = False

    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账户信息

        Returns:
            包含账户信息的字典
        """
        self._ensure_connection()

        try:
            # 获取账户资金（使用模拟环境）
            trd_env = TrdEnv.SIMULATE  # 强制使用模拟环境
            ret, data = self._trade_ctx_us.accinfo_query(trd_env=trd_env)
            if ret != 0:
                print(f"\033[91mMOOMOO ERROR\033[0m: Failed to get account info: {data}")
                return {}

            # 转换为更易于使用的格式
            account_info = {}
            if not data.empty:
                row = data.iloc[0]
                # 打印可用的列名，以便调试
                print(f"Available columns in account info: {list(row.index)}")

                # 安全地获取数据
                account_info = {
                    'power': row.get('power', 0),  # 购买力
                    'total_assets': row.get('total_assets', 0),  # 总资产
                    'cash': row.get('cash', 0),  # 现金
                    'market_value': row.get('market_val', 0) if 'market_val' in row else row.get('marketval', 0),  # 持仓市值
                    'frozen_cash': row.get('frozen_cash', 0),  # 冻结资金
                    'available_cash': row.get('avl_withdrawal_cash', 0),  # 可用资金
                }

            return account_info
        except Exception as e:
            print(f"\033[91mMOOMOO ERROR\033[0m: Error getting account info: {e}")
            return {}

    def get_positions(self) -> Dict[str, Any]:
        """
        获取持仓信息

        Returns:
            包含持仓信息的字典
        """
        self._ensure_connection()

        try:
            # 获取美股持仓（使用模拟环境）
            trd_env = TrdEnv.SIMULATE  # 强制使用模拟环境
            ret, data = self._trade_ctx_us.position_list_query(trd_env=trd_env)
            if ret != 0:
                print(f"\033[91mMOOMOO ERROR\033[0m: Failed to get US positions: {data}")
                return {}

            # 转换为更易于使用的格式
            positions = {}
            if not data.empty:
                # 打印可用的列名，以便调试
                print(f"Available columns in positions: {list(data.columns)}")

                for _, row in data.iterrows():
                    # 安全地获取股票代码
                    code = row.get('code', '')
                    if not code:
                        continue

                    ticker = code.split('.')[0]  # 去掉市场后缀
                    positions[ticker] = {
                        'quantity': row.get('qty', 0),
                        'cost_price': row.get('cost_price', 0),
                        'current_price': row.get('price', 0),
                        'market_value': row.get('market_val', 0) if 'market_val' in row else row.get('marketval', 0),
                        'profit_loss': row.get('pl_val', 0) if 'pl_val' in row else row.get('pl', 0),
                        'profit_loss_ratio': row.get('pl_ratio', 0),
                        'today_profit_loss': row.get('td_pl_val', 0) if 'td_pl_val' in row else row.get('td_pl', 0),
                        'position_ratio': row.get('position_ratio', 0),
                    }

            return positions
        except Exception as e:
            print(f"\033[91mMOOMOO ERROR\033[0m: Error getting positions: {e}")
            return {}

    def get_portfolio_tickers(self) -> List[str]:
        """
        获取投资组合中的股票代码列表

        Returns:
            股票代码列表
        """
        positions = self.get_positions()
        return list(positions.keys())

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
        self._ensure_connection()

        try:
            # 转换参数
            ticker_with_market = f"{ticker}.US"  # 添加市场后缀
            trd_side = TrdSide.BUY if side.lower() == "buy" else TrdSide.SELL

            # 设置订单类型
            if order_type.lower() == "market":
                price = 0  # 市价单价格设为0
                order_type_enum = OrderType.MARKET
            else:
                if price is None:
                    raise ValueError("Price must be specified for limit orders")
                order_type_enum = OrderType.NORMAL

            # 下单
            ret, data = self._trade_ctx_us.place_order(
                price=price,
                qty=quantity,
                code=ticker_with_market,
                trd_side=trd_side,
                order_type=order_type_enum
            )

            if ret != 0:
                print(f"\033[91mMOOMOO ERROR\033[0m: Failed to place order: {data}")
                return {"success": False, "error": str(data)}

            # 返回订单信息
            order_info = {
                "success": True,
                "order_id": data.iloc[0]['order_id'] if not data.empty else None,
                "ticker": ticker,
                "quantity": quantity,
                "price": price,
                "side": side,
                "order_type": order_type,
            }

            return order_info
        except Exception as e:
            print(f"\033[91mMOOMOO ERROR\033[0m: Error placing order: {e}")
            return {"success": False, "error": str(e)}

    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单

        Args:
            order_id: 订单ID

        Returns:
            是否成功取消
        """
        self._ensure_connection()

        try:
            # 取消订单
            ret, data = self._trade_ctx_us.modify_order(
                modify_order_op=1,  # 1表示取消订单
                order_id=order_id,
                qty=0,
                price=0
            )

            if ret != 0:
                print(f"\033[91mMOOMOO ERROR\033[0m: Failed to cancel order: {data}")
                return False

            return True
        except Exception as e:
            print(f"\033[91mMOOMOO ERROR\033[0m: Error canceling order: {e}")
            return False

    def get_orders(self) -> List[Dict[str, Any]]:
        """
        获取订单列表

        Returns:
            包含订单信息的列表
        """
        self._ensure_connection()

        try:
            # 获取订单列表
            ret, data = self._trade_ctx_us.order_list_query()
            if ret != 0:
                print(f"\033[91mMOOMOO ERROR\033[0m: Failed to get orders: {data}")
                return []

            # 转换为更易于使用的格式
            orders = []
            for _, row in data.iterrows():
                ticker = row['code'].split('.')[0]  # 去掉市场后缀
                orders.append({
                    'order_id': row['order_id'],
                    'ticker': ticker,
                    'quantity': row['qty'],
                    'price': row['price'],
                    'status': row['order_status'],
                    'create_time': row['create_time'],
                    'dealt_quantity': row['dealt_qty'],
                    'dealt_avg_price': row['dealt_avg_price'],
                })

            return orders
        except Exception as e:
            print(f"\033[91mMOOMOO ERROR\033[0m: Error getting orders: {e}")
            return []

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self._close_connection()
