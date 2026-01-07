import os

# ==========================================
# 基础配置信息
# ==========================================

# 考试类型选择："cet4" 代表四级，"cet6" 代表六级
CET_TYPE = "cet4"

# 四/六级真题主页地址 (根据 CET_TYPE 动态生成)
BASE_URL = f"https://zhenti.burningvocabulary.cn/{CET_TYPE}"

# ==========================================
# 筛选配置
# ==========================================

# 想要下载的年份范围
START_YEAR = 2025  # 起始年份（含）
END_YEAR = 2025    # 结束年份（含）

# 真题保存目录
# 使用 os.path.abspath 确保路径是绝对路径
# 逻辑：当前文件所在目录的上一级的 downloads 文件夹
DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "downloads"))

# ==========================================
# 页面元素定位 (XPath)
# ==========================================

# 详情页中“下载按钮”的完整 XPath 路径
DOWNLOAD_BUTTON_XPATH = "/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/div[2]/button[6]"

# ==========================================
# 浏览器运行配置
# ==========================================

# 是否开启无头模式 (Headless Mode)
# False: 会弹出浏览器窗口，可以看到自动操作过程
# True:  在后台运行，不显示界面
HEADLESS = False  

# 浏览器渠道
# "msedge": 优先使用系统安装的 Microsoft Edge 浏览器
BROWSER_CHANNEL = "msedge"

# 默认等待超时时间 (毫秒)
# 30000 毫秒即 30 秒
TIMEOUT = 30000  
