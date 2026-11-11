import os
import cohere


# ============================================================
# 【看懂即可】读取 API Key
# ============================================================

api_key = os.environ.get("COHERE_API_KEY")
#os.environ:Python 用来读取当前系统环境变量的地方。

# 如果没有读取到 API Key，就主动报错。
if not api_key:
    raise ValueError(
        "没有找到 COHERE_API_KEY 环境变量"
    )


# ============================================================
# 【看懂即可】创建 Cohere 客户端
# ============================================================

client = cohere.ClientV2(
    api_key=api_key
)
#可以类比 Java：CohereClient client = new CohereClient(apiKey);

# ============================================================
# 【必须理解】准备要向量化的文本
# ============================================================

text = (
    "Classic search is an index-first "
    "retrieval model."
)


# ============================================================
# 【必须理解】调用 Embedding API
# ============================================================

response = client.embed(
    model="embed-v5.0-pro",#使用哪个 Embedding Model。
    texts=[text],#把str转化成list[str]
    input_type="search_document",#官方对于 semantic search（语义搜索）的建议
    embedding_types=["float"]#希望 API 返回浮点数形式的 Embedding
)


# ============================================================
# 【必须理解】取出 Embedding Vector
# ============================================================

embedding = response.embeddings.float_[0]#取第一个文本对应的向量


# ============================================================
# 【必须理解】检查 Embedding 结果
# ============================================================

print("Embedding 类型：", type(embedding))
print("Embedding 维度：", len(embedding))

print("前 10 个数字：")
print(embedding[:10])















