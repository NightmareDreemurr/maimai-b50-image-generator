import os
from modules.song_cell import generate_song_cell

def main():
    """
    测试函数，用于生成一个乐曲单元格图像并保存。
    """
    # 确保输出目录存在
    if not os.path.exists('output'):
        os.makedirs('output')

    # 提供一组用于测试的示例参数
    # 你可以修改这些值来测试不同的情况
    test_params = {
        "cover_id": "1394",
        "difficulty": 3,  # 3: MASTER
        "is_dx": 1,         # 1: DX谱面
        "song_title": "World's End Loneliness",
        "achievement": 1010000, # 101.0000%
        "dx_score": 3702,
        "dx_total": 3702,
        "base": 14.9,
        "section_rank": 1
    }

    print("正在生成图片...")
    
    # 调用生成函数
    try:
        song_image = generate_song_cell(**test_params)
        
        # 保存图片
        output_path = os.path.join('output', 'song_cell_output.png')
        song_image.save(output_path)
        
        print(f"图片已成功保存到: {output_path}")

    except Exception as e:
        print(f"生成图片时发生错误: {e}")

if __name__ == '__main__':
    main() 