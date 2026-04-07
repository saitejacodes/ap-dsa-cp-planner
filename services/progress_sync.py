import requests
from models.db import users_collection,plans_collection
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; DSAPlanner/1.0)"}
def get_cf_solved_links(cf_handle):
    try:
        url=f"https://codeforces.com/api/user.status?handle={cf_handle}"
        res=requests.get(url,headers=HEADERS,timeout=10).json()
        if res.get("status")!="OK":
            return set()
        solved=set()
        for sub in res["result"]:
            if sub.get("verdict")=="OK":
                p=sub.get("problem",{})
                cid=p.get("contestId")
                idx=p.get("index")
                if cid and idx:
                    solved.add(f"https://codeforces.com/problemset/problem/{cid}/{idx}")
        return solved
    except Exception:
        return set()
def get_lc_solved_slugs(lc_username):
    try:
        url="https://leetcode.com/graphql"
        query='{ recentAcSubmissionList(username: "%s", limit: 100) { titleSlug } }' % lc_username
        res=requests.post(url,json={"query":query},headers=HEADERS,timeout=10).json()
        submissions=res.get("data",{}).get("recentAcSubmissionList",[]) or []
        return {s["titleSlug"] for s in submissions}
    except Exception:
        return set()
def extract_lc_slug(link):
    link=link.rstrip("/")
    parts=link.split("/")
    try:
        idx=parts.index("problems")
        return parts[idx+1]
    except (ValueError,IndexError):
        return None
def sync_progress(user_id):
    user=users_collection.find_one({"userId":user_id})
    if not user:
        return 0,0
    cf_handle=user.get("cfHandle","")
    lc_username=user.get("lcUsername","")
    cf_solved=get_cf_solved_links(cf_handle) if cf_handle else set()
    lc_solved=get_lc_solved_slugs(lc_username) if lc_username else set()
    plan=plans_collection.find_one({"userId":user_id})
    if not plan or not plan.get("days"):
        return 0,0
    days=plan["days"]
    newly_completed=0
    total_completed=0
    changed=False
    for day in days:
        for p in day.get("problems",[]):
            link=p.get("link","")
            platform=p.get("platform","")
            was_completed=p.get("completed",False)
            now_completed=False
            if platform=="CF":
                now_completed=link in cf_solved
            elif platform=="LC":
                slug=extract_lc_slug(link)
                now_completed=(slug in lc_solved) if slug else False
            if not was_completed and now_completed:
                newly_completed+=1
                changed=True
            if now_completed:
                total_completed+=1
            p["completed"]=now_completed
    if changed:
        plans_collection.update_one({"userId":user_id},{"$set":{"days":days}})
    return newly_completed,total_completed
