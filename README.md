![RESUM](https://github.com/user-attachments/assets/42c0a371-1336-4e31-85cf-f70b0400b2fc)

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

![1-main-screen png](https://github.com/user-attachments/assets/8f981604-7d95-4269-9919-3cbf33683732)

**Resume Analysis**

![2-analysis](https://github.com/user-attachments/assets/e20334d0-b53b-470f-b394-4df6ddd7f142)

**Skill Recommendation**

![3-recom](https://github.com/user-attachments/assets/e735a774-8478-4357-9806-3f176f88b94d)

**Course and Virtual Internship Recommendation**

![4-recom](https://github.com/user-attachments/assets/d6830f85-d496-4a8a-9211-e068542ae983)

**Tips and Overall Score**

![5-tipsscore](https://github.com/user-attachments/assets/c93f0ca4-6202-4155-86c0-d16e6c96eec5)

**Video Recommendation**

![6-recom](https://github.com/user-attachments/assets/610f2ca6-74f6-4902-a8c7-4b8699ffacd2)

## Feedback

**Feedback Form**

![1-form](https://github.com/user-attachments/assets/a40e1156-9019-496f-9b5a-e32076bebd1b)

**Overall Rating Analysis and Comment History**

![2-analytics](https://github.com/user-attachments/assets/df4d5b91-ab7b-4ddb-b5d9-5aafba36ba28)


## Admin

**Login**

![1-main-screen](https://github.com/user-attachments/assets/e47578e2-fbbd-4176-8cc7-fe4c3fd2d4df)

**User Count and it's data**

![2-user-data](https://github.com/user-attachments/assets/fdf1bb91-8a86-463c-a3c8-21f9eed6bd52)

**Exported csv file**

![3-user-datacsv](https://github.com/user-attachments/assets/abbd0813-e0a3-4d4c-b5f5-89bf7830d0ae)

**Feedback Data**

![4-feed-data](https://github.com/user-attachments/assets/2cbc9fb4-3659-4814-93d2-02b0dd7a606e)

**Pie Chart Analytical Representation of clusters**

![5-pieexp](https://github.com/user-attachments/assets/bcfc6989-f6dd-4603-ad5b-547aec2e889c)

![6-piescre jpg](https://github.com/user-attachments/assets/b64eef2a-55c5-4426-bfdc-257f83a4a77a)

![7-pielocation](https://github.com/user-attachments/assets/e765ef3d-8825-4adc-84df-71f5a60fdd97)















