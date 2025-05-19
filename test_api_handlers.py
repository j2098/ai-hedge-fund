#!/usr/bin/env python3
"""
测试脚本，用于比较FinancialDatasetsApiHandler和FinnhubApiHandler的数据
差异项会以红色标记
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.api_handlers.api_factory import ApiFactory, ApiProvider
from src.api_handlers.financial_datasets_handler import FinancialDatasetsApiHandler
from src.api_handlers.finnhub_handler import FinnhubApiHandler

# 加载环境变量
load_dotenv()

# ANSI颜色代码
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# 测试参数
TEST_TICKERS = ["AAPL", "MSFT", "GOOGL"]  # 美国股票
SG_TICKERS = ["D05.SI", "U11.SI", "C38U.SI"]  # 新加坡股票 (DBS, UOB, CapitaLand)
END_DATE = datetime.now().strftime("%Y-%m-%d")
START_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# 创建API处理程序
financial_datasets_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
finnhub_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)

def print_separator(title):
    """打印分隔符"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def compare_prices(ticker):
    """比较价格数据"""
    print_separator(f"比较价格数据: {ticker}")

    # 获取Financial Datasets数据
    try:
        fd_prices = financial_datasets_handler.get_prices(ticker, START_DATE, END_DATE)
        print(f"Financial Datasets API 返回 {len(fd_prices)} 条价格记录")
        if fd_prices:
            print(f"\n{BOLD}Financial Datasets 最新5条价格数据:{RESET}")
            for price in fd_prices[-5:]:
                print(f"日期: {price.time}, 开盘: {price.open:.2f}, 最高: {price.high:.2f}, 最低: {price.low:.2f}, 收盘: {price.close:.2f}, 成交量: {price.volume}")
    except Exception as e:
        print(f"{RED}Financial Datasets API 错误: {e}{RESET}")
        fd_prices = []

    # 获取Finnhub数据
    try:
        fh_prices = finnhub_handler.get_prices(ticker, START_DATE, END_DATE)
        print(f"\nFinnhub API 返回 {len(fh_prices)} 条价格记录")
        if fh_prices:
            print(f"\n{BOLD}Finnhub 最新5条价格数据:{RESET}")
            for price in fh_prices[-5:]:
                print(f"日期: {price.time}, 开盘: {price.open:.2f}, 最高: {price.high:.2f}, 最低: {price.low:.2f}, 收盘: {price.close:.2f}, 成交量: {price.volume}")
    except Exception as e:
        print(f"{RED}Finnhub API 错误: {e}{RESET}")
        fh_prices = []

    # 比较数据
    if fd_prices and fh_prices:
        print(f"\n{BOLD}数据比较 (一行一个指标):{RESET}")

        # 获取最新日期的数据
        fd_latest = fd_prices[-1]
        fh_latest = fh_prices[-1]

        # 定义要比较的字段
        fields = [
            ("日期", "time", None),
            ("开盘价", "open", 0.01),
            ("最高价", "high", 0.01),
            ("最低价", "low", 0.01),
            ("收盘价", "close", 0.01),
            ("成交量", "volume", 0.01)
        ]

        # 逐个比较字段
        for label, field, threshold in fields:
            fd_value = getattr(fd_latest, field)
            fh_value = getattr(fh_latest, field)

            # 检查是否有差异
            has_diff = False
            diff_pct = None

            if field == "time":
                has_diff = fd_value != fh_value
            elif fd_value and fh_value and threshold:
                diff_pct = abs(fd_value - fh_value) / fd_value * 100
                has_diff = diff_pct > threshold

            # 打印比较结果
            if has_diff:
                if diff_pct is not None:
                    print(f"{RED}{label}: Financial Datasets={fd_value}, Finnhub={fh_value}, 差异={diff_pct:.2f}%{RESET}")
                else:
                    print(f"{RED}{label}: Financial Datasets={fd_value}, Finnhub={fh_value}{RESET}")
            else:
                if diff_pct is not None:
                    print(f"{label}: Financial Datasets={fd_value}, Finnhub={fh_value}, 差异={diff_pct:.2f}%")
                else:
                    print(f"{label}: Financial Datasets={fd_value}, Finnhub={fh_value}")

def compare_financial_metrics(ticker):
    """比较财务指标"""
    print_separator(f"比较财务指标: {ticker}")

    # 获取Financial Datasets数据
    try:
        fd_metrics = financial_datasets_handler.get_financial_metrics(ticker, END_DATE)
        print(f"Financial Datasets API 返回 {len(fd_metrics)} 条财务指标记录")
        if fd_metrics:
            print(f"\n{BOLD}Financial Datasets 最新财务指标:{RESET}")
            metrics_dict = fd_metrics[0].model_dump()
            # 只打印非空值的前10个指标
            count = 0
            for key, value in metrics_dict.items():
                if value is not None and key not in ["ticker", "report_period", "period"]:
                    print(f"{key}: {value}")
                    count += 1
                    if count >= 10:
                        print("... (更多指标省略) ...")
                        break
    except Exception as e:
        print(f"{RED}Financial Datasets API 错误: {e}{RESET}")
        fd_metrics = []

    # 获取Finnhub数据
    try:
        fh_metrics = finnhub_handler.get_financial_metrics(ticker, END_DATE)
        print(f"\nFinnhub API 返回 {len(fh_metrics)} 条财务指标记录")
        if fh_metrics:
            print(f"\n{BOLD}Finnhub 最新财务指标:{RESET}")
            metrics_dict = fh_metrics[0].model_dump()
            # 只打印非空值的前10个指标
            count = 0
            for key, value in metrics_dict.items():
                if value is not None and key not in ["ticker", "report_period", "period"]:
                    print(f"{key}: {value}")
                    count += 1
                    if count >= 10:
                        print("... (更多指标省略) ...")
                        break
    except Exception as e:
        print(f"{RED}Finnhub API 错误: {e}{RESET}")
        fh_metrics = []

    # 比较数据
    if fd_metrics and fh_metrics:
        print(f"\n{BOLD}数据比较 (一行一个指标):{RESET}")
        fd_latest = fd_metrics[0]
        fh_latest = fh_metrics[0]

        # 获取所有可能的指标
        all_metrics = set()
        fd_dict = fd_latest.model_dump()
        fh_dict = fh_latest.model_dump()

        for key in fd_dict.keys():
            if fd_dict[key] is not None and key not in ["ticker", "report_period", "period"]:
                all_metrics.add(key)

        for key in fh_dict.keys():
            if fh_dict[key] is not None and key not in ["ticker", "report_period", "period"]:
                all_metrics.add(key)

        # 按字母顺序排序指标
        sorted_metrics = sorted(all_metrics)

        # 比较每个指标
        for metric in sorted_metrics:
            fd_value = getattr(fd_latest, metric, None)
            fh_value = getattr(fh_latest, metric, None)

            if fd_value is not None and fh_value is not None:
                # 检查是否有差异
                has_diff = False
                diff_pct = None

                if isinstance(fd_value, (int, float)) and isinstance(fh_value, (int, float)):
                    # 数值型指标，计算百分比差异
                    if abs(fd_value) > 0.0001:  # 避免除以零
                        diff_pct = abs(fd_value - fh_value) / abs(fd_value) * 100
                        has_diff = diff_pct > 1.0  # 差异超过1%视为有差异
                else:
                    # 非数值型指标，直接比较
                    has_diff = fd_value != fh_value

                # 打印比较结果
                if has_diff:
                    if diff_pct is not None:
                        print(f"{RED}{metric}: Financial Datasets={fd_value}, Finnhub={fh_value}, 差异={diff_pct:.2f}%{RESET}")
                    else:
                        print(f"{RED}{metric}: Financial Datasets={fd_value}, Finnhub={fh_value}{RESET}")
                else:
                    if diff_pct is not None:
                        print(f"{metric}: Financial Datasets={fd_value}, Finnhub={fh_value}, 差异={diff_pct:.2f}%")
                    else:
                        print(f"{metric}: Financial Datasets={fd_value}, Finnhub={fh_value}")
            elif fd_value is not None:
                print(f"{YELLOW}{metric}: Financial Datasets={fd_value}, Finnhub=None{RESET}")
            elif fh_value is not None:
                print(f"{YELLOW}{metric}: Financial Datasets=None, Finnhub={fh_value}{RESET}")

def compare_company_news(ticker):
    """比较公司新闻"""
    print_separator(f"比较公司新闻: {ticker}")

    # 获取Financial Datasets数据
    try:
        fd_news = financial_datasets_handler.get_company_news(ticker, END_DATE, START_DATE, limit=5)
        print(f"Financial Datasets API 返回 {len(fd_news)} 条新闻")
        if fd_news:
            print(f"\n{BOLD}Financial Datasets 最新新闻:{RESET}")
            for i, news in enumerate(fd_news[:3], 1):
                print(f"{i}. [{news.date}] {news.headline}")
    except Exception as e:
        print(f"{RED}Financial Datasets API 错误: {e}{RESET}")
        fd_news = []

    # 获取Finnhub数据
    try:
        fh_news = finnhub_handler.get_company_news(ticker, END_DATE, START_DATE, limit=5)
        print(f"\nFinnhub API 返回 {len(fh_news)} 条新闻")
        if fh_news:
            print(f"\n{BOLD}Finnhub 最新新闻:{RESET}")
            for i, news in enumerate(fh_news[:3], 1):
                print(f"{i}. [{news.date}] {news.headline}")
    except Exception as e:
        print(f"{RED}Finnhub API 错误: {e}{RESET}")
        fh_news = []

    # 比较数据
    if fd_news and fh_news:
        print(f"\n{BOLD}新闻标题比较:{RESET}")

        # 创建日期到新闻的映射
        fd_news_by_date = {news.date: news for news in fd_news}
        fh_news_by_date = {news.date: news for news in fh_news}

        # 找出共同的日期
        common_dates = set(fd_news_by_date.keys()) & set(fh_news_by_date.keys())

        if common_dates:
            for date in sorted(common_dates, reverse=True)[:3]:  # 最多比较3条
                fd_headline = fd_news_by_date[date].headline
                fh_headline = fh_news_by_date[date].headline

                if fd_headline != fh_headline:
                    print(f"{RED}[{date}] 标题不一致:{RESET}")
                    print(f"  Financial Datasets: {fd_headline}")
                    print(f"  Finnhub: {fh_headline}")
                else:
                    print(f"[{date}] 标题一致: {fd_headline}")
        else:
            print(f"{YELLOW}没有找到相同日期的新闻进行比较{RESET}")

def compare_market_cap(ticker):
    """比较市值"""
    print_separator(f"比较市值: {ticker}")

    # 获取Financial Datasets数据
    try:
        fd_market_cap = financial_datasets_handler.get_market_cap(ticker, END_DATE)
        if fd_market_cap:
            print(f"Financial Datasets 市值: {fd_market_cap:,.2f}")
        else:
            print(f"{YELLOW}Financial Datasets 市值: 无数据{RESET}")
    except Exception as e:
        print(f"{RED}Financial Datasets API 错误: {e}{RESET}")
        fd_market_cap = None

    # 获取Finnhub数据
    try:
        fh_market_cap = finnhub_handler.get_market_cap(ticker, END_DATE)
        if fh_market_cap:
            print(f"Finnhub 市值: {fh_market_cap:,.2f}")
        else:
            print(f"{YELLOW}Finnhub 市值: 无数据{RESET}")
    except Exception as e:
        print(f"{RED}Finnhub API 错误: {e}{RESET}")
        fh_market_cap = None

    # 比较数据
    if fd_market_cap and fh_market_cap:
        diff_pct = abs(fd_market_cap - fh_market_cap) / fd_market_cap * 100
        if diff_pct > 1.0:  # 差异超过1%视为有差异
            print(f"{RED}市值差异: {diff_pct:.2f}%{RESET}")
        else:
            print(f"市值差异: {diff_pct:.2f}%")
    elif fd_market_cap:
        print(f"{YELLOW}只有Financial Datasets提供了市值数据{RESET}")
    elif fh_market_cap:
        print(f"{YELLOW}只有Finnhub提供了市值数据{RESET}")
    else:
        print(f"{RED}两个API都没有提供市值数据{RESET}")

def run_tests():
    """运行所有测试"""
    print(f"\n{BOLD}API处理程序比较测试{RESET}")
    print(f"测试日期范围: {START_DATE} 至 {END_DATE}")
    print(f"差异项将以{RED}红色{RESET}标记，缺失项将以{YELLOW}黄色{RESET}标记")

    # 测试美国股票
    print_separator(f"{BOLD}测试美国股票{RESET}")
    for ticker in TEST_TICKERS:
        try:
            compare_prices(ticker)
            compare_financial_metrics(ticker)
            compare_company_news(ticker)
            compare_market_cap(ticker)
        except Exception as e:
            print(f"{RED}测试 {ticker} 时发生错误: {e}{RESET}")

    # 测试新加坡股票
    print_separator(f"{BOLD}测试新加坡股票{RESET}")
    for ticker in SG_TICKERS:
        try:
            compare_prices(ticker)
            compare_financial_metrics(ticker)
            compare_company_news(ticker)
            compare_market_cap(ticker)
        except Exception as e:
            print(f"{RED}测试 {ticker} 时发生错误: {e}{RESET}")

    print_separator(f"{BOLD}测试完成{RESET}")
    print("总结:")
    print(f"1. 美国股票: 测试了 {len(TEST_TICKERS)} 只股票 ({', '.join(TEST_TICKERS)})")
    print(f"2. 新加坡股票: 测试了 {len(SG_TICKERS)} 只股票 ({', '.join(SG_TICKERS)})")
    print(f"3. 差异项以{RED}红色{RESET}标记，缺失项以{YELLOW}黄色{RESET}标记")

if __name__ == "__main__":
    run_tests()
