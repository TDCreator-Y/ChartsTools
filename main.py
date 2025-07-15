#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ECharts矩阵热力图教学工具 - 主程序入口

作者: ECharts教学工具开发团队
版本: 1.0.0
"""

import sys
import os
import traceback

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_environment():
    """检查运行环境"""
    print("检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 10):
        print(f"❌ Python版本过低: {sys.version}")
        print("需要Python 3.10或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必需的依赖
    required_packages = [
        'pandas', 'numpy', 'pyecharts', 'jinja2', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n请安装缺失的包: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_gui_support():
    """检查GUI支持"""
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ GUI支持可用")
        return True
    except ImportError as e:
        print(f"⚠️ GUI支持不可用: {e}")
        print("可以使用命令行模式或解决PyQt6安装问题")
        return False

def run_console_mode():
    """运行控制台模式"""
    print("\n" + "="*50)
    print("ECharts矩阵热力图教学工具 - 控制台模式")
    print("="*50)
    
    # 这里可以添加一些基本的命令行功能
    print("当前可用功能:")
    print("1. 环境检查")
    print("2. 创建示例数据")
    print("3. 生成热力图HTML")
    
    # 导入核心模块（不依赖GUI）
    print("\n📝 核心模块开发状态:")
    core_modules = [
        "core.data_manager",
        "core.chart_renderer", 
        "core.code_generator",
        "core.config_manager"
    ]
    
    loaded_modules = 0
    for module_name in core_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} 已创建")
            loaded_modules += 1
        except ImportError:
            print(f"⏳ {module_name} 待创建")
    
    print(f"\n📊 进度: {loaded_modules}/{len(core_modules)} 个核心模块已完成")
    
    if loaded_modules == 0:
        print("🚀 准备开始核心模块开发！")
    elif loaded_modules == len(core_modules):
        print("🎉 所有核心模块已完成！")
    else:
        print("⚡ 继续开发剩余模块...")

def run_gui_mode():
    """运行GUI模式"""
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.splash_screen import show_splash_screen
        from ui.main_window import MainWindow
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        app.setApplicationName("ChartsTools")
        app.setApplicationVersion("1.2.1")
        app.setApplicationDisplayName("ECharts矩阵热力图教学工具")
        
        # 显示启动画面
        splash = show_splash_screen()
        splash.start_loading()
        
        # 等待启动画面加载完成
        while not splash.is_finished():
            app.processEvents()
        
        # 创建主窗口
        window = MainWindow()
        
        # 启动画面自动关闭后显示主窗口
        window.show()
        
        print("🎉 GUI模式启动成功")
        return app.exec()
        
    except ImportError as e:
        print(f"❌ GUI模式启动失败: {e}")
        print("尝试使用控制台模式")
        return False
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 ECharts矩阵热力图教学工具启动中...")
    print("="*50)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，程序退出")
        sys.exit(1)
    
    # 检查GUI支持
    gui_available = check_gui_support()
    
    # 根据参数决定运行模式
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_mode()
    elif gui_available:
        print("\n尝试启动GUI模式...")
        exit_code = run_gui_mode()
        if exit_code is False:
            print("GUI模式启动失败，切换到控制台模式")
            run_console_mode()
        else:
            # GUI模式正常退出
            sys.exit(exit_code)
    else:
        print("\nGUI不可用，使用控制台模式")
        run_console_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 程序出现未处理的错误: {e}")
        traceback.print_exc()
        sys.exit(1) 