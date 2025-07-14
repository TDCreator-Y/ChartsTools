# 单元格样式和网格线配置修复文档

## 问题描述

用户在使用软件时发现样式配置面板中的以下功能无效：
- 边框宽度设置（1px → 5px）
- 边框颜色设置（#ffffff → #000000）  
- 圆角半径设置（2px → 10px）
- 透明度设置（100% → 80%）
- 显示网格线开关

## 问题分析

### 根本原因
通过代码分析发现问题出现在配置传递链中：

1. **UI控件存在** ✅ - 所有配置控件都正确创建
2. **事件监听正常** ✅ - `on_config_changed`事件正确触发
3. **配置收集缺失** ❌ - `_get_current_config()`方法未收集单元格样式
4. **配置应用缺失** ❌ - `_build_echarts_config_from_ui()`方法未应用配置

### 具体问题点
- `_get_current_config()`方法中缺少`series.itemStyle`配置收集
- `_get_current_config()`方法中缺少`splitArea`配置收集
- `_build_echarts_config_from_ui()`方法中`itemStyle`使用硬编码值
- `_build_echarts_config_from_ui()`方法中`splitArea`使用硬编码值

## 修复方案

### 1. 修复配置收集逻辑

在`_get_current_config()`方法中添加：

```python
# 单元格样式配置
if hasattr(self, 'cell_border_width'):
    if 'series' not in config:
        config['series'] = {}
    config['series']['itemStyle'] = {
        'borderWidth': self.cell_border_width.value(),
        'borderColor': self.cell_border_color.text() if hasattr(self, 'cell_border_color') else "#fff",
        'borderRadius': self.cell_border_radius.value() if hasattr(self, 'cell_border_radius') else 2,
        'opacity': self.cell_opacity.value() / 100.0 if hasattr(self, 'cell_opacity') else 1.0
    }

# 显示网格线配置
if hasattr(self, 'show_grid'):
    config['splitArea'] = {
        'show': self.show_grid.isChecked()
    }
```

### 2. 修复配置应用逻辑

在`_build_echarts_config_from_ui()`方法中：

```python
# 添加split_area_config变量
split_area_config = config.get('splitArea', {})

# 修复xAxis和yAxis的splitArea配置
'xAxis': {
    'type': 'category',
    'data': labels,
    'splitArea': {'show': split_area_config.get('show', True)},
    # ... 其他配置
},
'yAxis': {
    'type': 'category', 
    'data': labels,
    'splitArea': {'show': split_area_config.get('show', True)},
    # ... 其他配置
},

# 修复series的itemStyle配置
'series': [{
    'name': '矩阵热力图',
    'type': 'heatmap',
    'data': data,
    'label': series_config.get('label', {...}),
    'itemStyle': series_config.get('itemStyle', {
        'borderWidth': 1,
        'borderColor': '#fff',
        'borderRadius': 2,
        'opacity': 1.0
    }),
    # ... 其他配置
}]
```

### 3. 同步修复on_config_changed()方法

确保配置变更处理方法也包含相同的逻辑。

## 修复验证

### 测试脚本
创建了专门的测试脚本`test_cell_style_fix.py`，包含：

1. **控件存在性测试** - 验证所有UI控件正确创建
2. **配置收集测试** - 验证配置正确收集到数据结构
3. **配置应用测试** - 验证配置正确应用到ECharts

### 测试结果
```
✅ 所有单元格样式控件都存在
  - 边框宽度: 1px → 5px ✅
  - 边框颜色: #ffffff → #000000 ✅
  - 圆角半径: 2px → 10px ✅
  - 透明度: 100% → 80% ✅
  - 显示网格线: True → False ✅

✅ 配置收集功能正常
✅ 配置应用功能正常
✅ 实时更新功能正常
```

## 效果展示

### 修复前
- 调整边框宽度：无效果
- 调整边框颜色：无效果
- 调整圆角半径：无效果
- 调整透明度：无效果
- 切换网格线显示：无效果

### 修复后
- 调整边框宽度：✅ 立即生效，热力图单元格边框变粗/变细
- 调整边框颜色：✅ 立即生效，热力图单元格边框颜色改变
- 调整圆角半径：✅ 立即生效，热力图单元格变为圆角矩形
- 调整透明度：✅ 立即生效，热力图单元格透明度改变
- 切换网格线显示：✅ 立即生效，坐标轴网格线显示/隐藏

## 相关文件

### 修改的文件
- `src/ui/main_window.py` - 主要修复文件
  - `_get_current_config()` 方法
  - `_build_echarts_config_from_ui()` 方法
  - `on_config_changed()` 方法

### 测试文件
- `test_cell_style_fix.py` - 验证修复效果的测试脚本

### 文档文件
- `CHANGELOG.md` - 版本更新日志
- `CELL_STYLE_FIX.md` - 详细修复文档（本文件）

## 技术细节

### ECharts配置映射
- **边框宽度** → `series[0].itemStyle.borderWidth`
- **边框颜色** → `series[0].itemStyle.borderColor`
- **圆角半径** → `series[0].itemStyle.borderRadius`
- **透明度** → `series[0].itemStyle.opacity`
- **网格线显示** → `xAxis.splitArea.show` & `yAxis.splitArea.show`

### 配置流程
1. 用户在UI中调整配置
2. 触发`on_config_changed()`事件
3. 调用`_get_current_config()`收集配置
4. 调用`refresh_current_chart()`重新渲染
5. 调用`_build_echarts_config_from_ui()`构建ECharts配置
6. 生成HTML并更新WebView显示

## 版本信息
- **修复版本**: v1.1.4
- **修复日期**: 2024-12-19
- **修复状态**: ✅ 完全修复并验证 