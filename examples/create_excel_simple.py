#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的Excel数据生成脚本（不依赖pandas）
使用csv模块和基本的文件操作
"""

import csv
import os

def csv_to_excel_content(csv_file, excel_file):
    """
    将CSV文件转换为Excel可读的格式
    注意：这里生成的是制表符分隔的文本文件，可以被Excel打开
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # 创建Excel兼容格式的文件（制表符分隔）
        with open(excel_file, 'w', encoding='utf-8', newline='') as f:
            for row in rows:
                f.write('\t'.join(row) + '\n')
        
        print(f"✓ 已转换: {csv_file} -> {excel_file}")
        return True
    
    except Exception as e:
        print(f"❌ 转换失败 {csv_file}: {e}")
        return False

def main():
    """转换所有CSV文件为Excel格式"""
    print("开始转换CSV文件为Excel格式...")
    
    # 定义文件映射
    csv_files = [
        '机房温度分布数据.csv',
        '网络延迟矩阵.csv',
        '服务器负载数据.csv',
        '学科成绩相关性.csv',
        '销售数据热力图.csv'
    ]
    
    success_count = 0
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            excel_file = csv_file.replace('.csv', '.txt')  # 生成Excel可读的txt文件
            if csv_to_excel_content(csv_file, excel_file):
                success_count += 1
        else:
            print(f"❌ 文件不存在: {csv_file}")
    
    print(f"\n✓ 转换完成！成功转换 {success_count} 个文件")
    print("\n生成的文件可以直接在Excel中打开：")
    print("- 机房温度分布数据.txt")
    print("- 网络延迟矩阵.txt")
    print("- 服务器负载数据.txt")
    print("- 学科成绩相关性.txt")
    print("- 销售数据热力图.txt")
    print("\n在Excel中打开这些.txt文件时，选择'分隔符'，然后选择'制表符'即可。")

if __name__ == "__main__":
    main() 