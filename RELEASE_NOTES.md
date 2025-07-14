# ChartsTools v1.1.0 发布说明

## 🎉 重要更新

### 📅 发布日期
2024-12-19

### 🔧 主要修复
- **配置面板联动功能**: 修复了配置面板修改参数后图表不更新的问题
- **实时参数调整**: 实现了60+配置项的实时调整和图表更新
- **配置状态管理**: 添加了配置状态保存和恢复机制

## 🆕 新增功能

### 🎛️ 配置面板系统
- **基础配置**: 图表标题、网格布局、坐标轴样式
- **样式配置**: 颜色方案、视觉映射、数据标签、单元格样式
- **交互配置**: 提示框、缩放功能
- **动画配置**: 动画开关、持续时间、缓动效果
- **高级配置**: 渲染模式、工具箱、性能优化、无障碍支持

### 📊 实时更新机制
- 配置面板参数修改后图表立即更新
- 配置参数变化实时反映到代码预览
- 优化的重绘机制，避免不必要的性能损耗

## 🔨 技术改进

### 核心方法新增
- `_get_current_config()`: 获取当前配置面板的所有参数
- `_build_echarts_config_from_ui()`: 根据UI配置构建ECharts配置对象
- `_create_local_heatmap_html_with_config()`: 创建使用配置参数的HTML内容
- `refresh_current_chart()`: 实时刷新当前图表

### 状态管理优化
- 添加图表状态属性 (`current_chart_data`, `current_chart_type`, `current_chart_name`)
- 优化配置面板控件信号连接
- 实现配置变化后的自动图表更新

## 🗂️ 项目整理

### 文件清理
- 删除 `test_config_fix.py` 测试文件
- 删除 `PROJECT_CLEANUP_SUMMARY.md` 临时文档
- 删除 `init_git.bat` 初始化脚本

### 文档更新
- 更新 `CHANGELOG.md` 添加v1.1.0版本记录
- 更新 `README.md` 添加配置面板使用说明
- 完善项目结构文档

## 📈 性能提升

- 优化配置更新频率，减少不必要的重绘
- 改进ECharts配置构建逻辑
- 提升配置面板响应速度

## 🎯 用户体验改进

- 配置面板参数实时生效，无需手动刷新
- 更直观的配置选项分类和组织
- 完善的配置项说明和提示

## 🔗 GitHub 仓库

项目地址: https://github.com/TDCreator-Y/ChartsTools

## 📋 升级指南

### 对于新用户
直接克隆最新版本即可：
```bash
git clone https://github.com/TDCreator-Y/ChartsTools.git
cd ChartsTools
pip install -r requirements.txt
python main.py
```

### 对于现有用户
更新到最新版本：
```bash
git pull origin main
python main.py
```

## 🔮 下一步计划

- [ ] 添加更多图表类型支持
- [ ] 实现配置导出/导入功能
- [ ] 添加图表导出功能（PNG、SVG、PDF）
- [ ] 扩展颜色方案和主题选项
- [ ] 添加数据统计分析功能

## 💝 致谢

感谢所有用户的反馈和建议，特别是配置面板联动功能的需求反馈。

---

**开发团队**: AI Assistant  
**版本**: v1.1.0  
**发布日期**: 2024-12-19 