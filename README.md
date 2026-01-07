# CET4 真题自动爬取工具

这是一个基于 Python 和 Playwright 的英语四级真题自动爬取脚本，支持自动识别详情页、点击下载按钮并按照规范格式保存 PDF 文件。

## 📁 目录结构

- `src/`: 脚本源代码文件夹
  - `config.py`: 项目配置文件（核心配置都在这里）
  - `main.py`: 爬虫主程序
- `downloads/`: 真题文件存放目录（运行后自动生成）
- `venv/`: Python 虚拟环境目录
- `requirements.txt`: 依赖清单

---

## ⚙️ 如何配置

所有的个性化设置都在 `src/config.py` 文件中。

### 1. 切换四级/六级
如果您想切换爬取目标，请修改：
```python
CET_TYPE = "cet4"  # 下载四级真题
# 或者
CET_TYPE = "cet6"  # 下载六级真题
```

### 2. 修改下载年份范围
如果您只想下载特定年份的真题，请修改：
```python
START_YEAR = 2020  # 起始年份（含）
END_YEAR = 2025    # 结束年份（含）
```

### 2. 浏览器显示模式
默认会打开 Edge 浏览器窗口以便观察进度。如果想在后台静默运行，请修改：
```python
HEADLESS = True  # True 为后台运行，False 为显示窗口
```

### 3. XPath 定位
如果网站结构发生变化导致无法点击下载按钮，请更新：
```python
DOWNLOAD_BUTTON_XPATH = "新的 XPath 路径"
```

---

## 🚀 如何运行

### 第一步：安装环境（仅需执行一次）
如果您是第一次使用，请在终端执行以下命令安装依赖：
```powershell
# 使用阿里源快速安装依赖
.\venv\Scripts\python.exe -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 安装浏览器驱动
.\venv\Scripts\playwright install msedge
```

### 第二步：启动爬虫
在项目根目录下执行：
```powershell
.\venv\Scripts\python.exe src/main.py
```

---

## 📝 注意事项
1. **网络稳定性**：脚本加入了 `networkidle` 等待机制，如果您的网络较慢，请确保不要关闭弹出的浏览器窗口。
2. **文件命名**：下载后的文件将自动命名为 `年份-月份-套数.pdf`（例如 `2024-12-01.pdf`），统一存放在 `downloads` 文件夹中。
3. **反爬虫**：脚本默认在每下载完一套题后会随机延时，请勿频繁、超高速运行以防被网站封禁 IP。
