from rag.vectorstore import dsa_collection,math_collection
def get_rating_range(cf_rating):
    if cf_rating<1000:
        return (800,1200)
    if cf_rating<1400:
        return (1000,1600)
    if cf_rating<2000:
        return (1400,2000)
    if cf_rating<2400:
        return (1800,2400)
    return (2200,3500)
def _query_and_filter(topic,user_level,cf_rating,solved_links,platform_pref,r_low,r_high):
    q=f"{topic} {user_level}"
    try:
        res=dsa_collection.query(query_texts=[q],n_results=30)
    except Exception:
        return []
    if not res["documents"] or not res["documents"][0]:
        return []
    results=[]
    for i,doc in enumerate(res["documents"][0]):
        meta=res["metadatas"][0][i] if res.get("metadatas") else {}
        link=meta.get("link","")
        if not link:
            continue
        if link in solved_links:
            continue
        p_rating=meta.get("cf_rating",0)
        if p_rating>0 and not (r_low<=p_rating<=r_high):
            continue
        if platform_pref and meta.get("platform","")!=platform_pref:
            continue
        results.append({"name":meta.get("name",""),"sheet":meta.get("sheet",""),"platform":meta.get("platform",""),"link":link,"difficulty":meta.get("difficulty","Medium"),"cf_rating":p_rating,"completed":False})
    seen=set()
    deduped=[]
    for r in results:
        if r["link"] not in seen:
            seen.add(r["link"])
            deduped.append(r)
    deduped.sort(key=lambda x:abs(x["cf_rating"]-cf_rating))
    return deduped
def recommend_problems(topic,user_level,cf_rating,solved_links=None,platform_pref=None):
    if solved_links is None:
        solved_links=[]
    solved_set=set(solved_links)
    r_low,r_high=get_rating_range(cf_rating)
    results=_query_and_filter(topic,user_level,cf_rating,solved_set,platform_pref,r_low,r_high)
    if len(results)>=3:
        return results[:3]
    results=_query_and_filter(topic,user_level,cf_rating,solved_set,platform_pref,r_low-200,r_high+200)
    if len(results)>=3:
        return results[:3]
    results=_query_and_filter(topic,user_level,cf_rating,solved_set,None,r_low-200,r_high+200)
    if results:
        return results[:3]
    return [{"name":f"{topic.replace('_',' ')} practice","sheet":"CF","platform":"CF","link":"https://codeforces.com/problemset","difficulty":"Medium","cf_rating":cf_rating,"completed":False}]
def get_prerequisites(topic_name):
    try:
        res=math_collection.query(query_texts=[topic_name],n_results=1)
        if res["documents"] and len(res["documents"][0])>0:
            return res["documents"][0][0]
    except Exception:
        pass
    return "Basic math"


