# ChartsTools - 矩阵热力图可视化工具

一个基于 PyQt6 和 ECharts 的专业矩阵热力图可视化工具，专为教学和数据分析设计。

## 功能特点

🔥 **矩阵热力图可视化** - 支持多种数据类型的热力图生成  
📊 **多种数据格式** - 支持 CSV、Excel 文件导入  
🎨 **多种颜色方案** - 内置多种专业配色方案  
💻 **完整代码预览** - 显示完整的 HTML/CSS/JavaScript 代码  
🖥️ **现代化界面** - 采用现代卡片式设计，支持主题切换  
📱 **响应式布局** - 适配不同屏幕尺寸  
🔧 **完全离线** - 无需网络连接，本地化运行  

## 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11 (主要测试平台)
- 2GB+ 内存
- 50MB+ 磁盘空间

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/ChartsTools.git
   cd ChartsTools
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   python main.py
   ```
   
   或者使用快速启动脚本：
   ```bash
   start_dev.bat
   ```

### 依赖包说明

- **PyQt6**: 现代化 GUI 框架
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **openpyxl**: Excel 文件支持

## 使用指南

### 基本操作

1. **选择数据类型**
   - 相关性矩阵 (5×5)
   - 随机数据 (6×6)
   - 模式数据 (7×7)

2. **导入自定义数据**
   - 点击"导入CSV"或"导入Excel"按钮
   - 选择数据文件
   - 自动生成热力图

3. **查看代码**
   - 在"HTML代码预览"面板中查看完整代码
   - 包含完整的 HTML、CSS 和 JavaScript

4. **主题切换**
   - 使用主题切换按钮在浅色和深色主题间切换

### 支持的数据格式

#### CSV 文件格式
```csv
,A,B,C,D
A,1.0,0.5,0.3,0.1
B,0.5,1.0,0.7,0.2
C,0.3,0.7,1.0,0.8
D,0.1,0.2,0.8,1.0
```

#### Excel 文件格式
- 支持 .xlsx 和 .xls 格式
- 读取第一个工作表
- 第一行作为列标题，第一列作为行标题

### 示例数据

项目包含多个示例数据文件，位于 `examples/` 目录：

- `机房温度分布数据.csv` - 8×8 温度矩阵
- `网络延迟矩阵.csv` - 6×6 对称矩阵
- `服务器负载数据.csv` - 5×6 负载矩阵
- `学科成绩相关性.csv` - 6×6 相关性矩阵
- `销售数据热力图.csv` - 12×5 销售数据
- `test_data.csv` - 4×4 测试数据

## 项目结构

```
ChartsTools/
├── main.py                    # 程序入口
├── requirements.txt           # 依赖包列表
├── start_dev.bat             # 快速启动脚本
├── README.md                 # 项目说明（本文件）
├── CHANGELOG.md              # 开发日志
├── src/                      # 源代码
│   ├── ui/main_window.py     # 主窗口实现
│   ├── core/                 # 核心功能模块
│   └── utils/                # 工具模块
├── config/                   # 配置文件
├── resources/                # 资源文件
│   ├── js/echarts.min.js     # ECharts 库
│   ├── styles/               # 样式文件
│   └── templates/            # HTML 模板
├── examples/                 # 示例数据
└── tests/                    # 测试文件
```

## 技术架构

### 核心技术栈

- **前端**: PyQt6 WebEngineView
- **图表引擎**: ECharts 5.4.0
- **数据处理**: Pandas + NumPy
- **界面设计**: 现代卡片式布局

### 关键特性

1. **本地 ECharts 集成**
   - 解决了 WebEngine 本地文件加载问题
   - 嵌入式脚本加载，完全离线运行

2. **文件导入系统**
   - 统一的文件处理流程
   - 支持多种数据格式
   - 自动数据类型检测

3. **代码预览功能**
   - 完整的 HTML 代码显示
   - 包含所有 CSS 和 JavaScript
   - 便于学习和调试

## 常见问题

### Q: 程序无法启动？
A: 请检查 Python 版本(3.8+)和依赖包是否正确安装。

### Q: 热力图不显示？
A: 确保 ECharts 文件存在于 `resources/js/echarts.min.js`。

### Q: 导入文件后没有变化？
A: 检查文件格式是否正确，确保数据为数值型。

### Q: 如何自定义颜色方案？
A: 修改 `src/ui/main_window.py` 中的颜色配置。

## 开发说明

### 开发环境设置

1. 克隆项目到本地
2. 创建虚拟环境（推荐）
3. 安装开发依赖
4. 使用 IDE 打开项目

### 代码规范

- 使用 Python 3.8+ 语法
- 遵循 PEP 8 编码规范
- 函数和类添加详细注释
- 模块化设计，保持代码清晰

## 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 发起 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 GitHub Issue
- 发送邮件至项目维护者

## 致谢

感谢以下开源项目：
- [ECharts](https://echarts.apache.org/) - 优秀的图表库
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 强大的 GUI 框架
- [Pandas](https://pandas.pydata.org/) - 数据分析利器

---

**项目状态**: 生产就绪  
**最后更新**: 2024-12-19  
**版本**: v1.0.0 