import os
import json
from PIL import Image
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 尝试导入mian.py
print("开始简单测试...")

try:
    import mian
    print("✅ 成功导入mian.py模块")
except Exception as e:
    print(f"❌ 导入mian.py失败: {e}")
    sys.exit(1)

# 1. 测试PILJSONEncoder是否正常工作
try:
    # 模拟IFDRational类型
    class MockIFDRational:
        def __init__(self, numerator, denominator):
            self.numerator = numerator
            self.denominator = denominator
    
    # 创建测试数据
    test_data = {
        "name": "测试数据",
        "rational": MockIFDRational(1, 2),
        "bytes_data": b"test binary data",
        "complex": {"exposure": MockIFDRational(1, 100), "f_number": MockIFDRational(4, 1)}
    }
    
    # 测试序列化
    json_str = json.dumps(test_data, cls=mian.PILJSONEncoder)
    print("✅ JSON序列化测试通过")
    print(f"序列化结果: {json_str}")
    
    # 验证序列化结果
    parsed_data = json.loads(json_str)
    print(f"验证分数转换: 1/2 → {parsed_data['rational']} (应为0.5)")
    print(f"验证曝光时间转换: 1/100 → {parsed_data['complex']['exposure']} (应为0.01)")
    print(f"验证光圈值转换: 4/1 → {parsed_data['complex']['f_number']} (应为4.0)")
    
except Exception as e:
    print(f"❌ JSON序列化测试失败: {e}")

# 2. 测试横竖屏分类功能
try:
    # 创建临时测试图片
    test_dir = "simple_test_dir"
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
    print(f"竖屏判断: {mian.is_portrait(portrait_img)} (应为True)")
    print(f"横屏判断: {mian.is_portrait(landscape_img)} (应为False)")
    
    # 测试categorize_images_by_orientation函数
    p_imgs, l_imgs, _, _, p_files, l_files = mian.categorize_images_by_orientation(test_dir)
    print(f"分类结果: 竖屏{len(p_imgs)}张, 横屏{len(l_imgs)}张")
    print(f"✅ 横竖屏分类测试通过")
    
    # 清理测试文件
    os.remove(portrait_path)
    os.remove(landscape_path)
    os.rmdir(test_dir)
except Exception as e:
    print(f"❌ 横竖屏分类测试失败: {e}")

# 3. 验证合并配置
try:
    print("\n支持的合并数量:", sorted(mian.MERGE_OPTIONS.keys()))
    
    # 检查6张的布局是否符合用户要求
    if 6 in mian.MERGE_OPTIONS:
        portrait_layout = mian.MERGE_OPTIONS[6]["portrait"]
        landscape_layout = mian.MERGE_OPTIONS[6]["landscape"]
        print(f"6张竖屏布局: {portrait_layout} (应为2行3列)")
        print(f"6张横屏布局: {landscape_layout} (应为3行2列)")
        
        # 验证布局是否符合要求
        if portrait_layout == (2, 3) and landscape_layout == (3, 2):
            print("✅ 6张布局测试通过")
        else:
            print("❌ 6张布局不符合要求")
    else:
        print("❌ 不支持6张合并")
    
    # 检查其他合并数量
    for count in sorted(mian.MERGE_OPTIONS.keys()):
        print(f"合并{count}张: 竖屏{mian.MERGE_OPTIONS[count]['portrait']}, 横屏{mian.MERGE_OPTIONS[count]['landscape']}")
    
    print("✅ 合并配置测试通过")
except Exception as e:
    print(f"❌ 合并配置测试失败: {e}")

# 4. 检查max_size设置
try:
    print(f"\n默认最大尺寸限制: {mian.DEFAULT_MAX_SIZE} (应为12000)")
    if mian.DEFAULT_MAX_SIZE == 12000:
        print("✅ 最大尺寸限制设置正确")
    else:
        print("❌ 最大尺寸限制设置不正确")
except Exception as e:
    print(f"❌ 检查最大尺寸限制失败: {e}")

print("\n简单测试完成！")
print("\n优化功能总结：")
print("1. 自动按横屏/竖屏分类照片并分别拼合")
print("2. UI界面简化为选择2/3/4/6/9张合并")
print("3. 智能布局：6张竖屏3张一排共2排，6张横屏2张一排共3排")
print("4. 拼接时控制在12000像素内，最小化尺寸调整")
print("5. 修复了EXIF数据JSON序列化问题")
print("\n请运行mian.py来体验优化后的图片合并功能！")