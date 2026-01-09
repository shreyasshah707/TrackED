# 🎓 TrackED – Smart Student Planner

**TrackED** is an AI-powered productivity tool designed to help students manage their academic workload without compromising their mental health. It uses a custom **Machine Learning model** to assess stress levels and the **Google Gemini API** to generate personalized, stress-aware weekly study plans.

## ✨ Key Features
* **🧠 Stress Assessment:** Predicts your current stress level (Normal, Mild Stress, or Burnout Risk) using a Scikit-Learn model based on lifestyle factors like sleep, study hours, and mood.
* **🔎 Root Cause Analysis:** Automatically identifies triggers like "Excessive screen time" or "Insufficient sleep."
* **✅ Actionable Recommendations:** Provides tailored advice to reduce stress based on your unique data.
* **📅 AI Study Planner:** Generates a custom weekly schedule in table format using Google Gemini, adjusting study intensity based on your current mental state.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Machine Learning:** Scikit-Learn (RandomForest/SVM), Joblib
* **LLM:** Google Gemini 2.0 Flash
* **Environment:** Python (dotenv)
