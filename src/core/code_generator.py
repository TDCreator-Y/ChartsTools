#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码生成器模块
负责生成完整的HTML和JavaScript代码供用户导出和学习
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime


class CodeGenerator(QObject):
    """代码生成器类
    
    负责生成教学用的完整代码，包括：
    - HTML页面代码
    - JavaScript代码
    - CSS样式代码
    - 完整的项目文件
    """
    
    # 代码生成信号
    code_generated = pyqtSignal(dict)  # 生成的代码字典
    code_error = pyqtSignal(str)       # 错误信息
    
    def __init__(self):
        super().__init__()
        self._current_config = None
        self._current_data = None
        
    def generate_code(self, data_info: Dict[str, Any], chart_config: Dict[str, Any]) -> Dict[str, str]:
        """生成完整代码
        
        Args:
            data_info: 数据信息
            chart_config: 图表配置
            
        Returns:
            Dict[str, str]: 包含各种代码的字典
        """
        try:
            self._current_data = data_info
            self._current_config = chart_config
            
            # 生成各种代码
            html_code = self._generate_html_code()
            js_code = self._generate_javascript_code()
            css_code = self._generate_css_code()
            complete_html = self._generate_complete_html()
            
            # 生成说明文档
            readme_content = self._generate_readme()
            
            code_dict = {
                "html": html_code,
                "javascript": js_code,
                "css": css_code,
                "complete_html": complete_html,
                "readme": readme_content
            }
            
            self.code_generated.emit(code_dict)
            return code_dict
            
        except Exception as e:
            error_msg = f"生成代码失败: {str(e)}"
            self.code_error.emit(error_msg)
            return {}
    
    def _generate_html_code(self) -> str:
        """生成HTML代码
        
        Returns:
            str: HTML代码
        """
        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECharts 矩阵热力图</title>
    <!-- 引入 ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.0/dist/echarts.min.js"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ECharts 矩阵热力图演示</h1>
            <p>基于 ECharts 的矩阵热力图可视化</p>
        </div>
        
        <div class="chart-container">
            <div id="heatmap-chart" class="chart"></div>
        </div>
        
        <div class="info-panel">
            <h3>数据信息</h3>
            <div class="info-item">
                <span class="label">数据维度:</span>
                <span class="value">{shape}</span>
            </div>
            <div class="info-item">
                <span class="label">数值范围:</span>
                <span class="value">{value_range}</span>
            </div>
            <div class="info-item">
                <span class="label">数据来源:</span>
                <span class="value">{data_source}</span>
            </div>
        </div>
        
        <div class="controls">
            <button id="reset-btn" class="btn">重置视图</button>
            <button id="export-btn" class="btn">导出图片</button>
            <button id="theme-btn" class="btn">切换主题</button>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>'''
        
        # 填充数据信息
        shape = f"{self._current_data['shape'][0]}×{self._current_data['shape'][1]}"
        value_range = f"{self._current_data['value_range'][0]:.2f} - {self._current_data['value_range'][1]:.2f}"
        data_source = self._current_data.get('file_path', '示例数据')
        
        return html_template.format(
            shape=shape,
            value_range=value_range,
            data_source=data_source
        )
    
    def _generate_javascript_code(self) -> str:
        """生成JavaScript代码
        
        Returns:
            str: JavaScript代码
        """
        # 获取配置
        data_config = self._current_config.get("data", {})
        style_config = self._current_config.get("style", {})
        interaction_config = self._current_config.get("interaction", {})
        animation_config = self._current_config.get("animation", {})
        
        # 生成ECharts配置
        echarts_option = {
            "title": style_config.get("title", {"text": "矩阵热力图"}),
            "tooltip": interaction_config.get("tooltip", {"trigger": "item"}),
            "animation": True,
            "animationDuration": animation_config.get("animationDuration", 1000),
            "animationEasing": animation_config.get("animationEasing", "cubicInOut"),
            "visualMap": {
                **style_config.get("visualMap", {}),
                "min": self._current_data["value_range"][0],
                "max": self._current_data["value_range"][1]
            },
            "xAxis": {
                **style_config.get("xAxis", {}),
                "data": self._current_data["col_labels"]
            },
            "yAxis": {
                **style_config.get("yAxis", {}),
                "data": self._current_data["row_labels"]
            },
            "series": [{
                "name": "矩阵热力图",
                "type": "heatmap",
                "data": self._current_data["matrix_data"],
                "label": {
                    "show": True
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }
        
        # 生成JavaScript代码
        js_template = '''// ECharts 矩阵热力图配置和初始化
(function() {{
    'use strict';
    
    // 全局变量
    let chart;
    let isDarkTheme = false;
    
    // 图表配置
    const option = {option_json};
    
    // 初始化图表
    function initChart() {{
        const chartDom = document.getElementById('heatmap-chart');
        chart = echarts.init(chartDom);
        
        // 设置配置项
        chart.setOption(option);
        
        // 响应式调整
        window.addEventListener('resize', function() {{
            chart.resize();
        }});
    }}
    
    // 重置视图
    function resetView() {{
        if (chart) {{
            chart.dispatchAction({{
                type: 'dataZoom',
                start: 0,
                end: 100
            }});
        }}
    }}
    
    // 导出图片
    function exportImage() {{
        if (chart) {{
            const url = chart.getDataURL({{
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#fff'
            }});
            
            const link = document.createElement('a');
            link.download = '矩阵热力图.png';
            link.href = url;
            link.click();
        }}
    }}
    
    // 切换主题
    function toggleTheme() {{
        if (chart) {{
            chart.dispose();
            const chartDom = document.getElementById('heatmap-chart');
            chart = echarts.init(chartDom, isDarkTheme ? 'light' : 'dark');
            chart.setOption(option);
            isDarkTheme = !isDarkTheme;
        }}
    }}
    
    // 事件监听
    document.addEventListener('DOMContentLoaded', function() {{
        initChart();
        
        // 按钮事件
        document.getElementById('reset-btn').addEventListener('click', resetView);
        document.getElementById('export-btn').addEventListener('click', exportImage);
        document.getElementById('theme-btn').addEventListener('click', toggleTheme);
    }});
    
    // 图表点击事件
    function setupChartEvents() {{
        if (chart) {{
            chart.on('click', function(params) {{
                console.log('点击数据:', params);
                
                // 显示详细信息
                const info = `
                    坐标: ({col_labels}[${{params.data[0]}}], {row_labels}[${{params.data[1]}}])
                    数值: ${{params.data[2]}}
                `;
                
                // 这里可以添加更多交互逻辑
                alert(info);
            }});
        }}
    }}
    
    // 设置图表事件
    setTimeout(setupChartEvents, 100);
}})();'''
        
        return js_template.format(
            option_json=json.dumps(echarts_option, ensure_ascii=False, indent=4),
            col_labels=json.dumps(self._current_data["col_labels"], ensure_ascii=False),
            row_labels=json.dumps(self._current_data["row_labels"], ensure_ascii=False)
        )
    
    def _generate_css_code(self) -> str:
        """生成CSS代码
        
        Returns:
            str: CSS代码
        """
        css_template = '''/* 矩阵热力图样式文件 */

/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* 头部样式 */
.header {
    text-align: center;
    margin-bottom: 30px;
    color: white;
}

.header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-weight: 300;
}

.header p {
    font-size: 1.2em;
    opacity: 0.9;
}

/* 图表容器 */
.chart-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    margin-bottom: 30px;
    overflow: hidden;
}

.chart {
    width: 100%;
    height: 600px;
    border-radius: 12px;
}

/* 信息面板 */
.info-panel {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
}

.info-panel h3 {
    color: #333;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.info-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    padding: 5px 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.info-item:last-child {
    border-bottom: none;
}

.label {
    font-weight: 600;
    color: #666;
}

.value {
    color: #333;
    font-family: 'Courier New', monospace;
}

/* 控制按钮 */
.controls {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.btn {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.btn:active {
    transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 15px;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .chart {
        height: 400px;
    }
    
    .info-item {
        flex-direction: column;
        gap: 5px;
    }
    
    .controls {
        flex-direction: column;
        align-items: center;
    }
    
    .btn {
        width: 200px;
    }
}

/* 动画效果 */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.chart-container,
.info-panel {
    animation: fadeIn 0.8s ease;
}

/* 加载动画 */
.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    font-size: 18px;
    color: #666;
}

.loading::after {
    content: '';
    width: 20px;
    height: 20px;
    border: 2px solid #667eea;
    border-top: 2px solid transparent;
    border-radius: 50%;
    margin-left: 10px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}'''
        
        return css_template
    
    def _generate_complete_html(self) -> str:
        """生成完整的HTML文件
        
        Returns:
            str: 完整的HTML代码
        """
        html_code = self._generate_html_code()
        css_code = self._generate_css_code()
        js_code = self._generate_javascript_code()
        
        # 内联样式和脚本
        complete_html = html_code.replace(
            '<link rel="stylesheet" href="style.css">',
            f'<style>\n{css_code}\n</style>'
        ).replace(
            '<script src="script.js"></script>',
            f'<script>\n{js_code}\n</script>'
        )
        
        return complete_html
    
    def _generate_readme(self) -> str:
        """生成说明文档
        
        Returns:
            str: README内容
        """
        readme_template = '''# ECharts 矩阵热力图项目

## 项目描述
这是一个基于 ECharts 的矩阵热力图可视化项目，展示了如何使用 ECharts 创建交互式的矩阵热力图。

## 生成信息
- 生成时间: {timestamp}
- 数据维度: {shape}
- 数值范围: {value_range}
- 数据来源: {data_source}

## 文件结构
```
矩阵热力图项目/
├── index.html          # 主页面文件
├── style.css           # 样式文件
├── script.js           # JavaScript脚本
├── complete.html       # 完整的单文件版本
└── README.md          # 说明文档
```

## 使用方法
1. 直接打开 `index.html` 文件即可查看完整的矩阵热力图
2. 或者打开 `complete.html` 查看单文件版本
3. 支持以下交互操作：
   - 鼠标悬停查看数值
   - 点击数据点查看详细信息
   - 重置视图按钮
   - 导出图片功能
   - 切换主题

## 技术特点
- 使用 ECharts 5.x 版本
- 响应式设计，支持移动设备
- 现代 CSS 样式，包含动画效果
- 完整的 JavaScript 交互功能
- 支持主题切换和图片导出

## 配置说明
图表配置包含以下部分：
- **数据配置**: 矩阵数据、行列标签、数值范围
- **样式配置**: 标题、颜色映射、坐标轴样式
- **交互配置**: 提示框、数据缩放功能
- **动画配置**: 过渡效果和动画参数

## 自定义修改
你可以通过修改以下部分来自定义图表：
1. 在 `script.js` 中修改 `option` 对象来调整图表配置
2. 在 `style.css` 中修改样式
3. 在 `index.html` 中修改页面结构

## 浏览器支持
- Chrome (推荐)
- Firefox
- Safari
- Edge
- 移动端浏览器

## 学习资源
- [ECharts 官方文档](https://echarts.apache.org/zh/index.html)
- [ECharts 热力图配置](https://echarts.apache.org/zh/option.html#series-heatmap)
- [JavaScript 基础教程](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)

## 注意事项
- 确保网络连接正常以加载 ECharts 库
- 大数据集可能影响性能，建议使用数据采样
- 移动设备上建议使用触摸友好的交互方式

---
*此项目由 ECharts 矩阵热力图工具自动生成*'''
        
        # 填充信息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shape = f"{self._current_data['shape'][0]}×{self._current_data['shape'][1]}"
        value_range = f"{self._current_data['value_range'][0]:.2f} - {self._current_data['value_range'][1]:.2f}"
        data_source = self._current_data.get('file_path', '示例数据')
        
        return readme_template.format(
            timestamp=timestamp,
            shape=shape,
            value_range=value_range,
            data_source=data_source
        )
    
    def export_project(self, output_dir: str) -> bool:
        """导出完整项目
        
        Args:
            output_dir: 输出目录
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成代码
            code_dict = self.generate_code(self._current_data, self._current_config)
            
            if not code_dict:
                return False
            
            # 保存文件
            files = {
                'index.html': code_dict['html'],
                'style.css': code_dict['css'],
                'script.js': code_dict['javascript'],
                'complete.html': code_dict['complete_html'],
                'README.md': code_dict['readme']
            }
            
            for filename, content in files.items():
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            self.code_error.emit(f"导出项目失败: {str(e)}")
            return False
    
    def get_code_preview(self, code_type: str) -> str:
        """获取代码预览
        
        Args:
            code_type: 代码类型 ("html", "javascript", "css")
            
        Returns:
            str: 代码内容
        """
        if not self._current_data or not self._current_config:
            return ""
        
        try:
            if code_type == "html":
                return self._generate_html_code()
            elif code_type == "javascript":
                return self._generate_javascript_code()
            elif code_type == "css":
                return self._generate_css_code()
            else:
                return ""
                
        except Exception as e:
            self.code_error.emit(f"获取代码预览失败: {str(e)}")
            return ""
    
    def get_teaching_comments(self, code_type: str) -> List[Dict[str, Any]]:
        """获取教学注释
        
        Args:
            code_type: 代码类型
            
        Returns:
            List[Dict[str, Any]]: 教学注释列表
        """
        if code_type == "javascript":
            return [
                {
                    "line": 5,
                    "type": "explanation",
                    "content": "这里定义了全局变量来存储图表实例和主题状态"
                },
                {
                    "line": 8,
                    "type": "explanation", 
                    "content": "option对象包含了ECharts的所有配置项"
                },
                {
                    "line": 15,
                    "type": "tip",
                    "content": "使用echarts.init()初始化图表实例"
                },
                {
                    "line": 20,
                    "type": "tip",
                    "content": "监听窗口大小变化，实现响应式图表"
                }
            ]
        elif code_type == "css":
            return [
                {
                    "line": 1,
                    "type": "explanation",
                    "content": "使用CSS Grid和Flexbox实现响应式布局"
                },
                {
                    "line": 15,
                    "type": "tip",
                    "content": "渐变背景增强视觉效果"
                }
            ]
        else:
            return [] 