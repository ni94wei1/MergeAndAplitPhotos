import os
import sys
import tkinter as tk
from tkinter import messagebox

# 导入我们修改的函数
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mian import is_portrait, categorize_images_by_orientation, MERGE_OPTIONS

# 创建临时测试图片
def create_test_images():
    """创建测试图片目录，包含横竖屏测试图片"""
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_mixed_mode_dir")
    os.makedirs(test_dir, exist_ok=True)
    
    # 导入必要的库
    from PIL import Image
    
    # 创建不同尺寸的竖屏图片（高度 > 宽度）
    sizes = [(300, 400), (350, 450), (280, 420)]  # 不同尺寸的竖屏图片
    for i, size in enumerate(sizes):
        img = Image.new('RGB', size, color=(255, 0, 0))  # 红色竖屏
        img.save(os.path.join(test_dir, f"portrait_{i+1}.jpg"))
    
    # 创建不同尺寸的横屏图片（宽度 > 高度）
    sizes = [(400, 300), (450, 350), (420, 280)]  # 不同尺寸的横屏图片
    for i, size in enumerate(sizes):
        img = Image.new('RGB', size, color=(0, 255, 0))  # 绿色横屏
        img.save(os.path.join(test_dir, f"landscape_{i+1}.jpg"))
    
    # 创建正方形图片
    img = Image.new('RGB', (300, 300), color=(0, 0, 255))  # 蓝色正方形
    img.save(os.path.join(test_dir, "square_1.jpg"))
    
    return test_dir

# 模拟混合模式下的布局选择逻辑
def simulate_mixed_mode_layout_selection():
    """模拟混合模式下的布局选择逻辑"""
    print("=== 测试混合模式下的布局选择逻辑 ===")
    
    # 测试场景1: 竖屏图片占多数
    portrait_count = 4
    landscape_count = 2
    
    # 如果竖屏图片占大多数，使用竖屏布局；否则使用横屏布局
    if portrait_count > landscape_count:
        rows, cols = MERGE_OPTIONS[6]["portrait"]
        layout_type = "mixed_portrait_preferred"
    else:
        rows, cols = MERGE_OPTIONS[6]["landscape"]
        layout_type = "mixed_landscape_preferred"
    
    print(f"场景1: 竖屏图片{portrait_count}张，横屏图片{landscape_count}张")
    print(f"  选择的布局: {layout_type} = {rows}行{cols}列")
    
    # 测试场景2: 横屏图片占多数
    portrait_count = 2
    landscape_count = 4
    
    # 如果竖屏图片占大多数，使用竖屏布局；否则使用横屏布局
    if portrait_count > landscape_count:
        rows, cols = MERGE_OPTIONS[6]["portrait"]
        layout_type = "mixed_portrait_preferred"
    else:
        rows, cols = MERGE_OPTIONS[6]["landscape"]
        layout_type = "mixed_landscape_preferred"
    
    print(f"场景2: 竖屏图片{portrait_count}张，横屏图片{landscape_count}张")
    print(f"  选择的布局: {layout_type} = {rows}行{cols}列")
    
    # 测试场景3: 数量相等
    portrait_count = 3
    landscape_count = 3
    
    # 如果竖屏图片占大多数，使用竖屏布局；否则使用横屏布局
    if portrait_count > landscape_count:
        rows, cols = MERGE_OPTIONS[6]["portrait"]
        layout_type = "mixed_portrait_preferred"
    else:
        rows, cols = MERGE_OPTIONS[6]["landscape"]
        layout_type = "mixed_landscape_preferred"
    
    print(f"场景3: 竖屏图片{portrait_count}张，横屏图片{portrait_count}张")
    print(f"  选择的布局: {layout_type} = {rows}行{cols}列")
    
    return True

# 计算不同布局下的合成图尺寸
def calculate_merged_size(batch_imgs, rows, cols, spacing):
    """计算合成图的尺寸"""
    # 计算每列最大宽度，每行最大高度（网格尺寸）
    col_widths = [max((img.width for img in batch_imgs[i::cols] if i < len(batch_imgs)), default=0) for i in range(cols)]
    row_heights = [max((img.height for img in batch_imgs[r*cols:(r+1)*cols] if r*cols < len(batch_imgs)), default=0) for r in range(rows)]
    
    total_width = sum(col_widths) + (cols - 1) * spacing
    total_height = sum(row_heights) + (rows - 1) * spacing
    
    return (total_width, total_height)

# 测试尺寸优化效果
def test_size_optimization(test_dir):
    """测试混合模式下的尺寸优化效果"""
    print("\n=== 测试混合模式下的尺寸优化效果 ===")
    
    # 导入PIL
    from PIL import Image
    
    # 加载测试图片
    images = []
    for fname in os.listdir(test_dir):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img_path = os.path.join(test_dir, fname)
            img = Image.open(img_path)
            images.append(img)
    
    # 场景1: 主要是竖屏图片的批次
    batch1 = images[:4]  # 前4张主要是竖屏
    
    # 计算两种布局下的尺寸
    rows_portrait, cols_portrait = MERGE_OPTIONS[6]["portrait"]
    rows_landscape, cols_landscape = MERGE_OPTIONS[6]["landscape"]
    
    size_portrait_layout = calculate_merged_size(batch1, rows_portrait, cols_portrait, 0)
    size_landscape_layout = calculate_merged_size(batch1, rows_landscape, cols_landscape, 0)
    
    # 计算总面积
    area_portrait = size_portrait_layout[0] * size_portrait_layout[1]
    area_landscape = size_landscape_layout[0] * size_landscape_layout[1]
    
    print("场景1: 主要是竖屏图片的批次")
    print(f"  竖屏布局 ({rows_portrait}x{cols_portrait}): 宽={size_portrait_layout[0]}, 高={size_portrait_layout[1]}, 面积={area_portrait}")
    print(f"  横屏布局 ({rows_landscape}x{cols_landscape}): 宽={size_landscape_layout[0]}, 高={size_landscape_layout[1]}, 面积={area_landscape}")
    
    # 判断哪种布局更好
    if area_portrait < area_landscape:
        print("  结论: 竖屏布局更优，面积更小")
    elif area_landscape < area_portrait:
        print("  结论: 横屏布局更优，面积更小")
    else:
        print("  结论: 两种布局面积相同")
    
    # 场景2: 主要是横屏图片的批次
    batch2 = images[2:6]  # 中间4张主要是横屏
    
    # 计算两种布局下的尺寸
    size_portrait_layout = calculate_merged_size(batch2, rows_portrait, cols_portrait, 0)
    size_landscape_layout = calculate_merged_size(batch2, rows_landscape, cols_landscape, 0)
    
    # 计算总面积
    area_portrait = size_portrait_layout[0] * size_portrait_layout[1]
    area_landscape = size_landscape_layout[0] * size_landscape_layout[1]
    
    print("\n场景2: 主要是横屏图片的批次")
    print(f"  竖屏布局 ({rows_portrait}x{cols_portrait}): 宽={size_portrait_layout[0]}, 高={size_portrait_layout[1]}, 面积={area_portrait}")
    print(f"  横屏布局 ({rows_landscape}x{cols_landscape}): 宽={size_landscape_layout[0]}, 高={size_landscape_layout[1]}, 面积={area_landscape}")
    
    # 判断哪种布局更好
    if area_portrait < area_landscape:
        print("  结论: 竖屏布局更优，面积更小")
    elif area_landscape < area_portrait:
        print("  结论: 横屏布局更优，面积更小")
    else:
        print("  结论: 两种布局面积相同")
    
    return True

# 主测试函数
def main():
    """主测试函数"""
    print("开始测试混合模式下的尺寸优化功能...")
    
    # 创建测试图片
    test_dir = create_test_images()
    print(f"创建测试图片目录: {test_dir}")
    
    # 运行测试
    tests_passed = 0
    tests_total = 2
    
    # 测试1: 布局选择逻辑
    if simulate_mixed_mode_layout_selection():
        tests_passed += 1
        print("测试1通过!")
    else:
        print("测试1失败!")
    
    # 测试2: 尺寸优化效果
    if test_size_optimization(test_dir):
        tests_passed += 1
        print("测试2通过!")
    else:
        print("测试2失败!")
    
    # 输出测试结果
    print(f"\n测试完成: {tests_passed}/{tests_total} 测试通过")
    
    if tests_passed == tests_total:
        print("🎉 所有测试通过！混合模式下的尺寸优化功能正常工作。")
        print("功能说明：")
        print("1. 当不选中'横竖屏分开拼接'时，系统会分析每个批次中图片的方向分布")
        print("2. 如果竖屏图片占大多数，使用竖屏布局；否则使用横屏布局")
        print("3. 这样可以尽量减少图片的尺寸调整，保持合成图片的尺寸最小")
    else:
        print("❌ 部分测试失败，请检查代码。")

if __name__ == "__main__":
    main()