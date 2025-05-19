#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Moomoo交易平台
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 加载环境变量
load_dotenv()

# 导入交易平台
from trading_platforms.moomoo_platform import MoomooPlatform

def test_moomoo_platform():
    """测试Moomoo交易平台"""
    print("\n=== 测试Moomoo交易平台 ===")

    try:
        # 创建Moomoo交易平台实例
        print("创建Moomoo交易平台实例...")
        platform = MoomooPlatform()
        print("Moomoo交易平台实例创建成功")

        # 获取账户信息
        print("\n获取账户信息...")
        account_info = platform.get_account_info()
        print("账户信息:")
        print(json.dumps(account_info, indent=2, ensure_ascii=False))

        # 获取持仓信息
        print("\n获取持仓信息...")
        positions = platform.get_positions()
        print("持仓信息:")
        print(json.dumps(positions, indent=2, ensure_ascii=False))

        # 获取投资组合股票代码
        print("\n获取投资组合股票代码...")
        tickers = platform.get_portfolio_tickers()
        print("投资组合股票代码:", tickers)

    except Exception as e:
        print(f"测试Moomoo交易平台异常: {e}")

if __name__ == "__main__":
    print("开始测试Moomoo交易平台...")

    # 设置环境变量（如果没有在.env文件中设置）
    if not os.environ.get("MOOMOO_API_HOST"):
        os.environ["MOOMOO_API_HOST"] = "127.0.0.1"
    if not os.environ.get("MOOMOO_API_PORT"):
        os.environ["MOOMOO_API_PORT"] = "11111"
    if not os.environ.get("MOOMOO_API_KEY"):
        os.environ["MOOMOO_API_KEY"] = ""  # 如果需要，请设置您的API密钥
    if not os.environ.get("MOOMOO_TRADE_ENV"):
        os.environ["MOOMOO_TRADE_ENV"] = "SIMULATE"  # 使用模拟环境

    # 测试Moomoo交易平台
    test_moomoo_platform()

    print("\n测试完成")
