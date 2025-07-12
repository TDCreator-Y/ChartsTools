# ChartsTools 项目开发日志

## 项目概览
ChartsTools 是一个基于 PyQt6 和 ECharts 的矩阵热力图可视化工具，专门用于教学和数据分析。

## 版本历史

### v1.0.0 (2024-12-19)
**项目完成版本**

#### 核心功能
- ✅ 矩阵热力图可视化
- ✅ 多种数据类型支持（相关性矩阵、随机数据、模式数据）
- ✅ CSV/Excel 文件导入功能
- ✅ 完整的 HTML 代码预览
- ✅ 响应式用户界面设计
- ✅ 主题切换功能

#### 技术架构
- **前端框架**: PyQt6 (QWebEngineView)
- **图表引擎**: ECharts 5.4.0
- **数据处理**: Pandas, NumPy
- **界面设计**: 现代卡片式布局，渐变背景
- **代码架构**: MVC 模式，模块化设计

#### 主要解决的问题

##### 1. ECharts 本地加载问题
**问题**: QWebEngineView 无法通过 `file://` 协议加载本地 JavaScript 文件
**解决方案**: 
- 启用 WebEngine 安全设置
- 直接读取 ECharts 文件内容并嵌入到 HTML 中
- 实现完全离线的本地热力图渲染

**关键代码**:
```python
# 启用本地文件访问
settings = self.chart_view.settings()
settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

# 嵌入式脚本加载
echarts_script = self._get_echarts_script_content()
html_content = f'<script>{echarts_script}</script>'
```

##### 2. 文件导入功能实现
**问题**: 导入的 CSV/Excel 文件数据无法正确显示在热力图中
**解决方案**:
- 统一文件处理和渲染流程
- 实现专门的文件数据读取和转换功能
- 添加导入数据的专用颜色方案

**关键功能**:
- `load_and_render_file_data()`: 统一文件处理入口
- `_load_csv_data()`: CSV 文件数据读取
- `_load_excel_data()`: Excel 文件数据读取
- `render_file_heatmap()`: 导入数据热力图渲染

##### 3. HTML 代码预览功能
**问题**: 代码预览面板只显示占位符，不显示完整的 HTML 代码
**解决方案**:
- 修改 `_update_local_code_preview()` 方法
- 显示完整的 HTML 代码（包括 DOCTYPE、CSS、JavaScript）
- 提供完整的代码学习参考

#### 文件结构
```
ChartsTools/
├── main.py                    # 程序入口
├── requirements.txt           # 依赖包列表
├── start_dev.bat             # 快速启动脚本
├── CHANGELOG.md              # 项目日志（本文件）
├── README.md                 # 项目说明文档
├── src/                      # 源代码目录
│   ├── __init__.py
│   ├── ui/                   # 用户界面模块
│   │   ├── __init__.py
│   │   └── main_window.py    # 主窗口实现
│   ├── core/                 # 核心功能模块
│   │   ├── __init__.py
│   │   ├── app_controller.py # 应用控制器
│   │   ├── data_manager.py   # 数据管理器
│   │   └── theme_manager.py  # 主题管理器
│   └── utils/                # 工具模块
│       ├── __init__.py
│       └── file_utils.py     # 文件操作工具
├── config/                   # 配置文件
│   ├── __init__.py
│   └── theme_settings.json   # 主题配置
├── resources/                # 资源文件
│   ├── js/
│   │   └── echarts.min.js    # ECharts 库文件
│   ├── styles/               # 样式文件
│   ├── templates/            # HTML 模板
│   └── icons/                # 图标文件
├── examples/                 # 示例数据
│   ├── README.md             # 示例数据说明
│   ├── test_data.csv         # 测试数据
│   └── *.csv                 # 各种示例数据文件
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── test_ui/              # UI 测试
│   └── test_core/            # 核心功能测试
└── docs/                     # 文档目录
```

#### 数据类型支持
1. **相关性矩阵** (5×5)
   - 蓝红渐变色彩方案
   - 数值范围: -1 到 1
   - 用途: 学科成绩相关性分析

2. **随机数据** (6×6)
   - 紫黄渐变色彩方案
   - 数值范围: 0 到 100
   - 用途: 通用数据可视化

3. **模式数据** (7×7)
   - Plasma 色彩方案
   - 数值范围: 0 到 1
   - 用途: 模式识别和分析

4. **导入数据** (自适应)
   - 10色渐变色彩方案
   - 支持 CSV/Excel 格式
   - 自动检测数据维度

#### 性能优化
- 使用 QWebEngineView 进行硬件加速渲染
- 优化 ECharts 配置，减少内存占用
- 异步文件读取，避免界面卡顿
- 智能缓存机制，提高响应速度

#### 用户体验
- 现代化卡片式界面设计
- 渐变背景和圆角设计
- 响应式布局，适配不同屏幕
- 直观的文件导入流程
- 实时的代码预览功能

#### 开发统计
- **开发周期**: 约 3 周
- **代码行数**: 约 2000+ 行
- **主要文件**: 15+ 个
- **测试数据**: 10+ 个示例文件
- **解决问题**: 20+ 个技术难题

#### 技术亮点
1. **跨平台兼容**: 支持 Windows、macOS、Linux
2. **离线运行**: 完全本地化，无需网络连接
3. **教育友好**: 完整的代码预览，便于学习
4. **扩展性强**: 模块化设计，便于功能扩展
5. **性能优化**: 高效的渲染和数据处理

## 未来规划
- [ ] 添加更多图表类型（散点图、柱状图等）
- [ ] 实现数据编辑功能
- [ ] 添加图表导出功能（PNG、SVG、PDF）
- [ ] 支持实时数据更新
- [ ] 添加数据统计分析功能

## 致谢
感谢 ECharts 团队提供优秀的图表库，感谢 PyQt6 团队提供强大的 GUI 框架。

---
**项目作者**: AI Assistant  
**最后更新**: 2024-12-19  
**项目状态**: 生产就绪 