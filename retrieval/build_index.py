from pathlib import Path
import json
import numpy as np


# ============================================================
# 【看懂即可】文件路径
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Embedding 阶段生成的 JSON。
EMBEDDINGS_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "embeddings"
        / "json"
        / "doc_001_chunks_with_embeddings.json"
)

# Index 输出目录。
INDEX_DIR = (
        PROJECT_ROOT
        / "datasets"
        / "index"
)

# 保存向量矩阵。
VECTORS_PATH = (
        INDEX_DIR
        / "vectors.npy"
)

# 保存与向量对应的 Chunk 信息。
RECORDS_PATH = (
        INDEX_DIR
        / "records.json"
)


# ============================================================
# 【必须理解】读取 Embedding 数据
# ============================================================

json_text = EMBEDDINGS_PATH.read_text(
    encoding="utf-8"
)

embedding_document = json.loads(
    json_text
)

chunks = embedding_document["chunks"]

print("Chunk 数量：", len(chunks))


# ============================================================
# 【必须理解】分别收集 Vector 和 Chunk Record
# ============================================================

vectors = []
records = []

for index, chunk in enumerate(chunks):

    # -------------------- Vector --------------------

    # 取出当前 chunk 的 embedding。
    embedding = chunk["embedding"]

    # 加入 vectors。
    vectors.append(embedding)

    # -------------------- Record --------------------

    # 保存与这个 vector 对应的知识记录。
    record = {
        "index": index,
        "chunk_id": chunk["chunk_id"],
        "document_id": chunk["document_id"],
        "chunk_index": chunk["chunk_index"],
        "section": chunk.get("section"),
        "source": chunk["source"],
        "source_url": chunk["source_url"],
        "text": chunk["text"]
    }

    records.append(record)


# ============================================================
# 【必须理解】把 Vector List 转成 NumPy Matrix
# ============================================================

vector_matrix = np.array(
    vectors,
    dtype=np.float32
)


# ============================================================
# 【必须理解】检查 Matrix 形状
# ============================================================

print("Vector Matrix shape：", vector_matrix.shape)

print(
    "第一条 Vector 维度：",
    len(vector_matrix[0])
)


# ============================================================
# 【必须理解】检查 Vector 和 Record 是否一一对应
# ============================================================

if len(vector_matrix) != len(records):
    raise ValueError(
        "Vector 数量和 Record 数量不一致"
    )


# ============================================================
# 【看懂即可】创建 Index 目录
# ============================================================

INDEX_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 【看懂即可】保存 Vector Matrix
# ============================================================

np.save(
    VECTORS_PATH,
    vector_matrix
)


# ============================================================
# 【看懂即可】保存 Records
# ============================================================

records_json = json.dumps(
    records,
    ensure_ascii=False,
    indent=2
)

RECORDS_PATH.write_text(
    records_json,
    encoding="utf-8"
)


# ============================================================
# 【必须理解】验证 Index
# ============================================================

print("\nIndex 构建完成")

print(
    "Vector 数量：",
    len(vector_matrix)
)

print(
    "Record 数量：",
    len(records)
)

print(
    "第一条 Vector 对应 Chunk：",
    records[0]["chunk_id"]
)

print(
    "第一条 Record section：",
    records[0]["section"]
)

print(
    "\nVector 文件：",
    VECTORS_PATH
)

print(
    "Record 文件：",
    RECORDS_PATH
)






