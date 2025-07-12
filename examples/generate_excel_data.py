#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成示例数据的Excel文件
"""

import pandas as pd
import numpy as np
import os

def create_datacenter_temperature_excel():
    """创建机房温度分布Excel数据"""
    # 机房温度数据 (8x8网格, 温度单位: 摄氏度)
    temperature_data = [
        [22.5, 23.1, 24.2, 25.8, 26.4, 25.9, 24.3, 23.2],
        [23.8, 24.5, 25.6, 27.2, 28.1, 27.6, 25.8, 24.6],
        [24.2, 25.8, 27.1, 29.3, 30.2, 29.8, 27.4, 25.9],
        [25.6, 27.2, 28.9, 31.5, 32.8, 31.9, 28.7, 27.1],
        [26.1, 28.3, 30.4, 33.2, 34.6, 33.5, 30.1, 28.5],
        [25.4, 26.9, 28.7, 30.8, 31.4, 30.9, 28.3, 26.7],
        [24.7, 25.3, 26.8, 28.1, 28.9, 28.4, 26.5, 25.1],
        [23.9, 24.2, 25.4, 26.7, 27.2, 26.8, 25.2, 24.0]
    ]
    
    columns = ['A列', 'B列', 'C列', 'D列', 'E列', 'F列', 'G列', 'H列']
    index = ['第1行', '第2行', '第3行', '第4行', '第5行', '第6行', '第7行', '第8行']
    
    df = pd.DataFrame(temperature_data, columns=columns, index=index)
    df.to_excel('机房温度分布数据.xlsx', sheet_name='温度分布')
    print("✓ 机房温度分布数据.xlsx 已创建")

def create_network_latency_excel():
    """创建网络延迟数据Excel文件"""
    # 网络延迟数据 (6x6网格, 延迟单位: 毫秒)
    latency_data = [
        [0, 12, 25, 45, 78, 102],
        [12, 0, 18, 38, 65, 89],
        [25, 18, 0, 22, 48, 72],
        [45, 38, 22, 0, 28, 55],
        [78, 65, 48, 28, 0, 32],
        [102, 89, 72, 55, 32, 0]
    ]
    
    locations = ['北京', '上海', '广州', '深圳', '杭州', '成都']
    
    df = pd.DataFrame(latency_data, columns=locations, index=locations)
    df.to_excel('网络延迟矩阵.xlsx', sheet_name='网络延迟')
    print("✓ 网络延迟矩阵.xlsx 已创建")

def create_server_load_excel():
    """创建服务器负载数据Excel文件"""
    # 服务器负载数据 (5x6网格, 负载百分比)
    load_data = [
        [15.2, 23.8, 45.6, 67.2, 78.9, 82.3],
        [18.5, 35.2, 52.7, 71.8, 85.4, 88.7],
        [22.1, 41.6, 58.3, 75.9, 89.2, 91.5],
        [19.8, 38.4, 55.1, 73.6, 87.3, 90.8],
        [16.7, 29.3, 48.9, 69.4, 81.7, 85.1]
    ]
    
    time_slots = ['08:00', '12:00', '16:00', '20:00', '00:00', '04:00']
    servers = ['Web服务器1', 'Web服务器2', '数据库服务器', '缓存服务器', '文件服务器']
    
    df = pd.DataFrame(load_data, columns=time_slots, index=servers)
    df.to_excel('服务器负载数据.xlsx', sheet_name='服务器负载')
    print("✓ 服务器负载数据.xlsx 已创建")

def create_student_correlation_excel():
    """创建学生成绩相关性数据Excel文件"""
    # 学科成绩相关性数据
    correlation_data = [
        [1.00, 0.78, 0.65, 0.45, 0.32, 0.28],
        [0.78, 1.00, 0.72, 0.55, 0.41, 0.35],
        [0.65, 0.72, 1.00, 0.58, 0.43, 0.39],
        [0.45, 0.55, 0.58, 1.00, 0.67, 0.62],
        [0.32, 0.41, 0.43, 0.67, 1.00, 0.75],
        [0.28, 0.35, 0.39, 0.62, 0.75, 1.00]
    ]
    
    subjects = ['数学', '物理', '化学', '英语', '语文', '历史']
    
    df = pd.DataFrame(correlation_data, columns=subjects, index=subjects)
    df.to_excel('学科成绩相关性.xlsx', sheet_name='相关性分析')
    print("✓ 学科成绩相关性.xlsx 已创建")

def create_sales_heatmap_excel():
    """创建销售热力图数据Excel文件"""
    # 销售数据 (12个月 x 5个地区)
    sales_data = [
        [120, 135, 142, 158, 165],  # 1月
        [125, 140, 148, 162, 170],  # 2月
        [130, 145, 152, 165, 175],  # 3月
        [135, 150, 158, 170, 180],  # 4月
        [140, 155, 162, 175, 185],  # 5月
        [145, 160, 168, 180, 190],  # 6月
        [150, 165, 172, 185, 195],  # 7月
        [155, 170, 178, 190, 200],  # 8月
        [160, 175, 182, 195, 205],  # 9月
        [165, 180, 188, 200, 210],  # 10月
        [170, 185, 192, 205, 215],  # 11月
        [175, 190, 198, 210, 220],  # 12月
    ]
    
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    regions = ['华北', '华东', '华南', '华中', '西南']
    
    df = pd.DataFrame(sales_data, columns=regions, index=months)
    df.to_excel('销售数据热力图.xlsx', sheet_name='销售数据')
    print("✓ 销售数据热力图.xlsx 已创建")

def main():
    """主函数 - 生成所有示例数据"""
    print("开始生成示例数据Excel文件...")
    
    try:
        create_datacenter_temperature_excel()
        create_network_latency_excel()
        create_server_load_excel()
        create_student_correlation_excel()
        create_sales_heatmap_excel()
        
        print("\n✓ 所有示例数据Excel文件已成功创建！")
        print("文件列表:")
        print("- 机房温度分布数据.xlsx")
        print("- 网络延迟矩阵.xlsx")
        print("- 服务器负载数据.xlsx")
        print("- 学科成绩相关性.xlsx")
        print("- 销售数据热力图.xlsx")
        
    except Exception as e:
        print(f"❌ 创建Excel文件时发生错误: {e}")
        print("请确保已安装pandas和openpyxl库:")
        print("pip install pandas openpyxl")

if __name__ == "__main__":
    main() 