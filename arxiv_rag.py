import os
import sys
import json
import requests
import argparse
import pandas as pd

"""
All categories
'mathLO', 'physicsaoph', 'condmatsoft', 'condmatmtrlsci', 'mathST', 'eessSY', 'nuclth', 'econEM', 'csGT', 'compgas', 'csSE', 'csDB', 'csLO', 'mathSP', 'csMM', 'csSD', 'nuclex', 'mathCA', 'eessAS', 'mathMP', 'condmatstatmech', 'physicsedph', 'physicspopph', 'physicsappph', 'qfinPR', 'qbioTO', 'qfinRM', 'mathIT', 'physicsdataan', 'econGN', 'astrophCO', 'atomph', 'astrophEP', 'csCG', 'qfinCP', 'mathOC', 'mathFA', 'physicsaccph', 'eessIV', 'grqc', 'csOS', 'econTH', 'physicsatmclus', 'cmplg', 'aosci', 'condmatstrel', 'csCL', 'csCY', 'mathGN', 'qfinGN', 'qbioSC', 'csMS', 'csLG', 'condmatdisnn', 'csET', 'astrophHE', 'qbioGN', 'csAR', 'csDC', 'nlinCG', 'astrophIM', 'dgga', 'qalg', 'physicschemph', 'csPL', 'csOH', 'suprcon', 'physicsatomph', 'bayesan', 'mathAC', 'physicsgenph', 'csNE', 'astrophSR', 'qbio', 'csRO', 'csAI', 'mathDS', 'qbioCB', 'mathQA', 'nlinAO', 'nlinSI', 'condmatquantgas', 'csPF', 'physicsclassph', 'mathCT', 'mathAG', 'eessSP', 'statOT', 'qbioOT', 'physicsgeoph', 'condmatsuprcon', 'statCO', 'physicsfludyn', 'mathRA', 'qfinTR', 'mathCV', 'physicsmedph', 'mathNT', 'mathKT', 'csGR', 'condmatother', 'physicsplasmph', 'quantph', 'csCE', 'mathRT', 'csCC', 'mtrlth', 'adaporg', 'statTH', 'csSY', 'astroph', 'hepth', 'plasmph', 'csDL', 'nlinPS', 'csDM', 'chaodyn', 'astrophGA', 'nlinCD', 'hepph', 'mathAT', 'functan', 'mathNA', 'accphys', 'csNA', 'qbioMN', 'mathPR', 'qbioNC', 'physicsspaceph', 'heplat', 'csMA', 'mathGR', 'csIR', 'csIT', 'mathHO', 'alggeom', 'csNI', 'qfinPM', 'qbioBM', 'csSI', 'mathAP', 'physicshistph', 'solvint', 'physicsinsdet', 'statME', 'csCV', 'condmat', 'mathMG', 'physicscompph', 'qfinEC', 'mathGM', 'csHC', 'chemph', 'mathSG', 'qbioPE', 'mathph', 'mathGT', 'csCR', 'condmatmeshall', 'csFL', 'physicsoptics', 'mathDG', 'statAP', 'csGL', 'pattsol', 'csSC', 'csDS', 'hepex', 'qbioQM', 'qfinMF', 'mathCO', 'qfinST', 'mathOA', 'statML', 'physicssocph', 'physicsbioph'
"""

def main():
    parser = argparse.ArgumentParser(description="Rerank documents using local API")
    parser.add_argument("--arxivdb_file", default=r"E:\dataset\arxiv-csv.csv", type=str, help="arxiv DB(csv)")
    parser.add_argument("--url", default="http://127.0.0.1:6666", type=str, help="rerank server url")
    parser.add_argument("--query", type=str, help="查询语句字符串")
    parser.add_argument("--categories", nargs='+', default=['*'], type=str, help="查询语句字符串")
    parser.add_argument("--top_n", type=int, default=15, required=False, help="最佳匹配结果显示数量")

    args = parser.parse_args()


    # 1. 读取查询语句
    if args.query:
        query = args.query
    else:
        query = ""

    if not query:
        print("❌ 查询文件为空")
        sys.exit(1)
    else:
        print(f"用户查询: {query}")

    df = pd.read_csv(args.arxivdb_file)
    
    #category_series = df['Categories'].str.split(' ', expand=True).stack()
    #print('all categories', set(category_series))


    n_cat = len(args.categories)
    cat = args.categories

    assert n_cat >= 1
    if cat == ['*']:
        filtered_db = df
    else:
        mask = df['Categories'].str.contains(cat[0], na=False)
        if n_cat > 1:
            for i in range(1, len(cat)):
                mask |= df['Categories'].str.contains(cat[i], na=False)

    filtered_db = df[mask]
    print('Filtered db size (should be less than llama-server -b -ub)', len(filtered_db))
    db_strings = list(filtered_db['Title'].map(str) + "\n" + filtered_db['Abstract'])


    # 2. 构造请求
    payload = {
        "model": "M",
        "query": query,
        "texts": True,
        "return_text": True,
        "top_n": args.top_n,
        "documents": db_strings
    }

    # 3. 发送请求
    try:
        response = requests.post(
            f"{args.url}/v1/rerank",
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
        
        # 按 score 排序（API返回的已经是排序好的，但保险起见）
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # 打印结果
        print(f"\n🏆 Reranked Results (Top {len(results)}):")
        print("-" * 80)
        
        for idx, result in enumerate(results[:args.top_n], start=1):  # 只显示前15个
            chunk_index = result.get("index", -1)
            score = result.get("score", 0.0)


            print(f"{idx:2d}. (score: {score})")
            print(f"    内容: {db_strings[chunk_index]}")
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
