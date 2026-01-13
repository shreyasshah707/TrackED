# 🎓 TrackED – Smart Student Planner

**TrackED** is a smart productivity and wellbeing tool that helps students plan their studies based on their mental state, not just time availability.
Unlike traditional planners, TrackED first assesses a student’s stress level using *machine learning*, identifies *why* they may be stressed, and then adapts their weekly study plan using **Google Gemini AI**

## ✨ Key Features
* **🧠 Stress Assessment:** Predicts your current stress level (Normal, Mild Stress, or Burnout Risk) using a Scikit-Learn model based on lifestyle factors like sleep, study hours, and mood.
* **🔎 Root Cause Analysis:** Automatically identifies triggers like "Excessive screen time" or "Insufficient sleep."
* **✅ Actionable Recommendations:** Provides tailored advice to reduce stress based on your unique data.
* **📅 AI Study Planner:** Generates a custom weekly schedule in table format using Google Gemini, adjusting study intensity based on your current mental state.

### 🛡️ Privacy-First & Reliable
* No personal data stored
* No medical diagnosis — awareness & productivity focused
* Works even when AI services are unavailable

## 🧪 How It Works
1. User enters daily habits and academic data  
2. ML model predicts stress level  
3. App explains stress causes and recommendations  
4. Study plan adapts to the student’s mental state  
5. AI planner runs safely with fallback logic
  
## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Machine Learning:** Scikit-Learn, Joblib
* **LLM:** Google Gemini 2.0 Flash
* **Environment & Config:** Python, dotenv, Streamlit secrets

## 🌱 Future Enhancements
* Long-term stress tracking
* Calendar integration
* Wearable data support
* Institutional dashboards for student wellbeing
