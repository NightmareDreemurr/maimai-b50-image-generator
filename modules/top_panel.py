import os
from PIL import Image, ImageFont, ImageDraw
import unicodedata

# class 坐标和尺寸表
CLASS_GEOM = {
    0: (333, 21, 69, 42),
    1: (333, 21, 69, 42),
    2: (333, 21, 69, 42),
    3: (333, 21, 69, 42),
    4: (333, 21, 69, 42),
    5: (328, 19, 77, 46),
    6: (328, 19, 77, 46),
    7: (328, 20, 77, 46),
    8: (328, 19, 77, 46),
    9: (328, 19, 77, 46),
    10: (326, 14, 85, 57),
    11: (326, 14, 85, 58),
    12: (326, 14, 85, 57),
    13: (326, 14, 85, 58),
    14: (326, 14, 85, 58),
    15: (317, 12, 100, 61),
    16: (317, 12, 100, 61),
    17: (317, 12, 100, 61),
    18: (317, 12, 100, 61),
    19: (317, 12, 100, 61),
    20: (317, 9, 104, 65),
    21: (314, 9, 107, 65),
    22: (314, 9, 107, 65),
    23: (315, 9, 106, 65),
    24: (315, 9, 105, 65),
    25: (313, 9, 108, 65),
}

# dani 坐标表
DANI_POSITIONS = {
    0: (325, 70), 1: (326, 70), 2: (326, 70), 3: (326, 70), 4: (326, 70), 5: (326, 70),
    6: (323, 70), 7: (323, 70), 8: (323, 70), 9: (323, 70), 10: (323, 70), 11: (323, 70),
    12: (326, 70), 13: (326, 70), 14: (326, 70), 15: (326, 70), 16: (326, 70), 17: (326, 70),
    18: (326, 70), 19: (326, 70), 20: (326, 70), 21: (326, 70), 22: (323, 70), 23: (323, 70)
}

# rating 坐标表
RATING_POSITIONS = {
    1: (142, 31), 2: (142, 31), 3: (142, 31), 4: (142, 31), 5: (142, 31),
    6: (142, 31), 7: (142, 31), 8: (142, 31), 9: (142, 31), 10: (142, 31), 11: (142, 31)
}

def find_asset(asset_name):
    """在 assets 目录中递归查找素材文件"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        project_root = os.path.abspath('.')
    
    assets_path = os.path.join(project_root, 'assets')
    
    for root, _, files in os.walk(assets_path):
        if asset_name in files:
            return os.path.join(root, asset_name)
    return None

def to_fullwidth(s):
    # 半角转全角
    result = ''
    for c in s:
        code = ord(c)
        if code == 0x20:
            code = 0x3000
        elif 0x21 <= code <= 0x7E:
            code += 0xFEE0
        result += chr(code)
    return result

def truncate_to_fullwidth(s, max_len):
    length = 0
    result = ''
    for c in s:
        if unicodedata.east_asian_width(c) in ('F', 'W', 'A'):
            add = 1
        else:
            add = 0.5
        if length + add > max_len:
            break
        result += c
        length += add
    return result

def draw_rating_number_img(rating, anchor=(304, 62)):
    """
    生成右对齐的rating数字图片，右下角锚点为anchor，数字染色为#f6c304。
    :param rating: int, 最多5位
    :param anchor: (x, y) 右下角锚点
    :return: (img, paste_x, paste_y)
    """
    from PIL import Image
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        project_root = os.path.abspath('.')
    num_path = os.path.join(project_root, 'assets', 'UI_CMN_Num_26p.png')
    num_img = Image.open(num_path).convert('RGBA')
    cell_w, cell_h = 34, 40
    target_h = 21
    spacing = -2
    # 修正数字分布：0 1 2 3 | 4 5 6 7 | 8 9
    num_map = {
        '0': (0, 0), '1': (1, 0), '2': (2, 0), '3': (3, 0),
        '4': (0, 1), '5': (1, 1), '6': (2, 1), '7': (3, 1),
        '8': (0, 2), '9': (1, 2)
    }
    rating_str = str(rating)[:5]
    digits = list(rating_str)
    digit_imgs = []
    for d in digits:
        if d not in num_map:
            continue
        cx, cy = num_map[d]
        crop = num_img.crop((cx*cell_w, cy*cell_h, (cx+1)*cell_w, (cy+1)*cell_h))
        scale = target_h / cell_h
        new_w = int(cell_w * scale)
        digit_img = crop.resize((new_w, target_h), Image.LANCZOS)
        # 染色为#f6c304
        r, g, b = 246, 195, 4
        datas = digit_img.getdata()
        new_data = []
        for item in datas:
            if item[3] > 0:
                new_data.append((r, g, b, item[3]))
            else:
                new_data.append(item)
        digit_img.putdata(new_data)
        digit_imgs.append(digit_img)
    # 右对齐拼接
    total_w = 0
    for img in digit_imgs:
        total_w += img.width
    if len(digit_imgs) > 1:
        total_w += spacing * (len(digit_imgs)-1)
    result_img = Image.new('RGBA', (total_w, target_h), (0,0,0,0))
    x = result_img.width
    for img in reversed(digit_imgs):
        x -= img.width
        result_img.paste(img, (x, 0), img)
        x -= spacing
    # 计算粘贴坐标
    px, py = anchor
    paste_x = px - result_img.width
    paste_y = py - result_img.height
    return result_img, paste_x, paste_y

def get_dx_rating_id_by_value(rating):
    """
    根据rating数值自动返回DX Rating皮肤ID (1~11)
    """
    if rating <= 999:
        return 1  # White
    elif rating <= 1999:
        return 2  # Blue
    elif rating <= 3999:
        return 3  # Green
    elif rating <= 6999:
        return 4  # Yellow
    elif rating <= 9999:
        return 5  # Red
    elif rating <= 11999:
        return 6  # Purple
    elif rating <= 12999:
        return 7  # Bronze
    elif rating <= 13999:
        return 8  # Silver
    elif rating <= 14499:
        return 9  # Gold
    elif rating <= 14999:
        return 10 # Platinum
    else:
        return 11 # Rainbow

def create_panel_image(
    frame_id: int,
    nameplate_id: int,
    shougou_type: int,  # 0-Normal, 1-Silver, 2-Bronze, 3-Gold, 4-Rainbow
    class_id: int,
    dani_id: int,
    icon_id: int,
    name: str = '',
    shougou_text: str = '',
    version_text: str = 'Ver.DX1.55-E',
    rating: int = 0,
    output_filename="generated_panel.png"):
    """
    根据传入的参数，动态生成玩家信息面板图片。

    Args:
        frame_id (int): 边框ID (例如: 559504)
        nameplate_id (int): 名牌ID (例如: 559502)
        shougou_type (int): 称号类型 (0-Normal, 1-Silver, 2-Bronze, 3-Gold, 4-Rainbow)
        class_id (int): 段位ID (0-25)
        dani_id (int): 段位认证板ID (0-23)
        icon_id (int): 用户头像ID (例如: 559501)。
        name (str): 玩家名字。
        shougou_text (str): 称号文本。
        version_text (str): 版本文本。
        rating (int): 评分。
        output_filename (str): 输出图片的文件名。
    """
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        project_root = os.path.abspath('.')

    output_path = os.path.join(project_root, output_filename)

    # 1. 创建画布 (1080x452)
    base_image = Image.new('RGBA', (1080, 452), (0, 0, 0, 0))

    # 2. 定义一个辅助函数来粘贴图层
    def paste_layer(asset_name, position):
        asset_full_path = find_asset(asset_name)
        if asset_full_path:
            try:
                asset_image = Image.open(asset_full_path).convert('RGBA')
                base_image.paste(asset_image, position, asset_image)
                print(f"  - 成功粘贴图层: {asset_name}")
            except Exception as e:
                print(f"  - 处理图片 {asset_name} 时出错: {e}")
        else:
            print(f"  - 警告: 未找到素材 '{asset_name}'。")

    print("开始合成图片...")
    
    # 3. 按照从下到上的顺序粘贴各个图层
    
    # 背景
    paste_layer("UI_CMN_SubBG_Game.png", (0, 0))
    
    # 边框 (Frame)
    frame_name = f"UI_Frame_{str(frame_id).zfill(6)}.png"
    paste_layer(frame_name, (0, 0))
    
    # 名牌 (Nameplate)
    nameplate_name = f"UI_Plate_{str(nameplate_id).zfill(6)}.png"
    paste_layer(nameplate_name, (30, 27))
    
    # DX Rating 皮肤（自动推断ID）
    dx_rating_id = get_dx_rating_id_by_value(rating)
    dx_rating_name = f"UI_CMN_DXRating_S_{str(dx_rating_id).zfill(2)}.png"
    dx_rating_pos = RATING_POSITIONS.get(dx_rating_id, (139, 34))
    paste_layer(dx_rating_name, dx_rating_pos)

    # 段位 (Class)
    class_name = f"UI_CMN_Class_S_{str(class_id).zfill(2)}.png"
    asset_full_path = find_asset(class_name)
    class_geom = CLASS_GEOM.get(class_id, (313, 9, 108, 65))
    x, y, w, h = class_geom
    if asset_full_path:
        try:
            class_image = Image.open(asset_full_path).convert('RGBA')
            src_w, src_h = class_image.size
            scale = min(w / src_w, h / src_h)
            new_w, new_h = int(src_w * scale), int(src_h * scale)
            class_image = class_image.resize((new_w, new_h), Image.LANCZOS)
            base_image.paste(class_image, (x, y), class_image)
            print(f"  - 成功粘贴段位: {class_name} at {(x, y)} (原始:{src_w}x{src_h} 缩放:{new_w}x{new_h})")
        except Exception as e:
            print(f"  - 处理段位时出错: {e}")
    else:
        print(f"  - 警告: 未找到段位素材 '{class_name}'。")

    # 称号 (Shougou)
    shougou_data = {
        0:  {"file": "UI_CMN_Shougou_Normal.png",  "pos": (140, 111)},
        4:  {"file": "UI_CMN_Shougou_Rainbow.png", "pos": (142, 110)},
        1:  {"file": "UI_CMN_Shougou_Silver.png",  "pos": (142, 112)},
        2:  {"file": "UI_CMN_Shougou_Bronze.png",  "pos": (140, 112)},
        3:  {"file": "UI_CMN_Shougou_Gold.png",    "pos": (142, 112)},
    }
    if shougou_type in shougou_data:
        shougou_info = shougou_data[shougou_type]
        paste_layer(shougou_info["file"], shougou_info["pos"])
    else:
        print(f"  - 警告: 未知的称号类型 '{shougou_type}'。")
        
    # 名字背景 (NameBackground)
    paste_layer("NameBackground.png", (145, 70))

    # 段位认证板 (Dani Plate)
    dani_name = f"UI_CMN_DaniPlate_{str(dani_id).zfill(2)}.png"
    asset_full_path = find_asset(dani_name)
    dani_pos = DANI_POSITIONS.get(dani_id, (325, 73))
    if asset_full_path:
        try:
            dani_image = Image.open(asset_full_path).convert('RGBA')
            dani_image = dani_image.resize((89, 41), Image.LANCZOS)
            base_image.paste(dani_image, dani_pos, dani_image)
            print(f"  - 成功粘贴段位认证板: {dani_name} at {dani_pos}")
        except Exception as e:
            print(f"  - 处理段位认证板时出错: {e}")
    else:
        print(f"  - 警告: 未找到段位认证板素材 '{dani_name}'。")

    # 头像 (Icon) - 这是最上层
    icon_name = f"UI_Icon_{str(icon_id).zfill(6)}.png"
    asset_full_path = find_asset(icon_name)
    if asset_full_path:
        try:
            icon_image = Image.open(asset_full_path).convert('RGBA')
            icon_image = icon_image.resize((100, 100), Image.LANCZOS)
            base_image.paste(icon_image, (39, 35), icon_image)
            print(f"  - 成功粘贴头像: {icon_name}")
        except Exception as e:
            print(f"  - 处理头像时出错: {e}")
    else:
        print(f"  - 警告: 未找到头像素材 '{icon_name}'。")

    # 绘制名字
    if name:
        # 1. 转全角
        name_full = to_fullwidth(name)
        # 2. 只截断超出8位，不补全
        if len(name_full) > 8:
            name_full = name_full[:8]
        # 3. 加载字体
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            project_root = os.path.abspath('.')
        font_path = os.path.join(project_root, 'assets', 'fonts', 'SEGAMaruGothicDB.ttf')
        try:
            font = ImageFont.truetype(font_path, 30)
        except Exception as e:
            print(f"  - 警告: 加载字体失败: {e}")
            font = None
        # 4. 绘制
        draw = ImageDraw.Draw(base_image)
        if font:
            draw.text((150, 75), name_full, font=font, fill=(0,0,0,255))
            print(f"  - 成功绘制名字: {name_full}")
        else:
            draw.text((150, 75), name_full, fill=(0,0,0,255))
            print(f"  - 用默认字体绘制名字: {name_full}")

    # 绘制称号（shougou_text）
    if shougou_text:
        # 截断到15个全角字符
        shougou_text = truncate_to_fullwidth(shougou_text, 15)
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            project_root = os.path.abspath('.')
        font_path = os.path.join(project_root, 'assets', 'fonts', 'SEGAMaruGothicDB.ttf')
        # 生成描边字图片
        outline_img = draw_text_with_outline_img(
            text=shougou_text,
            font_path=font_path,
            font_size=15,  # 字高15px
            letter_spacing=0, 
            outline_width=1
        )
        # 计算中心居中粘贴位置
        px, py = 277, 124
        img_w, img_h = outline_img.size
        paste_x = px - img_w // 2
        paste_y = py - img_h // 2
        base_image.paste(outline_img, (paste_x, paste_y), outline_img)
        print(f"  - 成功绘制称号: {shougou_text}，居中于({px},{py})")

    # 绘制rating数字
    if rating:
        rating_img, px, py = draw_rating_number_img(rating, anchor=(304, 62))
        base_image.paste(rating_img, (px, py), rating_img)
        print(f"  - 成功绘制rating: {rating} 右下角锚点(302,62)")

    # 最顶层粘贴 On.png
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        project_root = os.path.abspath('.')
    on_path = os.path.join(project_root, 'assets', 'On.png')
    if os.path.exists(on_path):
        try:
            on_image = Image.open(on_path).convert('RGBA')
            base_image.paste(on_image, (1018, 27), on_image)
            print("  - 成功粘贴 On.png 在 (1018, 27)")
        except Exception as e:
            print(f"  - 处理 On.png 时出错: {e}")
    else:
        print("  - 警告: 未找到 On.png")

    # 右上角绘制 CREDIT(S) 24
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        project_root = os.path.abspath('.')
    font_path = os.path.join(project_root, 'assets', 'fonts', 'SEGAMaruGothicDB.ttf')
    credit_text = 'CREDIT(S) 24'
    credit_img = draw_text_with_outline_img(
        text=credit_text,
        font_path=font_path,
        font_size=22,
        letter_spacing=1,
        outline_width=1
    )
    img_w, img_h = credit_img.size
    px = 1080 - 93  # 画布宽-93
    py = 33+3
    paste_x = px - img_w  # 右上角对齐
    paste_y = py
    base_image.paste(credit_img, (paste_x, paste_y), credit_img)
    print(f"  - 成功绘制CREDIT(S) 24于右上角({px},{py})")

    # 右上角绘制 version_text
    if version_text:
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            project_root = os.path.abspath('.')
        font_path = os.path.join(project_root, 'assets', 'fonts', 'SEGAMaruGothicDB.ttf')
        outline_width = 1
        version_img = draw_text_with_outline_img(
            text=version_text,
            font_path=font_path,
            font_size=17,
            letter_spacing=1,
            outline_width=outline_width
        )
        img_w, img_h = version_img.size
        px = 1080 - 25  # 画布宽-25
        py = 70+7
        paste_x = px - img_w  # 右上角对齐
        paste_y = py - outline_width  # 上边考虑黑边
        base_image.paste(version_img, (paste_x, paste_y), version_img)
        print(f"  - 成功绘制版本号: {version_text} 于右上角({px},{py})")

    # 4. 保存最终生成的图片
    try:
        base_image.save(output_path)
        print(f"成功生成面板图片: {output_path}")
    except Exception as e:
        print(f"保存最终图片时出错: {e}")

def draw_text_with_outline(
    base_image,
    text,
    font_path,
    font_size,
    position,
    letter_spacing=0,
    outline_width=2,
    fill=(255,255,255,255),
    outline_fill=(0,0,0,255)
):
    """
    在base_image上指定位置绘制带黑色描边的白字
    :param base_image: PIL.Image
    :param text: 文本内容
    :param font_path: 字体路径
    :param font_size: 字体大小
    :param position: (x, y)
    :param letter_spacing: 字距
    :param outline_width: 黑边粗度
    :param fill: 字体颜色
    :param outline_fill: 描边颜色
    """
    from PIL import ImageDraw, ImageFont

    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(base_image)

    x, y = position
    # 逐字绘制，支持字距
    for i, char in enumerate(text):
        char_x = x + i * (font.getsize(char)[0] + letter_spacing)
        # 先画描边
        for dx in range(-outline_width, outline_width+1):
            for dy in range(-outline_width, outline_width+1):
                if dx != 0 or dy != 0:
                    draw.text((char_x+dx, y+dy), char, font=font, fill=outline_fill)
        # 再画白字
        draw.text((char_x, y), char, font=font, fill=fill)

def draw_text_with_outline_img(
    text,
    font_path,
    font_size,
    letter_spacing=0,
    outline_width=2,
    fill=(255,255,255,255),
    outline_fill=(0,0,0,255)
):
    """
    生成带黑色描边的白字图片，返回PIL.Image对象（透明底）。
    :param text: 文本内容
    :param font_path: 字体路径
    :param font_size: 字体大小
    :param letter_spacing: 字距
    :param outline_width: 黑边粗度
    :param fill: 字体颜色
    :param outline_fill: 描边颜色
    :return: PIL.Image
    """
    from PIL import ImageDraw, ImageFont, Image
    font = ImageFont.truetype(font_path, font_size)
    # 计算整体宽高（支持字距）
    total_width = 0
    max_height = 0
    char_sizes = []
    for char in text:
        bbox = font.getbbox(char)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        char_sizes.append((w, h))
        total_width += w + letter_spacing
        max_height = max(max_height, h)
    if len(text) > 0:
        total_width -= letter_spacing  # 最后一个字不加字距
    # 获取字体 metrics
    ascent, descent = font.getmetrics()
    img_height = max_height + 2 * outline_width + descent
    img = Image.new('RGBA', (total_width + 2*outline_width, img_height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    x = outline_width
    y = outline_width
    for i, char in enumerate(text):
        w, h = char_sizes[i]
        # 画描边
        for dx in range(-outline_width, outline_width+1):
            for dy in range(-outline_width, outline_width+1):
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), char, font=font, fill=outline_fill)
        # 画白字
        draw.text((x, y), char, font=font, fill=fill)
        x += w + letter_spacing
    return img

if __name__ == '__main__':
    # --- 使用示例 ---
    create_panel_image(
        # 装饰
        frame_id=250401,                    # 底板ID
        nameplate_id=400401,                # 姓名框ID
        icon_id=400401,                     # 头像ID
        shougou_type=3,                     # 0 - Normal, 1-Silver, 2-Bronze, 3-Gold, 4-Rainbow 
        shougou_text='世紀末',              # 称号文本
        
        # 友人对战段位
        class_id=25,                        # 0~4 B5~B1, 5~9 A5~A1, 10~14 S5~S1, 15~19 SS5~SS1, 20~24 SSS5~SSS1, 25 LEGEND
        
        # 段位认定段位
        dani_id=23,                         # 0 初心者, 1~10 初段~十段, 11 皆传, 12~21 真初段~真十段, 22 真皆传, 23 里皆传
        
        # 用户基础信息
        name='リズ',                        # 名字       
        rating=16145,                       # rating

        # 右上角 版本信息    
        version_text='Ver.DX1.55-E'
    )
