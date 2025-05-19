import os
from enum import Enum
from typing import Dict, Optional

from src.trading_platforms.base_platform import BaseTradingPlatform


class TradingPlatform(Enum):
    """支持的交易平台枚举"""
    MOOMOO = "moomoo"
    # 未来可以添加更多交易平台，如Interactive Brokers、TD Ameritrade等


class TradingPlatformFactory:
    """
    交易平台工厂类，用于创建和管理交易平台API处理程序。
    """
    
    # 存储已创建的处理程序实例
    _handlers: Dict[TradingPlatform, BaseTradingPlatform] = {}
    
    # 默认交易平台
    _default_platform: Optional[TradingPlatform] = None
    
    @classmethod
    def initialize(cls) -> None:
        """
        初始化工厂类，确定默认交易平台。
        """
        cls._determine_default_platform()
    
    @classmethod
    def get_handler(cls, platform: Optional[TradingPlatform] = None) -> BaseTradingPlatform:
        """
        获取指定交易平台的处理程序。
        如果未指定平台，则使用默认平台。
        
        Args:
            platform: 交易平台枚举值
            
        Returns:
            交易平台API处理程序
            
        Raises:
            ValueError: 如果指定的平台不受支持或没有默认平台
        """
        # 如果未指定平台，使用默认平台
        if platform is None:
            if cls._default_platform is None:
                cls._determine_default_platform()
            
            platform = cls._default_platform
        
        # 如果仍然没有平台，抛出错误
        if platform is None:
            raise ValueError("No trading platform specified and no default platform available")
        
        # 如果处理程序不存在，创建它
        if platform not in cls._handlers:
            cls._create_handler(platform)
        
        return cls._handlers[platform]
    
    @classmethod
    def _create_handler(cls, platform: TradingPlatform) -> None:
        """
        创建指定交易平台的处理程序。
        
        Args:
            platform: 交易平台枚举值
            
        Raises:
            ValueError: 如果指定的平台不受支持
            ImportError: 如果无法导入平台处理程序
        """
        if platform == TradingPlatform.MOOMOO:
            try:
                from src.trading_platforms.moomoo_platform import MoomooPlatform, MOOMOO_AVAILABLE
                if not MOOMOO_AVAILABLE:
                    raise ImportError("Moomoo API is not available. Make sure moomoo-api is installed.")
                cls._handlers[platform] = MoomooPlatform()
            except ImportError as e:
                raise ImportError(f"Failed to create Moomoo platform handler: {e}")
        else:
            raise ValueError(f"Unsupported trading platform: {platform}")
    
    @classmethod
    def _determine_default_platform(cls) -> None:
        """
        确定默认交易平台。
        基于环境变量和可用性。
        """
        # 检查环境变量中指定的交易平台
        platform_name = os.environ.get("TRADING_PLATFORM", "").lower()
        
        if platform_name == "moomoo":
            try:
                from src.trading_platforms.moomoo_platform import MOOMOO_AVAILABLE
                if MOOMOO_AVAILABLE:
                    cls._default_platform = TradingPlatform.MOOMOO
                    return
            except ImportError:
                pass
        
        # 检查Moomoo API配置
        try:
            from src.trading_platforms.moomoo_platform import MOOMOO_AVAILABLE
            if MOOMOO_AVAILABLE and os.environ.get("MOOMOO_API_HOST"):
                cls._default_platform = TradingPlatform.MOOMOO
                return
        except ImportError:
            pass
        
        # 没有可用的交易平台
        cls._default_platform = None
    
    @classmethod
    def set_default_platform(cls, platform: TradingPlatform) -> None:
        """
        设置默认交易平台。
        
        Args:
            platform: 交易平台枚举值
        """
        cls._default_platform = platform
