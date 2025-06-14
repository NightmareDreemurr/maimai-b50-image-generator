from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

# --- 常量 ---

# 路径
ASSETS_DIR = 'assets'
JACKETS_DIR = os.path.join(ASSETS_DIR, 'jackets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')

# 尺寸 (来自 song_cell.json)
CANVAS_WIDTH = 432
CANVAS_HEIGHT = 216

# 难度颜色
DIFF_COLORS = {
    0: '#45C124',  # BASIC
    1: '#FFBA01',  # ADVANCED
    2: '#FF5A66',  # EXPERT
    3: '#9F51DC',  # MASTER
    4: '#DBAAFF',  # Re:MASTER
    10: '#FF6FFD' # UTAGE
}

# Rating 计算表
RATING_TABLE = [
    {"min": 0, "max": 0, "offset": 0},
    {"min": 100000, "max": 199999, "offset": 16},
    {"min": 200000, "max": 299999, "offset": 32},
    {"min": 300000, "max": 399999, "offset": 48},
    {"min": 400000, "max": 499999, "offset": 64},
    {"min": 500000, "max": 599999, "offset": 80},
    {"min": 600000, "max": 699999, "offset": 96},
    {"min": 700000, "max": 749999, "offset": 112},
    {"min": 750000, "max": 799999, "offset": 120},
    {"min": 800000, "max": 899999, "offset": 136},
    {"min": 900000, "max": 939999, "offset": 152},
    {"min": 940000, "max": 969999, "offset": 168},
    {"min": 970000, "max": 979999, "offset": 200},
    {"min": 980000, "max": 989999, "offset": 203},
    {"min": 990000, "max": 994999, "offset": 208},
    {"min": 995000, "max": 999999, "offset": 211},
    {"min": 1000000, "max": 1004999, "offset": 216},
    {"min": 1005000, "max": float('inf'), "offset": 224}
]

# --- Rank辅助函数 ---
RANK_TABLE = [
    (0, "D"),
    (100000, "D"),
    (200000, "D"),
    (300000, "D"),
    (400000, "D"),
    (500000, "C"),
    (600000, "B"),
    (700000, "BB"),
    (750000, "BBB"),
    (799999, "BBB"),
    (800000, "A"),
    (900000, "AA"),
    (940000, "AAA"),
    (969999, "AAA"),
    (970000, "S"),
    (980000, "S+"),
    (989999, "S+"),
    (990000, "SS"),
    (995000, "SS+"),
    (999999, "SS+"),
    (1000000, "SSS"),
    (1004999, "SSS"),
    (1005000, "SSS+")
]

# --- 辅助函数 ---

def calculate_rating(achievement, base):
    """
    根据达成率和谱面定数计算Rating。
    """
    if achievement == 0:
        return 0
    
    offset = 0
    for record in RATING_TABLE:
        if record["min"] <= achievement <= record["max"]:
            offset = record["offset"]
            break
            
    # 公式: floor(min(达成率, 100.5000%) * offset * base / 1000000 / 10)
    return math.floor(min(achievement, 1005000) * offset * base / 1000000 / 10)

def get_font(path, size):
    """
    加载字体文件，如果失败则返回Pillow默认字体。
    """
    try:
        return ImageFont.truetype(path, size=size)
    except IOError:
        print(f"字体文件未找到: {path}，将使用默认字体。")
        return ImageFont.load_default()

def truncate_title(title, max_len=11.5):
    """
    裁剪过长的标题。一个全角字符计为1，半角为0.5。
    """
    display_len = 0
    truncate_at = 0
    for i, char in enumerate(title):
        # 中日韩字符等通常为全角
        if '\u4e00' <= char <= '\u9fff' or '\u3040' <= char <= '\u30ff':
            display_len += 1
        else:
            display_len += 0.5
        
        if display_len > max_len:
            break
        truncate_at = i + 1
    
    if truncate_at < len(title):
        return title[:truncate_at] + '...'
    return title

def get_rank_by_achievement(achievement):
    """
    根据达成率返回Rank字符串。
    """
    last_rank = "D"
    for threshold, rank in RANK_TABLE:
        if achievement < threshold:
            break
        last_rank = rank
    return last_rank

def rank_to_asset_name(rank):
    """
    根据Rank字符串返回assets下的图片文件名。
    """
    mapping = {
        "D": "UI_GAM_Rank_D.png",
        "C": "UI_GAM_Rank_C.png",
        "B": "UI_GAM_Rank_B.png",
        "BB": "UI_GAM_Rank_BB.png",
        "BBB": "UI_GAM_Rank_BBB.png",
        "A": "UI_GAM_Rank_A.png",
        "AA": "UI_GAM_Rank_AA.png",
        "AAA": "UI_GAM_Rank_AAA.png",
        "S": "UI_GAM_Rank_S.png",
        "S+": "UI_GAM_Rank_Sp.png",
        "SS": "UI_GAM_Rank_SS.png",
        "SS+": "UI_GAM_Rank_SSp.png",
        "SSS": "UI_GAM_Rank_SSS.png",
        "SSS+": "UI_GAM_Rank_SSSp.png"
    }
    return mapping.get(rank, "UI_GAM_Rank_D.png")

# --- 主要生成函数 ---

def generate_song_cell(
    cover_id: str,
    difficulty: int,
    is_dx: int,
    song_title: str,
    achievement: int,
    dx_score: int,
    dx_total: int,
    base: float,
    section_rank: int,
    fc_indicator: int = 0,
    fs_indicator: int = 0
) -> Image.Image:
    """
    生成单个乐曲单元格的图像。

    :param cover_id: 6位封面ID (字符串)
    :param difficulty: 难度 (0-4, 10)
    :param is_dx: 是否为DX谱面 (1是, 0否)
    :param song_title: 歌曲标题
    :param achievement: 达成率 (整数, e.g., 1010000 for 101.0000%)
    :param dx_score: DX分数
    :param dx_total: 总DX分数
    :param base: 谱面定数 (e.g., 14.9)
    :param section_rank: 在section中的排名 (e.g., 1)
    :param fc_indicator: FC指示器 (0-4)
    :param fs_indicator: FS指示器 (0-4)
    :return: PIL.Image.Image 对象
    """
    # 1. 创建画布
    canvas = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # 2. 绘制歌曲封面 (底层)
    jacket_id_str = str(cover_id).zfill(6)
    jacket_path = os.path.join(JACKETS_DIR, f'UI_Jacket_{jacket_id_str}.png')
    try:
        jacket_img = Image.open(jacket_path).convert('RGBA')
        
        # 等比缩放至宽度填满
        w, h = jacket_img.size
        new_h = int(CANVAS_WIDTH * h / w)
        jacket_img = jacket_img.resize((CANVAS_WIDTH, new_h), Image.Resampling.LANCZOS)
        
        # 高斯模糊
        jacket_img = jacket_img.filter(ImageFilter.GaussianBlur(radius=8))
        
        # 根据json中的位置粘贴
        canvas.paste(jacket_img, (0, -107))
    except FileNotFoundError:
        print(f"封面文件未找到: {jacket_path}")
        # 可以在这里绘制一个占位符矩形
        draw.rectangle([(0,0), (CANVAS_WIDTH, CANVAS_HEIGHT)], fill=(20, 20, 20))


    # 3. 疊加黑色半透明蒙版
    overlay = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 102))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas) # 重新获取Draw对象

    # 4. 绘制左侧难度条
    bar_color = DIFF_COLORS.get(difficulty, '#FFFFFF') # 默认为白色
    draw.rectangle([(0, 0), (9, CANVAS_HEIGHT)], fill=bar_color)

    # 5. 绘制DX/标谱指示器
    icon_name = 'UI_TST_Infoicon_DeluxeMode.png' if is_dx else 'UI_TST_Infoicon_StandardMode.png'
    icon_path = os.path.join(ASSETS_DIR, icon_name)
    try:
        dx_icon = Image.open(icon_path).convert('RGBA')

        # 根据要求调整图标大小 (基于高度26px进行等比缩放)
        w, h = dx_icon.size
        new_h = 26
        new_w = int(w * new_h / h)
        dx_icon = dx_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas.paste(dx_icon, (24, 13), dx_icon)
    except FileNotFoundError:
        print(f"指示器图标未找到: {icon_path}")

    # 6. 绘制歌曲标题
    title_font = get_font(os.path.join(FONTS_DIR, 'combined.ttf'), size=30)
    truncated_title = truncate_title(song_title)
    draw.text((30, 48), truncated_title, font=title_font, fill=(255, 255, 255))

    # 7. 绘制达成率
    ach_font = get_font(os.path.join(FONTS_DIR, 'Torus-SemiBold.otf'), size=50)
    ach_text = f"{(achievement / 10000):.4f}%"
    draw.text((30, 75), ach_text, font=ach_font, fill=(255, 255, 255))

    # 8. 绘制DX分数
    dx_font = get_font(os.path.join(FONTS_DIR, 'Torus-SemiBold.otf'), size=30)
    dx_text = f"{dx_score}/{dx_total}"
    draw.text((30, 132), dx_text, font=dx_font, fill=(255, 255, 255))

    # 9. 绘制定数和Rating
    rating_font = get_font(os.path.join(FONTS_DIR, 'combined.ttf'), size=28)
    rating_val = calculate_rating(achievement, base)
    rating_text = f"{base:.1f} -> {rating_val}"
    draw.text((30, 175), rating_text, font=rating_font, fill=(255, 255, 255))

    # 10. 绘制排名
    rank_font = get_font(os.path.join(FONTS_DIR, 'combined.ttf'), size=28)
    rank_text = f"#{section_rank}"
    
    # 右上角对齐
    # json中位置为(383, 14), 尺寸为(28, 18), 右边缘 x = 383 + 28 = 411
    text_bbox = rank_font.getbbox(rank_text)
    text_width = text_bbox[2] - text_bbox[0]
    rank_x = 411 - text_width
    draw.text((rank_x, 14), rank_text, font=rank_font, fill=(255, 255, 255))

    # 9.5. 绘制Rank图标
    rank = get_rank_by_achievement(achievement)
    rank_asset = rank_to_asset_name(rank)
    rank_icon_path = os.path.join(ASSETS_DIR, rank_asset)
    try:
        rank_icon = Image.open(rank_icon_path).convert('RGBA')
        # 等比缩放到137x54的95%内
        scale_factor = 0.95
        target_w, target_h = int(137 * scale_factor), int(54 * scale_factor)
        w, h = rank_icon.size
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        rank_icon = rank_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
        # 居中贴到(276,85)的区域
        paste_x = 276 + (137 - new_w) // 2 + 5
        paste_y = 85 + (54 - new_h) // 2
        canvas.paste(rank_icon, (paste_x, paste_y), rank_icon)
    except FileNotFoundError:
        print(f"Rank图标未找到: {rank_icon_path}")

    # 指示器整体缩放比例
    indicator_scale = 1.2

    # 9.6. 绘制两个空白底图标
    blank_icon_path = os.path.join(ASSETS_DIR, 'UI_MSS_MBase_Icon_Blank.png')
    for pos_x in [302, 360]:
        try:
            # 原始参数
            base_x, base_y, base_w, base_h = pos_x, 152, 44, 44
            # 以中心为基准缩放
            center_x = base_x + base_w // 2
            center_y = base_y + base_h // 2
            new_w = int(base_w * indicator_scale)
            new_h = int(base_h * indicator_scale)
            new_x = center_x - new_w // 2
            new_y = center_y - new_h // 2
            blank_icon = Image.open(blank_icon_path).convert('RGBA')
            blank_icon = blank_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
            canvas.paste(blank_icon, (new_x, new_y), blank_icon)
        except FileNotFoundError:
            print(f"空白底图标未找到: {blank_icon_path}")

    # 指示器整体偏移量，便于整体调整
    indicator_offset_x = 2
    indicator_offset_y = 2
    fc_indicator_extra_offset_y = 1

    # 9.7. 绘制fc/ap图标
    fc_icon_map = {
        1: ("UI_MSS_MBase_Icon_FC.png", 301, 149, 44, 44, 65, 65),
        2: ("UI_MSS_MBase_Icon_FCp.png", 301, 149, 44, 44, 70, 65),
        3: ("UI_MSS_MBase_Icon_AP.png", 301, 149, 44, 44, 65, 65),
        4: ("UI_MSS_MBase_Icon_APp.png", 301, 149, 44, 44, 70, 65)
    }
    if fc_indicator in fc_icon_map:
        icon_name, x, y, w, h, raw_w, raw_h = fc_icon_map[fc_indicator]
        # 以中心为基准缩放
        center_x = x + w // 2 + indicator_offset_x
        center_y = y + h // 2 + indicator_offset_y + fc_indicator_extra_offset_y
        new_w = int(w * indicator_scale)
        new_h = int(h * indicator_scale)
        x = center_x - new_w // 2
        y = center_y - new_h // 2
        icon_path = os.path.join(ASSETS_DIR, icon_name)
        try:
            icon_img = Image.open(icon_path).convert('RGBA')
            # 判断是否为带+图标
            if raw_w == 70:
                scale = min(new_w / 65, new_h / 65)
                img_w = int(70 * scale)
                img_h = int(65 * scale)
                icon_img = icon_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
                paste_x = x + (new_w - int(65 * scale)) // 2 - int((70 - 65) * scale // 2)
                paste_y = y + (new_h - img_h) // 2
            else:
                scale = min(new_w / raw_w, new_h / raw_h)
                img_w = int(raw_w * scale)
                img_h = int(raw_h * scale)
                icon_img = icon_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
                paste_x = x + (new_w - img_w) // 2
                paste_y = y + (new_h - img_h) // 2
            canvas.paste(icon_img, (paste_x, paste_y), icon_img)
        except FileNotFoundError:
            print(f"FC/AP图标未找到: {icon_path}")

    # 9.8. 绘制fs/fdx图标
    fs_icon_map = {
        1: ("UI_MSS_MBase_Icon_FS.png", 358, 150, 44, 44, 65, 65),
        2: ("UI_MSS_MBase_Icon_FSp.png", 358, 150, 44, 44, 70, 65),
        3: ("UI_MSS_MBase_Icon_FSD.png", 358, 150, 44, 44, 65, 65),
        4: ("UI_MSS_MBase_Icon_FSDp.png", 361, 150, 44, 44, 70, 65),
        5: ("UI_MSS_MBase_Icon_SP.png", 358, 150, 44, 44, 65, 65)
    }
    if fs_indicator in fs_icon_map:
        icon_name, x, y, w, h, raw_w, raw_h = fs_icon_map[fs_indicator]
        # 以中心为基准缩放
        center_x = x + w // 2 + indicator_offset_x
        center_y = y + h // 2 + indicator_offset_y
        new_w = int(w * indicator_scale)
        new_h = int(h * indicator_scale)
        x = center_x - new_w // 2
        y = center_y - new_h // 2
        icon_path = os.path.join(ASSETS_DIR, icon_name)
        try:
            icon_img = Image.open(icon_path).convert('RGBA')
            if raw_w == 70:
                scale = min(new_w / 65, new_h / 65)
                img_w = int(70 * scale)
                img_h = int(65 * scale)
                icon_img = icon_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
                paste_x = x + (new_w - int(65 * scale)) // 2 - int((70 - 65) * scale // 2)
                paste_y = y + (new_h - img_h) // 2
            else:
                scale = min(new_w / raw_w, new_h / raw_h)
                img_w = int(raw_w * scale)
                img_h = int(raw_h * scale)
                icon_img = icon_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
                paste_x = x + (new_w - img_w) // 2
                paste_y = y + (new_h - img_h) // 2
            canvas.paste(icon_img, (paste_x, paste_y), icon_img)
        except FileNotFoundError:
            print(f"FS/FDX图标未找到: {icon_path}")

    return canvas