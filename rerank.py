import os
import sys
import json
import requests
from pathlib import Path
import argparse

# 文档文本提取函数
def extract_text_from_file(filepath):
    """根据文件扩展名，调用对应库提取文本"""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    try:
        if ext == ".pdf":
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        elif ext == ".html" or ext == ".htm":
            from bs4 import BeautifulSoup
            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "lxml")
                # 移除 script 和 style
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator="\n")
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\n".join(chunk for chunk in chunks if chunk)
                return text
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        elif ext == ".docx":
            from docx import Document
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        else:
            print(f"⚠️ 未知文件类型: {filepath.name}，跳过")
            return ""
    except Exception as e:
        print(f"❌ 读取 {filepath} 失败: {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="Rerank documents using local API")
    parser.add_argument("--docs_dir", required=True, help="目录路径，包含PDF、HTML、TXT、DOCX等文档")
    parser.add_argument("--query_file", required=True, help="包含查询语句的文本文件（一行一个或整个内容作为单条查询）")

    args = parser.parse_args()

    # 1. 读取查询语句
    with open(args.query_file, "r", encoding="utf-8") as f:
        query = f.read().strip()
    if not query:
        print("❌ 查询文件为空")
        sys.exit(1)
    else:
        print(f"用户查询: {query}")

    # 2. 遍历 docs_dir 下的所有支持文档
    supported_exts = {".pdf", ".html", ".htm", ".txt", ".docx"}
    docs_dir = Path(args.docs_dir)
    
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"❌ 文档目录不存在或不是目录: {docs_dir}")
        sys.exit(1)

    documents = []
    file_names = []

    for filepath in docs_dir.iterdir():
        if filepath.is_file() and filepath.suffix.lower() in supported_exts:
            text = extract_text_from_file(filepath)
            if text:  # 只保留非空文本
                documents.append(text)
                file_names.append(filepath.name)
    print('####################docs')
    print(documents)

    if not documents:
        print("❌ 未找到任何有效的文档（支持：PDF、HTML、TXT、DOCX）")
        sys.exit(1)

    print(f"✅ 成功加载 {len(documents)} 个文档")

    # 3. 构造请求
    URL = "http://127.0.0.1:5678"
    payload = {
        "model": "M",
        "query": query,
        "texts": False,
        "return_text": False,  # 不返回原文，只返回排序
        "top_n": len(documents),  # 可设为较小值，如10
        "documents": documents
    }

    # 4. 发送请求
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
        
        # 5. 按 relevance_score 排序（API返回的已经是排序好的，但保险起见）
        #results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # 打印结果
        print(f"\n🏆 Reranked Results (Top {len(results)}):")
        print("-" * 80)
        
        for idx, result in enumerate(results[:15], start=1):  # 只显示前15个
            doc_index = result.get("index", -1)
            score = result.get("relevance_score", 0.0)

            if doc_index < len(file_names):
                filename = file_names[doc_index]
            else:
                filename = f"[未知文档_{doc_index}]"

            print(f"{idx:2d}. {filename} (score: {score})")
            #print(f"文件内容:{documents[doc_index]}")

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
