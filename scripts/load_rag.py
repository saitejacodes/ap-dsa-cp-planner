import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from rag.vectorstore import dsa_collection,math_collection
def load_rag():
    cf_res=requests.get("https://codeforces.com/api/problemset.problems").json()
    if cf_res["status"]=="OK":
        problems=cf_res["result"]["problems"][:50]
        docs=[]
        ids=[]
        for i,p in enumerate(problems):
            name=p.get("name","")
            topic=",".join(p.get("tags",[]))
            rating=p.get("rating",800)
            diff="Easy" if rating<1000 else ("Intermediate" if rating<=1400 else "Advanced")
            link=f"https://codeforces.com/problemset/problem/{p['contestId']}/{p['index']}"
            txt=f"Problem: {name}\nTopic: {topic}\nSheet: CF_All\nPlatform: CF\nDifficulty: {diff}\nRating: {rating}\nLink: {link}\nMath Prerequisites: None"
            docs.append(txt)
            ids.append(f"cf_{i}")
        if docs:
            dsa_collection.add(documents=docs,ids=ids)
    lc_docs=[
        "Problem: Two Sum\nTopic: Arrays\nSheet: NeetCode150\nPlatform: LC\nDifficulty: Easy\nRating: 800\nLink: https://leetcode.com/problems/two-sum\nMath Prerequisites: None",
        "Problem: Binary Search\nTopic: Binary Search\nSheet: NeetCode150\nPlatform: LC\nDifficulty: Easy\nRating: 800\nLink: https://leetcode.com/problems/binary-search\nMath Prerequisites: Monotonic functions",
        "Problem: Number of Islands\nTopic: Graphs\nSheet: NeetCode150\nPlatform: LC\nDifficulty: Medium\nRating: 1200\nLink: https://leetcode.com/problems/number-of-islands\nMath Prerequisites: Graph theory"
    ]
    dsa_collection.add(documents=lc_docs,ids=["lc_1","lc_2","lc_3"])
    math_docs=[
        "Dynamic Programming -> recursion, combinatorics, modular arithmetic",
        "Graph Algorithms -> graph theory, BFS/DFS, shortest paths",
        "Number Theory -> prime sieves, GCD/LCM, modular inverse",
        "Binary Search -> monotonic functions, basic math",
        "Segment Trees -> range queries, lazy propagation"
    ]
    math_collection.add(documents=math_docs,ids=[f"m_{i}" for i in range(len(math_docs))])
if __name__=="__main__":
    load_rag()
