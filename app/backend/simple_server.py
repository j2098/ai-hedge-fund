from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import sys

# 添加本地Moomoo SDK路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sdk_path = os.path.join(project_root, 'MMAPI4Python_9.2.5208')
if os.path.exists(sdk_path):
    sys.path.insert(0, sdk_path)
    print(f"Added Moomoo SDK path: {sdk_path}")

# 尝试导入moomoo API
try:
    import moomoo as ft
    MOOMOO_AVAILABLE = True
    print(f"moomoo module imported successfully, version: {ft.__version__}")
except ImportError:
    try:
        import futu as ft
        MOOMOO_AVAILABLE = True
        print(f"futu module imported successfully, version: {ft.__version__}")
    except ImportError:
        MOOMOO_AVAILABLE = False
        print("Failed to import moomoo or futu module")

app = FastAPI(title="Simple Moomoo API", description="Simple API for Moomoo", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模型定义
class MoomooConnectionSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 11111
    api_key: str = ""
    trade_env: str = "SIMULATE"

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

class ImportPortfolioResponse(BaseModel):
    success: bool
    message: str
    portfolio: Dict[str, float]

# 路由：连接到Moomoo
@app.post("/api/moomoo/connect", response_model=MoomooConnectionStatus)
async def connect_moomoo(settings: MoomooConnectionSettings):
    """
    连接到Moomoo API
    """
    try:
        if not MOOMOO_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Moomoo API is not available. Please ensure Moomoo SDK is properly installed or located at the correct path."
            )

        # 尝试连接到Moomoo API
        try:
            # 创建行情上下文
            quote_ctx = ft.OpenQuoteContext(host=settings.host, port=settings.port)

            # 关闭连接
            quote_ctx.close()

            return MoomooConnectionStatus(
                connected=True,
                message="Successfully connected to Moomoo API"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Moomoo API: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Moomoo API: {str(e)}"
        )

# 路由：获取连接状态
@app.get("/api/moomoo/status", response_model=MoomooConnectionStatus)
async def get_moomoo_status():
    """
    获取Moomoo API连接状态
    """
    return MoomooConnectionStatus(
        connected=False,
        message="Not connected to Moomoo API"
    )

# 路由：获取持仓信息
@app.get("/api/moomoo/positions", response_model=MoomooPositionsResponse)
async def get_moomoo_positions():
    """
    获取Moomoo持仓信息
    """
    try:
        if not MOOMOO_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Moomoo API is not available. Please ensure Moomoo SDK is properly installed or located at the correct path."
            )

        # 创建模拟数据
        positions = {
            "AAPL": MoomooPosition(
                ticker="AAPL",
                quantity=10,
                cost_price=150.0,
                current_price=170.0,
                market_value=1700.0,
                profit_loss=200.0,
                profit_loss_ratio=0.13,
                today_profit_loss=20.0,
                position_ratio=0.05
            ),
            "MSFT": MoomooPosition(
                ticker="MSFT",
                quantity=5,
                cost_price=300.0,
                current_price=320.0,
                market_value=1600.0,
                profit_loss=100.0,
                profit_loss_ratio=0.07,
                today_profit_loss=10.0,
                position_ratio=0.04
            )
        }

        account_info = MoomooAccountInfo(
            power=100000.0,
            total_assets=105000.0,
            cash=101700.0,
            market_value=3300.0,
            frozen_cash=0.0,
            available_cash=101700.0
        )

        return MoomooPositionsResponse(
            positions=positions,
            account_info=account_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get positions from Moomoo API: {str(e)}"
        )

# 路由：断开连接
@app.post("/api/moomoo/disconnect", response_model=MoomooConnectionStatus)
async def disconnect_moomoo():
    """
    断开与Moomoo API的连接
    """
    return MoomooConnectionStatus(
        connected=False,
        message="Disconnected from Moomoo API"
    )

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
