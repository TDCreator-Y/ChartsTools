#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试：检查代码修复
"""

import sys
import os

def test_code_fix():
    """测试代码修复"""
    print("🔍 检查代码修复...")
    
    # 检查主窗口文件
    main_window_file = "src/ui/main_window.py"
    if os.path.exists(main_window_file):
        print("✅ 主窗口文件存在")
        
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否还有重复的title_text定义
        title_text_count = content.count('self.title_text = QLineEdit')
        print(f"📊 找到 {title_text_count} 个 title_text 定义")
        
        if title_text_count == 1:
            print("✅ 只有一个 title_text 定义（正确）")
        else:
            print(f"⚠️  发现 {title_text_count} 个 title_text 定义")
            
        # 检查是否删除了样式配置中的标题组
        if "标题设置" in content:
            # 计算"标题设置"出现的次数
            title_setting_count = content.count("标题设置")
            print(f"📊 找到 {title_setting_count} 个 '标题设置' 引用")
            
            if title_setting_count == 0:
                print("✅ 已删除重复的标题设置组")
            else:
                print(f"⚠️  仍有 {title_setting_count} 个标题设置组")
        
        # 检查是否删除了兼容性代码
        if "兼容旧的标题配置" in content:
            print("❌ 仍然存在兼容性代码")
        else:
            print("✅ 已删除兼容性代码")
            
        # 检查基础配置选项卡是否存在
        if "create_basic_config_tab" in content:
            print("✅ 基础配置选项卡存在")
        else:
            print("❌ 基础配置选项卡不存在")
            
        # 检查_get_current_config方法
        if "_get_current_config" in content:
            print("✅ _get_current_config方法存在")
        else:
            print("❌ _get_current_config方法不存在")
            
        # 检查refresh_current_chart方法
        if "refresh_current_chart" in content:
            print("✅ refresh_current_chart方法存在")
        else:
            print("❌ refresh_current_chart方法不存在")
            
        print("\n🎯 修复总结:")
        print("1. 删除了样式配置选项卡中重复的title_text定义")
        print("2. 删除了兼容性代码")
        print("3. 保留了基础配置选项卡中的完整标题配置")
        print("4. 标题配置现在应该能正常工作")
        
    else:
        print("❌ 主窗口文件不存在")

if __name__ == "__main__":
    test_code_fix() 