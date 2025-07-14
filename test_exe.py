#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChartsTools 打包测试脚本
用于验证打包后的exe程序是否能正常运行
"""

import os
import sys
import subprocess
import time

def test_exe_file(exe_path):
    """测试exe文件是否存在且能正常启动"""
    print(f"测试文件: {exe_path}")
    
    # 检查文件是否存在
    if not os.path.exists(exe_path):
        print("❌ EXE文件不存在")
        return False
    
    # 获取文件大小
    file_size = os.path.getsize(exe_path)
    print(f"✅ 文件大小: {file_size:,} 字节 ({file_size/1024/1024:.1f} MB)")
    
    # 尝试启动程序（非阻塞）
    try:
        print("🚀 尝试启动程序...")
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待2秒查看是否有立即错误
        time.sleep(2)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 程序启动成功，进程正在运行")
            
            # 询问用户是否要终止进程
            try:
                input("按回车键终止测试程序...")
                process.terminate()
                process.wait(timeout=5)
                print("✅ 程序已正常终止")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ 强制终止程序")
            except KeyboardInterrupt:
                process.terminate()
                print("⚠️ 用户中断测试")
            
            return True
        else:
            # 程序立即退出，检查错误
            stdout, stderr = process.communicate()
            print(f"❌ 程序启动失败，退出码: {process.returncode}")
            if stderr:
                print(f"错误信息: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
    except Exception as e:
        print(f"❌ 启动程序时出错: {e}")
        return False

def main():
    """主测试函数"""
    print("="*50)
    print("ChartsTools EXE 测试脚本")
    print("="*50)
    print()
    
    # 测试路径列表
    test_paths = [
        "dist/ChartsTools.exe",  # 单文件版本
        "dist/ChartsTools_Portable/ChartsTools.exe",  # 便携版
    ]
    
    success_count = 0
    total_count = 0
    
    for exe_path in test_paths:
        print(f"测试 {exe_path}:")
        print("-" * 40)
        
        total_count += 1
        if test_exe_file(exe_path):
            success_count += 1
        
        print()
    
    # 输出总结
    print("="*50)
    print("测试总结:")
    print(f"总共测试: {total_count} 个文件")
    print(f"成功: {success_count} 个")
    print(f"失败: {total_count - success_count} 个")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
    elif success_count > 0:
        print("⚠️ 部分测试通过")
    else:
        print("❌ 所有测试失败")
    
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
    
    input("\n按回车键退出...") 