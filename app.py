import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
st.write("Current Directory:", os.getcwd())
st.write("Database Exists:", os.path.exists("Database/student.db"))

# Database Connection
conn = sqlite3.connect("Database/student.db")

# Data Load
df = pd.read_sql("SELECT * FROM students", conn)

st.set_page_config(page_title="Student Performance Analytics",
                   page_icon="📊",
                   layout="wide")

st.title("📊 Student Performance Analytics Dashboard")
st.caption("SQLite + Pandas + Streamlit")

DB_PATH = os.path.join("Database", "student.db")

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM students", conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

st.sidebar.header("Filters")

school = st.sidebar.selectbox("School", ["All"] + sorted(df["school"].unique().tolist()))
gender = st.sidebar.selectbox("Gender", ["All"] + sorted(df["sex"].unique().tolist()))
study = st.sidebar.selectbox("Study Time", ["All"] + sorted(df["studytime"].unique().tolist()))

filtered = df.copy()
if school != "All":
    filtered = filtered[filtered["school"] == school]
if gender != "All":
    filtered = filtered[filtered["sex"] == gender]
if study != "All":
    filtered = filtered[filtered["studytime"] == study]

c1,c2,c3,c4 = st.columns(4)
c1.metric("Students", len(filtered))
c2.metric("Average Grade", round(filtered.G3.mean(),2))
c3.metric("Highest Grade", int(filtered.G3.max()))
c4.metric("Average Absences", round(filtered.absences.mean(),2))

st.divider()

st.subheader("Top 10 Students")
st.dataframe(filtered.sort_values("G3",ascending=False)[["school","sex","studytime","failures","absences","G3"]].head(10),use_container_width=True)

def bar(groupcol,title,xlabel):
    d=filtered.groupby(groupcol)["G3"].mean().reset_index()
    fig,ax=plt.subplots()
    ax.bar(d[groupcol].astype(str),d["G3"])
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Average G3")
    st.pyplot(fig)

bar("studytime","Study Time vs Grade","Study Time")

st.subheader("Absences vs Grade")
fig,ax=plt.subplots()
ax.scatter(filtered["absences"],filtered["G3"])
ax.set_xlabel("Absences")
ax.set_ylabel("G3")
st.pyplot(fig)

bar("failures","Failures vs Grade","Failures")
bar("sex","Gender Performance","Gender")
bar("school","School Performance","School")
bar("Medu","Mother Education Impact","Medu")
if "Fedu" in filtered.columns:
    bar("Fedu","Father Education Impact","Fedu")
bar("internet","Internet Access Impact","Internet")
if "Walc" in filtered.columns:
    bar("Walc","Weekend Alcohol Impact","Walc")
if "Dalc" in filtered.columns:
    bar("Dalc","Weekday Alcohol Impact","Dalc")

st.subheader("At-Risk Students")
risk=filtered[(filtered["G3"]<10)|(filtered["failures"]>0)|(filtered["absences"]>10)]
st.warning(f"Total At-Risk Students: {len(risk)}")
st.dataframe(risk,use_container_width=True)

st.subheader("Search Student")
q=st.text_input("Search by school/sex")
if q:
    res=filtered[filtered.astype(str).apply(lambda r:r.str.contains(q,case=False)).any(axis=1)]
    st.dataframe(res,use_container_width=True)

st.download_button("Download CSV", filtered.to_csv(index=False),"student_report.csv","text/csv")

st.markdown("---")
st.caption("Built with Streamlit, SQLite, Pandas and Matplotlib")