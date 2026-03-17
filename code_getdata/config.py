import os

# --- 关键词配置 ---
SEARCH_KEYWORD = "AIagent"  # 搜索关键词

# --- 路径配置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')  # 指向 xhs-data-collector/data
COOKIE_FILE = os.path.join(BASE_DIR, 'state.json')          # 登录状态文件 (旧版兼容，新版主要用 User Data)
USER_DATA_DIR = os.path.join(BASE_DIR, 'xhs_browser_data')  # 浏览器用户数据目录 (持久化存储)
OUTPUT_FILE = os.path.join(DATA_DIR, f'xhs_{SEARCH_KEYWORD}_data.csv')
OUTPUT_CSV_PATH = os.path.join(DATA_DIR, 'xhs_search_result_accumulated.csv') # 固定文件名用于增量存储

# --- 爬虫行为配置 ---
HEADLESS = False  # 必须为 False！小红书反爬极强，必须有头模式才能绕过大部分检测

MAX_POSTS_TO_SCRAPE = 1200   # 总爬取目标数量
POSTS_PER_BATCH_MIN = 30     # 每批次最少爬取多少条
POSTS_PER_BATCH_MAX = 50     # 每批次最多爬取多少条
BATCH_REST_TIME_MIN = 60     # 批次间休息最短时间 (秒)
BATCH_REST_TIME_MAX = 180    # 批次间休息最长时间 (秒)

SCROLL_COUNT = 5           # 在搜索结果页向下滚动的次数（每次加载更多帖子）
MAX_SCROLL_ATTEMPTS = 50   # 评论区最大向下滚动次数 (用于加载更多评论)
MAX_COMMENTS = 50        # 每个帖子最大评论抓取数 (设大一点以满足“所有”)

# --- 延时配置 (秒) ---
# 为了模拟真人操作，所有延时都会在基准值上增加随机波动
LOGIN_WAIT_TIME = 60       # 给用户手动登录的时间
PAGE_LOAD_TIMEOUT = 30000  # 页面加载超时 (毫秒)
MIN_SLEEP = 2              # 最小操作间隔
MAX_SLEEP = 5              # 最大操作间隔
