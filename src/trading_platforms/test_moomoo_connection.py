#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Moomoo SDK连接和获取持仓信息
"""

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

try:
    import moomoo as ft
    print(f"Successfully imported moomoo SDK, version: {ft.__version__}")
except ImportError:
    try:
        import futu as ft
        print(f"Successfully imported futu SDK, version: {ft.__version__}")
    except ImportError:
        print("Failed to import moomoo or futu SDK. Please check installation.")
        sys.exit(1)

def test_quote_connection():
    """测试行情连接"""
    print("\n=== 测试行情连接 ===")
    host = os.environ.get("MOOMOO_API_HOST", "127.0.0.1")
    port = int(os.environ.get("MOOMOO_API_PORT", "11111"))
    
    print(f"连接到 {host}:{port}")
    quote_ctx = ft.OpenQuoteContext(host=host, port=port)
    
    try:
        # 获取全局状态
        print("获取全局状态...")
        ret, data = quote_ctx.get_global_state()
        if ret == ft.RET_OK:
            print("全局状态:", data)
        else:
            print("获取全局状态失败:", data)
        
        # 获取美股市场状态
        print("\n获取美股市场状态...")
        ret, data = quote_ctx.get_market_state(['US.AAPL', 'US.MSFT'])
        if ret == ft.RET_OK:
            print("美股市场状态:", data)
        else:
            print("获取美股市场状态失败:", data)
            
    except Exception as e:
        print(f"行情连接测试异常: {e}")
    finally:
        quote_ctx.close()
        print("行情连接已关闭")

def test_trade_connection():
    """测试交易连接"""
    print("\n=== 测试交易连接 ===")
    host = os.environ.get("MOOMOO_API_HOST", "127.0.0.1")
    port = int(os.environ.get("MOOMOO_API_PORT", "11111"))
    
    print(f"连接到 {host}:{port}")
    trade_ctx = ft.OpenUSTradeContext(host=host, port=port)
    
    try:
        # 获取交易账户列表
        print("获取交易账户列表...")
        ret, data = trade_ctx.get_acc_list()
        if ret == ft.RET_OK:
            print("交易账户列表:", data)
            
            # 如果有账户，尝试获取持仓信息
            if not data.empty:
                print("\n获取持仓信息...")
                # 注意：这里不解锁交易，只是查询信息
                ret, data = trade_ctx.position_list_query(trd_env=ft.TrdEnv.SIMULATE)  # 使用模拟环境
                if ret == ft.RET_OK:
                    print("持仓信息:", data)
                else:
                    print("获取持仓信息失败:", data)
        else:
            print("获取交易账户列表失败:", data)
            
    except Exception as e:
        print(f"交易连接测试异常: {e}")
    finally:
        trade_ctx.close()
        print("交易连接已关闭")

if __name__ == "__main__":
    print("开始测试Moomoo SDK连接...")
    
    # 测试行情连接
    test_quote_connection()
    
    # 测试交易连接
    test_trade_connection()
    
    print("\n测试完成")
