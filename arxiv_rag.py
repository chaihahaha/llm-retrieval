import os
import sys
import json
import requests
import argparse
import pandas as pd

"""
All categories
{
  "physics": {
    "physicsaoph": "Atmospheric and Oceanic Physics",
    "physicsedph": "physics education",
    "physicspopph": "physics popular physics",
    "physicsappph": "physics applied physics",
    "physicsdataan": "physics Data Analysis, Statistics and Probability",
    "physicsaccph": "physics accelerator physics",
    "physicsatmclus": "physics atomic and molecular clusters",
    "physicschemph": "physics chemical physics",
    "physicsatomph": "physics atomic physics",
    "physicsgenph": "physics general physics",
    "physicsclassph": "physics classical physics",
    "physicsgeoph": "physics geophysics",
    "physicsfludyn": "physics fluid dynamics",
    "physicsmedph": "physics medical physics",
    "physicsplasmph": "physics plasma physics",
    "physicsspaceph": "physics space physics",
    "physicshistph": "physics history and philosophy of physics",
    "physicsinsdet": "physics instrumentation and detectors",
    "physicscompph": "physics computational physics",
    "physicsoptics": "physics optics",
    "physicssocph": "physics social and behavioral physics",
    "physicsbioph": "physics biological physics",
    "atomph": "atomic physics",
    "accphys": "accelerator physics",
    "plasmph": "plasma physics",
    "quantph": "quantum physics",
    "grqc": "general relativity and quantum cosmology",
    "nuclth": "nuclear theory",
    "nuclex": "nuclear experiment",
    "hepth": "high energy physics theory",
    "hepph": "high energy physics phenomenology",
    "heplat": "high energy physics lattice",
    "hepex": "high energy physics experiment",
    "astroph": "astrophysics",
    "astrophCO": "astrophysics cosmology and nongalactic astrophysics",
    "astrophEP": "astrophysics high energy astrophysical phenomena",
    "astrophHE": "astrophysics high energy astrophysical phenomena",
    "astrophIM": "astrophysics instrumentation and methods",
    "astrophSR": "astrophysics solar and stellar astrophysics",
    "astrophGA": "astrophysics galactic astrophysics"
    "compgas": "computing and gas dynamics",
  },
  "math": {
    "mathLO": "mathematics logic",
    "mathST": "mathematics statistics",
    "mathSP": "mathematics spectral theory",
    "mathCA": "mathematics classical analysis and odes",
    "mathMP": "mathematics mathematical physics",
    "mathIT": "mathematics information theory",
    "mathOC": "mathematics optimization and control",
    "mathFA": "mathematics functional analysis",
    "mathGN": "mathematics general topology",
    "mathAC": "mathematics Commutative Algebra",
    "mathDS": "mathematics dynamical systems",
    "mathQA": "mathematics quantum algebra",
    "mathCT": "mathematics category theory",
    "mathAG": "mathematics algebraic geometry",
    "mathRA": "mathematics Rings and Algebras",
    "mathCV": "mathematics complex variables",
    "mathNT": "mathematics number theory",
    "mathKT": "mathematics K-Theory and Homology",
    "mathRT": "mathematics representation theory",
    "mathAT": "mathematics algebraic topology",
    "mathNA": "mathematics numerical analysis",
    "mathPR": "mathematics probability",
    "mathGR": "mathematics Group Theory",
    "mathHO": "mathematics history and overview",
    "mathAP": "mathematics analysis of pdes",
    "mathMG": "mathematics metric geometry",
    "mathGM": "mathematics General Mathematics",
    "mathSG": "mathematics symplectic geometry",
    "mathGT": "mathematics geometric topology",
    "mathDG": "mathematics differential geometry",
    "mathCO": "mathematics combinatorics",
    "mathOA": "mathematics operator algebras",
    "dgga": "differential geometry and global analysis",
    "qalg": "quantum algebra",
    "functan": "functional analysis",
    "alggeom": "algebraic geometry",
    "mathph": "mathematical physics"
  },
  "computer science": {
    "csGT": "computer science game theory",
    "csSE": "computer science software engineering",
    "csDB": "computer science databases",
    "csLO": "computer science logic",
    "csMM": "computer science multimedia",
    "csSD": "computer science sound",
    "csCG": "computer science computational geometry",
    "csOS": "computer science operating systems",
    "csCL": "computer science computation and language",
    "csCY": "computer science computers and society",
    "csMS": "computer science Mathematical Software",
    "csLG": "computer science Machine Learning",
    "csET": "computer science emerging technologies",
    "csAR": "computer science Hardware Architecture",
    "csDC": "computer science Distributed, Parallel, and Cluster Computing",
    "csPL": "computer science programming languages",
    "csOH": "computer science other computer science",
    "csNE": "computer science neural and evolutionary computing",
    "csRO": "computer science robotics",
    "csAI": "computer science artificial intelligence",
    "csPF": "computer science performance",
    "csGR": "computer science graphics",
    "csCE": "computer science Computational Engineering, Finance, and Science",
    "csCC": "computer science computational complexity",
    "csSY": "computer science systems and control",
    "csDL": "computer science Digital Libraries",
    "csDM": "computer science discrete mathematics",
    "csNA": "computer science numerical analysis",
    "csMA": "computer science multiagent systems",
    "csIR": "computer science information retrieval",
    "csIT": "computer science information theory",
    "csNI": "computer science networking and internet architecture",
    "csSI": "computer science social and information networks",
    "csCV": "computer science computer vision and pattern recognition",
    "csHC": "computer science human-computer interaction",
    "csCR": "computer science cryptology and security",
    "csFL": "computer science formal languages and automata theory",
    "csGL": "computer science General Literature",
    "csSC": "computer science Symbolic Computation",
    "csDS": "computer science data structures and algorithms",
    "cmplg": "computing and logic",
    "aosci": "applied physics and scientific computing"
  },
  "chemistry": {
    "chemph": "chemical physics"
  },
  "biology": {
    "qbioTO": "quantitative biology Tissues and Organs",
    "qbioSC": "quantitative biology Subcellular Processes",
    "qbioGN": "quantitative biology Genomics",
    "qbio": "quantitative biology",
    "qbioCB": "quantitative biology cell behavior",
    "qbioOT": "quantitative biology other quantitative biology",
    "qbioMN": "quantitative biology molecular networks",
    "qbioNC": "quantitative biology Neurons and Cognition",
    "qbioBM": "quantitative biology Biomolecules",
    "qbioPE": "quantitative biology population and evolution",
    "qbioQM": "quantitative biology quantitative methods"
  },
  "condensed matter": {
    "condmatsoft": "condensed matter soft materials",
    "condmatmtrlsci": "condensed matter material science",
    "condmatstatmech": "condensed matter statistical mechanics",
    "condmatstrel": "condensed matter Strongly Correlated Electrons",
    "condmatdisnn": "condensed matter disordered systems and neural networks",
    "condmatquantgas": "condensed matter quantum gases",
    "condmatsuprcon": "condensed matter superconductivity",
    "condmatother": "condensed matter other",
    "condmat": "condensed matter",
    "condmatmeshall": "condensed matter Mesoscale and Nanoscale Physics",
    "suprcon": "superconductivity",
    "mtrlth": "material theory",
  },
  "economics": {
    "econEM": "economics econometrics",
    "econGN": "economics General Economics",
    "econTH": "economics theory"
  },
  "electrical engineering": {
    "eessSY": "electrical engineering systems and control",
    "eessAS": "electrical engineering audio and speech processing",
    "eessIV": "electrical engineering image and video processing",
    "eessSP": "electrical engineering signal processing"
  },
  "quantitative finance": {
    "qfinPR": "quantitative finance pricing of securities",
    "qfinRM": "quantitative finance risk management",
    "qfinCP": "quantitative finance Computational Finance",
    "qfinGN": "quantitative finance General Finance",
    "qfinTR": "quantitative finance trading and market microstructure",
    "qfinPM": "quantitative finance portfolio management",
    "qfinEC": "quantitative finance economics",
    "qfinMF": "quantitative finance Mathematical Finance",
    "qfinST": "quantitative finance statistical finance"
  },
  "statistics": {
    "statOT": "statistics other statistics",
    "statCO": "statistics Computation",
    "statTH": "statistics theory",
    "statME": "statistics machine learning",
    "statAP": "statistics applied statistics",
    "statML": "statistics machine learning",
    "bayesan": "Bayesian analysis"
  },
  "nonlinear sciences": {
    "nlinCG": "nonlinear sciences Cellular Automata and Lattice Gases",
    "nlinAO": "nonlinear sciences adaptation and self-organization",
    "nlinSI": "Nonlinear Sciences Exactly Solvable and Integrable Systems",
    "solvint": "Nonlinear Sciences Exactly Solvable and Integrable Systems"
    "nlinPS": "nonlinear sciences Pattern Formation and Solitons",
    "nlinCD": "nonlinear sciences Chaotic Dynamics",
    "chaodyn": "chaos dynamics",
    "pattsol": "pattern formation and solitons",
    "adaporg": "adaptive organization systems"
  }
}

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
