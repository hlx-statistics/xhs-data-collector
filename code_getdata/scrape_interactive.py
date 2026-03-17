import os
import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright
import config
import utils

def scrape_xhs_interactive():
    # 确保存储目录存在
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)

    data_list = []
    
    with sync_playwright() as p:
        try:
            print("正在连接到本地 Chrome 浏览器 (端口 9222)...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            if len(context.pages) > 0:
                page = context.pages[0]
                print("接管当前活跃页面...")
            else:
                page = context.new_page()
                print("新建页面...")

            # 注入防检测
            utils.inject_stealth(page)

            # 1. 确保在搜索结果页
            # 如果当前不在搜索页，且没有搜索结果，则跳转
            if "search_result" not in page.url:
               print("当前不在搜索结果页，尝试跳转...")
               search_url = f"https://www.xiaohongshu.com/search_result?keyword={config.SEARCH_KEYWORD}&source=web_search_result_notes"
               page.goto(search_url)
               time.sleep(5)
            else:
               print("当前已在搜索结果页，继续操作...")

            # 等待内容加载
            page.wait_for_selector("section.note-item", timeout=10000)
            
            # 2. 交互式爬取循环
            # 不再收集所有链接后跳转，而是模拟用户点击->查看->关闭
            # 这样最自然，不容易被封
            
            target_count = config.MAX_POSTS_TO_SCRAPE
            scraped_count = 0
            
            # 用于记录已爬取的ID，防止重复
            scraped_ids = set()

            print(f"目标爬取数量: {target_count}")

            # --- 增量爬取初始化 ---
            # 尝试读取已有的 CSV 文件，加载已爬取的 ID
            if os.path.exists(config.OUTPUT_CSV_PATH):
                try:
                    existing_df = pd.read_csv(config.OUTPUT_CSV_PATH)
                    if 'id' in existing_df.columns:
                        scraped_ids = set(existing_df['id'].astype(str).tolist())
                        print(f"已加载 {len(scraped_ids)} 条历史数据，将跳过重复爬取。")
                except Exception as e:
                    print(f"加载历史数据失败(将被忽略): {e}")
            
            # 批次控制
            posts_in_current_batch = 0
            current_batch_limit = random.randint(config.POSTS_PER_BATCH_MIN, config.POSTS_PER_BATCH_MAX)

            while scraped_count < target_count:
                
                # --- 批次休息检查 ---
                if posts_in_current_batch >= current_batch_limit:
                    rest_time = random.randint(config.BATCH_REST_TIME_MIN, config.BATCH_REST_TIME_MAX)
                    print(f"\n[休息模式] 已连续爬取 {posts_in_current_batch} 条，正在休息 {rest_time} 秒...")
                    print("您可以去喝杯水，或者手动浏览一下其他内容以增加真实性...")
                    
                    # 使用循环倒计时，避免假死
                    for i in range(rest_time, 0, -1):
                        if i % 10 == 0: print(f"  还剩 {i} 秒...")
                        time.sleep(1)
                    
                    # 重置批次计数
                    posts_in_current_batch = 0
                    current_batch_limit = random.randint(config.POSTS_PER_BATCH_MIN, config.POSTS_PER_BATCH_MAX)
                    print("休息结束，继续工作！\n")
                    
                    # 可以在这里做个小动作，比如随机滚动一下
                    utils.safe_scroll(page, 1)

                # 获取当前视图中的所有帖子卡片
                cards = page.query_selector_all("section.note-item")
                
                # 找到第一个未爬取的卡片
                target_card = None
                
                # 重新查询当前 DOM 中的卡片列表
                cards = page.query_selector_all("section.note-item")
                
                for card in cards:
                    try:
                        # 获取唯一标识
                        # 优先尝试 data-id 属性，或者 href
                        link_el = card.query_selector("a.cover") or card.query_selector("a")
                        if not link_el: continue
                        
                        href = link_el.get_attribute("href")
                        if not href: continue
                        
                        # 简单的 ID 提取逻辑
                        # href 通常是 /explore/65abc...
                        card_id = href.split("/")[-1].split("?")[0]
                        
                        if card_id and card_id not in scraped_ids:
                            target_card = card
                            scraped_ids.add(card_id)
                            break
                    except: continue

                if target_card:
                    print(f"\n[{scraped_count+1}/{target_count}] 正在查看帖子ID: {card_id}")
                    
                    try:
                        # 滚动到该卡片位置
                        target_card.scroll_into_view_if_needed()
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        # 点击卡片 (模拟进入详情)
                        # 注意：如果点击的是作者头像可能会跳转主页，所以尽量点击封面图
                        cover_el = target_card.query_selector(".cover") or target_card
                        cover_el.click()
                        
                        # 等待详情弹窗加载
                        # 关键：等待详情容器出现
                        # 常见的弹窗容器: #noteContainer, .note-detail-mask, .note-container
                        try:
                            page.wait_for_selector("#noteContainer, .note-detail-mask, .note-container", timeout=8000)
                            time.sleep(random.uniform(1.5, 3.0)) # 停留阅读
                            
                            # === 爬取数据 ===
                            post_data = {
                                "id": card_id,
                                "title": "N/A",
                                "content": "N/A",
                                "likes_count": "0",  # 点赞数
                                "collects_count": "0", # 收藏数
                                "comments_count": "0", # 评论数（显示值）
                                "comments": []
                            }
                            
                            # 提取标题
                            title_el = page.query_selector("#detail-title")
                            if title_el: post_data["title"] = title_el.inner_text()
                            
                            # 提取正文
                            desc_el = page.query_selector("div#detail-desc") or page.query_selector(".desc")
                            if desc_el: post_data["content"] = desc_el.inner_text()
                            
                            # --- 提取互动数据 (热度指标) ---
                            # 通常在右侧侧边栏或下方工具栏
                            # 点赞
                            try:
                                like_el = page.query_selector(".interact-container .like-wrapper .count")
                                if like_el: post_data["likes_count"] = like_el.inner_text()
                            except: pass

                            # 收藏
                            try:
                                collect_el = page.query_selector(".interact-container .collect-wrapper .count")
                                if collect_el: post_data["collects_count"] = collect_el.inner_text()
                            except: pass

                            # 评论数 (显示的数字)
                            try:
                                chat_el = page.query_selector(".interact-container .chat-wrapper .count")
                                if chat_el: post_data["comments_count"] = chat_el.inner_text()
                            except: pass
                            
                            # --- 提取评论 (全面深度爬取) ---
                            print("  -> 正在加载全部评论（可能会花费一点时间）...")
                            
                            # 找到可滚动的元素，通常是 .note-scroller
                            scroller = page.query_selector(".note-scroller")
                            if not scroller:
                                # 有时候是整个 note-container
                                scroller = page.query_selector(".note-content")

                            # 循环滚动加载更多评论
                            prev_comment_count = 0
                            no_change_count = 0
                            
                            for _ in range(config.MAX_SCROLL_ATTEMPTS): # 最大尝试次数，防止死循环
                                # 检查是否有“查看更多评论”按钮并点击 (有时需要点一下)
                                # load_more_btn = page.query_selector("div.show-more")
                                # if load_more_btn: load_more_btn.click()
                                
                                # 将滚动到底部
                                if scroller:
                                    scroller.evaluate("el => el.scrollBy(0, 1000)")
                                else:
                                    page.mouse.wheel(0, 1000)
                                
                                time.sleep(random.uniform(1.0, 1.5))
                                
                                # 检查当前加载的评论数
                                current_comments = page.query_selector_all(".comment-item")
                                current_count = len(current_comments)
                                
                                if current_count == prev_comment_count:
                                    no_change_count += 1
                                else:
                                    no_change_count = 0 # 重置计数器
                                    prev_comment_count = current_count
                                
                                # 如果连续几次滚动都没有新评论，认为到底了
                                if no_change_count >= 3:
                                    break
                                    
                                # 如果已经达到上限，停止
                                if current_count >= config.MAX_COMMENTS:
                                    break

                            # 提取所有可见评论及其回复
                            final_comments = []
                            low_quality_count = 0
                            
                            comment_items = page.query_selector_all(".comment-item")
                            
                            # 低质量关键词库
                            low_quality_keywords = ["已关", "互关", "dd", "求", "蹲", "怎么学", "资料", "三连", "好", "棒", "mark", "插眼", "分享", "私"]
                            
                            for item in comment_items:
                                try:
                                    # 主评论内容
                                    content_el = item.query_selector(".content")
                                    if content_el:
                                        raw_text = content_el.inner_text().replace('\n', ' ').strip()
                                        if not raw_text: continue
                                        
                                        # --- 评论质量判断逻辑 ---
                                        is_low_quality = False
                                        
                                        # 1. 长度判断 (过短通常无意义)
                                        if len(raw_text) < 5:
                                            is_low_quality = True
                                        
                                        # 2. 关键词判断
                                        if any(k in raw_text for k in low_quality_keywords):
                                            is_low_quality = True
                                        
                                        # --- 筛选逻辑 ---
                                        if is_low_quality:
                                            # 如果是低质量评论，且已收集超过10条，则跳过
                                            if low_quality_count >= 10:
                                                continue
                                            low_quality_count += 1
                                        
                                        # 查找回复列表 (如果有)
                                        replies_text = []
                                        reply_els = item.query_selector_all(".reply-list .content")
                                        for r in reply_els:
                                            r_text = r.inner_text().replace('\n', ' ').strip()
                                            if r_text:
                                                replies_text.append(f"[回复]{r_text}")
                                            
                                        # 组合该条评论及其回复
                                        full_text = raw_text
                                        if replies_text:
                                            full_text += " " + " ".join(replies_text)
                                            
                                        final_comments.append(full_text)
                                        
                                except: continue
                            
                            # 保存筛选后的评论
                            post_data["comments"] = " || ".join(final_comments[:config.MAX_COMMENTS]) # 双重保险截断
                            
                            print(f"  -> 标题: {post_data['title'][:15]}...")
                            print(f"  -> 热度: 点赞{post_data['likes_count']} 收藏{post_data['collects_count']} 评论{post_data['comments_count']}")
                            print(f"  -> 抓取评论: {len(final_comments)} (低质量已限制为{low_quality_count})")
                            
                            # === 实时增量保存 ===
                            try:
                                df_new = pd.DataFrame([post_data])
                                # 如果文件不存在，写入表头；否则追加且不写表头
                                if not os.path.exists(config.OUTPUT_CSV_PATH):
                                    df_new.to_csv(config.OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
                                else:
                                    df_new.to_csv(config.OUTPUT_CSV_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
                                print(f"  -> 数据已追加至 {config.OUTPUT_CSV_PATH}")
                            except Exception as save_err:
                                print(f"  ->保存失败: {save_err}")

                            scraped_count += 1
                            posts_in_current_batch += 1 # 更新批次计数
                            
                            # === 关闭弹窗 ===
                            # 尝试按 ESC 键关闭是最通用的
                            page.keyboard.press("Escape")
                            
                            # 检查是否关闭成功
                            time.sleep(1.5)
                            # 如果详情页还在，再试一次或者找关闭按钮
                            if page.query_selector("#detail-title"):
                                close_btn = page.query_selector(".close-mask-btn, .close-icon, [aria-label='Close'], .close-circle")
                                if close_btn:
                                    close_btn.click()
                                else:
                                    # 强制后退 (如果是页面跳转模式)
                                    if "explore" in page.url or "discovery" in page.url:
                                         page.go_back()
                            
                            time.sleep(random.uniform(1, 2))
                            
                        except Exception as e:
                            print(f"  -> 详情页加载超时(可能没点开或被拦截): {e}")
                            # 尝试恢复
                            page.keyboard.press("Escape")
                            time.sleep(1)

                    except Exception as e:
                        print(f"  -> 交互出错: {e}")
                
                else: 
                     # 没有新卡片，滚动加载更多
                    print("当前视图无新帖子，向下滚动...")
                    utils.safe_scroll(page, 1) # 滚一小段
                    
        except Exception as e:
            print(f"发生错误: {e}")
            print("请确认 Chrome 调试模式已启动 (运行 start_chrome_debug.bat)")

    print(f"数据处理完毕。请查看 {config.OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    scrape_xhs_interactive()
