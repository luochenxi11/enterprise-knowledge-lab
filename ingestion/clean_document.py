from pathlib import Path
import json


# -------------------- 文件定位 --------------------

# 获取项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Parsing 阶段生成的 JSON 文件。
PARSED_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "parsed"
        / "json"
        / "doc_001_azure_search_overview.json"
)

# Cleaning 后的输出文件。
CLEANED_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "normalized"
        / "json"
        / "doc_001_azure_search_overview.json"
)


# -------------------- 读取 Parsing 结果 --------------------

# 读取 JSON 文件。
json_text = PARSED_PATH.read_text(encoding="utf-8")

# JSON 字符串转换成 Python 字典。
parsed_document = json.loads(json_text)

title = parsed_document["title"]
blocks = parsed_document["blocks"]

print("文档标题：", title)
print("原始 block 数量：", len(blocks))


# -------------------- Cleaning 规则 --------------------

# 完全匹配这些文本时，认为它们属于网页噪声。
NOISE_TEXTS = {
    "Note",
    "Feedback",
    "Additional resources",
    "Was this page helpful?",
    "Need help with this topic?",
    "Want to try using Ask Learn to clarify or guide you through this topic?"
}


# -------------------- 执行 Cleaning --------------------

cleaned_blocks = []

for block in blocks:

    # table 使用 rows 保存内容，没有 text 字段。
    # 当前阶段先完整保留表格。
    if block["type"] == "table":
        cleaned_blocks.append(block)
        continue

    # 安全获取 text 字段。
    # 如果不存在，则返回空字符串。
    text = block.get("text", "").strip()

    # 删除空文本。
    if not text:
        continue

    # 删除完全匹配的已知页面噪声。
    if text in NOISE_TEXTS:
        continue

    # 删除 Microsoft Learn 的授权提示。
    if text.startswith("Access to this page requires authorization"):
        continue

    # 其他内容保留。
    cleaned_blocks.append(block)


# -------------------- 构建 Cleaning 结果 --------------------

cleaned_document = {
    "title": title,
    "blocks": cleaned_blocks
}

print("Cleaning 后 block 数量：", len(cleaned_blocks))
print("删除 block 数量：", len(blocks) - len(cleaned_blocks))


# -------------------- 保存 Cleaning 结果 --------------------

# 如果目录不存在，则自动创建。
CLEANED_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Python 对象转换成格式化 JSON 字符串。
cleaned_json = json.dumps(
    cleaned_document,
    ensure_ascii=False,
    indent=2
)

# 保存 Cleaning 后的 JSON。
CLEANED_PATH.write_text(
    cleaned_json,
    encoding="utf-8"
)

print("Cleaning 结果已保存：", CLEANED_PATH)