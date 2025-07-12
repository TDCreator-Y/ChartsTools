#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图表渲染器模块
负责使用PyEcharts生成矩阵热力图并与WebEngine集成
"""

import json
import os
import tempfile
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
try:
    from pyecharts import options as opts
    from pyecharts.charts import HeatMap
    from pyecharts.globals import ThemeType
    PYECHARTS_AVAILABLE = True
except ImportError as e:
    print(f"PyEcharts导入失败: {e}")
    print("请安装PyEcharts: pip install pyecharts")
    PYECHARTS_AVAILABLE = False
    # 创建虚拟类以避免运行时错误
    class ThemeType:
        WHITE = "white"
        DARK = "dark"
    HeatMap = None
    opts = None


class ChartRenderer(QObject):
    """图表渲染器类
    
    负责生成矩阵热力图并与WebEngine集成，包括：
    - 使用PyEcharts生成热力图
    - 与QWebEngineView集成
    - 图表主题管理
    - 交互事件处理
    """
    
    # 图表渲染信号
    chart_rendered = pyqtSignal(str)  # HTML内容
    chart_error = pyqtSignal(str)     # 错误信息
    
    def __init__(self, web_view: Optional[QWebEngineView] = None):
        super().__init__()
        self._web_view = web_view
        self._current_chart = None
        self._temp_file_path = None
        self._chart_theme = ThemeType.WHITE
        
    def set_web_view(self, web_view: QWebEngineView) -> None:
        """设置WebEngine视图
        
        Args:
            web_view: QWebEngineView实例
        """
        self._web_view = web_view
    
    def render_heatmap(self, data_info: Dict[str, Any], chart_config: Dict[str, Any]) -> bool:
        """渲染矩阵热力图
        
        Args:
            data_info: 数据信息
            chart_config: 图表配置
            
        Returns:
            bool: 是否渲染成功
        """
        print("🔄 开始渲染热力图...")
        print(f"📊 数据信息: {data_info.get('shape', 'Unknown')}")
        print(f"🎨 配置信息: {bool(chart_config)}")
        print(f"🔧 PyEcharts可用: {PYECHARTS_AVAILABLE}")
        
        try:
            # 检查PyEcharts是否可用
            if not PYECHARTS_AVAILABLE:
                self.chart_error.emit("PyEcharts库不可用，请安装PyEcharts")
                # 生成基于ECharts的HTML作为备用方案
                return self._render_fallback_heatmap(data_info, chart_config)
            
            # 提取数据
            matrix_data = data_info.get("matrix_data", [])
            row_labels = data_info.get("row_labels", [])
            col_labels = data_info.get("col_labels", [])
            value_range = data_info.get("value_range", [0, 1])
            
            if not matrix_data or not row_labels or not col_labels:
                self.chart_error.emit("数据不完整，无法渲染图表")
                return False
            
            # 创建热力图
            heatmap = self._create_heatmap(
                matrix_data, row_labels, col_labels, value_range, chart_config
            )
            
            # 生成HTML
            html_content = self._generate_html(heatmap, chart_config)
            
            # 保存到临时文件
            temp_file = self._save_to_temp_file(html_content)
            
            if temp_file:
                # 加载到WebEngine
                if self._web_view:
                    self._web_view.load(QUrl.fromLocalFile(temp_file))
                
                self._current_chart = heatmap
                self._temp_file_path = temp_file
                self.chart_rendered.emit(html_content)
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"渲染图表失败: {str(e)}"
            self.chart_error.emit(error_msg)
            # 尝试使用备用方案
            return self._render_fallback_heatmap(data_info, chart_config)
    
    def _create_heatmap(self, matrix_data: List[List[Any]], row_labels: List[str], 
                       col_labels: List[str], value_range: List[float], 
                       config: Dict[str, Any]) -> HeatMap:
        """创建热力图对象
        
        Args:
            matrix_data: 矩阵数据
            row_labels: 行标签
            col_labels: 列标签
            value_range: 数值范围
            config: 配置信息
            
        Returns:
            HeatMap: 热力图对象
        """
        # 获取配置
        style_config = config.get("style", {})
        interaction_config = config.get("interaction", {})
        animation_config = config.get("animation", {})
        
        # 创建热力图
        heatmap = (
            HeatMap(init_opts=opts.InitOpts(
                width="100%",
                height="100%",
                theme=self._chart_theme,
                animation_opts=opts.AnimationOpts(
                    animation_duration=animation_config.get("animationDuration", 1000),
                    animation_easing=animation_config.get("animationEasing", "cubicInOut")
                )
            ))
            .add_xaxis(col_labels)
            .add_yaxis(
                "矩阵热力图",
                row_labels,
                matrix_data,
                label_opts=opts.LabelOpts(is_show=True, position="inside"),
            )
            .set_global_opts(
                title_opts=self._get_title_opts(style_config),
                tooltip_opts=self._get_tooltip_opts(interaction_config),
                visualmap_opts=self._get_visualmap_opts(style_config, value_range),
                xaxis_opts=self._get_xaxis_opts(style_config),
                yaxis_opts=self._get_yaxis_opts(style_config),
                datazoom_opts=self._get_datazoom_opts(interaction_config)
            )
        )
        
        return heatmap
    
    def _get_title_opts(self, style_config: Dict[str, Any]) -> opts.TitleOpts:
        """获取标题配置
        
        Args:
            style_config: 样式配置
            
        Returns:
            opts.TitleOpts: 标题配置
        """
        title_config = style_config.get("title", {})
        
        return opts.TitleOpts(
            title=title_config.get("text", "矩阵热力图"),
            pos_left=title_config.get("left", "center"),
            pos_top=title_config.get("top", "5%"),
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=title_config.get("textStyle", {}).get("fontSize", 18),
                font_weight=title_config.get("textStyle", {}).get("fontWeight", "bold"),
                color=title_config.get("textStyle", {}).get("color", "#333")
            )
        )
    
    def _get_tooltip_opts(self, interaction_config: Dict[str, Any]) -> opts.TooltipOpts:
        """获取提示框配置
        
        Args:
            interaction_config: 交互配置
            
        Returns:
            opts.TooltipOpts: 提示框配置
        """
        tooltip_config = interaction_config.get("tooltip", {})
        
        return opts.TooltipOpts(
            trigger="item",
            formatter=tooltip_config.get("formatter", "{b0}: {b1}<br/>{c}")
        )
    
    def _get_visualmap_opts(self, style_config: Dict[str, Any], 
                           value_range: List[float]) -> opts.VisualMapOpts:
        """获取视觉映射配置
        
        Args:
            style_config: 样式配置
            value_range: 数值范围
            
        Returns:
            opts.VisualMapOpts: 视觉映射配置
        """
        visualmap_config = style_config.get("visualMap", {})
        
        return opts.VisualMapOpts(
            min_=value_range[0],
            max_=value_range[1],
            is_calculable=visualmap_config.get("calculable", True),
            orient=visualmap_config.get("orient", "horizontal"),
            pos_left=visualmap_config.get("left", "center"),
            pos_bottom=visualmap_config.get("bottom", "5%"),
            range_color=visualmap_config.get("inRange", {}).get("color", [
                "#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf",
                "#fee090", "#fdae61", "#f46d43", "#d73027"
            ])
        )
    
    def _get_xaxis_opts(self, style_config: Dict[str, Any]) -> opts.AxisOpts:
        """获取X轴配置
        
        Args:
            style_config: 样式配置
            
        Returns:
            opts.AxisOpts: X轴配置
        """
        xaxis_config = style_config.get("xAxis", {})
        
        return opts.AxisOpts(
            type_="category",
            position=xaxis_config.get("position", "top"),
            splitarea_opts=opts.SplitAreaOpts(
                is_show=xaxis_config.get("splitArea", {}).get("show", True),
                areastyle_opts=opts.AreaStyleOpts(opacity=1)
            )
        )
    
    def _get_yaxis_opts(self, style_config: Dict[str, Any]) -> opts.AxisOpts:
        """获取Y轴配置
        
        Args:
            style_config: 样式配置
            
        Returns:
            opts.AxisOpts: Y轴配置
        """
        yaxis_config = style_config.get("yAxis", {})
        
        return opts.AxisOpts(
            type_="category",
            splitarea_opts=opts.SplitAreaOpts(
                is_show=yaxis_config.get("splitArea", {}).get("show", True),
                areastyle_opts=opts.AreaStyleOpts(opacity=1)
            )
        )
    
    def _get_datazoom_opts(self, interaction_config: Dict[str, Any]) -> List[opts.DataZoomOpts]:
        """获取数据缩放配置
        
        Args:
            interaction_config: 交互配置
            
        Returns:
            List[opts.DataZoomOpts]: 数据缩放配置列表
        """
        datazoom_config = interaction_config.get("dataZoom", {})
        
        if not datazoom_config:
            return []
        
        return [
            opts.DataZoomOpts(
                type_="slider",
                xaxis_index=datazoom_config.get("xAxisIndex", 0),
                range_start=datazoom_config.get("start", 0),
                range_end=datazoom_config.get("end", 100),
                pos_bottom=datazoom_config.get("bottom", "20%")
            ),
            opts.DataZoomOpts(
                type_="slider",
                orient="vertical",
                yaxis_index=datazoom_config.get("yAxisIndex", 0),
                range_start=datazoom_config.get("start", 0),
                range_end=datazoom_config.get("end", 100)
            )
        ]
    
    def _generate_html(self, heatmap: HeatMap, config: Dict[str, Any]) -> str:
        """生成HTML内容
        
        Args:
            heatmap: 热力图对象
            config: 配置信息
            
        Returns:
            str: HTML内容
        """
        try:
            # 获取图表HTML
            chart_html = heatmap.render_embed()
            
            # 生成完整的HTML文档
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>矩阵热力图</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Microsoft YaHei', sans-serif;
            background-color: #f5f5f5;
        }}
        .chart-container {{
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .chart-wrapper {{
            width: 95%;
            height: 90%;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            box-sizing: border-box;
        }}
        .chart-title {{
            text-align: center;
            margin-bottom: 20px;
            color: #333;
            font-size: 18px;
            font-weight: bold;
        }}
        .chart-content {{
            width: 100%;
            height: calc(100% - 60px);
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="chart-wrapper">
            <div class="chart-content">
                {chart_html}
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            return html_template.format(chart_html=chart_html)
            
        except Exception as e:
            self.chart_error.emit(f"生成HTML失败: {str(e)}")
            return ""
    
    def _save_to_temp_file(self, html_content: str) -> Optional[str]:
        """保存HTML到临时文件
        
        Args:
            html_content: HTML内容
            
        Returns:
            Optional[str]: 临时文件路径
        """
        try:
            # 清理之前的临时文件
            if self._temp_file_path and os.path.exists(self._temp_file_path):
                os.remove(self._temp_file_path)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                           delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file_path = f.name
            
            return temp_file_path
            
        except Exception as e:
            self.chart_error.emit(f"保存临时文件失败: {str(e)}")
            return None
    
    def set_theme(self, theme: str) -> None:
        """设置图表主题
        
        Args:
            theme: 主题名称 ("white", "dark", "chalk", "vintage", etc.)
        """
        theme_mapping = {
            "white": ThemeType.WHITE,
            "dark": ThemeType.DARK,
            "chalk": ThemeType.CHALK,
            "vintage": ThemeType.VINTAGE,
            "roma": ThemeType.ROMA,
            "macarons": ThemeType.MACARONS,
            "infographic": ThemeType.INFOGRAPHIC,
            "shine": ThemeType.SHINE,
            "purple_passion": ThemeType.PURPLE_PASSION
        }
        
        self._chart_theme = theme_mapping.get(theme, ThemeType.WHITE)
    
    def get_current_chart(self) -> Optional[HeatMap]:
        """获取当前图表对象
        
        Returns:
            Optional[HeatMap]: 当前图表对象
        """
        return self._current_chart
    
    def export_chart_html(self, file_path: str) -> bool:
        """导出图表HTML
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        if not self._current_chart:
            self.chart_error.emit("没有可导出的图表")
            return False
        
        try:
            self._current_chart.render(file_path)
            return True
            
        except Exception as e:
            self.chart_error.emit(f"导出HTML失败: {str(e)}")
            return False
    
    def export_chart_image(self, file_path: str, width: int = 1200, height: int = 800) -> bool:
        """导出图表图片
        
        Args:
            file_path: 导出文件路径
            width: 图片宽度
            height: 图片高度
            
        Returns:
            bool: 是否导出成功
        """
        if not self._current_chart:
            self.chart_error.emit("没有可导出的图表")
            return False
        
        try:
            # 使用snapshot_selenium导出图片
            from pyecharts.render import make_snapshot
            from snapshot_selenium import snapshot
            
            make_snapshot(snapshot, self._current_chart.render(), file_path, 
                        pixel_ratio=1, width=width, height=height)
            return True
            
        except ImportError:
            self.chart_error.emit("导出图片需要安装snapshot-selenium包")
            return False
        except Exception as e:
            self.chart_error.emit(f"导出图片失败: {str(e)}")
            return False
    
    def clear_chart(self) -> None:
        """清除图表"""
        self._current_chart = None
        
        # 清理临时文件
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                os.remove(self._temp_file_path)
            except:
                pass
            self._temp_file_path = None
        
        # 清空WebEngine
        if self._web_view:
            self._web_view.setHtml("")
    
    def reload_chart(self) -> bool:
        """重新加载图表
        
        Returns:
            bool: 是否重新加载成功
        """
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            if self._web_view:
                self._web_view.reload()
                return True
        return False
    
    def get_chart_javascript(self) -> str:
        """获取图表JavaScript代码
        
        Returns:
            str: JavaScript代码
        """
        if not self._current_chart:
            return ""
        
        try:
            # 获取图表配置
            option = self._current_chart.options
            
            # 生成JavaScript代码
            js_code = f"""
// ECharts 矩阵热力图配置
var option = {json.dumps(option, ensure_ascii=False, indent=2)};

// 初始化图表
var chart = echarts.init(document.getElementById('chart-container'));

// 设置配置并渲染
chart.setOption(option);

// 响应式调整
window.addEventListener('resize', function() {{
    chart.resize();
}});
            """
            
            return js_code
            
        except Exception as e:
            self.chart_error.emit(f"生成JavaScript失败: {str(e)}")
            return ""
    
    def _render_fallback_heatmap(self, data_info: Dict[str, Any], chart_config: Dict[str, Any]) -> bool:
        """渲染备用热力图（不依赖PyEcharts）
        
        Args:
            data_info: 数据信息
            chart_config: 图表配置
            
        Returns:
            bool: 是否渲染成功
        """
        try:
            # 提取数据
            matrix_data = data_info.get("matrix_data", [])
            row_labels = data_info.get("row_labels", [])
            col_labels = data_info.get("col_labels", [])
            value_range = data_info.get("value_range", [0, 1])
            
            if not matrix_data or not row_labels or not col_labels:
                self.chart_error.emit("数据不完整，无法渲染图表")
                return False
            
            # 生成直接的ECharts HTML
            html_content = self._generate_fallback_html(
                matrix_data, row_labels, col_labels, value_range, chart_config
            )
            
            # 保存到临时文件
            temp_file = self._save_to_temp_file(html_content)
            
            if temp_file:
                # 加载到WebEngine
                if self._web_view:
                    self._web_view.load(QUrl.fromLocalFile(temp_file))
                
                self._temp_file_path = temp_file
                self.chart_rendered.emit(html_content)
                return True
            else:
                # 如果无法保存临时文件，直接设置HTML
                if self._web_view:
                    self._web_view.setHtml(html_content)
                self.chart_rendered.emit(html_content)
                return True
                
        except Exception as e:
            error_msg = f"渲染备用图表失败: {str(e)}"
            self.chart_error.emit(error_msg)
            return False
    
    def _generate_fallback_html(self, matrix_data: List, row_labels: List[str], 
                                col_labels: List[str], value_range: List[float], 
                                chart_config: Dict[str, Any]) -> str:
        """生成备用HTML内容（不依赖PyEcharts）
        
        Args:
            matrix_data: 矩阵数据
            row_labels: 行标签
            col_labels: 列标签
            value_range: 数值范围
            chart_config: 图表配置
            
        Returns:
            str: HTML内容
        """
        # 准备热力图数据 (转换为ECharts需要的格式)
        echarts_data = []
        if isinstance(matrix_data[0], list):
            # 如果是二维数组格式
            for i, row in enumerate(matrix_data):
                for j, value in enumerate(row):
                    echarts_data.append([j, i, float(value)])
        else:
            # 如果已经是ECharts格式的数据
            echarts_data = matrix_data
        
        # 获取样式配置
        style_config = chart_config.get("style", {})
        title_config = style_config.get("title", {"text": "矩阵热力图"})
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>矩阵热力图</title>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.0/dist/echarts.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: 'Microsoft YaHei', sans-serif;
                    background-color: #f5f5f5;
                }}
                .chart-container {{
                    width: 100%;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }}
                .chart-wrapper {{
                    width: 95%;
                    height: 90%;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    padding: 20px;
                    box-sizing: border-box;
                }}
                .chart-content {{
                    width: 100%;
                    height: calc(100% - 60px);
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <div class="chart-wrapper">
                    <div id="chart" class="chart-content"></div>
                </div>
            </div>
            
            <script>
                var chartDom = document.getElementById('chart');
                var myChart = echarts.init(chartDom);
                
                var option = {{
                    title: {{
                        text: '{title_config.get("text", "矩阵热力图")}',
                        left: 'center',
                        textStyle: {{
                            fontSize: {title_config.get("textStyle", {}).get("fontSize", 18)},
                            fontWeight: 'bold'
                        }}
                    }},
                    tooltip: {{
                        position: 'top',
                        formatter: function (params) {{
                            return '{col_labels}[' + params.data[0] + ']<br/>{row_labels}[' + params.data[1] + ']<br/>值: ' + params.data[2];
                        }}
                    }},
                    grid: {{
                        height: '50%',
                        top: '15%'
                    }},
                    xAxis: {{
                        type: 'category',
                        data: {json.dumps(col_labels, ensure_ascii=False)},
                        splitArea: {{
                            show: true
                        }}
                    }},
                    yAxis: {{
                        type: 'category',
                        data: {json.dumps(row_labels, ensure_ascii=False)},
                        splitArea: {{
                            show: true
                        }}
                    }},
                    visualMap: {{
                        min: {value_range[0]},
                        max: {value_range[1]},
                        calculable: true,
                        orient: 'horizontal',
                        left: 'center',
                        bottom: '15%',
                        inRange: {{
                            color: ['#313695', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027']
                        }}
                    }},
                    series: [{{
                        name: '热力图',
                        type: 'heatmap',
                        data: {json.dumps(echarts_data, ensure_ascii=False)},
                        label: {{
                            show: true,
                            fontSize: 10
                        }},
                        emphasis: {{
                            itemStyle: {{
                                shadowBlur: 10,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }}
                        }}
                    }}]
                }};
                
                myChart.setOption(option);
                
                window.addEventListener('resize', function() {{
                    myChart.resize();
                }});
            </script>
        </body>
        </html>
        """
        
        return html_template
    
    def __del__(self):
        """析构函数，清理临时文件"""
        if hasattr(self, '_temp_file_path') and self._temp_file_path:
            try:
                if os.path.exists(self._temp_file_path):
                    os.remove(self._temp_file_path)
            except:
                pass 