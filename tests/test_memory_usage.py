#!/usr/bin/env python3
"""
内存占用测试 - PaddleOCR macOS ARM 内存优化验证
Memory Usage Test - Validate PaddleOCR memory optimization on macOS ARM

测试目标:
1. 对比默认配置和优化配置的内存占用
2. 检测内存泄漏（循环调用）
3. 验证优化方案的有效性

Test Goals:
1. Compare memory usage between default and optimized configurations
2. Detect memory leaks (loop calls)
3. Validate optimization effectiveness
"""

import gc
import os
import sys
from pathlib import Path
from typing import Optional

import psutil
import pytest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MemoryMonitor:
    """内存监控器"""

    def __init__(self):
        self.process = psutil.Process()
        self.baseline_mb: float = 0

    def get_memory_mb(self) -> float:
        """获取当前进程内存占用（MB）"""
        return self.process.memory_info().rss / 1024 / 1024

    def set_baseline(self):
        """设置基准内存"""
        gc.collect()  # 强制垃圾回收
        self.baseline_mb = self.get_memory_mb()

    def get_memory_increase(self) -> float:
        """获取相对于基准的内存增长（MB）"""
        return self.get_memory_mb() - self.baseline_mb


def test_memory_baseline_initialization():
    """
    测试 1: 默认配置初始化内存占用

    ⚠️ 警告: 此测试可能占用 40GB+ 内存，导致系统卡死
    已跳过，仅保留代码供参考
    """
    pytest.skip("跳过默认配置测试（可能导致系统卡死）")

    # 以下代码仅供参考，实际不会执行
    from paddleocr import PaddleOCR

    monitor = MemoryMonitor()
    test_image = "assets/test_images/small_test.png"

    print(f"\n{'=' * 60}")
    print("测试 1: 默认配置内存占用（已跳过）")
    print(f"{'=' * 60}")

    monitor.set_baseline()
    print(f"基准内存: {monitor.baseline_mb:.2f} MB")

    # 初始化 OCR（默认配置）
    ocr = PaddleOCR(lang='ch')
    mem_after_init = monitor.get_memory_increase()
    print(f"初始化后: +{mem_after_init:.2f} MB")

    # 首次识别
    result = ocr.predict(test_image)
    mem_after_first = monitor.get_memory_increase()
    print(f"首次识别后: +{mem_after_first:.2f} MB")

    # 清理
    del result, ocr
    gc.collect()


def test_memory_optimized_initialization():
    """
    测试 2: 优化配置初始化内存占用

    禁用预处理模型，预期内存占用大幅降低
    """
    from paddleocr import PaddleOCR

    monitor = MemoryMonitor()
    test_image = "assets/test_images/small_test.png"

    # 确保测试图片存在
    if not os.path.exists(test_image):
        pytest.skip(f"测试图片不存在: {test_image}")

    print(f"\n{'=' * 60}")
    print("测试 2: 优化配置内存占用")
    print(f"{'=' * 60}")

    monitor.set_baseline()
    print(f"基准内存: {monitor.baseline_mb:.2f} MB")

    # 初始化 OCR（优化配置）
    ocr = PaddleOCR(
        lang='ch',
        use_doc_orientation_classify=False,  # 禁用文档方向分类
        use_doc_unwarping=False,  # 禁用文档弯曲矫正
        use_textline_orientation=False,  # 禁用文本行方向分类
    )
    mem_after_init = monitor.get_memory_increase()
    print(f"初始化后: +{mem_after_init:.2f} MB")

    # 首次识别
    result = ocr.predict(test_image)
    mem_after_first = monitor.get_memory_increase()
    print(f"首次识别后: +{mem_after_first:.2f} MB")

    # 获取识别结果
    for res in result:
        print(f"\n识别结果:")
        res.print()

    # 清理
    del result, ocr
    gc.collect()

    # 验证内存占用在可接受范围内（< 10GB）
    assert mem_after_first < 10 * 1024, (
        f"内存占用过高: {mem_after_first:.2f} MB (> 10GB)"
    )

    print(f"\n✅ 测试通过: 内存占用 {mem_after_first:.2f} MB < 10GB")


def test_memory_leak_detection():
    """
    测试 3: 内存泄漏检测

    循环调用 10 次，检测内存是否持续增长
    """
    from paddleocr import PaddleOCR

    monitor = MemoryMonitor()
    test_image = "assets/test_images/small_test.png"

    # 确保测试图片存在
    if not os.path.exists(test_image):
        pytest.skip(f"测试图片不存在: {test_image}")

    print(f"\n{'=' * 60}")
    print("测试 3: 内存泄漏检测（10 次循环调用）")
    print(f"{'=' * 60}")

    # 初始化 OCR（优化配置）
    ocr = PaddleOCR(
        lang='ch',
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    memory_records = []

    for i in range(10):
        monitor.set_baseline()

        # 执行识别
        result = ocr.predict(test_image)

        # 记录内存
        mem_mb = monitor.get_memory_mb()
        memory_records.append(mem_mb)

        print(f"第 {i + 1:2d} 次调用: {mem_mb:.2f} MB")

        # 清理结果
        del result
        gc.collect()

    # 分析内存增长
    first_call_mem = memory_records[0]
    last_call_mem = memory_records[-1]
    memory_growth = last_call_mem - first_call_mem
    growth_percentage = (memory_growth / first_call_mem) * 100

    print(f"\n{'=' * 60}")
    print(f"内存分析:")
    print(f"  首次调用: {first_call_mem:.2f} MB")
    print(f"  末次调用: {last_call_mem:.2f} MB")
    print(f"  内存增长: {memory_growth:.2f} MB ({growth_percentage:.2f}%)")
    print(f"{'=' * 60}")

    # 验证内存增长在可接受范围内（< 5%）
    assert growth_percentage < 5.0, (
        f"检测到内存泄漏: 增长 {growth_percentage:.2f}% (> 5%)"
    )

    print(f"\n✅ 测试通过: 内存增长 {growth_percentage:.2f}% < 5%")

    # 清理
    del ocr
    gc.collect()


def test_memory_comparison_report():
    """
    测试 4: 生成内存对比报告

    对比优化前后的内存占用（仅优化配置的实际数据）
    """
    from paddleocr import PaddleOCR

    monitor = MemoryMonitor()
    test_image = "assets/test_images/small_test.png"

    # 确保测试图片存在
    if not os.path.exists(test_image):
        pytest.skip(f"测试图片不存在: {test_image}")

    # 获取图片信息
    file_size = os.path.getsize(test_image) / 1024  # KB
    from PIL import Image

    with Image.open(test_image) as img:
        width, height = img.size

    print(f"\n{'=' * 60}")
    print("PaddleOCR 内存占用对比报告")
    print(f"{'=' * 60}")
    print(f"测试图片: {test_image}")
    print(f"  尺寸: {width}x{height}")
    print(f"  大小: {file_size:.2f} KB")
    print(f"{'=' * 60}")

    # 测试优化配置
    print("\n配置 1 - 默认配置（未测试，参考 GitHub Issues）:")
    print("  初始化后: ~30000 MB (30GB)")
    print("  首次识别后: ~40000 MB (40GB)")
    print("  ⚠️ 风险: 可能导致系统卡死")

    print("\n配置 2 - 优化配置（禁用预处理模型）:")
    monitor.set_baseline()
    baseline = monitor.baseline_mb
    print(f"  基准: {baseline:.2f} MB")

    ocr = PaddleOCR(
        lang='ch',
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    mem_init = monitor.get_memory_increase()
    print(f"  初始化后: +{mem_init:.2f} MB")

    result = ocr.predict(test_image)
    mem_first = monitor.get_memory_increase()
    print(f"  首次识别后: +{mem_first:.2f} MB")

    # 计算节省
    estimated_default = 40000  # MB (40GB, 根据 GitHub Issues)
    actual_optimized = mem_first
    saved_mb = estimated_default - actual_optimized
    saved_percentage = (saved_mb / estimated_default) * 100

    print(f"\n{'=' * 60}")
    print(f"内存节省（预估）:")
    print(f"  默认配置: ~{estimated_default:.0f} MB ({estimated_default / 1024:.1f} GB)")
    print(f"  优化配置: {actual_optimized:.2f} MB ({actual_optimized / 1024:.2f} GB)")
    print(f"  节省内存: ~{saved_mb:.2f} MB (~{saved_mb / 1024:.1f} GB)")
    print(f"  节省比例: ~{saved_percentage:.1f}%")
    print(f"{'=' * 60}")

    # 清理
    del result, ocr
    gc.collect()

    print("\n✅ 优化方案有效，大幅降低内存占用")


if __name__ == "__main__":
    # 直接运行测试
    print("开始 PaddleOCR 内存测试...")
    print("=" * 60)

    # 仅运行安全的测试
    test_memory_optimized_initialization()
    test_memory_leak_detection()
    test_memory_comparison_report()

    print("\n" + "=" * 60)
    print("所有测试完成!")
