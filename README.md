# xhs-data-collector

> [!CAUTION]
> 本项目仅供学习和研究使用，请勿用于非法用途。使用本工具产生的任何后果由使用者自行承担。

基于 Playwright + Chrome Remote Debugging 的小红书数据采集工具。通过接管本地浏览器模拟真人操作，有效规避反爬虫检测，支持增量爬取与断点续传。

## ✨ 特性

- **抗反爬**: 采用本地浏览器接管技术，完全模拟真人浏览行为（点击、滚动、查看）。
- **增量抓取**: 自动记录已爬取的笔记 ID，重启程序不重复抓取，支持断点续传。
- **拟人化**: 内置随机等待、批次休息机制（每抓取 30-50 条自动休息 1-3 分钟），降低封号风险。
- **数据完整**: 采集笔记标题、正文、点赞/收藏/评论数、发布时间及前 50 条热门评论。

## 🛠️ 环境准备

1. **Google Chrome 浏览器**: 必须安装。
2. **Python 3.8+**: 建议使用 Anaconda 或虚拟环境。
3. **依赖库**:
   ```bash
   pip install playwright pandas openpyxl
   ```

## 🚀 快速开始

### 1. 启动调试浏览器
双击运行 `code_getdata/start_chrome_debug.bat`。
- 将启动一个开启了远程调试端口 (9222) 的 Chrome 窗口。
- **首次运行请在该窗口手动登录小红书账号**。
- **请勿关闭**此 Chrome 窗口和伴随的命令行窗口。

### 2. 运行爬虫
在 VS Code 终端或新的命令行窗口中执行：
```bash
python code_getdata/scrape_interactive.py
```
程序将自动连接已打开的浏览器，进入搜索页开始采集。

## ⚙️ 配置说明

修改 `code_getdata/config.py` 自定义采集行为：

| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `SEARCH_KEYWORD` | `"AIagent"` | 搜索关键词 |
| `MAX_POSTS_TO_SCRAPE` | `1200` | 目标采集数量 |
| `POSTS_PER_BATCH_MIN/MAX` | `30` / `50` | 单次连续采集数量区间 |
| `BATCH_REST_TIME_MIN/MAX` | `60` / `180` | 批次间休息时长（秒） |
| `MAX_COMMENTS` | `50` | 单篇笔记最大采集评论数 |

## 📂 数据输出

采集结果实时保存至 `data/` 目录：
- 文件名: `xhs_search_result_accumulated.csv`
- 包含字段: `id` (笔记ID), `title` (标题), `content` (正文), `likes_count` (点赞数), `collects_count` (收藏数), `comments_count` (评论数), `comments` (评论内容).

## ⚠️ 注意事项

1. **不要关闭浏览器**: 爬虫运行时需保持调试浏览器开启。
2. **人工干预**: 如遇验证码，请直接在浏览器中手动完成验证，程序会自动恢复。
3. **休息机制**: 程序提示"休息中"时，建议不要频繁操作浏览器，可适当手动浏览以增加真实感。
