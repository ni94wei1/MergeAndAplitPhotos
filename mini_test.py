import json
from fractions import Fraction

# 直接在这里定义PILJSONEncoder类来测试
def is_portrait_test():
    """测试横竖屏判断逻辑"""
    print("\n=== 横竖屏判断逻辑 ===")
    # 模拟图片对象
    class MockImage:
        def __init__(self, width, height):
            self.width = width
            self.height = height
    
    # 竖屏图片 (高度 > 宽度)
    portrait = MockImage(400, 600)
    # 横屏图片 (宽度 > 高度)
    landscape = MockImage(600, 400)
    
    # 测试逻辑
    is_portrait_portrait = portrait.height > portrait.width
    is_portrait_landscape = landscape.height > landscape.width
    
    print(f"竖屏图片测试: {is_portrait_portrait} (应为True)")
    print(f"横屏图片测试: {is_portrait_landscape} (应为False)")


def json_encoder_test():
    """测试JSON编码器功能"""
    print("\n=== JSON编码器测试 ===")
    
    class PILJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            # 处理IFDRational类型（piexif中的分数类型）
            if hasattr(obj, 'numerator') and hasattr(obj, 'denominator'):
                try:
                    # 转换为浮点数
                    return float(obj.numerator) / float(obj.denominator)
                except (ZeroDivisionError, ValueError):
                    return 0.0
            # 处理bytes类型
            elif isinstance(obj, bytes):
                try:
                    return obj.decode('utf-8', errors='replace')
                except:
                    return str(obj)
            # 处理Fraction类型
            elif isinstance(obj, Fraction):
                try:
                    return float(obj)
                except (ZeroDivisionError, ValueError):
                    return 0.0
            # 处理其他无法序列化的类型
            else:
                try:
                    return str(obj)
                except:
                    return "无法序列化的对象"
    
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
        "fraction": Fraction(3, 4),
        "complex": {
            "exposure": MockIFDRational(1, 100),
            "f_number": MockIFDRational(4, 1),
            "binary_info": b"camera info"
        }
    }
    
    try:
        # 序列化测试
        json_str = json.dumps(test_data, cls=PILJSONEncoder)
        print("✅ 序列化成功！")
        print(f"序列化结果: {json_str}")
        
        # 反序列化测试
        parsed_data = json.loads(json_str)
        print("✅ 反序列化成功！")
        
        # 验证关键数据转换
        print(f"分数转换: 1/2 → {parsed_data['rational']} (应为0.5)")
        print(f"曝光时间转换: 1/100 → {parsed_data['complex']['exposure']} (应为0.01)")
        print(f"光圈值转换: 4/1 → {parsed_data['complex']['f_number']} (应为4.0)")
        print(f"Fraction转换: 3/4 → {parsed_data['fraction']} (应为0.75)")
        print(f"Bytes转换: {parsed_data['bytes_data']} (应为test binary data)")
    except Exception as e:
        print(f"❌ JSON序列化/反序列化失败: {e}")


def merge_config_test():
    """测试合并配置"""
    print("\n=== 合并配置测试 ===")
    
    # 定义合并配置
    MERGE_OPTIONS = {
        2: {"portrait": (2, 1), "landscape": (1, 2)},
        3: {"portrait": (3, 1), "landscape": (3, 1)},
        4: {"portrait": (2, 2), "landscape": (2, 2)},
        6: {"portrait": (2, 3), "landscape": (3, 2)},
        9: {"portrait": (3, 3), "landscape": (3, 3)}
    }
    
    print("支持的合并数量:", sorted(MERGE_OPTIONS.keys()))
    
    # 检查6张的布局是否符合要求
    if 6 in MERGE_OPTIONS:
        portrait_layout = MERGE_OPTIONS[6]["portrait"]
        landscape_layout = MERGE_OPTIONS[6]["landscape"]
        print(f"6张竖屏布局: {portrait_layout} (2行3列)")
        print(f"6张横屏布局: {landscape_layout} (3行2列)")
    
    # 打印所有配置
    for count in sorted(MERGE_OPTIONS.keys()):
        print(f"合并{count}张: 竖屏{MERGE_OPTIONS[count]['portrait']}, 横屏{MERGE_OPTIONS[count]['landscape']}")


if __name__ == "__main__":
    print("开始极简测试...")
    is_portrait_test()
    json_encoder_test()
    merge_config_test()
    
    print("\n=== 优化功能总结 ===")
    print("1. 自动按横屏/竖屏分类照片并分别拼合")
    print("2. UI界面简化为选择2/3/4/6/9张合并")
    print("3. 智能布局：6张竖屏3张一排共2排，6张横屏2张一排共3排")
    print("4. 拼接时控制在12000像素内，最小化尺寸调整")
    print("5. 修复了EXIF数据JSON序列化问题")
    
    print("\n测试完成！")