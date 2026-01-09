import streamlit as st
import joblib
import warnings
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Setup
warnings.filterwarnings("ignore")
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = joblib.load("stress_model.pkl")
scaler = joblib.load("scaler.pkl")

# Session State Initialization
if "stress_label" not in st.session_state:
    st.session_state.stress_label = "Normal"
if "reasons" not in st.session_state:
    st.session_state.reasons = []
if "recs" not in st.session_state:
    st.session_state.recs = []

# Reasons for Stress and Recommendations
def get_stress_reasons(inputs):
    reasons = []
    if inputs["sleep_hours"] <= 5:
        reasons.append("Insufficient sleep (under 5 hours)")

    if inputs["sleep_quality"] <= 2 and inputs["sleep_hours"] > 0:
        reasons.append("Poor sleep quality")

    if inputs["study_hours"] > 8:
        reasons.append("Overstudying without enough rest (over 8 hours)")

    if inputs["screen_time"] > 8:
        reasons.append("Excessive screen time (over 8 hours)")

    if inputs["academic_pressure"] >= 4:
        reasons.append("High academic pressure")

    if inputs["exercise_minutes"] < 20:
        reasons.append("Lack of physical activity (under 20 mins)")

    if inputs["mood"] <= 2:
        reasons.append("Low mood levels")
    return reasons

def get_recommendations(stress_label, reasons):
    recs = []
    if stress_label == "Burnout Risk":
        recs.append("Take a full rest day and reset your routine")
        recs.append("Reduce academic workload temporarily")
        recs.append("Prioritize sleep and recovery")

    if "Insufficient sleep (under 5 hours)" in reasons:
        recs.append("Aim for at least 7–8 hours of sleep daily")

    if "Poor sleep quality" in reasons:
        recs.append("Reduce screen usage 1 hour before bedtime")

    if "Overstudying without enough rest (over 8 hours)" in reasons:
        recs.append("Use the Pomodoro technique (25–5 rule)")

    if "Excessive screen time (over 8 hours)" in reasons:
        recs.append("Schedule screen-free breaks during the day")

    if "Lack of physical activity (under 20 mins)" in reasons:
        recs.append("Add at least 20 minutes of light exercise")

    if "High academic pressure" in reasons:
        recs.append("Break tasks into smaller, manageable goals")

    if "Low mood levels" in reasons:
        recs.append("Take short mental breaks or talk to someone you trust")

    return list(dict.fromkeys(recs))[:5]

# Study Planner Logic
def generate_study_plan(stress_label, syllabus, lecture_schedule, study_hours):
    prompt = f"""
You are an expert student productivity coach.
Stress level: {stress_label}
Daily study capacity: {study_hours} hours
Syllabus: {syllabus}
Lecture Schedule: {lecture_schedule}

Create a realistic weekly study plan that:
- Avoids burnout
- Includes breaks
- Covers all topics
- Adjusts intensity based on stress level

Format as a Markdown table:
Day | Time | Task | Notes
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7)
    )
    return response.text

# Main Page UI
st.set_page_config("TrackED – Student Planner", layout="centered")
st.title("🎓 TrackED – Smart Student Planner")
st.caption("Stress-aware study planning using ML + Google Gemini")

tabs = st.tabs(["🧠 Stress Check", "📖 Study Planner"])

# --- TAB 1: STRESS CHECK ---
with tabs[0]:
    st.subheader("Stress Assessment")

    sleep_hours = st.slider("Sleep Hours", 0.0, 9.0, 7.0)
    if sleep_hours == 0:
        sleep_quality = 0
        st.info("Sleep quality not applicable when sleep hours are 0")
    else:
        sleep_quality = st.slider("Sleep Quality (1–5)", 1, 5, 4)

    study_hours = st.slider("Study Hours / Day", 0.0, 10.0, 5.0)
    screen_time = st.slider("Screen Time (hours)", 0.0, 12.0, 5.0)
    mood = st.slider("Mood (1–5)", 1, 5, 4)
    exercise_minutes = st.slider("Exercise Minutes", 0, 120, 30)
    academic_pressure = st.slider("Academic Pressure (1–5)", 1, 5, 3)

    if st.button("🔍 Predict Stress"):
        sleep_deficit = max(0, 7 - sleep_hours)
        overstudy = max(0, study_hours - 7)

        inputs = {
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "study_hours": study_hours,
            "screen_time": screen_time,
            "mood": mood,
            "exercise_minutes": exercise_minutes,
            "academic_pressure": academic_pressure
        }

        input_data = scaler.transform([[
            sleep_hours, sleep_quality, study_hours, screen_time, 
            mood, exercise_minutes, academic_pressure, sleep_deficit, overstudy
        ]])

        prediction = model.predict(input_data)[0]
        labels = {0: "Normal", 1: "Mild Stress", 2: "Burnout Risk"}
        
        # Save to session state
        st.session_state.stress_label = labels[prediction]
        st.session_state.reasons = get_stress_reasons(inputs)
        st.session_state.recs = get_recommendations(st.session_state.stress_label, st.session_state.reasons)

    # Display Results (Outside button block so they persist)
    if st.session_state.stress_label:
        st.divider()
        st.success(f"Predicted Stress Level: **{st.session_state.stress_label}**")

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔎 Possible Reasons")
            if st.session_state.reasons:
                for r in st.session_state.reasons:
                    st.write(f"• {r}")
            else:
                st.write("✨ No major lifestyle stressors detected.")

        with col2:
            st.subheader("✅ Recommendations")
            if st.session_state.recs:
                for r in st.session_state.recs:
                    st.write(f"• {r}")
            else:
                st.write("🌟 Maintain your current healthy habits!")

# --- TAB 2: STUDY PLANNER ---
with tabs[1]:
    st.subheader("AI Study Planner")
    
    study_hours_plan = st.slider("Available Study Hours / Day", 0.0, 10.0, 5.0, key="plan_slider")
    syllabus = st.text_area("📘 Syllabus", placeholder="Math: Algebra...\nPhysics: Mechanics...")
    lecture_schedule = st.text_area("🏫 Lecture Schedule", placeholder="Mon 9-11 Math...")

    st.info(f"Currently planning for: **{st.session_state.stress_label}** mode")

    if st.button("✨ Generate Study Plan"):
        if not syllabus:
            st.warning("Please enter your syllabus first!")
        else:
            with st.spinner("Gemini is crafting your plan..."):
                plan = generate_study_plan(
                    st.session_state.stress_label,
                    syllabus,
                    lecture_schedule,
                    study_hours_plan
                )
            st.subheader("📅 Your Personalized Schedule")
            st.markdown(plan)
            st.caption("This plan is adjusted based on your Stress Assessment results.")