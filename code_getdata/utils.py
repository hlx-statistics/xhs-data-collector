import time
import random
import config
from playwright.sync_api import Page

def random_sleep(min_seconds=config.MIN_SLEEP, max_seconds=config.MAX_SLEEP):
    """随机等待一段时间，模拟人类操作"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"Waiting for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)

def safe_scroll(page: Page, scroll_times=3):
    """
    模拟更像人类的平滑滚动
    """
    print(f"开始模拟人类浏览滚动...")
    for i in range(scroll_times):
        # 每次滚动的总距离
        total_distance = random.randint(600, 1000)
        
        # 分段滚动，模拟手指滑动或滚轮滚动的惯性
        steps = random.randint(10, 20)
        step_distance = total_distance / steps
        
        for _ in range(steps):
            # 添加一点随机抖动
            delta = step_distance + random.randint(-10, 10)
            page.mouse.wheel(0, delta)
            # 极短的间隔
            time.sleep(random.uniform(0.02, 0.08))
        
        # 滚动一段后，停顿阅读
        random_sleep(1.5, 3.5)
        
        # 偶尔向上回滚一点点，模拟查看上一条
        if random.random() < 0.2:
            page.mouse.wheel(0, -random.randint(100, 200))
            random_sleep(0.5, 1.5)
            
        print(f"已浏览页面进度 {i+1}/{scroll_times}")

def check_login_status(page: Page):
    """简单检查是否登录，这里通过检查是否存在特定元素来判断（需要根据实际页面调整）"""
    # 小红书登录后通常会有头像元素，这里仅作示例，实际可根据 storage_state 是否载入成功判断
    pass

def inject_stealth(page: Page):
    """注入强力反爬虫检测脚本"""
    js = """
    () => {
        // 覆盖 webdriver 属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // 伪造 navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });

        // 伪造 navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // 伪造 chrome 对象
        if (!window.chrome) {
            window.chrome = { runtime: {} };
        }

        // 绕过 permissions 检测
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 伪造 WebGL Vendor
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // 37445: UNMASKED_VENDOR_WEBGL
            // 37446: UNMASKED_RENDERER_WEBGL
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel(R) Iris(R) Xe Graphics';
            }
            return getParameter(parameter);
        };
    }
    """
    page.add_init_script(js)
