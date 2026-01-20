import os
import time
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config

def format_answers(raw_text):
    """
    优化答案排版格式：
    处理 5个答案+5个题号 的特殊网页结构
    """
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    results = []
    
    i = 0
    while i < len(lines):
        # 检查当前行是否是题号行 (例如 "1 2 3 4 5" 或 "26 27 28 29 30")
        if re.match(r'^(\d+\s+)+\d+$', lines[i]):
            nums = lines[i].split()
            # 题号行之前的行应该是答案
            # 往前找对应数量的答案行
            for j, num in enumerate(nums):
                answer_idx = i - len(nums) + j
                if answer_idx >= 0:
                    ans = lines[answer_idx]
                    # 确保 ans 看起来像个答案（单个字母或单词）
                    if re.match(r'^[A-Z]$|^[A-Z][a-z]+$', ans):
                        results.append((int(num), ans))
            i += 1
        else:
            # 尝试匹配 "26. A" 这种标准格式
            m = re.match(r'^(\d+)[:.]?\s*([A-Z][a-z]+|[A-Z])$', lines[i])
            if m:
                results.append((int(m.group(1)), m.group(2)))
            i += 1

    # 再次兜底：如果有些行是 "1 A" 这种形式
    if not results:
        for line in lines:
            m = re.search(r'(\d+)\s+([A-Z][a-z]+|[A-Z])', line)
            if m:
                results.append((int(m.group(1)), m.group(2)))

    # 去重并排序
    final_dict = {}
    for num, ans in results:
        final_dict[num] = ans
    
    sorted_nums = sorted(final_dict.keys())
    return "\n".join([f"{num}:{final_dict[num]}" for num in sorted_nums])

def crawl_answers():
    """
    使用 Selenium 爬取答案（优化版）：
    1. 尝试多个 XPath 点击“显示答案”
    2. 格式化输出答案文本
    """
    print(f"正在启动 Edge 浏览器 (使用 Selenium)...")
    
    edge_options = EdgeOptions()
    if config.HEADLESS:
        edge_options.add_argument("--headless")
    
    driver = webdriver.Edge(options=edge_options)
    wait = WebDriverWait(driver, 10)

    try:
        print(f"正在访问主页: {config.BASE_URL}")
        driver.get(config.BASE_URL)

        if not os.path.exists(config.DOWNLOAD_DIR):
            os.makedirs(config.DOWNLOAD_DIR)

        links = driver.find_elements(By.CSS_SELECTOR, f"a[href^='/{config.CET_TYPE}/']")
        paper_links = []
        for link in links:
            href = link.get_attribute("href")
            match = re.search(rf'/{config.CET_TYPE}/(\d{{4}})-\d{{2}}/\d+', href)
            if match:
                year = int(match.group(1))
                if config.START_YEAR <= year <= config.END_YEAR:
                    if href not in paper_links:
                        paper_links.append(href)

        print(f"共发现 {len(paper_links)} 套{config.CET_TYPE.upper()}真题详情页。")

        for paper_url in paper_links:
            try:
                print(f"\n[任务] 正在处理: {paper_url}")
                driver.get(paper_url)

                # 尝试多个 XPath 点击显示答案按钮
                clicked = False
                for xpath in config.SHOW_ANSWER_BUTTON_XPATHS:
                    try:
                        show_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        driver.execute_script("arguments[0].scrollIntoView();", show_btn)
                        time.sleep(0.5)
                        show_btn.click()
                        print(f"成功点击按钮 (XPath: {xpath})")
                        clicked = True
                        break
                    except:
                        continue
                
                if not clicked:
                    print(f"警告: 无法在 {paper_url} 中找到显示答案按钮。")
                    continue

                # 提取并格式化答案
                answer_section = wait.until(EC.visibility_of_element_located((By.XPATH, config.ANSWER_CONTENT_XPATH)))
                raw_answer = answer_section.text
                
                if not raw_answer.strip():
                    print(f"警告: {paper_url} 的答案内容为空。")
                    continue

                # 格式化处理
                formatted_answer = format_answers(raw_answer)

                # 命名并保存
                parts = paper_url.rstrip('/').split('/')
                date_part = parts[-2]
                set_number = parts[-1]
                filename = f"{config.CET_TYPE.upper()}_{date_part}-{set_number}_答案.txt"
                
                save_path = os.path.join(config.DOWNLOAD_DIR, filename)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(f"--- {filename} ---\n\n")
                    f.write(formatted_answer)
                
                print(f"成功保存优化后的答案到: {save_path}")
                time.sleep(1)

            except Exception as e:
                print(f"处理失败 {paper_url}: {e}")
                continue

    finally:
        driver.quit()
        print("\n所有任务处理完成。")

if __name__ == "__main__":
    crawl_answers()
