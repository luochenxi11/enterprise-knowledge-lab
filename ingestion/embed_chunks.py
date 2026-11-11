from pathlib import Path
import json
import os
import cohere


# ============================================================
# 【看懂即可】文件路径
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Metadata 阶段输出的文件。
METADATA_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "metadata"
        / "json"
        / "doc_001_chunks_with_metadata.json"
)

# Embedding 阶段输出的文件。
OUTPUT_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "embeddings"
        / "json"
        / "doc_001_chunks_with_embeddings.json"
)


# ============================================================
# 【看懂即可】读取 Cohere API Key
# ============================================================

api_key = os.environ.get("COHERE_API_KEY")

if not api_key:
    raise ValueError(
        "没有找到 COHERE_API_KEY 环境变量"
    )


# ============================================================
# 【看懂即可】创建 Cohere Client
# ============================================================

client = cohere.ClientV2(
    api_key=api_key
)


# ============================================================
# 【必须理解】读取 Metadata JSON
# ============================================================

json_text = METADATA_PATH.read_text(
    encoding="utf-8"
)

metadata_document = json.loads(
    json_text
)

document_metadata = metadata_document["document_metadata"]
chunks = metadata_document["chunks"]

print("文档 ID：", document_metadata["document_id"])
print("Chunk 数量：", len(chunks))


# ============================================================
# 【必须理解】提取所有 Chunk 的文本
# ============================================================

texts = []

for chunk in chunks:
    texts.append(
        chunk["text"]
    )

print("准备 Embedding 的文本数量：", len(texts))


# ============================================================
# 【必须理解】批量调用 Embedding API:Batch Embedding（批量向量化）
# ============================================================

response = client.embed(
    model="embed-v5.0-pro",
    texts=texts,
    input_type="search_document",
    embedding_types=["float"]
)


# ============================================================
# 【必须理解】取出所有 Embedding
# ============================================================

embeddings = response.embeddings.float_

print("返回 Embedding 数量：", len(embeddings))


# ============================================================
# 【必须理解】检查数量是否一致
# ============================================================

if len(chunks) != len(embeddings):
    raise ValueError(
        "Chunk 数量和 Embedding 数量不一致"
    )


# ============================================================
# 【必须理解】把 Embedding 写回对应 Chunk
# ============================================================

embedded_chunks = []

for chunk, embedding in zip(chunks, embeddings):
#zip(chunks, embeddings)会把相同位置组合起来

    # 复制原 chunk，保留原有 Metadata。
    embedded_chunk = chunk.copy()

    # 新增 embedding 字段。
    embedded_chunk["embedding"] = embedding

    # 保存到新的列表。
    embedded_chunks.append(
        embedded_chunk
    )


# ============================================================
# 【必须理解】构建最终输出
# ============================================================

output_document = {
    "document_metadata": document_metadata,
    "embedding_model": "embed-v5.0-pro",
    "embedding_dimension": (
        len(embeddings[0])
        if embeddings
        else 0
    ),
    "chunks": embedded_chunks
}


# ============================================================
# 【必须理解】检查结果
# ============================================================

print("\nEmbedding 完成")

print(
    "Embedding 维度：",
    output_document["embedding_dimension"]
)

print(
    "第一个 Chunk ID：",
    embedded_chunks[0]["chunk_id"]
)

print(
    "第一个 Embedding 前 10 个数字："
)

print(
    embedded_chunks[0]["embedding"][:10]
)


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
    "\nEmbedding 结果已保存：",
    OUTPUT_PATH
)