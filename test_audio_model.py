#!/usr/bin/env python3
"""
测试 AudioModel 类的模型路径检测功能
"""

from AudioExtract import AudioModel

def test_nonexistent_path():
    """测试不存在的模型路径"""
    print("=== 测试不存在的模型路径 ===")
    try:
        model = AudioModel("./nonexistent_model_path")
        print("错误：应该已经终止程序")
    except SystemExit as e:
        print(f"程序正确终止，退出码: {e.code}")
    except Exception as e:
        print(f"捕获到异常: {e}")

def test_existing_path():
    """测试存在的模型路径（如果有的话）"""
    print("\n=== 测试存在的模型路径 ===")
    # 这里可以测试一个实际存在的模型路径
    # 例如: "./whisper-base" 如果存在的话
    test_paths = [
        "./whisper-base",
        "./whisper-large-v3-turbo",
        "./models/whisper-base"
    ]
    
    for path in test_paths:
        print(f"尝试路径: {path}")
        try:
            model = AudioModel(path)
            print(f"成功加载模型: {path}")
            break
        except SystemExit:
            print(f"路径不存在: {path}")
        except Exception as e:
            print(f"加载失败: {e}")

if __name__ == "__main__":
    print("AudioModel 模型路径检测测试")
    print("=" * 40)
    
    # 测试不存在的路径
    test_nonexistent_path()
    
    # 测试可能存在的路径
    test_existing_path()
    
    print("\n测试完成！")
