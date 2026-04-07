import requests
def get_lc_data(username):
    url="https://leetcode.com/graphql"
    query="""
    {
      matchedUser(username: "%s") {
        tagProblemCounts {
          advanced { tagName problemsSolved }
          intermediate { tagName problemsSolved }
          fundamental { tagName problemsSolved }
        }
      }
    }
    """%username
    try:
        res=requests.post(url,json={"query":query}).json()
        return res.get("data",{}).get("matchedUser",{})
    except:
        return None
def process_lc_data(lc_user_data):
    topic_stats={}
    if not lc_user_data:
        return topic_stats
    tags=lc_user_data.get("tagProblemCounts",{})
    if not tags:
        return topic_stats
    for level in ["advanced","intermediate","fundamental"]:
        for t in tags.get(level,[]):
            tgt=t.get("tagName")
            if tgt not in topic_stats:
                topic_stats[tgt]={"attempted":t.get("problemsSolved",0),"solved":t.get("problemsSolved",0),"failed":0}
    return topic_stats

