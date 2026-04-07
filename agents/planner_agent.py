import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from models.db import users_collection,plans_collection
from rag.query_rag import recommend_problems
load_dotenv()
TOPIC_GRAPH={
    "arrays":[],
    "math_basics":[],
    "recursion":["arrays"],
    "binary_search":["arrays","math_basics"],
    "two_pointers":["arrays"],
    "sliding_window":["two_pointers"],
    "sorting":["arrays"],
    "greedy":["sorting"],
    "linked_list":["arrays"],
    "stack_queue":["arrays"],
    "hashing":["arrays"],
    "bfs_dfs":["recursion"],
    "graphs":["bfs_dfs","hashing"],
    "trees":["recursion","bfs_dfs"],
    "binary_search_trees":["trees","binary_search"],
    "dp_1d":["recursion","math_basics"],
    "dp_2d":["dp_1d"],
    "dp_advanced":["dp_2d","greedy"],
    "number_theory":["math_basics"],
    "segment_trees":["trees","arrays"],
    "advanced_graphs":["graphs","dp_1d"],
    "bit_manipulation":["math_basics"]
}
def get_all_topics():
    return sorted(list(TOPIC_GRAPH.keys()))
CF_TAG_TO_GRAPH={
    "graphs":"graphs","graph matchings":"advanced_graphs","flows":"advanced_graphs",
    "shortest paths":"advanced_graphs","dp":"dp_1d","dynamic programming":"dp_1d",
    "dsu":"graphs","dfs and similar":"bfs_dfs","trees":"trees","math":"math_basics",
    "number theory":"number_theory","binary search":"binary_search",
    "two pointers":"two_pointers","sortings":"sorting","greedy":"greedy",
    "strings":"hashing","hashing":"hashing","bitmasks":"bit_manipulation",
    "bit manipulation":"bit_manipulation","combinatorics":"math_basics",
    "divide and conquer":"recursion","recursion":"recursion",
    "implementation":"arrays","brute force":"arrays","data structures":"segment_trees",
    "segment tree":"segment_trees","stack":"stack_queue","queue":"stack_queue",
    "linked list":"linked_list","sliding window":"sliding_window",
    "interactive":"graphs","constructive algorithms":"greedy","games":"dp_1d",
    "probabilities":"math_basics","matrices":"dp_2d","geometry":"math_basics",
    "string suffix structures":"hashing","expression parsing":"hashing",
    "2-sat":"advanced_graphs","meet-in-the-middle":"dp_advanced",
    "ternary search":"binary_search","*special":"arrays"
}
MATH_PREREQS={
    "arrays":["basic indexing","iteration"],
    "math_basics":["arithmetic","modular arithmetic"],
    "recursion":["function calls","base cases"],
    "binary_search":["monotonic functions","sorted arrays"],
    "two_pointers":["array traversal"],
    "sliding_window":["window invariants"],
    "sorting":["comparisons","swap operations"],
    "greedy":["proof by exchange argument"],
    "linked_list":["pointers","memory"],
    "stack_queue":["LIFO FIFO concepts"],
    "hashing":["hash functions","collision"],
    "bfs_dfs":["graph theory","queue stack"],
    "graphs":["adjacency list","edge traversal"],
    "trees":["recursion","parent child"],
    "binary_search_trees":["BST property","in-order traversal"],
    "dp_1d":["recurrence relations","memoization"],
    "dp_2d":["2D recurrence","tabulation"],
    "dp_advanced":["optimization","greedy extension"],
    "number_theory":["prime sieves","GCD LCM","modular inverse"],
    "segment_trees":["range queries","lazy propagation"],
    "advanced_graphs":["Dijkstra","Bellman-Ford","SCC"],
    "bit_manipulation":["binary number system","XOR properties"]
}
TOPIC_LINKS={
    "arrays":"https://www.geeksforgeeks.org/array-data-structure/",
    "math_basics":"https://cp-algorithms.com/algebra/binary-exp.html",
    "recursion":"https://www.freecodecamp.org/news/recursion-in-python-with-examples/",
    "binary_search":"https://cp-algorithms.com/num_methods/binary_search.html",
    "two_pointers":"https://leetcode.com/discuss/study-guide/1688903/Solved-all-two-pointers-problems-in-1-month",
    "sliding_window":"https://stackoverflow.com/questions/8269916/what-is-sliding-window-algorithm-examples",
    "sorting":"https://www.geeksforgeeks.org/sorting-algorithms/",
    "greedy":"https://cp-algorithms.com/geometry/convex-hull.html",
    "linked_list":"https://www.tutorialspoint.com/data_structures_algorithms/linked_list_algorithms.htm",
    "stack_queue":"https://www.programiz.com/dsa/stack",
    "hashing":"https://cp-algorithms.com/string/string-hashing.html",
    "bfs_dfs":"https://paltas.org/graph-traversal-bfs-dfs/",
    "graphs":"https://cp-algorithms.com/graph/breadth-first-search.html",
    "trees":"https://www.geeksforgeeks.org/binary-tree-data-structure/",
    "binary_search_trees":"https://algorithms.tutorialhorizon.com/introduction-to-binary-search-tree/",
    "dp_1d":"https://leetcode.com/discuss/study-guide/458695/Dynamic-Programming-Patterns",
    "dp_2d":"https://www.geeksforgeeks.org/longest-common-subsequence-dp-4/",
    "dp_advanced":"https://cp-algorithms.com/dynamic_programming/profile-dynamic-programming.html",
    "number_theory":"https://cp-algorithms.com/algebra/sieve-of-eratosthenes.html",
    "segment_trees":"https://cp-algorithms.com/data_structures/segment_tree.html",
    "advanced_graphs":"https://cp-algorithms.com/graph/dijkstra.html",
    "bit_manipulation":"https://graphics.stanford.edu/~seander/bithacks.html"
}
BASIC_TOPICS={"arrays","math_basics","recursion","sorting","two_pointers","linked_list","stack_queue"}
DIFFICULTY_PROGRESSION={
    "beginner":{"early":"Easy","mid":"Easy","late":"Medium"},
    "intermediate":{"early":"Easy","mid":"Medium","late":"Medium"},
    "advanced":{"early":"Medium","mid":"Medium","late":"Hard"}
}
DAYS_PER_TOPIC={"beginner":2,"intermediate":3,"advanced":4}
def normalize_tags(cf_tags):
    result=set()
    for tag in cf_tags:
        key=CF_TAG_TO_GRAPH.get(tag.lower())
        if key:
            result.add(key)
    return list(result)
def get_learning_order(weak_topics):
    needed=set()
    def add_prereqs(topic):
        for prereq in TOPIC_GRAPH.get(topic,[]):
            needed.add(prereq)
            add_prereqs(prereq)
    for topic in weak_topics:
        needed.add(topic)
        add_prereqs(topic)
    visited=set()
    order=[]
    def dfs(topic):
        if topic in visited:
            return
        visited.add(topic)
        for prereq in TOPIC_GRAPH.get(topic,[]):
            dfs(prereq)
        order.append(topic)
    for topic in needed:
        dfs(topic)
    return order
def get_phase(index,total):
    pct=index/total if total>0 else 0
    if pct<0.4:
        return "early"
    if pct<0.8:
        return "mid"
    return "late"
def get_difficulty_focus(user_level,phase):
    prog=DIFFICULTY_PROGRESSION.get(user_level.lower(),DIFFICULTY_PROGRESSION["intermediate"])
    return prog.get(phase,"Medium")
def generate_why(topic,user_level,cf_rating,llm,cache):
    key=f"{topic}_{user_level}_{cf_rating}"
    if key in cache:
        return cache[key]
    try:
        prompt=f"In max 15 words, one sentence, no markdown: why should a {user_level} programmer with CF rating {cf_rating} study {topic.replace('_',' ')}?"
        res=llm.invoke(prompt)
        why=res.content.strip().replace("\n"," ")
        words=why.split()
        if len(words)>15:
            why=" ".join(words[:15])
        cache[key]=why
    except Exception:
        cache[key]=f"Study {topic.replace('_',' ')} to strengthen your competitive programming foundation."
    return cache[key]
def generate_quiz(topic,user_level):
    llm=ChatGroq(model="llama-3.3-70b-versatile",api_key=os.getenv("GROQ_API_KEY"))
    prompt=f"Generate 5 medium-to-hard multiple choice questions about {topic.replace('_',' ')} for a {user_level} programmer. Format as JSON list of objects: 'question', 'options' (list of 4), 'answer' (exact string from options). No markdown, no filler."
    try:
        res=llm.invoke(prompt)
        import json,re
        clean=re.sub(r'```json|```','',res.content).strip()
        return json.loads(clean)
    except Exception:
        return []
def score_plan(plan_days,weak_topics,solved_links,user_cf_rating):
    score=0
    weak_set=set(weak_topics)
    for day in plan_days:
        for p in day.get("problems",[]):
            link=p.get("link","")
            if link in solved_links:
                score-=2
            else:
                score+=1
            if day.get("topic") in weak_set:
                score+=3
            p_rating=p.get("cf_rating",0)
            if p_rating>0 and abs(p_rating-user_cf_rating)<=200:
                score+=2
    return score
def _build_days(order,weak_topics,cf_rating,user_level,solved_links,platform_pref,llm,why_cache):
    base_days=DAYS_PER_TOPIC.get(user_level.lower(),3)
    total=len(order)
    plan_days=[]
    day=1
    used_problems=set()
    for i,topic in enumerate(order):
        if day>30:
            break
        is_prereq=topic not in weak_topics
        prereq_count=len(TOPIC_GRAPH.get(topic,[]))
        days_for_topic=base_days+(1 if prereq_count>0 and is_prereq else 0)
        phase=get_phase(i,total)
        difficulty_focus=get_difficulty_focus(user_level,phase)
        why=generate_why(topic,user_level,cf_rating,llm,why_cache)
        time.sleep(0.3)
        for d in range(days_for_topic):
            if day>30:
                break
            
            # Fetch 3 unique problems specifically for THIS individual day
            raw=recommend_problems(topic,user_level,cf_rating,list(solved_links|used_problems),platform_pref)
            day_problems=[]
            for p in raw:
                link=p.get("link","")
                if link in used_problems or link in solved_links:
                    continue
                p_rating=p.get("cf_rating",0)
                if p_rating>0 and p_rating<cf_rating-300:
                    continue
                used_problems.add(link)
                p["difficulty"]=difficulty_focus
                p["completed"]=False
                day_problems.append(p)
                if len(day_problems)>=3:
                    break

            plan_days.append({
                "day":day,
                "topic":topic,
                "why":why,
                "is_prereq":is_prereq,
                "math_prereqs":MATH_PREREQS.get(topic,[]),
                "difficulty_focus":difficulty_focus,
                "problems":day_problems,
                "estimated_time":"2 hours"
            })
            day+=1

    return plan_days
def build_plan(user_id,progress_callback=None):
    user=users_collection.find_one({"userId":user_id})
    if not user:
        return {"userId":user_id,"days":[]}
    cf_rating=user.get("cfRating",800)
    user_level=user.get("level","beginner").lower()
    solved_links=set(user.get("solvedLinks",[]))
    platform_pref=user.get("platformPref",None)
    weaknesses=user.get("weaknesses",[])
    weak_topics=user.get("manual_weak_topics",[])
    if not weak_topics:
        if cf_rating>2000:
            weak_raw=[w["tag"] for w in weaknesses if w.get("success_rate",100)<40 or w.get("rate",1)<0.4]
        else:
            weak_raw=[w["tag"] for w in weaknesses if w.get("status") in ["WEAK","UNTOUCHED"]]
        weak_topics=normalize_tags(weak_raw)
    if not weak_topics:
        weak_topics=["graphs","binary_search","dp_1d"]
    order=get_learning_order(weak_topics)
    if cf_rating>1400:
        order=[t for t in order if t not in BASIC_TOPICS or t in set(weak_topics)]
    if not order:
        order=list(weak_topics)
    llm=ChatGroq(model="llama-3.3-70b-versatile",api_key=os.getenv("GROQ_API_KEY"))
    why_cache={}
    total_topics=len(order)
    def progress_wrap(i):
        if progress_callback:
            progress_callback(int(((i+1)/total_topics)*100))
    plan_days=_build_days(order,set(weak_topics),cf_rating,user_level,solved_links,platform_pref,llm,why_cache)
    for i in range(total_topics):
        progress_wrap(i)
    score=score_plan(plan_days,weak_topics,solved_links,cf_rating)
    if score<50:
        plan_days=_build_days(order,set(weak_topics),cf_rating,user_level,solved_links,None,llm,why_cache)
    plan_doc={
        "userId":user_id,
        "generatedAt":time.strftime("%Y-%m-%d"),
        "userLevel":user_level,
        "cfRating":cf_rating,
        "weeklyGoal":f"Master {', '.join([t.replace('_',' ') for t in weak_topics[:3]])}",
        "completionRate":0.0,
        "days":plan_days
    }
    plans_collection.update_one({"userId":user_id},{"$set":plan_doc},upsert=True)
    return plan_doc







