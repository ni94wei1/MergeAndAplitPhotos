import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Scale
from PIL import Image, ImageEnhance
from PIL.ExifTags import TAGS
import piexif
import os
from fractions import Fraction

# 定义常用的合并数量和对应的行列配置
MERGE_OPTIONS = {
    2: {"portrait": (2, 1), "landscape": (1, 2)},  # 竖屏2张: 2行1列, 横屏2张: 1行2列
    3: {"portrait": (3, 1), "landscape": (3, 1)},  # 竖屏3张: 3行1列, 横屏3张: 3行1列
    4: {"portrait": (2, 2), "landscape": (2, 2)},  # 竖屏4张: 2行2列, 横屏4张: 2行2列
    6: {"portrait": (2, 3), "landscape": (3, 2)},  # 竖屏6张: 2行3列, 横屏6张: 3行2列
    9: {"portrait": (3, 3), "landscape": (3, 3)}   # 竖屏9张: 3行3列, 横屏9张: 3行3列
}

# 默认最大尺寸限制为12000像素
DEFAULT_MAX_SIZE = 12000

# 定义保存的常量
FILE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp')


class PILJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，用于处理PIL和EXIF相关的特殊类型"""
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

# 配置文件路径
CONFIG_FILE = "watermark_config.json"

def load_watermark_config():
    """加载保存的水印配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    # 默认配置
    return {
        "watermark_path": "",
        "watermark_size": 50,
        "watermark_pos": 3,  # 3表示右下
        "watermark_opacity": 70,
        "watermark_enabled": 1  # 1=开启, 0=关闭
    }


def is_portrait(image):
    """判断图片是否为竖屏
    竖屏：高度 > 宽度
    横屏：宽度 > 高度
    正方形：宽度 == 高度，这里统一归为横屏处理
    """
    return image.height > image.width


def categorize_images_by_orientation(src_dir):
    """按横竖屏分类图片
    返回：(portrait_images, landscape_images, portrait_exif, landscape_exif, portrait_filenames, landscape_filenames)
    """
    portrait_images = []
    landscape_images = []
    portrait_exif = []
    landscape_exif = []
    portrait_filenames = []
    landscape_filenames = []
    
    for fname in sorted(os.listdir(src_dir)):
        if fname.lower().endswith(FILE_EXTENSIONS):
            try:
                img_path = os.path.join(src_dir, fname)
                img = Image.open(img_path)
                
                # 提取并保存EXIF元数据
                exif_data = extract_exif_data(img_path)
                
                # 根据方向分类图片
                if is_portrait(img):
                    portrait_images.append(img)
                    portrait_exif.append(exif_data)
                    portrait_filenames.append(fname)
                else:
                    landscape_images.append(img)
                    landscape_exif.append(exif_data)
                    landscape_filenames.append(fname)
            except Exception as e:
                print(f"无法打开 {fname}: {e}")
    
    print(f"共找到 {len(portrait_images)} 张竖屏图片，{len(landscape_images)} 张横屏图片")
    return portrait_images, landscape_images, portrait_exif, landscape_exif, portrait_filenames, landscape_filenames


def extract_exif_data(image_path):
    """提取图片的EXIF数据"""
    exif_data = {}
    try:
        img = Image.open(image_path)
        
        # 方法1：使用_getexif()
        exif = img._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                # 确保值是可序列化的
                if isinstance(value, bytes):
                    value = value.decode('utf-8', errors='replace')
                exif_data[tag] = str(value)
            
            # 专门保存相机信息和曝光参数
            # 1. 相机制造商和型号
            make = exif.get(271, '')  # Manufacturer
            model = exif.get(272, '')  # Model
            if make: exif_data['CameraMake'] = str(make)
            if model: exif_data['CameraModel'] = str(model)
              
            # 2. 曝光参数
            exposure = exif.get(33434, '')  # ExposureTime
            aperture = exif.get(33437, '')  # FNumber
            iso = exif.get(34855, '')  # ISOSpeedRatings
            focal = exif.get(37386, '')  # FocalLength
              
            if exposure: exif_data['ExposureTime'] = str(exposure)
            if aperture: exif_data['Aperture'] = str(aperture)
            if iso: exif_data['ISO'] = str(iso)
            if focal: exif_data['FocalLength'] = str(focal)
              
            # 3. 拍摄时间
            datetime = exif.get(36867, '')  # DateTimeOriginal
            if datetime: exif_data['DateTimeOriginal'] = str(datetime)

        # 如果方法1没有提取到数据，尝试使用info字典
        if not exif_data:
            try:
                # 尝试直接从info中获取信息
                if hasattr(img, 'info'):
                    # 复制所有非图像数据的信息
                    for key, value in img.info.items():
                        if key != 'exif' and key != 'icc_profile':
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='replace')
                                except:
                                    value = str(value)
                            exif_data[key] = str(value)
            except:
                pass
        
        # 如果提取到了任何数据，标记为有EXIF
        if exif_data:
            exif_data['_has_exif'] = 'True'
    except Exception as e:
        print(f"无法提取EXIF数据: {e}")
    
    return exif_data

def save_watermark_config(config):
    """保存水印配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4, cls=PILJSONEncoder)
    except Exception as e:
        print(f"保存配置文件失败: {e}")


def merge_images_grid(src_dir, merge_count, spacing, max_size, progress_var):
    """按横竖屏分类合并图片
    src_dir: 源图片目录
    merge_count: 每张合并图片包含的图片数量（2,3,4,6,9）
    spacing: 图片间距
    max_size: 最大尺寸限制
    progress_var: 进度条变量
    """
    if not src_dir or not os.path.exists(src_dir):
        messagebox.showerror("错误", "请选择有效的源图片文件夹")
        return

    # 验证合并数量是否在支持的选项中
    if merge_count not in MERGE_OPTIONS:
        messagebox.showerror("错误", f"不支持的合并数量: {merge_count}，请选择 2,3,4,6,9")
        return

    dst_dir = os.path.join(src_dir, "merged_output")
    os.makedirs(dst_dir, exist_ok=True)
    record_file = os.path.join(dst_dir, "record.json")

    # 按横竖屏分类图片
    portrait_images, landscape_images, portrait_exif, landscape_exif, portrait_filenames, landscape_filenames = \
        categorize_images_by_orientation(src_dir)

    if not portrait_images and not landscape_images:
        messagebox.showerror("错误", "没有找到图片文件")
        return

    record_data = []
    total_batches = 0
    processed_batches = 0
    
    # 处理竖屏图片
    if portrait_images:
        rows, cols = MERGE_OPTIONS[merge_count]["portrait"]
        batch_size = rows * cols
        total_portrait_batches = (len(portrait_images) + batch_size - 1) // batch_size
        total_batches += total_portrait_batches
        
        processed_batches = merge_image_batches(
            portrait_images, portrait_filenames, portrait_exif, 
            rows, cols, spacing, max_size, progress_var,
            dst_dir, record_data, "portrait", processed_batches
        )
    
    # 处理横屏图片
    if landscape_images:
        rows, cols = MERGE_OPTIONS[merge_count]["landscape"]
        batch_size = rows * cols
        total_landscape_batches = (len(landscape_images) + batch_size - 1) // batch_size
        total_batches += total_landscape_batches
        
        merge_image_batches(
            landscape_images, landscape_filenames, landscape_exif, 
            rows, cols, spacing, max_size, progress_var,
            dst_dir, record_data, "landscape", processed_batches
        )
    
    # 保存记录文件
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(record_data, f, ensure_ascii=False, indent=4, cls=PILJSONEncoder)
    
    progress_var.set(100)
    messagebox.showinfo("完成", f"拼接完成，输出目录: {dst_dir}")
    

def merge_image_batches(images, filenames, exif_metadata, rows, cols, spacing, max_size, 
                        progress_var, dst_dir, record_data, orientation, start_index):
    """批量合并一组图片
    images: 图片列表
    filenames: 文件名列表
    exif_metadata: EXIF数据列表
    rows, cols: 网格行列数
    spacing: 图片间距
    max_size: 最大尺寸限制
    progress_var: 进度条变量
    dst_dir: 输出目录
    record_data: 记录数据列表
    orientation: 方向标识（portrait或landscape）
    start_index: 起始批次索引
    """
    idx = 0
    batch_size = rows * cols
    total_batches = (len(images) + batch_size - 1) // batch_size
    
    while idx < len(images):
        batch_imgs = images[idx:idx + batch_size]
        batch_names = filenames[idx:idx + batch_size]

        # 计算每列最大宽度，每行最大高度（网格尺寸）
        col_widths = [max((img.width for img in batch_imgs[i::cols]), default=0) for i in range(cols)]
        row_heights = [max((img.height for img in batch_imgs[r*cols:(r+1)*cols]), default=0) for r in range(rows)]

        total_width = sum(col_widths) + (cols - 1) * spacing
        total_height = sum(row_heights) + (rows - 1) * spacing

        merged = Image.new('RGB', (total_width, total_height), color=(255, 255, 255))

        positions = []
        y_offset = 0
        for r in range(rows):
            x_offset = 0
            for c in range(cols):
                idx_in_batch = r * cols + c
                if idx_in_batch < len(batch_imgs):
                    im = batch_imgs[idx_in_batch]
                    merged.paste(im, (x_offset, y_offset))
                    # 获取对应图片的EXIF数据
                    img_idx = idx + idx_in_batch
                    exif_data = exif_metadata[img_idx] if img_idx < len(exif_metadata) else {}
                    
                    positions.append({
                        "file": batch_names[idx_in_batch],
                        "x": x_offset,
                        "y": y_offset,
                        "w": im.width,
                        "h": im.height,
                        "exif_data": exif_data
                    })
                x_offset += col_widths[c] + spacing
            y_offset += row_heights[r] + spacing

        # 限制合成图最大宽高 max_size，超过则整体缩放
        w, h = merged.size
        scale = min(max_size / w, max_size / h, 1.0)
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            merged = merged.resize((new_w, new_h), Image.LANCZOS)
            for pos in positions:
                pos["x"] = int(pos["x"] * scale)
                pos["y"] = int(pos["y"] * scale)
                pos["w"] = int(pos["w"] * scale)
                pos["h"] = int(pos["h"] * scale)

        # 生成带方向标识的文件名
        batch_index = start_index + (idx // batch_size) + 1
        merged_name = f"merged_{orientation}_{batch_index:04d}.png"
        merged_path = os.path.join(dst_dir, merged_name)
        merged.save(merged_path)

        record_data.append({
            "merged_file": merged_name,
            "positions": positions,
            "spacing": spacing,
            "rows": rows,
            "cols": cols,
            "scale": scale,
            "orientation": orientation
        })

        idx += batch_size
        current_progress = (batch_index) / (total_batches + start_index) * 100
        progress_var.set(int(current_progress))
        root.update_idletasks()
        
    return start_index + total_batches




def add_watermark(image, watermark_path, watermark_size, position, opacity):
    if not watermark_path or not os.path.exists(watermark_path):
        return image

    try:
        watermark = Image.open(watermark_path).convert("RGBA")

        # 背景图尺寸
        img_width, img_height = image.size
        original_width, original_height = watermark.size

        # 关键修改：使用宽度和高度中的较小值作为基准计算水印大小
        base_dimension = min(img_width, img_height)  # 取宽高中的较小值
        target_ratio = watermark_size / 100.0        # 例如 20 = 占基准尺寸的 20%
        target_width = int(base_dimension * target_ratio)
        scale = target_width / original_width
        target_height = int(original_height * scale)

        watermark = watermark.resize((target_width, target_height), Image.LANCZOS)

        # 调整透明度
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 100)
        watermark.putalpha(alpha)

        wm_width, wm_height = watermark.size

        # 计算位置
        if position == 0:      # 左上
            x, y = 10, 10
        elif position == 1:    # 右上
            x, y = img_width - wm_width - 10, 10
        elif position == 2:    # 左下
            x, y = 10, img_height - wm_height - 10
        elif position == 3:    # 右下
            x, y = img_width - wm_width - 10, img_height - wm_height - 10
        elif position == 4:    # 居中
            x, y = (img_width - wm_width) // 2, (img_height - wm_height) // 2
        elif position == 5:    # 底部居中
            x, y = (img_width - wm_width) // 2, img_height - wm_height - 10

        # 合成水印
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image.paste(watermark, (x, y), watermark)

        return image.convert('RGB')
    except Exception as e:
        print(f"添加水印失败: {e}")
        return image


def split_images(merged_dir, progress_var, watermark_path, watermark_size, watermark_pos, watermark_opacity):
    if not merged_dir or not os.path.exists(merged_dir):
        messagebox.showerror("错误", "请选择有效的拼接图片文件夹")
        return

    record_file = os.path.join(merged_dir, "record.json")
    if not os.path.exists(record_file):
        messagebox.showerror("错误", "找不到 record.json 文件")
        return

    with open(record_file, 'r', encoding='utf-8') as f:
        record_data = json.load(f)

    dst_dir = os.path.join(merged_dir, "split_output")
    os.makedirs(dst_dir, exist_ok=True)

    total_batches = len(record_data)
    for i, entry in enumerate(record_data, start=1):
        merged_path = os.path.join(merged_dir, entry["merged_file"])
        if not os.path.exists(merged_path):
            print(f"跳过缺失文件: {merged_path}")
            continue

        merged_img = Image.open(merged_path)
        positions = entry["positions"]

        for pos in positions:
            crop_img = merged_img.crop((
                pos["x"], pos["y"],
                pos["x"] + pos["w"], pos["y"] + pos["h"]
            ))
            
            # 添加水印
            if watermark_enabled_var.get() == 1 and watermark_path and os.path.exists(watermark_path):
                crop_img = add_watermark(crop_img, watermark_path, watermark_size, watermark_pos, watermark_opacity)
            
            # 获取目标文件路径和扩展名
            target_file = os.path.join(dst_dir, pos["file"])
            file_ext = os.path.splitext(pos["file"])[1].lower()
            
            # 如果有EXIF数据，尝试将其还原到拆分后的图片
            exif_data = pos.get("exif_data", {})
            exif_bytes = exif_from_json(exif_data)
            if file_ext in ['.jpg', '.jpeg'] and exif_bytes:
                crop_img.save(target_file, "jpeg", quality=95, exif=exif_bytes)
            elif file_ext == ".png":
                from PIL.PngImagePlugin import PngInfo
                pnginfo = PngInfo()
                for k, v in exif_data.items():
                    if not k.startswith("_"):
                        pnginfo.add_text(k, str(v))
                crop_img.save(target_file, "PNG", pnginfo=pnginfo, optimize=True)
            else:
                crop_img.save(target_file)


        progress_var.set(int(i / total_batches * 100))
        root.update_idletasks()

    # 保存当前水印设置
    config = {
        "watermark_path": watermark_path,
        "watermark_size": watermark_size,
        "watermark_pos": watermark_pos,
        "watermark_opacity": watermark_opacity,
        "watermark_enabled": 1   # 1=开启, 0=关闭

    }
    save_watermark_config(config)

    progress_var.set(100)
    messagebox.showinfo("完成", f"拆分完成，输出目录: {dst_dir}")


def choose_folder(entry_widget):
    folder = filedialog.askdirectory()
    if folder:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder)


def choose_watermark(entry_widget):
    file = filedialog.askopenfilename(
        filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if file:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file)


def start_merge():
    try:
        merge_count = int(merge_count_var.get())
        spacing = int(entry_spacing.get().strip())
        max_size = int(entry_maxsize.get().strip())
    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字")
        return
    merge_images_grid(entry_merge_src.get().strip(), merge_count, spacing, max_size, progress_var)


def start_split():
    watermark_path = entry_watermark.get().strip()
    try:
        watermark_size = int(watermark_size_var.get())
        watermark_pos = watermark_pos_var.get()
        watermark_opacity = int(watermark_opacity_var.get())
    except ValueError:
        messagebox.showerror("错误", "水印参数设置错误")
        return
        
    split_images(
        entry_split_src.get().strip(), 
        progress_var,
        watermark_path,
        watermark_size,
        watermark_pos,
        watermark_opacity
    )


def exif_from_json(exif_data: dict):
    """
    把 record.json 里保存的 exif_data 转换成 piexif 可以写入的 exif_bytes
    """
    if not exif_data or "_has_exif" not in exif_data:
        return None

    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # 建立映射表（常见的字段）
    EXIF_MAP = {
        # 0th IFD
        "Make": (piexif.ImageIFD.Make, "0th"),
        "Model": (piexif.ImageIFD.Model, "0th"),
        "Software": (piexif.ImageIFD.Software, "0th"),
        "Artist": (piexif.ImageIFD.Artist, "0th"),
        "XResolution": (piexif.ImageIFD.XResolution, "0th"),
        "YResolution": (piexif.ImageIFD.YResolution, "0th"),
        "ResolutionUnit": (piexif.ImageIFD.ResolutionUnit, "0th"),
        "DateTime": (piexif.ImageIFD.DateTime, "0th"),

        # Exif IFD
        "ExposureTime": (piexif.ExifIFD.ExposureTime, "Exif"),
        "FNumber": (piexif.ExifIFD.FNumber, "Exif"),
        "ExposureProgram": (piexif.ExifIFD.ExposureProgram, "Exif"),
        "ISOSpeedRatings": (piexif.ExifIFD.ISOSpeedRatings, "Exif"),
        "SensitivityType": (piexif.ExifIFD.SensitivityType, "Exif"),
        "DateTimeOriginal": (piexif.ExifIFD.DateTimeOriginal, "Exif"),
        "DateTimeDigitized": (piexif.ExifIFD.DateTimeDigitized, "Exif"),
        "ShutterSpeedValue": (piexif.ExifIFD.ShutterSpeedValue, "Exif"),
        "ApertureValue": (piexif.ExifIFD.ApertureValue, "Exif"),
        "ExposureBiasValue": (piexif.ExifIFD.ExposureBiasValue, "Exif"),
        "MeteringMode": (piexif.ExifIFD.MeteringMode, "Exif"),
        "LightSource": (piexif.ExifIFD.LightSource, "Exif"),
        "Flash": (piexif.ExifIFD.Flash, "Exif"),
        "FocalLength": (piexif.ExifIFD.FocalLength, "Exif"),
        "FocalLengthIn35mmFilm": (piexif.ExifIFD.FocalLengthIn35mmFilm, "Exif"),
        "SubsecTimeOriginal": (piexif.ExifIFD.SubSecTimeOriginal, "Exif"),
        "SubsecTimeDigitized": (piexif.ExifIFD.SubSecTimeDigitized, "Exif"),
        "LensMake": (piexif.ExifIFD.LensMake, "Exif"),
        "LensModel": (piexif.ExifIFD.LensModel, "Exif"),
        "LensSerialNumber": (piexif.ExifIFD.LensSerialNumber, "Exif"),
        "BodySerialNumber": (piexif.ExifIFD.BodySerialNumber, "Exif"),
        "Contrast": (piexif.ExifIFD.Contrast, "Exif"),
        "Saturation": (piexif.ExifIFD.Saturation, "Exif"),
        "Sharpness": (piexif.ExifIFD.Sharpness, "Exif"),
        "UserComment": (piexif.ExifIFD.UserComment, "Exif"),
    }

    for key, val in exif_data.items():
        if key not in EXIF_MAP:
            continue
        tag_id, ifd = EXIF_MAP[key]

        try:
            # 类型转换
            if key in ["XResolution", "YResolution"]:
                val = (int(float(val)), 1)
            elif key in ["ExposureTime", "FNumber", "ApertureValue",
                         "ShutterSpeedValue", "ExposureBiasValue", "FocalLength"]:
                # 转成分数（分子, 分母）
                f = float(val)
                val = (int(f * 10000), 10000)
            elif key in ["ISOSpeedRatings", "MeteringMode", "LightSource",
                         "Flash", "ResolutionUnit", "FocalLengthIn35mmFilm",
                         "Contrast", "Saturation", "Sharpness",
                         "ExposureProgram", "SensitivityType"]:
                val = int(val)
            elif key == "UserComment":
                val = b"ASCII\0\0\0" + str(val).encode("utf-8")
            else:
                val = str(val)
        except Exception:
            val = str(val)

        exif_dict[ifd][tag_id] = val

    try:
        return piexif.dump(exif_dict)
    except Exception as e:
        print("piexif.dump 出错:", e)
        return None


# 初始化主窗口
root = tk.Tk()
root.title("图片拼接/拆分工具（带水印记忆功能）")
root.geometry("700x500")

# 加载水印配置
config = load_watermark_config()

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=680, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)

frame_merge = tk.LabelFrame(root, text="功能1: 图片网格拼接")
frame_merge.pack(fill="x", padx=10, pady=5)

tk.Label(frame_merge, text="源图片文件夹:").grid(row=0, column=0, sticky="w")
entry_merge_src = tk.Entry(frame_merge, width=50)
entry_merge_src.grid(row=0, column=1)
tk.Button(frame_merge, text="选择", command=lambda: choose_folder(entry_merge_src)).grid(row=0, column=2)

# 合并数量选择
merge_count_var = tk.IntVar(value=6)  # 默认选择6张
merge_count_frame = tk.Frame(frame_merge)
merge_count_frame.grid(row=1, column=0, columnspan=3, pady=5)
tk.Label(merge_count_frame, text="每张合并图片包含的图片数量: ").pack(side=tk.LEFT)

# 创建合并数量选项按钮
for count in sorted(MERGE_OPTIONS.keys()):
    tk.Radiobutton(merge_count_frame, text=str(count), variable=merge_count_var, value=count).pack(side=tk.LEFT, padx=10)

# 添加布局说明
layout_desc = tk.Label(frame_merge, text="注: 图片会自动按横竖屏分类，6张时竖屏2行3列，横屏3行2列", 
                       fg="gray", font=("SimHei", 9))
layout_desc.grid(row=2, column=0, columnspan=3, sticky="w", padx=5)

tk.Label(frame_merge, text="间距(px):").grid(row=3, column=0, sticky="w")
entry_spacing = tk.Entry(frame_merge, width=5)
entry_spacing.grid(row=3, column=1, sticky="w")
entry_spacing.insert(0, "0")

tk.Label(frame_merge, text="最大合成图宽高限制(px):").grid(row=3, column=1, sticky="e", padx=(100, 0))
entry_maxsize = tk.Entry(frame_merge, width=7)
entry_maxsize.grid(row=3, column=1, sticky="e", padx=(200, 0))
entry_maxsize.insert(0, str(DEFAULT_MAX_SIZE))

tk.Button(frame_merge, text="开始拼接", command=start_merge).grid(row=4, column=1, pady=5)

frame_split = tk.LabelFrame(root, text="功能2: 图片拆分")
frame_split.pack(fill="x", padx=10, pady=5)

tk.Label(frame_split, text="拼接图片文件夹:").grid(row=0, column=0, sticky="w")
entry_split_src = tk.Entry(frame_split, width=50)
entry_split_src.grid(row=0, column=1)
tk.Button(frame_split, text="选择", command=lambda: choose_folder(entry_split_src)).grid(row=0, column=2)

# 水印设置区域
frame_watermark = tk.LabelFrame(frame_split, text="水印设置")
frame_watermark.grid(row=1, column=0, columnspan=3, sticky="we", padx=5, pady=5)
# 水印开关
watermark_enabled_var = tk.IntVar(value=config.get("watermark_enabled", 1))
tk.Checkbutton(frame_watermark, text="启用水印", variable=watermark_enabled_var).grid(row=0, column=3, padx=10)


tk.Label(frame_watermark, text="水印图片:").grid(row=0, column=0, sticky="w")
entry_watermark = tk.Entry(frame_watermark, width=40)
entry_watermark.grid(row=0, column=1, sticky="w")
entry_watermark.insert(0, config["watermark_path"])  # 加载保存的路径
tk.Button(frame_watermark, text="选择", command=lambda: choose_watermark(entry_watermark)).grid(row=0, column=2)

# 水印大小
tk.Label(frame_watermark, text="水印大小(%):").grid(row=1, column=0, sticky="w")
watermark_size_var = tk.IntVar(value=config["watermark_size"])
scale_size = Scale(frame_watermark, from_=10, to=100, orient="horizontal", variable=watermark_size_var)
scale_size.grid(row=1, column=1, sticky="we")

# 水印位置
tk.Label(frame_watermark, text="水印位置:").grid(row=2, column=0, sticky="w")
watermark_pos_var = tk.IntVar(value=config["watermark_pos"])
pos_frame = tk.Frame(frame_watermark)
pos_frame.grid(row=2, column=1, sticky="w")
tk.Radiobutton(pos_frame, text="左上", variable=watermark_pos_var, value=0).pack(side=tk.LEFT, padx=5)
tk.Radiobutton(pos_frame, text="右上", variable=watermark_pos_var, value=1).pack(side=tk.LEFT, padx=5)
tk.Radiobutton(pos_frame, text="左下", variable=watermark_pos_var, value=2).pack(side=tk.LEFT, padx=5)
tk.Radiobutton(pos_frame, text="右下", variable=watermark_pos_var, value=3).pack(side=tk.LEFT, padx=5)
tk.Radiobutton(pos_frame, text="居中", variable=watermark_pos_var, value=4).pack(side=tk.LEFT, padx=5)
tk.Radiobutton(pos_frame, text="底部居中", variable=watermark_pos_var, value=5).pack(side=tk.LEFT, padx=5)

# 水印透明度
tk.Label(frame_watermark, text="透明度(%):").grid(row=3, column=0, sticky="w")
watermark_opacity_var = tk.IntVar(value=config["watermark_opacity"])
scale_opacity = Scale(frame_watermark, from_=10, to=100, orient="horizontal", variable=watermark_opacity_var)
scale_opacity.grid(row=3, column=1, sticky="we")

tk.Button(frame_split, text="开始拆分", command=start_split).grid(row=2, column=1, pady=10)

# 让拆分区域的列能够自适应宽度
frame_split.grid_columnconfigure(1, weight=1)
frame_watermark.grid_columnconfigure(1, weight=1)

root.mainloop()
