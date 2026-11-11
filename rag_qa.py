import os

import cohere

from retrieval.retrieve import retrieve


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
# 【必须理解】Context Construction
# ============================================================

def build_context(results):
    """
    把 Retrieval Results
    整理成提供给 LLM 的 Context。
    """

    context_parts = []

    for index, result in enumerate(
            results,
            start=1
    ):

        context_part = (
            f"[Source {index}]\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Section: {result['section']}\n"
            f"Source: {result['source']}\n"
            f"URL: {result['source_url']}\n"
            f"Content:\n"
            f"{result['text']}"
        )

        context_parts.append(
            context_part
        )

    context = "\n\n".join(
        context_parts
    )

    return context


# ============================================================
# 【必须理解】Prompt Construction
# ============================================================

def build_prompt(
        query,
        context
):
    """
    把用户问题和检索证据
    组织成发送给 LLM 的 Prompt。
    """

    prompt = f"""
Use only the provided context to answer the question.

Rules:
1. Do not use unsupported information.
2. If the context does not contain enough evidence,
   clearly say that the available evidence is insufficient.
3. Cite evidence using [Source N].
4. Keep the answer concise and factual.

Context:
{context}

Question:
{query}
"""

    return prompt.strip()


# ============================================================
# 【必须理解】LLM Generation
# ============================================================

def generate_answer(
        query,
        context
):
    """
    根据 Query + Context
    调用 LLM 生成答案。
    """

    prompt = build_prompt(
        query,
        context
    )

    response = client.chat(
        model="command-a-plus-05-2026",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a knowledge-base QA assistant. "
                    "Answer only from the supplied evidence."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer_parts = []

    for content_item in response.message.content:

        if content_item.type == "text":
            answer_parts.append(
            content_item.text
        )

    answer = "".join(
        answer_parts
)

    return answer


# ============================================================
# 【必须理解】显示程序控制的 Citation 信息
# ============================================================

def print_sources(results):
    """
    显示 Retrieval 真正返回的来源信息。

    Citation Metadata 来自程序，
    而不是让 LLM 自己编造。
    """

    print("\nSources:")

    for index, result in enumerate(
            results,
            start=1
    ):

        print(
            f"\n[Source {index}]"
        )

        print(
            "Chunk ID：",
            result["chunk_id"]
        )

        print(
            "Section：",
            result["section"]
        )

        print(
            "Source：",
            result["source"]
        )

        print(
            "URL：",
            result["source_url"]
        )


# ============================================================
# 【必须理解】完整 RAG Pipeline
# ============================================================

def answer_question(
        query,
        top_k=3
):
    """
    完成一次最小 RAG 问答：

    Query
    → Retrieval
    → Context
    → LLM
    → Answer + Citation
    """

    # 1. Retrieval
    results = retrieve(
        query=query,
        top_k=top_k
    )

    # 2. Context Construction
    context = build_context(
        results
    )

    # 3. LLM Generation
    answer = generate_answer(
        query=query,
        context=context
    )

    return answer, results, context


# ============================================================
# 【必须理解】程序入口
# ============================================================

if __name__ == "__main__":

    query = "How does classic search work?"

    answer, results, context = answer_question(
        query=query,
        top_k=3
    )

    print("Question:")
    print(query)

    print("\n====================")

    print("Answer:")
    print(answer)

    print("\n====================")

    print_sources(
        results
    )