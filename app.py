import streamlit as st
import joblib
import warnings
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

#Setup
warnings.filterwarnings("ignore")
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

model = joblib.load("stress_model.pkl")
scaler = joblib.load("scaler.pkl")

#Initialize session state
if "stress_label" not in st.session_state:
    st.session_state.stress_label = "Normal"

if "reasons" not in st.session_state:
    st.session_state.reasons = []

if "recs" not in st.session_state:
    st.session_state.recs = []

if "study_plan" not in st.session_state:
    st.session_state.study_plan = None

#Logic Functions
def get_stress_reasons(inputs):
    reasons = []

    if inputs["sleep_hours"] <= 5:
        reasons.append("Insufficient sleep (under 5 hours)")
    if inputs["sleep_quality"] <= 2 and inputs["sleep_hours"] > 0:
        reasons.append("Poor sleep quality")
    if inputs["study_hours"] > 8:
        reasons.append("Overstudying without enough rest")
    if inputs["screen_time"] > 8:
        reasons.append("Excessive screen time")
    if inputs["academic_pressure"] >= 4:
        reasons.append("High academic pressure")
    if inputs["exercise_minutes"] < 20:
        reasons.append("Low physical activity")
    if inputs["mood"] <= 2:
        reasons.append("Low mood levels")

    return reasons


def get_recommendations(stress_label, reasons):
    recs = []

    if stress_label == "Burnout Risk":
        recs += [
            "Take a full rest day",
            "Reduce workload temporarily",
            "Prioritize sleep and recovery"
        ]

    if "Insufficient sleep (under 5 hours)" in reasons:
        recs.append("Aim for 7-8 hours of sleep")
    if "Poor sleep quality" in reasons:
        recs.append("Avoid screens before bedtime")
    if "Overstudying without enough rest" in reasons:
        recs.append("Use Pomodoro (25-5 rule)")
    if "Low physical activity" in reasons:
        recs.append("Add 20-30 mins of exercise")
    if "High academic pressure" in reasons:
        recs.append("Break tasks into smaller goals")
    if "Low mood levels" in reasons:
        recs.append("Take mental breaks or talk to someone")

    return list(dict.fromkeys(recs))[:5]

#Local Planner
def rule_based_study_plan(stress_label, study_hours):
    intensity = {
        "Normal": "High focus sessions",
        "Mild Stress": "Moderate paced sessions",
        "Burnout Risk": "Light sessions with extra breaks"
    }

    return f"""
### 📅 Weekly Study Plan

| Day | Time | Task | Notes |
|----|------|------|------|
| Mon | 1.5h | Core Subject | {intensity[stress_label]} |
| Tue | 1.5h | Secondary Subject | Include breaks |
| Wed | 1h | Revision | Light review |
| Thu | 1.5h | Practice Problems | Active recall |
| Fri | 1h | Weak Areas | Low pressure |
| Sat | 1h | Mock / Summary | Stop early |
| Sun | — | Rest | Recovery day |

⚠️ *This plan was generated locally since AI quota exceeded.*
"""

#Gemini Planner
def generate_study_plan(stress_label, syllabus, lecture_schedule, study_hours):
    prompt = f"""
You are an expert student productivity coach.
Stress Level: {stress_label}
Daily Study Capacity: {study_hours} hours
Syllabus:
{syllabus}
Lecture Schedule:
{lecture_schedule}
Create a realistic weekly study plan as a Markdown table.
"""

    try: 
        response = client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9
            )
        )
        return response.text

    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            return rule_based_study_plan(stress_label, study_hours)
        else:
            raise e


#UI
st.set_page_config("TrackED: Smart Student Planner")
st.title("🎓TrackED: Smart Student Planner")
st.caption("Stress-aware study planner using ML + Gemini")
tabs = st.tabs(["🧠 Stress Check", "📖 Study Planner"])

#Stress UI
with tabs[0]:
    st.subheader("Stress Assessment")

    sleep_hours = st.slider("Sleep Hours", 0.0, 9.0, 7.0)
    sleep_quality = 0 if sleep_hours == 0 else st.slider("Sleep Quality (1-5)", 1, 5, 4)
    study_hours = st.slider("Study Hours / Day", 0.0, 10.0, 5.0)
    screen_time = st.slider("Screen Time", 0.0, 12.0, 5.0)
    mood = st.slider("Mood (1-5)", 1, 5, 4)
    exercise_minutes = st.slider("Exercise Minutes", 0, 120, 30)
    academic_pressure = st.slider("Academic Pressure (1-5)", 1, 5, 3)

    if st.button("🔍 Predict Stress"):
        features = scaler.transform([[
            sleep_hours, sleep_quality, study_hours, screen_time,
            mood, exercise_minutes, academic_pressure,
            max(0, 7 - sleep_hours), max(0, study_hours - 7)
        ]])

        labels = {0: "Normal", 1: "Mild Stress", 2: "Burnout Risk"}
        st.session_state.stress_label = labels[model.predict(features)[0]]

        inputs = {
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "study_hours": study_hours,
            "screen_time": screen_time,
            "mood": mood,
            "exercise_minutes": exercise_minutes,
            "academic_pressure": academic_pressure
        }

        st.session_state.reasons = get_stress_reasons(inputs)
        st.session_state.recs = get_recommendations(
            st.session_state.stress_label,
            st.session_state.reasons
        )

    st.divider()
    st.success(f"Predicted Stress Level: **{st.session_state.stress_label}**")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔎 Possible Reasons")
        for r in st.session_state.reasons:
            st.write(f"• {r}")
    with c2:
        st.subheader("✅ Recommendations")
        for r in st.session_state.recs:
            st.write(f"• {r}")

#Planner UI
with tabs[1]:
    st.subheader("AI Study Planner")

    plan_hours = st.slider("Available Study Hours / Day", 0.0, 10.0, 5.0)
    syllabus = st.text_area("📘 Syllabus")
    lectures = st.text_area("🏫 Lecture Schedule")

    if st.button("✨ Generate Study Plan"):
        with st.spinner("Creating study plan..."):
            st.session_state.study_plan = generate_study_plan(
                st.session_state.stress_label,
                syllabus,
                lectures,
                plan_hours
            )

    if st.session_state.study_plan:
        st.markdown(st.session_state.study_plan)
