from PIL import Image

def repeat_image(input_path, output_path, repeat_x=5, repeat_y=7):
    # 打开原始图片
    img = Image.open(input_path)
    w, h = img.size

    # 创建新图片
    new_img = Image.new('RGB', (w * repeat_x, h * repeat_y))

    # 逐步粘贴
    for y in range(repeat_y):
        for x in range(repeat_x):
            new_img.paste(img, (x * w, y * h))

    # 保存新图片
    new_img.save(output_path)
    print(f"已保存到 {output_path}")

if __name__ == "__main__":
    input_path = "song_cell_test.png"  # 替换为你的图片路径
    output_path = "output.png"      # 输出图片路径
    repeat_image(input_path, output_path)