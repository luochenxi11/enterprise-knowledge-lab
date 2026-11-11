from pathlib import Path
import json
import csv


# ============================================================
# 【看懂即可】文件路径
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Corpus 文档清单。
MANIFEST_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "corpus_manifest.csv"
)

# Chunking 阶段输出。
CHUNKS_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "chunks"
        / "json"
        / "doc_001_azure_search_overview_chunks.json"
)

# Metadata 阶段输出。
OUTPUT_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "metadata"
        / "json"
        / "doc_001_chunks_with_metadata.json"
)


# ============================================================
# 【必须理解】当前要处理哪份文档
# ============================================================

DOCUMENT_ID = "doc_001"


# ============================================================
# 【必须理解】从 corpus manifest 中读取文档 Metadata
# ============================================================

def load_document_metadata(document_id):
    """
    根据 document_id，
    从 corpus_manifest.csv 中找到对应文档的 Metadata。
    """

    # newline="" 是读取 CSV 时的常见写法，
    # encoding="utf-8-sig" 可以兼容部分带 BOM 的 CSV。
    with MANIFEST_PATH.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
    ) as file:

        # DictReader 会把 CSV 的每一行
        # 转换成一个 Python dict。
        reader = csv.DictReader(file)

        # 遍历 manifest 中的每一份文档。
        for row in reader:

            # 找到当前需要处理的 document_id。
            if row["document_id"] == document_id:

                document_metadata = {
                    "document_id": row["document_id"],
                    "title": row["title"],
                    "source": row["source"],
                    "source_url": row["source_url"],
                    "source_type": row["source_type"],
                    "language": row["language"],
                    "raw_file": row["raw_file"],
                    "normalized_file": row["normalized_file"]
                }

                return document_metadata

    # 如果整个 CSV 遍历完都没有找到，
    # 说明 document_id 或 manifest 存在问题。
    raise ValueError(
        f"在 corpus_manifest.csv 中找不到文档：{document_id}"
    )


# ============================================================
# 【必须理解】加载文档 Metadata
# ============================================================

document_metadata = load_document_metadata(
    DOCUMENT_ID
)

print("读取到文档 Metadata：")
print(document_metadata)


# ============================================================
# 【看懂即可】读取 Chunking 结果
# ============================================================

json_text = CHUNKS_PATH.read_text(
    encoding="utf-8"
)

chunked_document = json.loads(
    json_text
)

chunks = chunked_document["chunks"]


# ============================================================
# 【必须理解】把文档 Metadata 传播给每一个 Chunk
# ============================================================

enriched_chunks = []

for index, chunk in enumerate(chunks, start=1):

    # 复制原来的 chunk。
    enriched_chunk = chunk.copy()

    # -------------------- 文档级 Metadata --------------------

    enriched_chunk["document_id"] = (
        document_metadata["document_id"]
    )

    enriched_chunk["document_title"] = (
        document_metadata["title"]
    )

    enriched_chunk["source"] = (
        document_metadata["source"]
    )

    enriched_chunk["source_url"] = (
        document_metadata["source_url"]
    )

    enriched_chunk["source_type"] = (
        document_metadata["source_type"]
    )

    enriched_chunk["language"] = (
        document_metadata["language"]
    )

    # -------------------- Chunk 级 Metadata --------------------

    enriched_chunk["chunk_index"] = index

    enriched_chunks.append(
        enriched_chunk
    )


# ============================================================
# 【必须理解】构建最终输出
# ============================================================

output_document = {
    "document_metadata": document_metadata,
    "chunks": enriched_chunks
}


# ============================================================
# 【必须理解】检查结果
# ============================================================

print("\n文档 ID：", document_metadata["document_id"])
print("文档标题：", document_metadata["title"])
print("Chunk 数量：", len(enriched_chunks))

for chunk in enriched_chunks[:2]:

    print("\n--------------------")
    print("chunk_id：", chunk["chunk_id"])
    print("document_id：", chunk["document_id"])
    print("chunk_index：", chunk["chunk_index"])
    print("section：", chunk.get("section"))
    print("source：", chunk["source"])
    print("source_url：", chunk["source_url"])

    print("text：")
    print(chunk["text"][:200])


# ============================================================
# 【看懂即可】保存 JSON
# ============================================================

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
    "\nMetadata 结果已保存：",
    OUTPUT_PATH
)