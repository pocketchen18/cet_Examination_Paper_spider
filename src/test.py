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
        # 规则：href 属性以 /cet4/ 开头
        links = await page.query_selector_all("a[href^='/cet4/']")
        paper_links = []
        for link in links:
            href = await link.get_attribute("href")
            # 使用正则表达式匹配特定格式，如 /cet4/2025-06/01
            # 并通过捕获组获取年份进行过滤
            match = re.search(r'/cet4/(\d{4})-\d{2}/\d+', href)
            if match:
                year = int(match.group(1))
                # 检查年份是否在设定的范围内
                if config.START_YEAR <= year <= config.END_YEAR:
                    full_url = f"https://zhenti.burningvocabulary.cn{href}"
                    if full_url not in paper_links:
                        paper_links.append(full_url)
                        print(f"{full_url}")

        print(f"分析完成，在 {config.START_YEAR}-{config.END_YEAR} 范围内共发现 {len(paper_links)} 套真题详情页。")

        # ---------------------------------------------------------
        # 3. 循环进入每个详情页进行下载
        # ---------------------------------------------------------

        close_btn_xpath=config.DOWNLOAD_BUTTON_XPATH
        # await page.goto(paper_links[1])
        # await page.locator(f"xpath={close_btn_xpath}").wait_for(state="visible", timeout=3000)

        # 等待页面完全加载
        for paper_url in paper_links:
        # paper_url = paper_links[4]  # 将当前URL赋值给paper_url变量
            await page.goto(paper_url)
            await page.wait_for_load_state("networkidle")  # 等待网络空闲

            # # 等待按钮可点击
            # await page.wait_for_selector(f"xpath={config.DOWNLOAD_BUTTON_XPATH}",
            #                            state="visible",
            #                            timeout=10000)
            # 在点击前添加事件监听
            # page.on("console", lambda msg: print(f"页面控制台: {msg.text}"))

            # 执行点击并捕获异常
            try:
                # 监听下载事件
                async with page.expect_download(timeout=15000) as download_info:
                    await page.click(f"xpath={config.DOWNLOAD_BUTTON_XPATH}")
                
                # 获取下载对象
                download = await download_info.value
                
                # 根据URL解析年份、月份和套数，生成符合规范的文件名
                # URL格式如: https://zhenti.burningvocabulary.cn/cet4/2025-06/03
                parts = paper_url.split('/')
                # 获取倒数第二部分（年份-月份，如2025-06）和最后一部分（套数，如03）
                date_part = parts[-2]  # 例如: 2025-06
                set_number = parts[-1]  # 例如: 03
                
                # 根据规范生成文件名: 年份+月份+第几套.pdf
                filename = f"{date_part}-{set_number}.pdf"
                
                # 保存到指定路径
                save_path = os.path.join(config.DOWNLOAD_DIR, filename)
                await download.save_as(save_path)
                print(f"成功保存到: {save_path}")
                
            except Exception as e:
                print(f"下载失败: {e}")

        # 保持浏览器窗口打开
        # print("浏览器窗口保持打开状态，按 Ctrl+C 退出...")
        # try:
        #     # 保持程序运行，等待用户中断
        #     while True:
        #         await asyncio.sleep(1)
        # except KeyboardInterrupt:
        #     print("\n用户中断，正在关闭浏览器...")
        #     await browser.close()
        #     return

        # 原来的关闭代码被上面的逻辑替代
        # await browser.close()





        # for paper_url in paper_links:
            # try:
            #     print(f"\n[任务] 正在处理: {paper_url}")
            #     await page.goto(paper_url)

            #     # 等待下载按钮出现在 DOM 中
            #     # 使用 XPath 定位，超时时间设为 10 秒
            #     await page.wait_for_selector(f"xpath={config.DOWNLOAD_BUTTON_XPATH}", timeout=10000)

            #     # 关键：使用异步上下文管理器监听下载事件
            #     # 必须在点击按钮之前开始监听
            #     async with page.expect_download() as download_info:
            #         # 模拟用户点击下载按钮
            #         await page.click(f"xpath={config.DOWNLOAD_BUTTON_XPATH}")
            #         await asyncio.sleep(10)
            #     # 获取下载对象
            #     download = await download_info.value

            #     # 确定保存的文件名
            #     # 根据URL解析年份、月份和套数，生成符合规范的文件名
            #     # URL格式如: https://zhenti.burningvocabulary.cn/cet4/2025-06/03
            #     parts = paper_url.split('/')
            #     # 获取倒数第二部分（年份-月份，如2025-06）和最后一部分（套数，如03）
            #     date_part = parts[-2]  # 例如: 2025-06
            #     set_number = parts[-1]  # 例如: 03
                
            #     # 根据规范生成文件名: 年份+月份+第几套.pfd
            #     filename = f"{date_part}-{set_number}.pfd"

            #     # 执行保存操作
            #     save_path = os.path.join(config.DOWNLOAD_DIR, filename)
            #     await download.save_as(save_path)
            #     print(f"成功保存到: {save_path}")

            #     # 礼貌性延时 2 秒，防止请求过快触发反爬虫
            #     await asyncio.sleep(2)

            # except Exception as e:
            #     # 记录单次任务的错误，但不中断整个循环
            #     print(f"处理失败 {paper_url}: {e}")
            #     continue

        # 任务结束，关闭浏览器
        await browser.close()
        print("\n==========================================")
        print("所有下载任务已处理完毕！")
        print("==========================================")


if __name__ == "__main__":
    # 使用 asyncio 运行异步主函数
    asyncio.run(download_cet4_papers())
