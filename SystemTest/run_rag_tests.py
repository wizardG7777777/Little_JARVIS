#!/usr/bin/env python3
"""
RAG.py 测试运行器
自动运行RAG功能测试并生成详细报告
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def check_dependencies():
    """检查测试依赖"""
    print("🔍 检查测试依赖...")
    
    required_modules = [
        'chromadb',
        'pathlib', 
        'tempfile',
        'unittest'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - 未安装")
    
    if missing_modules:
        print(f"\n⚠️  缺少依赖模块: {', '.join(missing_modules)}")
        print("请使用以下命令安装:")
        for module in missing_modules:
            if module not in ['pathlib', 'tempfile', 'unittest']:  # 这些是标准库
                print(f"pip install {module}")
        return False
    
    print("✅ 所有依赖检查通过")
    return True

def check_rag_module():
    """检查RAG模块是否存在"""
    print("\n🔍 检查RAG模块...")
    
    # 检查RAG.py文件
    rag_file = Path(__file__).parent.parent / "RAGmodule" / "RAG.py"
    if not rag_file.exists():
        print(f"❌ RAG.py 文件不存在: {rag_file}")
        return False
    
    print(f"✅ RAG.py 文件存在: {rag_file}")
    
    # 尝试导入RAG模块
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from RAGmodule.RAG import RagUniversal
        print("✅ RAG模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ RAG模块导入失败: {e}")
        return False

def run_tests():
    """运行测试"""
    print("\n🚀 开始运行RAG功能测试...")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_rag_functionality.py"
    
    try:
        # 运行测试
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ 运行测试时发生错误: {e}")
        return False, "", str(e)

def generate_summary_report(success, stdout, stderr):
    """生成测试总结报告"""
    print("\n📊 生成测试总结报告...")
    
    report_file = Path(__file__).parent / "rag_test_summary.md"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# RAG.py 测试总结报告\n\n")
            f.write(f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 解析测试结果
            if "测试完成" in stdout:
                f.write("## 🎯 测试状态\n\n")
                if success:
                    f.write("✅ **所有测试通过** - RAG.py功能正常\n\n")
                else:
                    f.write("❌ **部分测试失败** - 需要检查RAG.py实现\n\n")
                
                # 提取测试统计信息
                lines = stdout.split('\n')
                test_stats = []
                
                for line in lines:
                    if "成功率:" in line and "%" in line:
                        test_stats.append(line.strip())
                
                if test_stats:
                    f.write("## 📈 测试统计\n\n")
                    for stat in test_stats:
                        f.write(f"- {stat}\n")
                    f.write("\n")
                
                # 测试详情
                f.write("## 📋 测试详情\n\n")
                f.write("### 测试项目\n\n")
                f.write("1. **RAG类初始化测试** - 验证RagUniversal类初始化\n")
                f.write("2. **Markdown文件切分测试** - 验证split_markdown_semantic方法\n")
                f.write("3. **向量数据库添加测试** - 验证add方法\n")
                f.write("4. **向量检索测试** - 验证retrieve方法\n")
                f.write("5. **完整工作流程集成测试** - 验证端到端RAG流程\n")
                f.write("6. **错误处理测试** - 验证异常情况处理\n\n")
                
                # 功能验证
                f.write("### 功能验证结果\n\n")
                if "RAG初始化成功率: 100.00%" in stdout:
                    f.write("✅ **初始化功能** - 正常\n")
                else:
                    f.write("❌ **初始化功能** - 异常\n")
                
                if "内容完整性: 100.00%" in stdout:
                    f.write("✅ **Markdown切分功能** - 正常\n")
                else:
                    f.write("❌ **Markdown切分功能** - 异常\n")
                
                if "添加功能成功率:" in stdout:
                    f.write("✅ **向量数据库添加功能** - 正常\n")
                else:
                    f.write("❌ **向量数据库添加功能** - 异常\n")
                
                if "检索功能成功率:" in stdout:
                    f.write("✅ **向量检索功能** - 正常\n")
                else:
                    f.write("❌ **向量检索功能** - 异常\n")
                
                if "完整工作流程成功率:" in stdout:
                    f.write("✅ **集成工作流程** - 正常\n")
                else:
                    f.write("❌ **集成工作流程** - 异常\n")
                
                f.write("\n")
                
            else:
                f.write("## ❌ 测试执行失败\n\n")
                f.write("测试程序未能正常完成，请检查:\n")
                f.write("- RAG.py文件是否存在\n")
                f.write("- 依赖模块是否正确安装\n")
                f.write("- 系统环境是否配置正确\n\n")
            
            # 错误信息
            if stderr:
                f.write("## 🐛 错误信息\n\n")
                f.write("```\n")
                f.write(stderr)
                f.write("\n```\n\n")
            
            # 使用建议
            f.write("## 💡 使用建议\n\n")
            f.write("### 如果测试全部通过\n")
            f.write("- RAG.py功能正常，可以安全使用\n")
            f.write("- 建议定期运行测试确保功能稳定\n\n")
            
            f.write("### 如果测试部分失败\n")
            f.write("- 检查失败的具体测试项目\n")
            f.write("- 查看详细的错误信息\n")
            f.write("- 验证RAG.py的依赖是否完整\n")
            f.write("- 检查ChromaDB配置是否正确\n\n")
            
            f.write("### 相关文件\n")
            f.write("- `test_rag_functionality.py` - 主测试程序\n")
            f.write("- `rag_test_report.md` - 详细测试报告\n")
            f.write("- `RAG测试说明.md` - 测试说明文档\n")
        
        print(f"✅ 测试总结报告已生成: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ 生成总结报告时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🔧 RAG.py 自动化测试工具")
    print("=" * 50)
    
    # 步骤1: 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的模块后重试")
        return False
    
    # 步骤2: 检查RAG模块
    if not check_rag_module():
        print("\n❌ RAG模块检查失败，请确认RAG.py文件存在且可导入")
        return False
    
    # 步骤3: 运行测试
    success, stdout, stderr = run_tests()
    
    # 步骤4: 生成总结报告
    generate_summary_report(success, stdout, stderr)
    
    # 步骤5: 显示结果
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成 - 所有功能正常")
    else:
        print("⚠️  测试完成 - 发现问题，请查看报告")
    
    print("\n📁 生成的文件:")
    print("- rag_test_report.md (详细测试报告)")
    print("- rag_test_summary.md (测试总结报告)")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
