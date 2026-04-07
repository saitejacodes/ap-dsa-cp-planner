import streamlit as st
from agents.planner_agent import build_plan,get_all_topics,normalize_tags
from models.db import plans_collection,users_collection
from services.progress_sync import sync_progress
st.set_page_config(page_title="My Plan",layout="wide")
st.title("30-Day Training Plan")
if not st.session_state.get("user_id"):
    st.warning("Please onboard first on the Home page.")
    st.stop()
user_id=st.session_state["user_id"]
user=users_collection.find_one({"userId":user_id})
if not user:
    st.error("User not found.")
    st.stop()
cf_rating=user.get("cfRating",800)
weaknesses=user.get("weaknesses",[])
if cf_rating>2000:
    weak_raw=[w["tag"] for w in weaknesses if w.get("success_rate",100)<40 or w.get("rate",1)<0.4]
else:
    weak_raw=[w["tag"] for w in weaknesses if w.get("status") in ["WEAK","UNTOUCHED"]]
ai_suggested=normalize_tags(weak_raw)
all_topics=get_all_topics()
default_vals=user.get("manual_weak_topics",ai_suggested)
selected_topics=st.multiselect(
    "Refine your weak topics (AI-detected defaults shown):",
    options=all_topics,
    default=default_vals if all(t in all_topics for t in default_vals) else []
)
col1,col2,col3=st.columns([2,1,1])
with col1:
    if st.button("Generate / Replan Schedule",type="primary"):
        users_collection.update_one({"userId":user_id},{"$set":{"manual_weak_topics":selected_topics}})
        prog_bar=st.progress(0)
        status_text=st.empty()
        def update_progress(pct):
            prog_bar.progress(pct)
            status_text.text(f"Processing topics... {pct}%")
        with st.spinner("Building RAG-powered plan..."):
            plan_data=build_plan(user_id,progress_callback=update_progress)
        prog_bar.progress(100)
        status_text.text("Done!")
        st.success(f"Plan generated — {len(plan_data.get('days',[]))} days scheduled.")
        st.rerun()
with col2:
    if st.button("Sync Progress",help="Fetches your latest CF and LC accepted submissions and auto-marks problems as completed."):
        with st.spinner("Syncing with Codeforces and LeetCode..."):
            new_count,total_count=sync_progress(user_id)
        if new_count>0:
            st.success(f"+{new_count} newly completed! ({total_count} total)")
        else:
            st.info(f"No new completions found. ({total_count} already done)")
        st.rerun()
plan=plans_collection.find_one({"userId":user_id})
with col3:
    if plan:
        st.metric("Level",plan.get("userLevel","—").capitalize())
        st.metric("CF Rating",plan.get("cfRating","—"))
if plan and plan.get("days"):
    days=plan["days"]
    total_problems=sum(len(d.get("problems",[])) for d in days)
    completed=sum(1 for d in days for p in d.get("problems",[]) if p.get("completed",False))
    if total_problems>0:
        st.progress(completed/total_problems,text=f"Completion: {completed}/{total_problems} problems done")
    st.write(f"**Goal:** {plan.get('weeklyGoal','—')} | **Total days:** {len(days)}")
    st.caption("Problems are marked as completed automatically when you sync. CSES problems require manual tick.")
    st.divider()
    widget_idx=0
    for day in days:
        topic=day.get("topic","")
        is_prereq=day.get("is_prereq",False)
        difficulty_focus=day.get("difficulty_focus","Medium")
        day_problems=day.get("problems",[])
        day_done=sum(1 for p in day_problems if p.get("completed",False))
        status_text="[DONE] " if day_done==len(day_problems) and day_problems else ""
        label=f"{status_text}Day {day.get('day')}: {topic.replace('_',' ').title()} [{difficulty_focus}]"
        if is_prereq:
            label+=" — Prerequisite"
        with st.expander(label):
            why=day.get("why","")
            if why:
                st.info(why)
            st.caption(f"Estimated time: {day.get('estimated_time','2 hours')}")
            if day_problems:
                for p in day_problems:
                    name=p.get("name","")
                    platform=p.get("platform","")
                    link=p.get("link","")
                    diff=p.get("difficulty","")
                    cf_r=p.get("cf_rating",0)
                    completed_flag=p.get("completed",False)
                    rating_str=f" | CF {cf_r}" if cf_r>0 else ""
                    if platform in ("CF","LC"):
                        status="[DONE] " if completed_flag else "[ ] "
                        st.markdown(f"{status}**[{platform}]** [{diff}{rating_str}] [{name}]({link})")
                    else:
                        key=f"prob_{widget_idx}"
                        widget_idx+=1
                        st.checkbox(f"[{platform}] [{diff}] {name}  →  {link}",value=completed_flag,key=key)
            else:
                st.caption("No problems assigned for this day.")
else:
    st.info("No plan yet. Click Generate above.")


