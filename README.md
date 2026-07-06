# Study Buddy 🎓

An intelligent, adaptive exam preparation assistant designed to optimize your learning. Simply upload or paste your study materials, and let the generative AI model construct customized multiple-choice and short-answer practice sessions, giving you instant conceptual explanations while tracking your progress to automatically reinforce your weaker areas.

---

## 🌟 Key Features

1. **🏠 Interactive Landing Page:** 
   Clean, modern dashboard landing page with programmatic routing. Includes card blocks detailing features that take the user to specialized deep-dive explanations.

2. **🗂️ Multi-Deck Subject Management:** 
   Organize your studies by subject or class (e.g. *Accounting Unit 2*, *Biology Unit 1*). Each deck contains its own notes context, practice history logs, strengths/weaknesses list, and custom study sheets.

3. **📝 Adaptive Quiz Generation:** 
   Constructs practice sessions of MCQ and short-answer questions. The system analyzes your performance logs to dynamically adjust the question difficulty level (EASY/MEDIUM/HARD) per topic based on correct/incorrect streaks. Roughly 60% of the questions are biased to prioritize your weak topics.

4. **🤖 Multi-Agent Explanation Critic:** 
   When you answer a question incorrectly, a team of two generative agents collaborates to help you learn:
   - **Agent 1 (Generator):** Drafts a detailed explanation for the correct answer.
   - **Agent 2 (Critique & Refiner):** Reviews the draft explanation, verifying accuracy, clarity, and conciseness to return a premium, refined review. An expander below the review shows the draft vs. final comparison for demo visibility.

5. **📈 Topic Mastery Map:** 
   An interactive visual Plotly grid scatter-plot of your subject topics. Eeach topic is mapped as a node where:
   - **Color** reflects performance: Mastered (🟢 Green, >75% accuracy), Developing (🟡 Yellow, 40-75%), or Needs Review (🔴 Red, <40%).
   - **Size** reflects question volume (more attempts = larger node).
   - **Selection:** Clicking any node filters the rolling accuracy timelines and recent logs to display stats specifically for that topic.

6. **📚 Revision Sheets Library:** 
   Compiles summaries covering concepts where your accuracy score is below 70%. It acts as a senior tutor to generate a concise summary of key points and common mistakes, and lets you view, download, or delete past sheets from a persistent historical database library.

7. **🏆 Achievements & Badges:** 
   Visual rewards tracking your learning habits over SQLite history:
   - **7-Day Streak:** Unlocked by studying 7 consecutive days.
   - **Topic Master:** Earned by reaching >=90% accuracy on any topic with 5+ attempts.
   - **Comeback Kid:** Earned by improving a topic from early failure (<40% accuracy on first 3 attempts) to mastery (>70% accuracy on last 3 attempts).
   - Unlocked badges are colored with detailed unlocked logs, while locked badges remain grayscale.

---

## 🛠️ Setup Instructions

### Prerequisites
* Python 3.9 or higher installed.
* A Gemini API key (obtainable from Google AI Studio).

### Installation
1. Clone this repository to your local machine:
   ```bash
   git clone <your-repository-url>
   cd study-buddy
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Usage Guide

1. **Create a Subject Deck:** On the Home page, scroll down to the decks section, click "Configure New Deck" inside the **Create Deck** card, type in a subject name (e.g. "Physics 101"), paste or upload notes, and click "Create Deck".
2. **Practice a Quiz:** Navigate to **📝 Upload & Study** in the sidebar. Select a question count preference, select your input method, and click "Generate Study Session". Answering incorrectly shows the multi-agent critique explainer.
3. **Drill Down into Mastery:** Go to the **📈 Progress Dashboard** to inspect overall stats. Click nodes on the **Topic Mastery Map** to filter timelines and log history details.
4. **Generate Revision Guides:** Click "Generate Revision Sheet" on the Progress Dashboard to compile custom summaries of your weak topics, then head to **📚 Revision Sheets** to read or download the Markdown files.
5. **Unlock Badges:** Navigate to **🏆 Achievements** to monitor streak progress and unlock mastery badges.
