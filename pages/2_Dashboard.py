import streamlit as st
import plotly.express as px
import pandas as pd
from models.db import users_collection
st.set_page_config(page_title="Dashboard",layout="wide")
st.title("Analytics Dashboard")
if not st.session_state.get("user_id"):
    st.warning("Please onboard through Home page first.")
    st.stop()
user=users_collection.find_one({"userId":st.session_state["user_id"]})
st.markdown(f"### Level: {user.get('level')} | CF Rating: {user.get('cfRating')}")
weaknesses=user.get("weaknesses",[])
if weaknesses:
    df=pd.DataFrame(weaknesses)
    fig1=px.bar(df,x="tag",y="rate",color="status",title="Strength per Topic (Success Rate)")
    st.plotly_chart(fig1,use_container_width=True)
    st.subheader("Top 5 Weaknesses")
    weak_only=[w for w in weaknesses if w["status"]=="WEAK"][:5]
    for w in weak_only:
        st.write(f"- **{w['tag']}**: {w['evidence']}")
else:
    st.info("No data available. Please re-onboard.")
if st.button("Generate My Plan"):
    st.info("Navigate to My Plan page to generate!")


