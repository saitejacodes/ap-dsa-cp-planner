import streamlit as st
import time
from models.db import users_collection
from rag.vectorstore import math_collection
from agents.planner_agent import MATH_PREREQS,normalize_tags,TOPIC_LINKS,generate_quiz
st.set_page_config(page_title="Math Foundations",layout="wide")
st.title("Math Foundations")
if not st.session_state.get("user_id"):
    st.warning("Please onboard first.")
    st.stop()
user_id=st.session_state["user_id"]
user=users_collection.find_one({"userId":user_id})
if not user:
    st.error("User not found.")
    st.stop()
manual_weak=user.get("manual_weak_topics",[])
if not manual_weak:
    weaknesses=user.get("weaknesses",[])
    cf_rating=user.get("cfRating",800)
    if cf_rating>2000:
        weak_raw=[w["tag"] for w in weaknesses if w.get("success_rate",100)<40 or w.get("rate",1)<0.4]
    else:
        weak_raw=[w["tag"] for w in weaknesses if w.get("status") in ["WEAK","UNTOUCHED"]]
    weak_topics=normalize_tags(weak_raw)
else:
    weak_topics=manual_weak
if not weak_topics:
    st.info("No weak topics identified yet. Please go to the Plan page first.")
    st.stop()
completed_topics=user.get("completed_math_topics",{})
st.write(f"### Foundational Math & Concepts for your focus: **{', '.join([t.replace('_',' ') for t in weak_topics])}**")
st.divider()
for topic in weak_topics:
    label=f"Topic: {topic.replace('_',' ').title()}"
    status=completed_topics.get(topic,{})
    is_done=status.get("read",False) and status.get("quiz_passed",False)
    if is_done:
        label+=" [COMPLETE]"
    with st.expander(label,expanded=not is_done):
        col1,col2=st.columns([1,2])
        link=TOPIC_LINKS.get(topic,"https://cp-algorithms.com/")
        with col1:
            st.write("**Foundations**")
            prereqs=MATH_PREREQS.get(topic,[])
            for p in prereqs:
                st.markdown(f"- {p}")
            st.divider()
            read_btn=st.checkbox("I have read the external resource",value=status.get("read",False),key=f"read_{topic}")
            if read_btn!=status.get("read",False):
                completed_topics[topic]=completed_topics.get(topic,{})
                completed_topics[topic]["read"]=read_btn
                users_collection.update_one({"userId":user_id},{"$set":{"completed_math_topics":completed_topics}})
                st.rerun()
            st.link_button(f"Open Study Material for {topic.title()}",link)
        with col2:
            st.write("**Topic Mastery Quiz**")
            if status.get("quiz_passed",False):
                st.success("You passed the quiz for this topic!")
                if st.button(f"Retake Quiz for {topic}",key=f"retake_{topic}"):
                    completed_topics[topic]["quiz_passed"]=False
                    users_collection.update_one({"userId":user_id},{"$set":{"completed_math_topics":completed_topics}})
                    st.rerun()
            else:
                if f"quiz_data_{topic}" not in st.session_state:
                    if st.button(f"Generate Quiz for {topic}",key=f"gen_{topic}"):
                        with st.spinner("Generating 5 questions..."):
                            st.session_state[f"quiz_data_{topic}"]=generate_quiz(topic,user.get("level","advanced"))
                        st.rerun()
                else:
                    quiz=st.session_state[f"quiz_data_{topic}"]
                    if not quiz:
                        st.error("Failed to generate quiz. Try again.")
                        if st.button("Retry",key=f"retry_{topic}"):
                            del st.session_state[f"quiz_data_{topic}"]
                            st.rerun()
                    else:
                        correct_count=0
                        for idx,q in enumerate(quiz):
                            ans=st.radio(f"Q{idx+1}: {q['question']}",q['options'],key=f"q_{topic}_{idx}")
                            if ans==q['answer']:
                                correct_count+=1
                        if st.button(f"Submit Quiz for {topic}",key=f"submit_{topic}"):
                            if correct_count>=4:
                                st.success(f"Score: {correct_count}/5. You passed!")
                                completed_topics[topic]=completed_topics.get(topic,{})
                                completed_topics[topic]["quiz_passed"]=True
                                users_collection.update_one({"userId":user_id},{"$set":{"completed_math_topics":completed_topics}})
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Score: {correct_count}/5. Try again. You need at least 4/5 to pass.")
st.divider()
st.caption("Complete all foundations to unlock your practice plan effectively.")





