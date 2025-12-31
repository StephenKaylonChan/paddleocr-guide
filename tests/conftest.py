# -*- coding: utf-8 -*-
"""
Pytest 配置和 Fixtures
Pytest Configuration and Fixtures

本文件包含所有测试共享的 fixtures 和配置。
This file contains shared fixtures and configurations for all tests.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Generator, Optional

import pytest

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# 路径相关 Fixtures
# Path Related Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    项目根目录

    Returns:
        Path: 项目根目录路径
    """
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def examples_dir(project_root: Path) -> Path:
    """
    示例代码目录

    Returns:
        Path: examples 目录路径
    """
    return project_root / "examples"


@pytest.fixture(scope="session")
def test_images_dir(project_root: Path) -> Path:
    """
    测试图片目录

    如果目录不存在，则创建它。

    Returns:
        Path: 测试图片目录路径
    """
    path = project_root / "test_images"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def outputs_dir(project_root: Path) -> Path:
    """
    测试输出目录

    如果目录不存在，则创建它。

    Returns:
        Path: 测试输出目录路径
    """
    path = project_root / "test_outputs"
    path.mkdir(parents=True, exist_ok=True)
    return path


# =============================================================================
# 测试图片 Fixtures
# Test Image Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def sample_image_path(test_images_dir: Path) -> Optional[Path]:
    """
    示例测试图片路径

    查找测试图片目录中的第一张图片。

    Returns:
        Optional[Path]: 图片路径，如果没有找到则返回 None
    """
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}

    for ext in extensions:
        images = list(test_images_dir.glob(f"*{ext}"))
        if images:
            return images[0]

    return None


@pytest.fixture
def create_test_image(test_images_dir: Path) -> Generator[Path, None, None]:
    """
    创建临时测试图片

    创建一个简单的测试图片用于测试，测试完成后自动删除。

    Yields:
        Path: 临时测试图片路径
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        pytest.skip("Pillow 未安装")

    # 创建测试图片
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体，如果不可用则使用默认字体
    try:
        # macOS 系统字体
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    except (OSError, IOError):
        try:
            # Linux 系统字体
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except (OSError, IOError):
            # 使用默认字体
            font = ImageFont.load_default()

    # 绘制测试文本
    draw.text((50, 50), "测试文本 Test Text", fill="black", font=font)
    draw.text((50, 100), "PaddleOCR 3.x", fill="blue", font=font)

    # 保存图片
    test_image_path = test_images_dir / "_pytest_temp_test.png"
    img.save(test_image_path)

    yield test_image_path

    # 清理
    if test_image_path.exists():
        test_image_path.unlink()


# =============================================================================
# OCR 相关 Fixtures
# OCR Related Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def paddleocr_available() -> bool:
    """
    检查 PaddleOCR 是否可用

    Returns:
        bool: PaddleOCR 是否已安装且可导入
    """
    try:
        import paddleocr

        return True
    except ImportError:
        return False


@pytest.fixture
def skip_without_paddleocr(paddleocr_available: bool) -> None:
    """
    如果 PaddleOCR 不可用则跳过测试

    Usage:
        def test_ocr(skip_without_paddleocr):
            # 此测试需要 PaddleOCR
            ...
    """
    if not paddleocr_available:
        pytest.skip("PaddleOCR 未安装")


# =============================================================================
# 公共模块 Fixtures
# Common Module Fixtures
# =============================================================================


@pytest.fixture
def common_module():
    """
    导入公共模块

    Returns:
        module: examples._common 模块
    """
    try:
        from examples import _common

        return _common
    except ImportError as e:
        pytest.skip(f"无法导入 examples._common: {e}")


@pytest.fixture
def path_config(common_module):
    """
    获取路径配置

    Returns:
        PathConfig: 路径配置对象
    """
    return common_module.PATH_CONFIG


# =============================================================================
# 测试辅助函数
# Test Helper Functions
# =============================================================================


def assert_file_exists(path: Path, message: str = "") -> None:
    """
    断言文件存在

    Args:
        path: 文件路径
        message: 错误消息

    Raises:
        AssertionError: 文件不存在时
    """
    assert path.exists(), message or f"文件不存在: {path}"


def assert_directory_exists(path: Path, message: str = "") -> None:
    """
    断言目录存在

    Args:
        path: 目录路径
        message: 错误消息

    Raises:
        AssertionError: 目录不存在时
    """
    assert path.is_dir(), message or f"目录不存在: {path}"


def assert_valid_ocr_result(result: dict[str, Any]) -> None:
    """
    断言 OCR 结果格式正确

    Args:
        result: OCR 结果字典

    Raises:
        AssertionError: 结果格式不正确时
    """
    assert isinstance(result, dict), "结果必须是字典"
    assert "text" in result, "结果必须包含 'text' 字段"
    assert "confidence" in result, "结果必须包含 'confidence' 字段"
    assert 0.0 <= result["confidence"] <= 1.0, "置信度必须在 0-1 之间"
