<p align="center">
  <img src="https://github.com/youjaepark/KCU-Fall-2024-Group-4/blob/develop/client/icon.png?raw=true" alt="Rate My Schedule Logo" width="200" height="200"/>
</p>

<h1 align="center">Rate My Schedule</h1>

<p align="center">
  <b>Your AI-Powered Course Schedule Advisor for UW-Madison</b>
</p>

<p align="center">
  <i>Combine historical course data, professor ratings, and AI analysis to build your perfect semester schedule.</i>
</p>

---

## 🚀 Key Features

- **AI-Powered Schedule Analysis**: 
  - Overall schedule rating with personalized feedback
  - Course load evaluation
  - Schedule balance assessment
  - Instructor quality analysis

- **Data-Driven Insights**: 
  - Historical GPA data from Madgrades
  - Instructor ratings from Rate My Professors
  - Course difficulty metrics

- **User-Friendly Interface**: 
  - Seamless integration with UW-Madison's enrollment page
  - Interactive side panel
  - Animated scoring visualizations
  - Detailed course statistics table

---

## 🛠️ Technical Architecture

### Frontend (Chrome Extension)
- **Service Worker**: Controls side panel behavior and tab management
- **Content Scripts**: Extract real-time course data from enrollment page
- **UI Components**:
  - Animated circular progress indicators
  - Dynamic score cards
  - Interactive course information table
  - Loading states and transitions

### Backend
1. **Flask Server (Hosted on Vercel)**
   - CORS-enabled architecture
   - JSON data processing

2. **Data Layer**
   - **Firebase Firestore**:
     - Course GPA and information
     - Instructor ratings and information
     - Quick data retrieval for extension

3. **AI Engine**
   - **RAG (Retrieval-Augmented Generation)**:
     - MongoDB for vector storage and retrieval
     - Contextual schedule analysis using historical data
     - Personalized feedback generation
   - **LLM Integration (GPT 4o-mini)**:
     - Section-specific scores (Course, Instructor, Schedule Balance)
     - Overall schedule evaluation
     - AI-generated comments and recommendations for schedule optimization

---

## 📥 Installation

1. Clone the repository
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode"
4. Select "Load unpacked"
5. Choose the `client` directory

---

## 🎯 Usage Guide

1. Visit [UW-Madison Course Enrollment](https://enroll.wisc.edu/scheduler)
2. Add desired courses to your cart
3. Click the extension icon to open side panel
4. Review your schedule analysis:
   - Overall score
   - Individual metrics
   - Course-specific data
   - AI recommendations

---

## 📽️ Resources

- **Demo Video**: [Watch Here](*needed*)
- **Project Presentation**: [View Slides](https://docs.google.com/presentation/d/1T6ejn-tbRW3X8HMoUQkoalOnBdDWDFUXGMeHr3Wal7k/edit?usp=sharing)
