import os
import sys
import json
import requests
from pathlib import Path
import argparse
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 文档文本提取函数
def extract_text_from_file(filepath, supported_exts, keep_chunks=False):
    """根据文件扩展名，调用对应库提取文本"""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    try:
        if ext == ".pdf":
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                chunks = []
                for page in reader.pages:
                    chunks.append(page.extract_text().strip())
                if keep_chunks:
                    return chunks
                else:
                    return "\n".join(chunks)
        elif ext in [".html", ".htm"]:
            from bs4 import BeautifulSoup
            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "lxml")
                # 移除 script 和 style
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator="\n")
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                if keep_chunks:
                    return list(chunks)
                else:
                    text = "\n".join(chunk for chunk in chunks if chunk)
                    return text
        elif ext in [".doc", ".docx"]:
            from docx import Document
            doc = Document(filepath)
            chunks = [para.text for para in doc.paragraphs]
            if keep_chunks:
                return list(chunks)
            else:
                text = "\n".join(chunks)
                return text.strip()
        elif ext in supported_exts:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if keep_chunks:
                    return [text]
                else:
                    return text
        else:
            print(f"⚠️ 未知文件类型: {filepath.name}，跳过")
            if keep_chunks:
                return []
            else:
                return ""
    except Exception as e:
        print(f"❌ 读取 {filepath} 失败: {e}")
        if keep_chunks:
            return []
        else:
            return ""

def subdivide_chunks(chunks, text_splitter):
    documents_chunks = []
    documents_chunks_filename = []
    for doc_index,doc in enumerate(chunks):
        new_chunks = text_splitter.split_text(doc)
        documents_chunks += new_chunks
    return documents_chunks

def main():
    parser = argparse.ArgumentParser(description="Rerank documents using local API")
    parser.add_argument("--docs_dir", required=True, help="目录路径，包含PDF、HTML、TXT、DOCX等文档")
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--query_file", type=str, help="包含查询语句的文本文件")
    query_group.add_argument("--query", type=str, help="查询语句字符串")
    parser.add_argument("--add_ext", default=".py.cpp.c.rs", required=False, help="额外的文本格式文件后缀")
    parser.add_argument("--top_n", type=int, default=15, required=False, help="最佳匹配结果显示数量")
    parser.add_argument("--chunk_lines", type=int, default=2, required=False, help="搜索最小单元为多少行")

    args = parser.parse_args()

    # 1. 添加额外的文本文件后缀
    supported_exts = {".pdf", ".html", ".htm", ".txt", ".docx", ".doc"}
    for ext in args.add_ext.split("."):
        if ext:
            supported_exts.add(f".{ext}")


    # 2. 读取查询语句
    if args.query:
        query = args.query
    elif args.query_file:
        query = extract_text_from_file(args.query_file, supported_exts)
    else:
        query = ""

    if not query:
        print("❌ 查询文件为空")
        sys.exit(1)
    else:
        print(f"用户查询: {query}")

    # 3. 遍历 docs_dir 下的所有支持文档
    docs_dir = Path(args.docs_dir)
    
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"❌ 文档目录不存在或不是目录: {docs_dir}")
        sys.exit(1)

    documents = []
    documents_chunks = []
    chunk2filename_idx = []
    documents_paths = []
    fn_idx = 0
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    for ext in supported_exts:
        for filepath in docs_dir.rglob(f"*{ext}"):
            if filepath.is_file() and filepath.suffix.lower() in supported_exts:
                documents_paths.append(filepath.name)

                new_chunks = extract_text_from_file(filepath, supported_exts, keep_chunks=True)
                if new_chunks:
                    documents.append("\n".join(new_chunks))
                    new_chunks = subdivide_chunks(new_chunks, text_splitter)
                    documents_chunks += new_chunks
                    chunk2filename_idx += [fn_idx] * len(new_chunks)

                fn_idx += 1

    if not documents:
        print("❌ 未找到任何有效的文档（支持：PDF、HTML、TXT、DOCX）")
        sys.exit(1)

    print(f"✅ 成功加载 {len(documents)} 个文档")


    # 4. 构造请求
    URL = "http://127.0.0.1:5678"
    payload = {
        "model": "M",
        "query": query,
        "texts": True,
        "return_text": True,
        "top_n": args.top_n,
        "documents": documents_chunks
    }

    # 5. 发送请求
    try:
        response = requests.post(
            f"{URL}/v1/rerank",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        # 打印状态
        print(f"\n📊 Status Code: {response.status_code}")

        # 解析响应
        response_json = response.json()
        
        if "results" not in response_json:
            #print(json.dumps(response_json, indent=4, ensure_ascii=False))
            results = response_json
        else:
            results = response_json["results"]
        
        # 6. 按 score 排序（API返回的已经是排序好的，但保险起见）
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # 打印结果
        print(f"\n🏆 Reranked Results (Top {len(results)}):")
        print("-" * 80)
        
        for idx, result in enumerate(results[:args.top_n], start=1):  # 只显示前15个
            chunk_index = result.get("index", -1)
            score = result.get("score", 0.0)

            if chunk_index < len(chunk2filename_idx):
                filename = documents_paths[chunk2filename_idx[chunk_index]]
            else:
                filename = f"[未知文档_{chunk_index}]"

            print(f"{idx:2d}. {filename} (score: {score})")
            print(f"    内容: {documents_chunks[chunk_index]}")
            print()

        # 可选：输出完整结果（用于调试）
        print(f"\n🔍 完整响应:")
        print(json.dumps(response_json, indent=4, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ 响应不是合法 JSON:")
        print(response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()
