![RESUM](https://github.com/user-attachments/assets/a09d12d0-a9ba-4f91-afbd-b5e9e0e05d56)

<h1 align="center">💻 AI RESUME ANALYZER 💻</h1>

<p align="center">
A Tool for Resume Analysis, Predictions and Recommendations
</p>

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# About the Project ⚙️

A tool that parses information from a resume using natural language processing (NLP), finds the relevant keywords, clusters them into sectors based on their content, and provides recommendations, predictions, and analytics for applicants and recruiters. It aims to help improve resumes, predict suitable job roles, and offer analytics based on keyword matching.

## Features

### Client Side: 👨‍💻 / 👩‍💻
- **Resume Parsing:** Automatically fetches basic info, skills, and keywords from uploaded resumes.
- **Recommendations:** Suggests:
  - Additional skills to add.
  - Predicted job roles.
  - Relevant courses and certificates.
  - Resume tips and improvements.
  - Interview and resume-related video suggestions.
- **Resume Score:** Provides a score based on the parsed data.

### Admin Side: 👨‍💼 / 👩‍💼
- **Data Export:** Download applicant data in CSV format.
- **Resume Management:** View all uploaded resumes and stored user data.
- **Analytics:**
  - Pie charts for user ratings, predicted roles, experience levels, and city/state/country distribution.
  - Monitor user feedback, count, and ratings.

### Feedback Section: 📝
- Collect feedback with rating from 1-5.
- Display user comments and past feedback.

## Tech Stack 🐍 🗃️ 🧠 🌐 🔧
- **Frontend:** Streamlit
- **Backend:** Python, Flask
- **Database:** MySQL
- **NLP:** spaCy (en_core_web_sm), pyresparser
- **Others:** Pandas, Matplotlib, pyMySQL

## Requirements 💡
Ensure you have the following installed:
- Python 3.9.12 [Download Python](https://www.python.org/downloads/release/python-3912/)
- MySQL [Download MySQL](https://www.mysql.com/downloads/)
- Visual Studio Code [Download VS Code](https://code.visualstudio.com/Download)
- Visual Studio Build Tools [Download Build Tools](https://aka.ms/vs/17/release/vs_BuildTools.exe)

## Setup & Installation ⚙️

Follow these steps to get the project up and running:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GauravGhandat-23/AI-Resume-Analyzer.git

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venvapp
   cd venvapp/Scripts
   activate

3. **Install required packages: Navigate to the App folder and install dependencies:**
   ```bash
   cd ../..
   cd App
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm

4. **Setup Database: Create a MySQL database named cv and configure your credentials in App.py:**
   ```bash
   connection = pymysql.connect(host='localhost', user='root', password='root@MySQL4admin', db='cv')

5. **Update resume_parser.py: Go to venvapp\Lib\site-packages\pyresparser and replace resume_parser.py with the provided version.** 

6. **Run the App: Navigate to the App folder and run:**
   ```bash
   streamlit run App.py

## Known Issues ⚠️ 🚨

- **GeocoderUnavailable Error: Ensure your internet connection is stable if this error occurs.**

## Usage

Once set up:

- **Upload a resume and see the results.**
- **Try with the sample resume located in the Uploaded_Resumes folder.**
- **Admin credentials:**
- **Username: admin**
- **Password: admin@resume-analyzer**

## Roadmap 🛣️ 📈 🔄

- **Predict user experience level based on resume data.**
- **Add scoring for skills and projects.**
- **Expand recommendations for various roles.**
- **Fetch more details from resumes for better analysis.**
- **View individual user data and feedback.**

## Contributing 🤝 🔀 🛠️

- **Pull requests are welcome! For major changes, please open an issue to discuss your proposed modifications.**

## Preview 💻

## Client Side

**Main Screen**

![1-main-screen png](https://github.com/user-attachments/assets/b45eef02-6122-4f1b-9e3b-e4e15d34f104)

**Resume Analysis**

![2-analysis](https://github.com/user-attachments/assets/d946f652-1aad-48bb-ade4-493e1d4007bf)

**Skill Recommendation**

![3-recom](https://github.com/user-attachments/assets/a1b8dd67-4744-43af-8ccd-4af1a2d5c2c8)

**Course and Virtual Internship Recommendation**

![4-recom](https://github.com/user-attachments/assets/0a633f92-3abf-4529-9c33-8948e3b7eb34)

**Tips and Overall Score**

![5-tipsscore](https://github.com/user-attachments/assets/0c67fe4e-4a83-46ae-b3fa-5efe4efac0d4)

**Video Recommendation**

![6-recom](https://github.com/user-attachments/assets/fff0c7b7-c942-45b0-8404-b1b405a9a592)

## Feedback

**Feedback Form**

![1-form](https://github.com/user-attachments/assets/8e00f820-4c4e-4734-be70-e646645bdfbf)

**Overall Rating Analysis and Comment History**

![2-analytics](https://github.com/user-attachments/assets/0fc1b796-e2d2-462d-bb65-02a862d02d60)

## Admin

**Login**

![1-main-screen](https://github.com/user-attachments/assets/e6c85386-37e5-4179-a801-46c194e06d16)

**User Count and it's data**

![2-user-data](https://github.com/user-attachments/assets/59ce00a6-5d98-4280-9f01-be5ade996c87)

**Exported csv file**

![3-user-datacsv](https://github.com/user-attachments/assets/b3ed7f0e-7ba4-4b73-a7fa-577cf89258d5)

**Feedback Data**

![4-feed-data](https://github.com/user-attachments/assets/5035b570-4671-4a5b-8d69-72dd146b512b)

**Pie Chart Analytical Representation of clusters**

![5-pieexp](https://github.com/user-attachments/assets/79b72334-31e3-4a8f-9390-7f18a077b737)

![6-piescre jpg](https://github.com/user-attachments/assets/1369d598-ca07-4b23-9151-581460ac0e41)

![7-pielocation](https://github.com/user-attachments/assets/6fdb2dae-733d-4668-bb6e-46ac6e6e8437)














