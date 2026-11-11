from pathlib import Path
import json
import os

import cohere
import numpy as np


# ============================================================
# 【看懂即可】文件路径
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTORS_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "index"
        / "vectors.npy"
)

RECORDS_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "index"
        / "records.json"
)


# ============================================================
# 【看懂即可】创建 Cohere Client
# ============================================================

api_key = os.environ.get("COHERE_API_KEY")

if not api_key:
    raise ValueError(
        "没有找到 COHERE_API_KEY 环境变量"
    )

client = cohere.ClientV2(
    api_key=api_key
)


# ============================================================
# 【看懂即可】加载 Index
# ============================================================

vector_matrix = np.load(
    VECTORS_PATH
)

records_json = RECORDS_PATH.read_text(
    encoding="utf-8"
)

records = json.loads(
    records_json
)


# ============================================================
# 【必须理解】检查 Index 完整性
# ============================================================

if len(vector_matrix) != len(records):
    raise ValueError(
        "Vector 数量和 Record 数量不一致"
    )


# ============================================================
# 【必须理解】Cosine Similarity
# ============================================================

def cosine_similarity(
        query_vector,
        document_vectors
):
    """
    计算 Query Vector
    与所有 Document Vectors 的余弦相似度。
    """

    query_norm = np.linalg.norm(
        query_vector
    )

    document_norms = np.linalg.norm(
        document_vectors,
        axis=1
    )

    dot_products = (
            document_vectors @ query_vector
    )

    similarities = (
            dot_products
            /
            (
                    document_norms
                    * query_norm
            )
    )

    return similarities


# ============================================================
# 【必须理解】Retrieval 主函数
# ============================================================

def retrieve(
        query,
        top_k=3
):
    """
    输入：
        query：用户问题
        top_k：返回最相关的前几个 Chunk

    输出：
        Retrieval Results
    """

    # --------------------------------------------------------
    # 1. Query Embedding
    # --------------------------------------------------------

    response = client.embed(
        model="embed-v5.0-pro",
        texts=[query],
        input_type="search_query",
        embedding_types=["float"]
    )

    query_vector = np.array(
        response.embeddings.float_[0],
        dtype=np.float32
    )


    # --------------------------------------------------------
    # 2. 检查向量维度
    # --------------------------------------------------------

    if query_vector.shape[0] != vector_matrix.shape[1]:
        raise ValueError(
            "Query Vector 与 Index Vector 维度不一致"
        )


    # --------------------------------------------------------
    # 3. Similarity Search
    # --------------------------------------------------------

    similarities = cosine_similarity(
        query_vector,
        vector_matrix
    )


    # --------------------------------------------------------
    # 4. Ranking
    # --------------------------------------------------------

    sorted_indices = np.argsort(
        similarities
    )[::-1]


    # --------------------------------------------------------
    # 5. Top-K
    # --------------------------------------------------------

    top_indices = sorted_indices[:top_k]


    # --------------------------------------------------------
    # 6. 找回 Record
    # --------------------------------------------------------

    results = []

    for index in top_indices:

        record = records[index]

        result = {
            "score": float(
                similarities[index]
            ),
            "chunk_id": record["chunk_id"],
            "document_id": record["document_id"],
            "section": record["section"],
            "source": record["source"],
            "source_url": record["source_url"],
            "text": record["text"]
        }

        results.append(
            result
        )

    return results


# ============================================================
# 【必须理解】直接运行此文件时进行 Retrieval 测试
# ============================================================

if __name__ == "__main__":

    query = "How does classic search work?"

    results = retrieve(
        query=query,
        top_k=3
    )

    print("Query：", query)

    for rank, result in enumerate(
            results,
            start=1
    ):

        print("\n====================")

        print("Rank：", rank)
        print("Score：", result["score"])
        print("Chunk ID：", result["chunk_id"])
        print("Section：", result["section"])
        print("Source：", result["source"])

        print("Text：")
        print(
            result["text"][:500]
        )