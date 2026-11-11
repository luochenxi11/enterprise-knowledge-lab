from pathlib import Path
import json


# ============================================================
# 【看懂即可】文件路径配置
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NORMALIZED_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "normalized"
        / "json"
        / "doc_001_azure_search_overview.json"
)

OUTPUT_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "chunks"
        / "fixed_size"
        / "doc_001_fixed_size_chunks.json"
)


# ============================================================
# 【必须理解】Chunking 参数
# ============================================================

# 每个 chunk 最多包含多少个字符。
CHUNK_SIZE = 500


# ============================================================
# 【看懂即可】读取 Cleaning 后的数据
# ============================================================

json_text = NORMALIZED_PATH.read_text(encoding="utf-8")

normalized_document = json.loads(json_text)

title = normalized_document["title"]
blocks = normalized_document["blocks"]


# ============================================================
# 【必须理解】把不同 block 转成普通文本
# ============================================================

text_parts = []

for block in blocks:

    block_type = block["type"]

    # heading：保留标题文本。
    if block_type == "heading":
        text_parts.append(block["text"])

    # paragraph：直接保留正文。
    elif block_type == "paragraph":
        text_parts.append(block["text"])

    # list_item：增加 "- "，保留一点列表结构。
    elif block_type == "list_item":
        text_parts.append("- " + block["text"])

    # table：把每一行转换成文本。
    elif block_type == "table":

        for row in block["rows"]:
            row_text = " | ".join(row)
            text_parts.append(row_text)


# ============================================================
# 【必须理解】合并成一个长字符串
# ============================================================

full_text = "\n".join(text_parts)

print("全文字符数：", len(full_text))


# ============================================================
# 【必须理解】Fixed-size Chunking 核心逻辑
# ============================================================

chunks = []

# start 表示当前 chunk 从哪个字符开始。
start = 0

while start < len(full_text):

    # end 表示当前 chunk 在哪里结束。
    end = start + CHUNK_SIZE

    # 从 full_text 中截取固定长度文本。
    chunk_text = full_text[start:end]
    #把一个字符串列表，按指定分隔符拼接成一个字符串。

    # 保存 chunk。
    chunks.append({
        "text": chunk_text
    })

    # 下一个 chunk 从当前 end 开始。
    start = end


# ============================================================
# 【看懂即可】添加 chunk_id
# ============================================================

for index, chunk in enumerate(chunks, start=1):

    chunk["chunk_id"] = (
        f"doc_001_fixed_{index:03d}"
    )


# ============================================================
# 【必须理解】观察 Chunking 结果
# ============================================================

print("生成 chunk 数量：", len(chunks))

for chunk in chunks[:5]:

    print("\n--------------------")
    print("chunk_id：", chunk["chunk_id"])
    print("字符数：", len(chunk["text"]))
    print("text：")
    print(chunk["text"][:300])


# ============================================================
# 【看懂即可】保存 JSON
# ============================================================

output_document = {
    "title": title,
    "strategy": "fixed_size",
    "chunk_size": CHUNK_SIZE,
    "chunks": chunks
}

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

output_json = json.dumps(
    output_document,
    ensure_ascii=False,
    indent=2
)

OUTPUT_PATH.write_text(
    output_json,
    encoding="utf-8"
)

print("\nFixed-size Chunking 结果已保存：", OUTPUT_PATH)