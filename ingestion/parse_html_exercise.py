from pathlib import Path
from bs4 import BeautifulSoup
import json


# -------------------- 文件定位 --------------------

# 获取项目根目录。
# __file__：当前 Python 文件路径。
# resolve()：转换成规范的绝对路径。
# parent.parent：从 ingestion/parse_html.py 向上两层到项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 拼接原始 HTML 文件路径。
HTML_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "raw"
        / "html"
        / "doc_001_azure_search_overview.html"
)


# -------------------- 文件读取 --------------------

# 将 HTML 文件读取为 Python 字符串。
# encoding="utf-8" 指定字符编码。
html_text = HTML_PATH.read_text(encoding="utf-8")


# -------------------- HTML Parsing --------------------

# 将 HTML 字符串解析为 BeautifulSoup 文档对象。
# 解析后可以按 HTML 标签和结构访问内容。
soup = BeautifulSoup(html_text, "html.parser")

# 提取网页 <title> 标签中的文本。
# 如果没有 <title>，则返回 None。
page_title = soup.title.get_text(strip=True) if soup.title else None

print("网页标题：", page_title)


# -------------------- 定位正文区域 --------------------

# 优先使用 <main> 作为网页正文区域。
# 避免直接从整个页面中提取导航、页脚等站点级内容。
main_content = soup.find("main")

if main_content is None:
    raise ValueError("没有找到 <main> 标签，无法继续解析正文。")

print("成功找到 <main> 标签")


# -------------------- 构建结构化 Parsing 结果 --------------------

# blocks 用于按照网页原始顺序保存正文块。
# 每个 block 都会记录自己的类型和内容。
blocks = []

# 按照 HTML 中原本出现的顺序，
# 查找标题、段落、列表项和表格。
elements = main_content.find_all(
    ["h1", "h2", "h3", "h4", "p", "li", "table"]
)

for element in elements:

    # 如果 <p> 位于 <li> 或 <table> 内部，
    # 就不单独保存。
    # 因为父级结构之后会整体保存，避免重复。
    if element.name == "p" and (
            element.find_parent("li") is not None
            or element.find_parent("table") is not None
    ):
        continue

    # 如果 <li> 位于 <table> 内部，
    # 也交给 table 整体处理，避免重复。
    if element.name == "li" and element.find_parent("table") is not None:
        continue

    # 提取标签中的纯文本。
    text = element.get_text(" ", strip=True)

    # 空文本不进入解析结果。
    if not text:
        continue

    # -------------------- 标题块 --------------------

    if element.name in ["h1", "h2", "h3", "h4"]:
        blocks.append({
            "type": "heading",
            "level": int(element.name[1]),
            "text": text
        })

    # -------------------- 普通段落块 --------------------

    elif element.name == "p":
        blocks.append({
            "type": "paragraph",
            "text": text
        })

    # -------------------- 列表项块 --------------------

    elif element.name == "li":
        blocks.append({
            "type": "list_item",
            "text": text
        })

    # -------------------- 表格块 --------------------

    elif element.name == "table":

        # rows 用于保存表格中的所有行。
        rows = []

        # 遍历表格中的每一行 <tr>。
        for row in element.find_all("tr"):

            # 一行中可能有：
            # <th> 表头单元格
            # <td> 普通单元格
            cells = row.find_all(["th", "td"])

            # 提取这一行所有单元格中的文本。
            cell_texts = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]

            # 空行不保存。
            if cell_texts:
                rows.append(cell_texts)

        # 只有真正包含内容的表格才保存。
        if rows:
            blocks.append({
                "type": "table",
                "rows": rows
            })


# -------------------- 构建 Parsed Document --------------------

# 整个文档的结构化 Parsing 结果。
parsed_document = {
    "title": page_title,
    "blocks": blocks
}

print("\n解析后的 block 数量：", len(blocks))

# 打印前 10 个 block，快速检查解析结果。
for block in blocks[:10]:
    print(block)


# -------------------- 保存 Parsing 中间结果 --------------------

PARSED_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "parsed"
        / "json"
        / "doc_001_azure_search_overview.json"
)

# 如果目标目录不存在，则自动创建。
PARSED_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

# ensure_ascii=False：
# 保存 JSON 时保留正常 Unicode 字符。
#
# indent=2：
# 使用缩进格式保存，方便人工查看和调试。
json_text = json.dumps(
    parsed_document,
    ensure_ascii=False,
    indent=2
)

# 将 JSON 写入文件。
PARSED_PATH.write_text(
    json_text,
    encoding="utf-8"
)

print("\nParsing 结果已保存：", PARSED_PATH)