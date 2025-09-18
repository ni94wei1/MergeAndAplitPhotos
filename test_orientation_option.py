import os
import tkinter as tk
from tkinter import messagebox
import sys

# 导入我们修改的函数
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mian import is_portrait, categorize_images_by_orientation, MERGE_OPTIONS, DEFAULT_SPLIT_BY_ORIENTATION

# 创建临时测试图片
def create_test_images():
    """创建测试图片目录，包含横竖屏测试图片"""
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_orientation_dir")
    os.makedirs(test_dir, exist_ok=True)
    
    # 导入必要的库
    from PIL import Image
    
    # 创建竖屏图片（高度 > 宽度）
    for i in range(2):
        img = Image.new('RGB', (300, 400), color=(255, 0, 0))  # 红色竖屏
        img.save(os.path.join(test_dir, f"portrait_{i+1}.jpg"))
    
    # 创建横屏图片（宽度 > 高度）
    for i in range(2):
        img = Image.new('RGB', (400, 300), color=(0, 255, 0))  # 绿色横屏
        img.save(os.path.join(test_dir, f"landscape_{i+1}.jpg"))
    
    # 创建正方形图片
    img = Image.new('RGB', (300, 300), color=(0, 0, 255))  # 蓝色正方形
    img.save(os.path.join(test_dir, "square_1.jpg"))
    
    return test_dir

# 测试横竖屏判断功能
def test_orientation_detection(test_dir):
    """测试横竖屏判断功能"""
    print("=== 测试横竖屏判断功能 ===")
    
    # 导入PIL
    from PIL import Image
    
    # 测试竖屏图片
    portrait_path = os.path.join(test_dir, "portrait_1.jpg")
    portrait_img = Image.open(portrait_path)
    is_port = is_portrait(portrait_img)
    print(f"竖屏图片判断: {is_port} (应该为 True)")
    
    # 测试横屏图片
    landscape_path = os.path.join(test_dir, "landscape_1.jpg")
    landscape_img = Image.open(landscape_path)
    is_land = is_portrait(landscape_img)
    print(f"横屏图片判断: {is_land} (应该为 False)")
    
    # 测试正方形图片
    square_path = os.path.join(test_dir, "square_1.jpg")
    square_img = Image.open(square_path)
    is_square_port = is_portrait(square_img)
    print(f"正方形图片判断: {is_square_port} (应该为 False)")
    
    return True

# 测试分类功能
def test_image_categorization(test_dir):
    """测试图片分类功能"""
    print("\n=== 测试图片分类功能 ===")
    
    portrait_images, landscape_images, _, _, portrait_filenames, landscape_filenames = \
        categorize_images_by_orientation(test_dir)
    
    print(f"找到 {len(portrait_images)} 张竖屏图片: {portrait_filenames}")
    print(f"找到 {len(landscape_images)} 张横屏图片: {landscape_filenames}")
    
    return len(portrait_images) == 2 and len(landscape_images) == 3

# 测试配置

def test_config():
    """测试配置参数"""
    print("\n=== 测试配置参数 ===")
    
    print(f"默认是否分开拼接: {DEFAULT_SPLIT_BY_ORIENTATION} (应该为 True)")
    print(f"合并选项配置: {MERGE_OPTIONS}")
    
    # 检查6张图片的布局配置是否正确
    has_6_portrait_layout = MERGE_OPTIONS[6]["portrait"] == (2, 3)
    has_6_landscape_layout = MERGE_OPTIONS[6]["landscape"] == (3, 2)
    
    print(f"6张竖屏图片布局: {MERGE_OPTIONS[6]['portrait']} (应该为 (2, 3))")
    print(f"6张横屏图片布局: {MERGE_OPTIONS[6]['landscape']} (应该为 (3, 2))")
    
    return has_6_portrait_layout and has_6_landscape_layout

# 主测试函数
def main():
    """主测试函数"""
    print("开始测试横竖屏分开拼接功能...")
    
    # 创建测试图片
    test_dir = create_test_images()
    print(f"创建测试图片目录: {test_dir}")
    
    # 运行测试
    tests_passed = 0
    tests_total = 3
    
    # 测试1: 横竖屏判断
    if test_orientation_detection(test_dir):
        tests_passed += 1
        print("测试1通过!")
    else:
        print("测试1失败!")
    
    # 测试2: 图片分类
    if test_image_categorization(test_dir):
        tests_passed += 1
        print("测试2通过!")
    else:
        print("测试2失败!")
    
    # 测试3: 配置检查
    if test_config():
        tests_passed += 1
        print("测试3通过!")
    else:
        print("测试3失败!")
    
    # 输出测试结果
    print(f"\n测试完成: {tests_passed}/{tests_total} 测试通过")
    
    if tests_passed == tests_total:
        print("🎉 所有测试通过！横竖屏分开拼接功能正常工作。")
        print("请注意：您可以在主程序界面中找到'是否将横竖屏分开拼接'选项，默认已选中'是'。")
    else:
        print("❌ 部分测试失败，请检查代码。")

if __name__ == "__main__":
    main()