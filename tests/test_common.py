# -*- coding: utf-8 -*-
"""
公共模块测试
Common Module Tests

测试 examples/_common/ 模块中的所有组件。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# 导入测试
# Import Tests
# =============================================================================


class TestImports:
    """测试模块导入"""

    def test_import_common_module(self):
        """测试导入 _common 模块"""
        from examples import _common

        assert _common is not None

    def test_import_exceptions(self):
        """测试导入异常类"""
        from examples._common import (
            OCRConfigError,
            OCRException,
            OCRFileNotFoundError,
            OCRInitError,
            OCROutputError,
            OCRProcessError,
        )

        assert issubclass(OCRInitError, OCRException)
        assert issubclass(OCRProcessError, OCRException)
        assert issubclass(OCRFileNotFoundError, OCRException)
        assert issubclass(OCROutputError, OCRException)
        assert issubclass(OCRConfigError, OCRException)

    def test_import_logging(self):
        """测试导入日志模块"""
        from examples._common import (
            ProgressLogger,
            get_logger,
            setup_logging,
        )

        assert callable(setup_logging)
        assert callable(get_logger)
        assert ProgressLogger is not None

    def test_import_config(self):
        """测试导入配置模块"""
        from examples._common import (
            PATH_CONFIG,
            SUPPORTED_IMAGE_EXTENSIONS,
            SUPPORTED_LANGUAGES,
        )

        assert PATH_CONFIG is not None
        assert isinstance(SUPPORTED_IMAGE_EXTENSIONS, (set, frozenset))
        assert isinstance(SUPPORTED_LANGUAGES, dict)

    def test_import_utils(self):
        """测试导入工具函数"""
        from examples._common import (
            ensure_directory,
            find_images,
            format_ocr_result,
            load_json,
            save_json,
            validate_file_exists,
        )

        assert callable(ensure_directory)
        assert callable(validate_file_exists)
        assert callable(find_images)
        assert callable(format_ocr_result)
        assert callable(save_json)
        assert callable(load_json)


# =============================================================================
# 异常类测试
# Exception Class Tests
# =============================================================================


class TestExceptions:
    """测试自定义异常类"""

    def test_ocr_exception_basic(self):
        """测试基础异常"""
        from examples._common import OCRException

        exc = OCRException("测试错误")
        assert str(exc) == "测试错误"

    def test_ocr_exception_with_error_code(self):
        """测试带错误代码的异常"""
        from examples._common import OCRException

        exc = OCRException("测试错误", error_code="E001")
        assert exc.error_code == "E001"

    def test_ocr_exception_with_details(self):
        """测试带详细信息的异常"""
        from examples._common import OCRException

        exc = OCRException("测试错误", details={"key": "value"})
        assert exc.details == {"key": "value"}

    def test_ocr_init_error(self):
        """测试初始化错误"""
        from examples._common import OCRInitError

        exc = OCRInitError("初始化失败", error_code="E101")
        assert "初始化失败" in str(exc)

    def test_ocr_file_not_found_error(self):
        """测试文件不存在错误"""
        from examples._common import OCRFileNotFoundError

        exc = OCRFileNotFoundError("文件不存在", file_path="/path/to/file")
        assert exc.file_path == "/path/to/file"


# =============================================================================
# 配置测试
# Configuration Tests
# =============================================================================


class TestConfiguration:
    """测试配置模块"""

    def test_path_config_attributes(self):
        """测试路径配置属性"""
        from examples._common import PATH_CONFIG

        assert hasattr(PATH_CONFIG, "project_root")
        assert hasattr(PATH_CONFIG, "examples_dir")
        assert hasattr(PATH_CONFIG, "test_images_dir")
        assert hasattr(PATH_CONFIG, "outputs_dir")

    def test_path_config_types(self):
        """测试路径配置类型"""
        from examples._common import PATH_CONFIG

        assert isinstance(PATH_CONFIG.project_root, Path)
        assert isinstance(PATH_CONFIG.examples_dir, Path)

    def test_supported_image_extensions(self):
        """测试支持的图片格式"""
        from examples._common import SUPPORTED_IMAGE_EXTENSIONS

        assert ".png" in SUPPORTED_IMAGE_EXTENSIONS
        assert ".jpg" in SUPPORTED_IMAGE_EXTENSIONS
        assert ".jpeg" in SUPPORTED_IMAGE_EXTENSIONS

    def test_supported_languages(self):
        """测试支持的语言"""
        from examples._common import SUPPORTED_LANGUAGES

        assert "ch" in SUPPORTED_LANGUAGES
        assert "en" in SUPPORTED_LANGUAGES


# =============================================================================
# 工具函数测试
# Utility Function Tests
# =============================================================================


class TestUtilityFunctions:
    """测试工具函数"""

    def test_ensure_directory(self, tmp_path):
        """测试创建目录"""
        from examples._common import ensure_directory

        new_dir = tmp_path / "new_directory"
        result = ensure_directory(new_dir)

        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_existing(self, tmp_path):
        """测试已存在的目录"""
        from examples._common import ensure_directory

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = ensure_directory(existing_dir)
        assert result == existing_dir

    def test_validate_file_exists(self, tmp_path):
        """测试文件存在验证"""
        from examples._common import OCRFileNotFoundError, validate_file_exists

        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # 应该不抛出异常
        result = validate_file_exists(test_file)
        assert result == test_file

        # 文件不存在应该抛出异常
        with pytest.raises(OCRFileNotFoundError):
            validate_file_exists(tmp_path / "nonexistent.txt")

    def test_is_supported_image(self):
        """测试图片格式检查"""
        from examples._common import is_supported_image

        assert is_supported_image("test.png")
        assert is_supported_image("test.PNG")
        assert is_supported_image("test.jpg")
        assert is_supported_image("test.jpeg")
        assert not is_supported_image("test.txt")
        assert not is_supported_image("test.pdf")

    def test_find_images(self, tmp_path):
        """测试查找图片"""
        from examples._common import find_images

        # 创建测试图片文件（空文件）
        (tmp_path / "image1.png").touch()
        (tmp_path / "image2.jpg").touch()
        (tmp_path / "document.txt").touch()

        images = list(find_images(tmp_path))

        assert len(images) == 2
        assert all(img.suffix.lower() in {".png", ".jpg"} for img in images)

    def test_save_and_load_json(self, tmp_path):
        """测试 JSON 保存和加载"""
        from examples._common import load_json, save_json

        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        json_path = tmp_path / "test.json"

        # 保存
        save_json(data, json_path)
        assert json_path.exists()

        # 加载
        loaded = load_json(json_path)
        assert loaded == data

    def test_get_timestamp(self):
        """测试时间戳生成"""
        from examples._common import get_timestamp

        timestamp = get_timestamp()
        assert isinstance(timestamp, str)
        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS

    def test_format_ocr_result_empty(self):
        """测试格式化空结果"""
        from examples._common import format_ocr_result

        result = format_ocr_result(None)
        assert result == []

        result = format_ocr_result([])
        assert result == []


# =============================================================================
# 日志测试
# Logging Tests
# =============================================================================


class TestLogging:
    """测试日志模块"""

    def test_get_logger(self):
        """测试获取日志器"""
        from examples._common import get_logger

        logger = get_logger("test")
        assert logger is not None
        assert logger.name == "test"

    def test_setup_logging(self):
        """测试设置日志"""
        from examples._common import setup_logging

        # 应该不抛出异常
        setup_logging()

    def test_progress_logger(self):
        """测试进度日志器"""
        from examples._common import ProgressLogger

        progress = ProgressLogger(total=10, description="测试")
        assert progress.total == 10

        # 更新进度
        progress.update(5, "处理中")
        progress.finish()


# =============================================================================
# 语言工具测试
# Language Utility Tests
# =============================================================================


class TestLanguageUtilities:
    """测试语言工具函数"""

    def test_is_supported_language(self):
        """测试语言支持检查"""
        from examples._common import is_supported_language

        assert is_supported_language("ch")
        assert is_supported_language("en")
        assert is_supported_language("japan")
        assert not is_supported_language("invalid_lang")

    def test_normalize_language(self):
        """测试语言代码标准化"""
        from examples._common import normalize_language

        assert normalize_language("ch") == "ch"
        assert normalize_language("CH") == "ch"
        assert normalize_language("chinese") == "ch"
        assert normalize_language("en") == "en"
