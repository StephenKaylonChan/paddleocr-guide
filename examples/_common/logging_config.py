#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置 - 统一的日志管理系统
Logging Configuration - Unified Logging Management System

本模块提供了统一的日志配置，替代散落在各处的 print() 语句。
通过使用 Python 标准库的 logging 模块，可以实现：
- 日志级别控制（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 控制台和文件双输出
- 格式化的日志信息（时间、模块、级别、消息）
- 彩色控制台输出（可选）

This module provides unified logging configuration to replace scattered
print() statements. Using Python's logging module enables:
- Log level control
- Console and file dual output
- Formatted log messages
- Colored console output (optional)

作者: paddleocr-guide
API 版本: PaddleOCR 3.x
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# =============================================================================
# 日志格式常量
# Log Format Constants
# =============================================================================

# 详细格式 - 包含时间、模块、级别、消息
DETAILED_FORMAT = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"

# 简洁格式 - 仅包含级别和消息
SIMPLE_FORMAT = "%(levelname)-8s | %(message)s"

# 文件格式 - 包含完整信息
FILE_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"

# 时间格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# =============================================================================
# 彩色日志支持
# Colored Log Support
# =============================================================================


# ANSI 颜色代码
class LogColors:
    """日志颜色代码（ANSI 转义序列）"""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 高亮前景色
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


# 日志级别对应的颜色
LEVEL_COLORS = {
    logging.DEBUG: LogColors.CYAN,
    logging.INFO: LogColors.GREEN,
    logging.WARNING: LogColors.YELLOW,
    logging.ERROR: LogColors.RED,
    logging.CRITICAL: LogColors.BRIGHT_RED + LogColors.BOLD,
}


class ColoredFormatter(logging.Formatter):
    """
    彩色日志格式化器

    为控制台输出添加颜色，使日志更易读。
    不同日志级别使用不同颜色：
    - DEBUG: 青色
    - INFO: 绿色
    - WARNING: 黄色
    - ERROR: 红色
    - CRITICAL: 亮红色加粗

    Example:
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(ColoredFormatter(SIMPLE_FORMAT))
        >>> logger.addHandler(handler)
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: bool = True,
    ) -> None:
        """
        初始化彩色格式化器

        Args:
            fmt: 日志格式字符串
            datefmt: 日期格式字符串
            use_colors: 是否启用颜色（在不支持的终端中应禁用）
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and self._supports_color()

    @staticmethod
    def _supports_color() -> bool:
        """
        检测当前终端是否支持颜色

        Returns:
            bool: 是否支持颜色输出
        """
        # 检查是否为终端
        if not hasattr(sys.stdout, "isatty"):
            return False
        if not sys.stdout.isatty():
            return False

        # Windows 需要特殊处理
        if sys.platform == "win32":
            try:
                import os

                return os.environ.get("TERM") is not None or "ANSICON" in os.environ
            except Exception:
                return False

        return True

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录，添加颜色

        Args:
            record: 日志记录对象

        Returns:
            str: 格式化后的日志字符串
        """
        # 保存原始级别名称
        original_levelname = record.levelname

        if self.use_colors:
            # 获取对应的颜色
            color = LEVEL_COLORS.get(record.levelno, "")
            # 添加颜色
            record.levelname = f"{color}{record.levelname}{LogColors.RESET}"

        # 调用父类格式化
        result = super().format(record)

        # 恢复原始级别名称
        record.levelname = original_levelname

        return result


# =============================================================================
# 日志配置函数
# Logging Configuration Functions
# =============================================================================


def setup_logging(
    level: int = logging.INFO,
    *,
    use_colors: bool = True,
    log_to_file: bool = False,
    log_file_path: Optional[str | Path] = None,
    file_level: int = logging.DEBUG,
    format_style: str = "simple",
) -> logging.Logger:
    """
    配置全局日志系统

    该函数设置 Python 日志系统的根配置，包括：
    - 控制台输出（可选彩色）
    - 文件输出（可选）
    - 日志级别控制

    Args:
        level: 控制台日志级别，默认 INFO
        use_colors: 是否使用彩色输出，默认 True
        log_to_file: 是否同时输出到文件，默认 False
        log_file_path: 日志文件路径，默认为 logs/ocr_{date}.log
        file_level: 文件日志级别，默认 DEBUG
        format_style: 格式风格，"simple" 或 "detailed"

    Returns:
        logging.Logger: 配置好的根日志器

    Example:
        >>> # 基本使用
        >>> setup_logging()
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("开始处理...")

        >>> # 同时输出到文件
        >>> setup_logging(log_to_file=True, file_level=logging.DEBUG)
    """
    # 选择格式
    console_format = SIMPLE_FORMAT if format_style == "simple" else DETAILED_FORMAT

    # 获取根日志器
    root_logger = logging.getLogger()

    # 避免重复添加处理器
    if root_logger.handlers:
        return root_logger

    # 设置根日志器级别（使用最低级别，让处理器控制实际输出）
    root_logger.setLevel(logging.DEBUG)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(console_format, DATE_FORMAT, use_colors))
    root_logger.addHandler(console_handler)

    # 添加文件处理器（如果需要）
    if log_to_file:
        # 确定日志文件路径
        if log_file_path is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = log_dir / f"ocr_{datetime.now().strftime('%Y%m%d')}.log"
        else:
            log_file_path = Path(log_file_path)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT, DATE_FORMAT))
        root_logger.addHandler(file_handler)

    # 抑制第三方库的详细日志
    _suppress_third_party_logs()

    return root_logger


def _suppress_third_party_logs() -> None:
    """
    抑制第三方库的详细日志输出

    PaddlePaddle 和其他库可能输出大量日志，
    这里将它们的级别设置为 WARNING 以减少噪音。
    """
    # 抑制 PaddlePaddle 日志
    logging.getLogger("paddle").setLevel(logging.WARNING)
    logging.getLogger("paddleocr").setLevel(logging.WARNING)

    # 抑制 PIL 日志
    logging.getLogger("PIL").setLevel(logging.WARNING)

    # 抑制 urllib3 日志
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # 抑制 matplotlib 日志（如果使用）
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志器实例

    这是一个便捷函数，用于获取指定名称的日志器。
    如果全局日志系统尚未配置，会自动进行配置。

    Args:
        name: 日志器名称，通常使用 __name__

    Returns:
        logging.Logger: 日志器实例

    Example:
        >>> from examples._common.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("处理开始")
    """
    # 确保日志系统已配置
    if not logging.getLogger().handlers:
        setup_logging()

    return logging.getLogger(name)


# =============================================================================
# 上下文日志管理
# Context Logging Management
# =============================================================================


class LogContext:
    """
    日志上下文管理器

    用于在特定代码块中临时修改日志配置，
    退出时自动恢复原有配置。

    Example:
        >>> with LogContext(level=logging.DEBUG):
        ...     logger.debug("这条消息会显示")
        >>> logger.debug("这条消息不会显示")
    """

    def __init__(
        self,
        level: Optional[int] = None,
        logger_name: Optional[str] = None,
    ) -> None:
        """
        初始化日志上下文

        Args:
            level: 临时日志级别
            logger_name: 要修改的日志器名称，None 表示根日志器
        """
        self.level = level
        self.logger_name = logger_name
        self._original_level: Optional[int] = None

    def __enter__(self) -> "LogContext":
        """进入上下文，保存并修改配置"""
        logger = logging.getLogger(self.logger_name)
        self._original_level = logger.level
        if self.level is not None:
            logger.setLevel(self.level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文，恢复原有配置"""
        if self._original_level is not None:
            logger = logging.getLogger(self.logger_name)
            logger.setLevel(self._original_level)


# =============================================================================
# 进度日志
# Progress Logging
# =============================================================================


class ProgressLogger:
    """
    进度日志器 - 用于批量处理时显示进度

    提供了格式化的进度输出，包括当前进度、百分比等信息。

    Example:
        >>> progress = ProgressLogger(total=100, description="处理图片")
        >>> for i in range(100):
        ...     # 处理逻辑
        ...     progress.update(i + 1)
        >>> progress.finish()
    """

    def __init__(
        self,
        total: int,
        description: str = "处理中",
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        初始化进度日志器

        Args:
            total: 总任务数
            description: 任务描述
            logger: 使用的日志器，默认使用模块日志器
        """
        self.total = total
        self.description = description
        self.logger = logger or get_logger(__name__)
        self.current = 0
        self.start_time = datetime.now()

    def update(self, current: Optional[int] = None, message: str = "") -> None:
        """
        更新进度

        Args:
            current: 当前进度，None 表示自增 1
            message: 附加消息
        """
        if current is None:
            self.current += 1
        else:
            self.current = current

        percentage = (self.current / self.total) * 100
        progress_msg = f"[{self.current}/{self.total}] ({percentage:.1f}%) {self.description}"

        if message:
            progress_msg += f" - {message}"

        self.logger.info(progress_msg)

    def finish(self, message: str = "完成") -> None:
        """
        完成进度

        Args:
            message: 完成消息
        """
        elapsed = datetime.now() - self.start_time
        self.logger.info(
            f"{self.description} {message}. "
            f"总计: {self.total} 项, 耗时: {elapsed.total_seconds():.2f} 秒"
        )
