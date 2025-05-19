from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os

# 导入交易平台工具
try:
    from src.tools.trading import get_positions, get_account_info, get_portfolio_tickers
    from src.tools.portfolio import get_portfolio_from_moomoo, save_portfolio_to_file
    from src.trading_platforms.platform_factory import TradingPlatform, TradingPlatformFactory

    # 初始化交易平台工厂
    TradingPlatformFactory.initialize()

    # 检查Moomoo平台是否可用
    try:
        from src.trading_platforms.moomoo_platform import MOOMOO_AVAILABLE
    except ImportError:
        MOOMOO_AVAILABLE = False
except ImportError:
    MOOMOO_AVAILABLE = False
    print("\033[93mWARNING\033[0m: Trading platform tools not available. To install required package, run: pip install moomoo-api")

# 创建路由器
router = APIRouter(
    prefix="/api/moomoo",
    tags=["moomoo"],
    responses={404: {"description": "Not found"}},
)

# 定义请求和响应模型
class MoomooConnectionSettings(BaseModel):
    host: str
    port: int
    api_key: Optional[str] = None
    trade_env: str = "SIMULATE"  # SIMULATE 或 REAL

class MoomooConnectionStatus(BaseModel):
    connected: bool
    message: str

class MoomooPosition(BaseModel):
    ticker: str
    quantity: float
    cost_price: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_ratio: float
    today_profit_loss: float
    position_ratio: float

class MoomooAccountInfo(BaseModel):
    power: float
    total_assets: float
    cash: float
    market_value: float
    frozen_cash: float
    available_cash: float

class MoomooPositionsResponse(BaseModel):
    positions: Dict[str, MoomooPosition]
    account_info: MoomooAccountInfo

# 检查Moomoo API是否可用的依赖项
def check_moomoo_available():
    if not MOOMOO_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Moomoo API is not available. Make sure futu-api is installed."
        )
    return True

# 检查Moomoo API是否已配置的依赖项
def check_moomoo_configured():
    if not os.environ.get("MOOMOO_API_HOST"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Moomoo API is not configured. Please connect to Moomoo first."
        )
    return True

# 路由：连接到Moomoo
@router.post("/connect", response_model=MoomooConnectionStatus)
async def connect_moomoo(settings: MoomooConnectionSettings, _: bool = Depends(check_moomoo_available)):
    """
    连接到Moomoo API
    """
    try:
        # 设置环境变量
        os.environ["MOOMOO_API_HOST"] = settings.host
        os.environ["MOOMOO_API_PORT"] = str(settings.port)
        os.environ["MOOMOO_TRADE_ENV"] = settings.trade_env

        if settings.api_key:
            os.environ["MOOMOO_API_KEY"] = settings.api_key

        # 设置交易平台为Moomoo
        os.environ["TRADING_PLATFORM"] = "moomoo"

        # 重新初始化交易平台工厂
        TradingPlatformFactory.initialize()

        # 测试连接
        account_info = get_account_info(TradingPlatform.MOOMOO)
        if not account_info:
            raise Exception("Failed to connect to Moomoo API")

        return MoomooConnectionStatus(
            connected=True,
            message="Successfully connected to Moomoo API"
        )
    except Exception as e:
        # 清除环境变量
        for key in ["MOOMOO_API_HOST", "MOOMOO_API_PORT", "MOOMOO_API_KEY", "MOOMOO_TRADE_ENV"]:
            if key in os.environ:
                del os.environ[key]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to Moomoo API: {str(e)}"
        )

# 路由：获取连接状态
@router.get("/status", response_model=MoomooConnectionStatus)
async def get_moomoo_status(_: bool = Depends(check_moomoo_available)):
    """
    获取Moomoo API连接状态
    """
    if os.environ.get("MOOMOO_API_HOST"):
        try:
            # 测试连接
            account_info = get_account_info(TradingPlatform.MOOMOO)
            if account_info:
                return MoomooConnectionStatus(
                    connected=True,
                    message="Connected to Moomoo API"
                )
        except Exception as e:
            return MoomooConnectionStatus(
                connected=False,
                message=f"Connection error: {str(e)}"
            )

    return MoomooConnectionStatus(
        connected=False,
        message="Not connected to Moomoo API"
    )

# 路由：断开连接
@router.post("/disconnect", response_model=MoomooConnectionStatus)
async def disconnect_moomoo(_: bool = Depends(check_moomoo_available)):
    """
    断开与Moomoo API的连接
    """
    # 清除环境变量
    for key in ["MOOMOO_API_HOST", "MOOMOO_API_PORT", "MOOMOO_API_KEY", "MOOMOO_TRADE_ENV"]:
        if key in os.environ:
            del os.environ[key]

    # 重置交易平台
    if os.environ.get("TRADING_PLATFORM") == "moomoo":
        del os.environ["TRADING_PLATFORM"]

    # 重新初始化交易平台工厂
    TradingPlatformFactory.initialize()

    return MoomooConnectionStatus(
        connected=False,
        message="Disconnected from Moomoo API"
    )

# 路由：获取美股持仓
@router.get("/positions", response_model=MoomooPositionsResponse)
async def get_moomoo_positions(
    _: bool = Depends(check_moomoo_available),
    __: bool = Depends(check_moomoo_configured)
):
    """
    获取Moomoo账户中的美股持仓信息
    """
    try:
        # 获取持仓信息
        positions_data = get_positions(TradingPlatform.MOOMOO)
        account_data = get_account_info(TradingPlatform.MOOMOO)

        if not positions_data or not account_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get positions from Moomoo API"
            )

        # 转换为响应模型
        positions = {}
        for ticker, position in positions_data.items():
            positions[ticker] = MoomooPosition(
                ticker=ticker,
                quantity=position["quantity"],
                cost_price=position["cost_price"],
                current_price=position["current_price"],
                market_value=position["market_value"],
                profit_loss=position["profit_loss"],
                profit_loss_ratio=position["profit_loss_ratio"],
                today_profit_loss=position["today_profit_loss"],
                position_ratio=position["position_ratio"]
            )

        account_info = MoomooAccountInfo(
            power=account_data.get("power", 0),
            total_assets=account_data.get("total_assets", 0),
            cash=account_data.get("cash", 0),
            market_value=account_data.get("market_value", 0),
            frozen_cash=account_data.get("frozen_cash", 0),
            available_cash=account_data.get("available_cash", 0)
        )

        return MoomooPositionsResponse(
            positions=positions,
            account_info=account_info
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting positions: {str(e)}"
        )

# 路由：获取投资组合股票代码
@router.get("/portfolio/tickers", response_model=List[str])
async def get_moomoo_portfolio_tickers(
    _: bool = Depends(check_moomoo_available),
    __: bool = Depends(check_moomoo_configured)
):
    """
    获取Moomoo账户中的投资组合股票代码列表
    """
    try:
        tickers = get_portfolio_tickers(TradingPlatform.MOOMOO)
        return tickers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting portfolio tickers: {str(e)}"
        )

class ImportPortfolioResponse(BaseModel):
    success: bool
    message: str
    portfolio: Dict[str, float]

@router.post("/portfolio/import", response_model=ImportPortfolioResponse)
async def import_moomoo_portfolio(
    _: bool = Depends(check_moomoo_available),
    __: bool = Depends(check_moomoo_configured)
):
    """
    从Moomoo账户导入投资组合并保存到文件
    """
    try:
        # 获取投资组合
        portfolio = get_portfolio_from_moomoo()
        if not portfolio:
            return ImportPortfolioResponse(
                success=False,
                message="No portfolio data found in Moomoo account",
                portfolio={}
            )

        # 保存到文件
        file_path = "data/portfolios/moomoo_portfolio.json"
        save_success = save_portfolio_to_file(portfolio, file_path)

        if save_success:
            return ImportPortfolioResponse(
                success=True,
                message=f"Successfully imported portfolio with {len(portfolio)} stocks",
                portfolio=portfolio
            )
        else:
            return ImportPortfolioResponse(
                success=False,
                message="Failed to save portfolio to file",
                portfolio=portfolio
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing portfolio: {str(e)}"
        )
