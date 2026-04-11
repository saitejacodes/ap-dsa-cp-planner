import streamlit as st
from services.cf_fetcher import get_cf_user_info,get_cf_submissions,process_cf_data
from services.lc_fetcher import get_lc_data,process_lc_data
from services.weakness_detector import detect_weaknesses
from services.user_level_detector import get_user_level
from models.db import users_collection
st.set_page_config(page_title="Home - Onboarding",layout="wide")
st.title("User Onboarding")
cf_handle=st.text_input("Codeforces Handle",placeholder="e.g. tourist")
lc_user=st.text_input("LeetCode Username (optional)",placeholder="e.g. neal_wu")
platform_pref=st.selectbox("Preferred Practice Platform",["Any","LC","CF","CSES"],index=0)
if st.button("Analyze & Onboard",type="primary"):
    if cf_handle or lc_user:
        with st.spinner("Fetching submissions and analyzing weaknesses..."):
            cf_stats={}
            rating=800
            level="Beginner"
            solved_links=[]
            
            if cf_handle:
                cf_info=get_cf_user_info(cf_handle)
                rating=cf_info.get("rating",800) if cf_info else 800
                level=get_user_level(rating)
                cf_subs=get_cf_submissions(cf_handle)
                cf_stats=process_cf_data(cf_subs)
                for sub in cf_subs:
                    if sub.get("verdict")=="OK":
                        p=sub.get("problem",{})
                        cid=p.get("contestId")
                        idx=p.get("index")
                        if cid and idx:
                            solved_links.append(f"https://codeforces.com/problemset/problem/{cid}/{idx}")
                            
            lc_stats={}
            if lc_user:
                lc_raw=get_lc_data(lc_user)
                lc_stats=process_lc_data(lc_raw)
                
            weaknesses=detect_weaknesses(cf_stats,lc_stats)
            pref=None if platform_pref=="Any" else platform_pref
            
            user_id = cf_handle if cf_handle else lc_user
            
            user_doc={
                "userId":user_id,
                "cfHandle":cf_handle,
                "lcUsername":lc_user,
                "cfRating":rating,
                "level":level,
                "weaknesses":weaknesses,
                "solvedLinks":list(set(solved_links)),
                "platformPref":pref
            }
            users_collection.update_one({"userId":user_id},{"$set":user_doc},upsert=True)
            st.session_state["user_id"]=user_id
            
            if cf_handle:
                st.success(f"Onboarded! Detected Level: {level} | CF Rating: {rating}")
            else:
                st.success(f"Onboarded! Detected Level: {level}")
                
            weak_shown=[w for w in weaknesses if w["status"] in ["WEAK","UNTOUCHED"]][:5]
            if weak_shown:
                st.write("**Top weak topics:**")
                for w in weak_shown:
                    st.write(f"- {w['tag']} ({w['status']}) — {w.get('evidence','')}")
            st.info("Go to the Plan page to generate your 30-day schedule.")
    else:
        st.error("Please enter either a Codeforces handle or a LeetCode username.")
