import os
import asyncio
import re
from playwright.async_api import async_playwright
import config

async def download_cet4_papers():
    """
    爬虫主函数：
    1. 访问四级真题主页获取所有套装链接
    2. 遍历链接进入详情页
    3. 点击下载按钮并保存文件
    """
    async with async_playwright() as p:
        # ---------------------------------------------------------
        # 1. 初始化浏览器环境
        # ---------------------------------------------------------
        print(f"正在启动浏览器 ({config.BROWSER_CHANNEL})...")
        browser = await p.chromium.launch(
            headless=config.HEADLESS, 
            channel=config.BROWSER_CHANNEL
        )
        # 创建新的上下文，并显式开启允许下载
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        # ---------------------------------------------------------
        # 2. 访问主页并提取所有真题套装链接
        # ---------------------------------------------------------
        print(f"正在访问主页: {config.BASE_URL}")
        await page.goto(config.BASE_URL)

        # 检查并创建本地下载目录
        if not os.path.exists(config.DOWNLOAD_DIR):
            os.makedirs(config.DOWNLOAD_DIR)
            print(f"创建下载目录: {config.DOWNLOAD_DIR}")

        # 获取页面中所有指向真题详情页的 a 标签
        # 规则：href 属性以 /cet4/ 或 /cet6/ 开头
        links = await page.query_selector_all(f"a[href^='/{config.CET_TYPE}/']")
        paper_links = []
        for link in links:
            href = await link.get_attribute("href")
            # 动态匹配特定格式，如 /cet4/2025-06/01 或 /cet6/2025-06/01
            match = re.search(rf'/{config.CET_TYPE}/(\d{{4}})-\d{{2}}/\d+', href)
            if match:
                year = int(match.group(1))
                # 检查年份是否在设定的范围内
                if config.START_YEAR <= year <= config.END_YEAR:
                    full_url = f"https://zhenti.burningvocabulary.cn{href}"
                    if full_url not in paper_links:
                        paper_links.append(full_url)
                        print(f"发现{config.CET_TYPE.upper()}真题: {full_url}")

        print(f"分析完成，在 {config.START_YEAR}-{config.END_YEAR} 范围内共发现 {len(paper_links)} 套{config.CET_TYPE.upper()}真题。")

        # ---------------------------------------------------------
        # 3. 循环进入每个详情页进行下载
        # ---------------------------------------------------------
        for paper_url in paper_links:
            try:
                print(f"\n[任务] 正在处理: {paper_url}")
                await page.goto(paper_url)
                
                # 参考 test.py：等待网络空闲，确保页面加载完整
                await page.wait_for_load_state("networkidle")
                
                # 等待下载按钮出现在 DOM 中并可见
                button_selector = f"xpath={config.DOWNLOAD_BUTTON_XPATH}"
                await page.wait_for_selector(button_selector, state="visible", timeout=10000)
                
                # 确保按钮在视口内并尝试点击
                button_element = page.locator(button_selector)
                await button_element.scroll_into_view_if_needed()
                
                # 监听下载事件，设置 15 秒超时
                async with page.expect_download(timeout=15000) as download_info:
                    # 模拟用户点击下载按钮，使用 force=True 确保触发
                    await button_element.click(force=True)
                
                # 获取下载对象
                download = await download_info.value
                
                # 命名逻辑：CET类型-年份-月份-套数.pdf
                parts = paper_url.split('/')
                date_part = parts[-2]   # 例如: 2025-06
                set_number = parts[-1]  # 例如: 03
                filename = f"{config.CET_TYPE.upper()}_{date_part}_{set_number}.pdf"
                
                # 执行保存操作
                save_path = os.path.join(config.DOWNLOAD_DIR, filename)
                await download.save_as(save_path)
                print(f"成功保存到: {save_path}")

                # 礼貌性延时，防止请求过快
                await asyncio.sleep(2)

            except Exception as e:
                print(f"处理失败 {paper_url}: {e}")
                continue

        # 任务结束，关闭浏览器
        await browser.close()
        print("\n==========================================")
        print("所有下载任务已处理完毕！")
        print("==========================================")

if __name__ == "__main__":
    asyncio.run(download_cet4_papers())
