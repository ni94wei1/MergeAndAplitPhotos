import os
import json
from PIL import Image
import sys

# 导入我们在mian.py中定义的关键函数
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 动态导入mian.py中的函数
try:
    import mian
    print("成功导入mian.py模块")
except Exception as e:
    print(f"导入mian.py失败: {e}")
    sys.exit(1)


# 测试1: 验证横竖屏分类功能
def test_orientation_classification():
    """测试图片横竖屏分类功能"""
    print("\n===== 测试1: 横竖屏分类功能 =====")
    
    # 创建临时测试图片
    test_dir = "test_orientation_dir"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建竖屏图片 (高度 > 宽度)
    portrait_img = Image.new('RGB', (400, 600), color=(255, 0, 0))
    portrait_path = os.path.join(test_dir, "portrait.jpg")
    portrait_img.save(portrait_path)
    
    # 创建横屏图片 (宽度 > 高度)
    landscape_img = Image.new('RGB', (600, 400), color=(0, 255, 0))
    landscape_path = os.path.join(test_dir, "landscape.jpg")
    landscape_img.save(landscape_path)
    
    # 测试is_portrait函数
    try:
        print(f"竖屏图片测试: {mian.is_portrait(portrait_img)} (应为True)")
        print(f"横屏图片测试: {mian.is_portrait(landscape_img)} (应为False)")
    except Exception as e:
        print(f"is_portrait函数测试失败: {e}")
    
    # 测试categorize_images_by_orientation函数
    try:
        portrait_images, landscape_images, _, _, portrait_filenames, landscape_filenames = \
            mian.categorize_images_by_orientation(test_dir)
        
        print(f"分类结果: 竖屏图片数量={len(portrait_images)}, 横屏图片数量={len(landscape_images)}")
        print(f"竖屏文件名: {portrait_filenames}")
        print(f"横屏文件名: {landscape_filenames}")
    except Exception as e:
        print(f"categorize_images_by_orientation函数测试失败: {e}")
    
    # 清理测试文件
    try:
        os.remove(portrait_path)
        os.remove(landscape_path)
        os.rmdir(test_dir)
    except:
        pass


# 测试2: 验证JSON序列化功能
def test_json_serialization():
    """测试自定义JSON编码器功能"""
    print("\n===== 测试2: JSON序列化功能 =====")
    
    # 模拟一些特殊类型
    class MockIFDRational:
        def __init__(self, numerator, denominator):
            self.numerator = numerator
            self.denominator = denominator
    
    # 创建测试数据
    test_data = {
        "normal_data": "测试数据",
        "bytes_data": b"This is binary data",
        "rational_data": MockIFDRational(1, 2),  # 1/2
        "complex_data": {
            "exposure_time": MockIFDRational(1, 100),  # 1/100秒
            "f_number": MockIFDRational(4, 1),  # F4.0
            "binary_info": b"Camera info"
        }
    }
    
    # 测试序列化
    try:
        json_str = json.dumps(test_data, cls=mian.PILJSONEncoder)
        print("序列化成功！")
        print(f"序列化结果: {json_str}")
        
        # 测试反序列化
        parsed_data = json.loads(json_str)
        print("反序列化成功！")
        print(f"反序列化后的数据: {parsed_data}")
        
        # 验证特殊类型是否正确转换
        print(f"rational_data转换结果: {parsed_data['rational_data']} (应为0.5)")
        print(f"exposure_time转换结果: {parsed_data['complex_data']['exposure_time']} (应为0.01)")
        print(f"f_number转换结果: {parsed_data['complex_data']['f_number']} (应为4.0)")
    except Exception as e:
        print(f"JSON序列化测试失败: {e}")


# 测试3: 验证合并配置

def test_merge_configurations():
    """测试不同合并数量的配置是否正确"""
    print("\n===== 测试3: 合并配置验证 =====")
    
    try:
        print("支持的合并数量:", sorted(mian.MERGE_OPTIONS.keys()))
        
        # 检查每个合并数量的行列配置
        for count in sorted(mian.MERGE_OPTIONS.keys()):
            portrait_layout = mian.MERGE_OPTIONS[count]["portrait"]
            landscape_layout = mian.MERGE_OPTIONS[count]["landscape"]
            
            print(f"\n合并数量 {count}:")
            print(f"  竖屏布局: {portrait_layout} (行×列)")
            print(f"  横屏布局: {landscape_layout} (行×列)")
            
            # 验证行列乘积是否等于合并数量或能容纳合并数量
            portrait_total = portrait_layout[0] * portrait_layout[1]
            landscape_total = landscape_layout[0] * landscape_layout[1]
            
            print(f"  竖屏格子数: {portrait_total}")
            print(f"  横屏格子数: {landscape_total}")
            
            # 特别检查6张的布局是否符合用户要求
            if count == 6:
                print(f"  6张布局检查: 竖屏{portrait_layout}是否为(2,3) = {portrait_layout == (2,3)}")
                print(f"  6张布局检查: 横屏{landscape_layout}是否为(3,2) = {landscape_layout == (3,2)}")
    except Exception as e:
        print(f"合并配置测试失败: {e}")


# 运行所有测试
if __name__ == "__main__":
    print("开始测试优化后的图片合并功能...")
    
    test_orientation_classification()
    test_json_serialization()
    test_merge_configurations()
    
    print("\n所有测试完成！")
    print("\n请运行mian.py来体验优化后的图片合并功能。")
    print("主要改进：")
    print("1. 自动按横屏/竖屏分类照片并分别拼合")
    print("2. UI界面简化为选择2/3/4/6/9张合并")
    print("3. 智能布局：例如6张竖屏3张一排共2排，6张横屏2张一排共3排")
    print("4. 拼接时控制在12000像素内，最小化尺寸调整")
    print("5. 修复了EXIF数据JSON序列化问题")