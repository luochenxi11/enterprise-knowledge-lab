from pathlib import Path
import json


# -------------------- 文件定位 --------------------

# 获取项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Cleaning 阶段输出的 normalized JSON。
NORMALIZED_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "normalized"
        / "json"
        / "doc_001_azure_search_overview.json"
)

# Chunking 阶段输出文件。
CHUNKS_PATH = (
        PROJECT_ROOT
        / "datasets"
        / "chunks"
        / "json"
        / "doc_001_azure_search_overview_chunks.json"
)


# -------------------- 读取 Cleaning 结果 --------------------

json_text = NORMALIZED_PATH.read_text(encoding="utf-8")

normalized_document = json.loads(json_text)
#Python的dict字典，可以把它类比成 Java 里的：Map<String, Object>

title = normalized_document["title"]
#从字典里取出key为“title”的value，类似map.get("title")

blocks = normalized_document["blocks"]
#从字典里取出key为“blocks”的value,block本质是一个list
#粗略类比：List<Map<String, Object>> blocks;

print("文档标题：", title)
print("block 数量：", len(blocks))


# -------------------- Chunking --------------------

chunks = []
#创建一个空列表，类比：List<Something> chunks = new ArrayList<>();
#因为Python是动态类型语言，会在运行的时候知道是什么类型的数据

current_heading = None
#类比java：null

current_content = []
#类比java：List<String> currentContent = new ArrayList<>();


def save_current_chunk():
    #Python声明方法的语句，类比java：void saveCurrentChunk(){}
    """
    将当前累积的 section 保存成一个 chunk。

    只有 current_content 中真正有内容时才保存。
    """

    if not current_content:
        return

    chunk_text = "\n".join(current_content)

    chunk = {
        "section": current_heading,
        "text": chunk_text
    }

    chunks.append(chunk)


for block in blocks:

    block_type = block["type"]
    #从这个字典里取 "type" 这个 key 的 value。

    # -------------------- Heading --------------------

    if block_type == "heading":

        # 遇到新的 heading，
        # 说明前一个 section 已经结束。
        save_current_chunk()

        # 更新当前 section 标题。
        current_heading = block["text"]

        # 新 section 开始时，清空之前的内容。
        current_content = []

    # -------------------- Paragraph --------------------

    elif block_type == "paragraph":
        current_content.append(block["text"])

    # -------------------- List Item --------------------

    elif block_type == "list_item":
        current_content.append(
            "- " + block["text"]
        )

    # -------------------- Table --------------------

    elif block_type == "table":

        for row in block["rows"]:
            row_text = " | ".join(row)
            current_content.append(row_text)


# 循环结束后，最后一个 section 还没有机会被保存。
# 所以需要手动保存一次。
save_current_chunk()


# -------------------- 添加 chunk_id --------------------

for index, chunk in enumerate(chunks, start=1):

    chunk["chunk_id"] = f"doc_001_chunk_{index:03d}"


# -------------------- 查看 Chunking 结果 --------------------

print("生成 chunk 数量：", len(chunks))

for chunk in chunks:
    print("\n", chunk["chunk_id"])
    print("section：", chunk["section"])
    print("text：")
    print(chunk["text"][:300])


# -------------------- 保存 Chunking 结果 --------------------

chunked_document = {
    "title": title,
    "chunks": chunks
}

CHUNKS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

chunked_json = json.dumps(
    chunked_document,
    ensure_ascii=False,
    indent=2
)

CHUNKS_PATH.write_text(
    chunked_json,
    encoding="utf-8"
)

print("\nChunking 结果已保存：", CHUNKS_PATH)