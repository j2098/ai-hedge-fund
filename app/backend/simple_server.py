from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import sys
import time

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

# 全局变量，用于跟踪连接状态
MOOMOO_CONNECTION_STATUS = {
    "connected": False,
    "message": "Not connected to Moomoo API",
    "last_connected_time": 0,
    "host": "",
    "port": 0
}

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

            # 更新全局连接状态
            global MOOMOO_CONNECTION_STATUS
            MOOMOO_CONNECTION_STATUS = {
                "connected": True,
                "message": "Successfully connected to Moomoo API",
                "last_connected_time": time.time(),
                "host": settings.host,
                "port": settings.port
            }

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
    global MOOMOO_CONNECTION_STATUS

    # 如果连接已经建立，但是超过5分钟没有活动，则认为连接已断开
    if MOOMOO_CONNECTION_STATUS["connected"] and time.time() - MOOMOO_CONNECTION_STATUS["last_connected_time"] > 300:
        MOOMOO_CONNECTION_STATUS["connected"] = False
        MOOMOO_CONNECTION_STATUS["message"] = "Connection timed out"

    # 如果连接已经建立，尝试验证连接是否仍然有效
    if MOOMOO_CONNECTION_STATUS["connected"]:
        try:
            # 尝试创建一个新的连接，验证连接是否仍然有效
            host = MOOMOO_CONNECTION_STATUS["host"]
            port = MOOMOO_CONNECTION_STATUS["port"]
            quote_ctx = ft.OpenQuoteContext(host=host, port=port)
            quote_ctx.close()

            # 更新最后连接时间
            MOOMOO_CONNECTION_STATUS["last_connected_time"] = time.time()
        except Exception as e:
            # 连接失败，更新状态
            MOOMOO_CONNECTION_STATUS["connected"] = False
            MOOMOO_CONNECTION_STATUS["message"] = f"Connection lost: {str(e)}"

    return MoomooConnectionStatus(
        connected=MOOMOO_CONNECTION_STATUS["connected"],
        message=MOOMOO_CONNECTION_STATUS["message"]
    )

# 路由：获取持仓信息
@app.get("/api/moomoo/positions")
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

        print("尝试从Moomoo API获取真实持仓信息...")

        try:
            # 创建行情上下文
            quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

            # 创建美股交易上下文
            trade_ctx = ft.OpenUSTradeContext(host="127.0.0.1", port=11111)

            # 获取账户信息
            print("获取账户信息...")
            ret, acc_data = trade_ctx.accinfo_query(trd_env=ft.TrdEnv.SIMULATE)
            if ret != 0:
                print(f"获取账户信息失败: {acc_data}")
                raise Exception(f"Failed to get account info: {acc_data}")

            print(f"账户信息列: {list(acc_data.columns)}")

            # 获取持仓信息
            print("获取持仓信息...")
            ret, pos_data = trade_ctx.position_list_query(trd_env=ft.TrdEnv.SIMULATE)
            if ret != 0:
                print(f"获取持仓信息失败: {pos_data}")
                raise Exception(f"Failed to get positions: {pos_data}")

            print(f"持仓信息列: {list(pos_data.columns)}")

            # 转换账户信息为字典
            account_info_dict = {}
            if not acc_data.empty:
                row = acc_data.iloc[0]
                account_info_dict = {
                    "power": float(row.get("power", 0)),
                    "total_assets": float(row.get("total_assets", 0)),
                    "cash": float(row.get("cash", 0)),
                    "market_value": float(row.get("market_val", 0)) if "market_val" in row else float(row.get("marketval", 0)),
                    "frozen_cash": float(row.get("frozen_cash", 0)),
                    "available_cash": float(row.get("avl_withdrawal_cash", 0))
                }

            # 转换持仓信息为字典
            positions_dict = {}
            for _, row in pos_data.iterrows():
                code = row.get("code", "")
                if not code:
                    continue

                ticker = code.split(".")[1] if "." in code else code  # 提取股票代码

                positions_dict[ticker] = {
                    "ticker": ticker,
                    "quantity": float(row.get("qty", 0)),
                    "cost_price": float(row.get("cost_price", 0)),
                    "current_price": float(row.get("price", 0)),
                    "market_value": float(row.get("market_val", 0)) if "market_val" in row else float(row.get("market_value", 0)),
                    "profit_loss": float(row.get("pl_val", 0)) if "pl_val" in row else float(row.get("pl", 0)),
                    "profit_loss_ratio": float(row.get("pl_ratio", 0)),
                    "today_profit_loss": float(row.get("td_pl_val", 0)) if "td_pl_val" in row else float(row.get("td_pl", 0)),
                    "position_ratio": float(row.get("position_ratio", 0))
                }

            # 关闭连接
            quote_ctx.close()
            trade_ctx.close()

            print(f"获取到 {len(positions_dict)} 个持仓")

            # 如果没有持仓，直接返回空列表
            if not positions_dict:
                print("没有持仓，返回空列表...")

            return {
                "positions": positions_dict,
                "account_info": account_info_dict
            }
        except Exception as e:
            print(f"获取真实持仓信息失败: {str(e)}")
            # 直接抛出异常，暴露错误
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"获取持仓信息失败: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_moomoo_positions: {str(e)}")
        import traceback
        traceback.print_exc()
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
    global MOOMOO_CONNECTION_STATUS

    # 更新全局连接状态
    MOOMOO_CONNECTION_STATUS = {
        "connected": False,
        "message": "Disconnected from Moomoo API",
        "last_connected_time": 0,
        "host": "",
        "port": 0
    }

    return MoomooConnectionStatus(
        connected=False,
        message="Disconnected from Moomoo API"
    )

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
