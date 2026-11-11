from pathlib import Path
import json


# ============================================================
# 【看懂即可】文件路径
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
        / "paragraph"
        / "doc_001_paragraph_chunks.json"
)


# ============================================================
# 【看懂即可】读取 Cleaning 后的数据
# ============================================================

json_text = NORMALIZED_PATH.read_text(encoding="utf-8")

normalized_document = json.loads(json_text)

title = normalized_document["title"]
blocks = normalized_document["blocks"]


# ============================================================
# 【必须理解】Paragraph-based Chunking
# ============================================================

chunks = []

for block in blocks:

    # 获取当前 block 的类型。
    block_type = block["type"]

    # 当前策略只把 paragraph 作为 chunk。
    if block_type == "paragraph":

        paragraph_text = block["text"]

        #→ list[dict] → 可以继续挂 metadata
        chunks.append({
            "text": paragraph_text
        })



# ============================================================
# 【看懂即可】添加 chunk_id
# ============================================================

for index, chunk in enumerate(chunks, start=1):

    chunk["chunk_id"] = (
        f"doc_001_paragraph_{index:03d}"
    )


# ============================================================
# 【必须理解】观察 Paragraph Chunk 的长度差异
# ============================================================

print("生成 chunk 数量：", len(chunks))

for chunk in chunks[:10]:

    print("\n--------------------")
    print("chunk_id：", chunk["chunk_id"])
    print("字符数：", len(chunk["text"]))
    print("text：")
    print(chunk["text"][:300])


# ============================================================
# 【看懂即可】统计最短 / 最长 chunk
# ============================================================

if chunks:

    shortest_chunk = min(
        chunks,
        key=lambda chunk: len(chunk["text"])
    )

    longest_chunk = max(
        chunks,
        key=lambda chunk: len(chunk["text"])
    )

    print("\n最短 chunk：")
    print("chunk_id：", shortest_chunk["chunk_id"])
    print("字符数：", len(shortest_chunk["text"]))
    print("text：", shortest_chunk["text"][:200])

    print("\n最长 chunk：")
    print("chunk_id：", longest_chunk["chunk_id"])
    print("字符数：", len(longest_chunk["text"]))
    print("text：", longest_chunk["text"][:200])


# ============================================================
# 【看懂即可】保存 JSON
# ============================================================

output_document = {
    "title": title,
    "strategy": "paragraph",
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

print(
    "\nParagraph-based Chunking 结果已保存：",
    OUTPUT_PATH
)