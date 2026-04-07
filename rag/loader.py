import requests
import time
import hashlib
import re
from collections import defaultdict
from bs4 import BeautifulSoup
from rag.vectorstore import dsa_collection
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; DSAPlanner/1.0; +https://github.com/dsa-planner)"}
MAX_RETRIES=3
TIMEOUT=10
def safe_get(url,**kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            r=requests.get(url,headers=HEADERS,timeout=TIMEOUT,**kwargs)
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt==MAX_RETRIES-1:
                raise
            time.sleep(2**attempt)
def make_doc_text(name,sheet,topic,platform,difficulty,cf_rating,link,tags):
    return f"Problem: {name}\nSheet: {sheet}\nTopic: {topic}\nPlatform: {platform}\nDifficulty: {difficulty}\nCF Rating: {cf_rating}\nLink: {link}\nTags: {tags}"
def make_id(link,sheet):
    return hashlib.md5(f"{link}_{sheet}".encode()).hexdigest()
def upsert_problems(problems):
    if not problems:
        return
    batch_size=100
    ids=[p["id"] for p in problems]
    docs=[p["text"] for p in problems]
    metas=[p["metadata"] for p in problems]
    for i in range(0,len(problems),batch_size):
        dsa_collection.upsert(ids=ids[i:i+batch_size],documents=docs[i:i+batch_size],metadatas=metas[i:i+batch_size])
def load_neetcode150():
    sheet="NeetCode150"
    try:
        url="https://raw.githubusercontent.com/krmanik/Anki-NeetCode/main/neetcode-150-list.json"
        r=safe_get(url)
        data=r.json()
        problems=[]
        for category,prob_dict in data.items():
            if not isinstance(prob_dict,dict):
                continue
            for name,details in prob_dict.items():
                if not isinstance(details,dict):
                    continue
                link=details.get("url","")
                difficulty=details.get("difficulty","Medium")
                if not name or not link:
                    continue
                text=make_doc_text(name,sheet,category,"LC",difficulty,0,link,category)
                problems.append({"id":make_id(link,sheet),"text":text,"metadata":{"sheet":sheet,"topic":category,"platform":"LC","cf_rating":0,"difficulty":difficulty,"link":link,"name":name,"tags":category}})
        upsert_problems(problems)
        print(f"{sheet}: {len(problems)} loaded")
        return len(problems)
    except Exception as e:
        print(f"{sheet}: failed - {e}")
        return 0
def _parse_striver_primary(html):
    soup=BeautifulSoup(html,"html.parser")
    problems=[]
    seen=set()
    for a in soup.find_all("a",href=True):
        href=a.get("href","").strip()
        name=a.get_text(strip=True)
        if not name or not href or href in seen:
            continue
        if any(d in href for d in ["leetcode.com","geeksforgeeks.org","codeforces.com","takeuforward.org/data"]):
            seen.add(href)
            problems.append({"name":name,"link":href,"topic":"General"})
    return problems
def _parse_striver_fallback(md_text):
    problems=[]
    seen=set()
    for line in md_text.splitlines():
        urls=re.findall(r'https?://[^\s\)\]]+',line)
        names=re.findall(r'\[([^\]]+)\]',line)
        name=names[0] if names else "Unknown"
        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            problems.append({"name":name,"link":url,"topic":"General"})
    return problems
def load_striver_sde():
    sheet="StriverSDE"
    raw_problems=[]
    try:
        r=safe_get("https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/")
        raw_problems=_parse_striver_primary(r.text)
        if len(raw_problems)<10:
            raise Exception(f"only {len(raw_problems)} from primary")
        src="primary"
    except Exception as e:
        print(f"{sheet}: primary failed ({e}), trying fallback")
        try:
            r=safe_get("https://raw.githubusercontent.com/Tanmaygupta8503/strivers-sde-sheet-top-coding-interview-problems/main/README.md")
            raw_problems=_parse_striver_fallback(r.text)
            src="fallback"
        except Exception as e2:
            print(f"{sheet}: fallback failed - {e2}")
            return 0
    problems=[]
    for p in raw_problems:
        text=make_doc_text(p["name"],sheet,p["topic"],"LC","Medium",0,p["link"],"")
        problems.append({"id":make_id(p["link"],sheet),"text":text,"metadata":{"sheet":sheet,"topic":p["topic"],"platform":"LC","cf_rating":0,"difficulty":"Medium","link":p["link"],"name":p["name"],"tags":""}})
    upsert_problems(problems)
    print(f"{sheet}: {len(problems)} loaded ({src if 'src' in dir() else 'unknown'})")
    return len(problems)
def load_cses():
    sheet="CSES"
    try:
        r=safe_get("https://cses.fi/problemset/")
        soup=BeautifulSoup(r.text,"html.parser")
        problems=[]
        current_topic="General"
        for tag in soup.find_all(["h2","a"]):
            if tag.name=="h2":
                current_topic=tag.get_text(strip=True)
            elif tag.name=="a":
                href=tag.get("href","")
                if href.startswith("/problemset/task/"):
                    name=tag.get_text(strip=True)
                    link=f"https://cses.fi{href}"
                    text=make_doc_text(name,sheet,current_topic,"CSES","Medium",0,link,current_topic)
                    problems.append({"id":make_id(link,sheet),"text":text,"metadata":{"sheet":sheet,"topic":current_topic,"platform":"CSES","cf_rating":0,"difficulty":"Medium","link":link,"name":name,"tags":current_topic}})
        upsert_problems(problems)
        print(f"{sheet}: {len(problems)} loaded")
        return len(problems)
    except Exception as e:
        print(f"{sheet}: failed - {e}")
        return 0
def _fetch_cf_api():
    r=safe_get("https://codeforces.com/api/problemset.problems")
    data=r.json()
    if data.get("status")!="OK":
        raise Exception("CF API returned non-OK status")
    problems_raw=data["result"]["problems"]
    stats_map={(s["contestId"],s["index"]):s["solvedCount"] for s in data["result"]["problemStatistics"]}
    return problems_raw,stats_map
def _cf_problem_to_doc(p,solved,sheet):
    name=p.get("name","")
    rating=p.get("rating",0)
    tags=p.get("tags",[])
    cid=p.get("contestId")
    idx=p.get("index")
    if not cid or not idx:
        return None
    link=f"https://codeforces.com/problemset/problem/{cid}/{idx}"
    topic=tags[0] if tags else "general"
    diff=str(rating) if rating else "Unrated"
    text=make_doc_text(name,sheet,topic,"CF",diff,rating,link,", ".join(tags))
    return {"id":make_id(link,sheet),"text":text,"metadata":{"sheet":sheet,"topic":topic,"platform":"CF","cf_rating":int(rating),"difficulty":diff,"link":link,"name":name,"tags":", ".join(tags),"solved_count":int(solved)}}
def load_cp31():
    sheet="CP31"
    try:
        problems_raw,stats_map=_fetch_cf_api()
        filtered=[]
        for p in problems_raw:
            rating=p.get("rating",0)
            tags=p.get("tags",[])
            key=(p.get("contestId"),p.get("index"))
            solved=stats_map.get(key,0)
            if 800<=rating<=1600 and solved>1000 and len(tags)>=1:
                filtered.append({**p,"_solved":solved})
        buckets=defaultdict(list)
        for p in filtered:
            buckets[p.get("rating")].append(p)
        selected=[]
        for rating,probs in buckets.items():
            probs_sorted=sorted(probs,key=lambda x:x["_solved"],reverse=True)
            selected.extend(probs_sorted[:31])
        problems=[]
        for p in selected:
            doc=_cf_problem_to_doc(p,p.get("_solved",0),sheet)
            if doc:
                problems.append(doc)
        upsert_problems(problems)
        print(f"{sheet}: {len(problems)} loaded")
        return len(problems)
    except Exception as e:
        print(f"{sheet}: failed - {e}")
        return 0
def load_codeforces_full():
    sheet="Codeforces"
    try:
        problems_raw,stats_map=_fetch_cf_api()
        problems=[]
        for p in problems_raw:
            key=(p.get("contestId"),p.get("index"))
            solved=stats_map.get(key,0)
            doc=_cf_problem_to_doc(p,solved,sheet)
            if doc:
                problems.append(doc)
        upsert_problems(problems)
        print(f"{sheet}: {len(problems)} loaded")
        return len(problems)
    except Exception as e:
        print(f"{sheet}: failed - {e}")
        return 0
def run_all_loaders():
    total=0
    total+=load_neetcode150()
    total+=load_striver_sde()
    total+=load_cses()
    total+=load_cp31()
    total+=load_codeforces_full()
    print(f"Total: {total} problems")
    return total
