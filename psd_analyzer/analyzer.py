import os
from psd_tools import PSDImage
import json

def analyze_psd(psd_path):
    """
    分析PSD文件并返回所有图层的信息
    
    Args:
        psd_path (str): PSD文件的路径
        
    Returns:
        dict: 包含所有图层信息的字典
    """
    if not os.path.exists(psd_path):
        raise FileNotFoundError(f"找不到PSD文件: {psd_path}")
    
    psd = PSDImage.open(psd_path)
    layers_info = []
    
    def process_layer(layer, depth=0):
        layer_info = {
            "name": layer.name,
            "visible": layer.visible,
            "opacity": layer.opacity,
            "position": {
                "x": layer.offset[0],
                "y": layer.offset[1]
            },
            "size": {
                "width": layer.size[0],
                "height": layer.size[1]
            },
            "depth": depth
        }
        layers_info.append(layer_info)
        
        # 递归处理子图层
        if hasattr(layer, 'layers'):
            for child in layer.layers:
                process_layer(child, depth + 1)
    
    # 处理所有图层
    for layer in psd.descendants():
        process_layer(layer)
    
    return {
        "document_size": {
            "width": psd.size[0],
            "height": psd.size[1]
        },
        "layers": layers_info
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='PSD文件分析工具')
    parser.add_argument('psd_path', help='PSD文件的路径')
    parser.add_argument('--output', '-o', help='输出JSON文件的路径（可选）')
    
    args = parser.parse_args()
    
    try:
        result = analyze_psd(args.psd_path)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"分析结果已保存到: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == '__main__':
    main()
