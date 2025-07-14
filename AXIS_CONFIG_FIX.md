# 坐标轴配置修复说明

## 问题描述

在ChartsTools v1.1.1版本中，用户反馈配置面板中的"显示轴线"和"显示刻度"选项无效，无论如何调整这些设置，热力图中的坐标轴线和刻度都不会发生变化。

## 问题分析

通过代码审查和测试，发现问题出现在配置传递链路中：

### 1. UI控件定义正常
```python
# 在 create_basic_config_tab() 方法中
self.axis_line_show = QCheckBox("显示轴线")
self.axis_tick_show = QCheckBox("显示刻度")
```

### 2. 配置收集存在遗漏
在 `_get_current_config()` 方法中，坐标轴配置缺少了 axisLine 和 axisTick 配置：

**修复前（有问题）**：
```python
config['xAxis'] = {
    'axisLabel': {
        'show': self.x_axis_label_show.isChecked(),
        # ... 其他axisLabel配置
    }
    # ❌ 缺少 axisLine 和 axisTick 配置
}
```

**修复后（正确）**：
```python
config['xAxis'] = {
    'axisLabel': {
        'show': self.x_axis_label_show.isChecked(),
        # ... 其他axisLabel配置
    },
    'axisLine': {
        'show': self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
    },
    'axisTick': {
        'show': self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
    }
}
```

### 3. ECharts配置构建不完整
在 `_build_echarts_config_from_ui()` 方法中，也缺少对 axisLine 和 axisTick 配置的处理：

**修复前（有问题）**：
```python
'xAxis': {
    'type': 'category',
    'data': labels,
    'splitArea': {'show': True},
    'axisLabel': xaxis_config.get('axisLabel', {...})
    # ❌ 缺少 axisLine 和 axisTick
}
```

**修复后（正确）**：
```python
'xAxis': {
    'type': 'category',
    'data': labels,
    'splitArea': {'show': True},
    'axisLabel': xaxis_config.get('axisLabel', {...}),
    'axisLine': xaxis_config.get('axisLine', {'show': False}),
    'axisTick': xaxis_config.get('axisTick', {'show': False})
}
```

## 修复内容

### 文件修改
- **文件**: `src/ui/main_window.py`
- **方法**: `_get_current_config()` 和 `_build_echarts_config_from_ui()`
- **行数**: 约20行代码修改

### 修复点
1. 在 `_get_current_config()` 方法中添加 axisLine 和 axisTick 配置收集
2. 在 `_build_echarts_config_from_ui()` 方法中添加 axisLine 和 axisTick 配置应用
3. 确保X轴和Y轴的配置都完整

## 验证结果

### 测试程序验证
创建了专门的测试程序 `test_axis_config.py` 进行验证：

```
🔄 开始测试坐标轴配置...
✅ 找到轴线和刻度配置控件
🔧 开启轴线和刻度显示...
X轴 - 轴线: True, 刻度: True
Y轴 - 轴线: True, 刻度: True
✅ 轴线和刻度配置正确应用

🔧 关闭轴线和刻度显示...
关闭后 - X轴轴线: False, 刻度: False
关闭后 - Y轴轴线: False, 刻度: False
✅ 轴线和刻度关闭配置正确应用
🎉 坐标轴配置测试完成
```

### 功能验证
- ✅ "显示轴线"复选框现在能正确控制轴线显示
- ✅ "显示刻度"复选框现在能正确控制刻度显示
- ✅ 配置变更立即反映到热力图显示
- ✅ X轴和Y轴都能独立控制（虽然UI是统一控制）

## 配置效果

### 默认状态（轴线和刻度关闭）
```javascript
xAxis: {
    axisLine: { show: false },
    axisTick: { show: false }
}
```

### 开启状态（轴线和刻度显示）
```javascript
xAxis: {
    axisLine: { show: true },
    axisTick: { show: true }
}
```

## 影响范围

- **用户界面**: 配置面板中的"显示轴线"和"显示刻度"选项现在正常工作
- **图表显示**: 热力图的坐标轴可以根据配置显示或隐藏轴线和刻度
- **配置导出**: 导出的HTML代码中包含正确的轴线和刻度配置
- **向后兼容**: 修复不影响现有配置文件的兼容性

## 版本信息

- **修复版本**: v1.1.2
- **发布日期**: 2024-12-19
- **修复类型**: Bug修复
- **优先级**: 中等（影响用户体验但不影响核心功能） 