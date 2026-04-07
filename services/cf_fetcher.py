import requests
import time
def get_cf_user_info(handle):
    url=f"https://codeforces.com/api/user.info?handles={handle}"
    res=requests.get(url).json()
    if res["status"]=="OK":
        return res["result"][0]
    return None
def get_cf_submissions(handle):
    url=f"https://codeforces.com/api/user.status?handle={handle}"
    res=requests.get(url).json()
    time.sleep(1)
    if res["status"]=="OK":
        return res["result"]
    return []
def process_cf_data(submissions):
    topic_stats={}
    for sub in submissions:
        verdict=sub.get("verdict")
        problem=sub.get("problem",{})
        tags=problem.get("tags",[])
        for tag in tags:
            if tag not in topic_stats:
                topic_stats[tag]={"attempted":0,"solved":0,"failed":0}
            topic_stats[tag]["attempted"]+=1
            if verdict=="OK":
                topic_stats[tag]["solved"]+=1
            else:
                topic_stats[tag]["failed"]+=1
    return topic_stats


