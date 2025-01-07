import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import Software_Development_course,web_course,android_course,ios_course,uiux_course,cybersecurity_course,artificial_intelligence_course,network_engineering_course,cloud_computing_course,game_development_course,vr_ar_course,Data_Science_course,blockchain_course,devops_course,mobile_app_development_course,digital_marketing_course,robotics_course,machine_learning_course,embedded_systems_course,resume_videos,interview_videos
from Virtual_Internship import Software_Development_Virtual_Internship,Web_development_Virtual_Internship,Android_Development_Virtual_Internship,IOS_Development_Virtual_Internship,UI_UX_Development_Virtual_Internship,Cyber_Security_Virtual_Internship,Artificial_Intelligence_Virtual_Internship,Network_Engineering_Virtual_Internship,Cloud_Computing_Virtual_Internship,Game_Development_Virtual_Internship,Virtual_Reality_Augmented_Reality_Virtual_Internship,Data_Science_Virtual_Internship,Blockchain_Development_Virtual_Internship,DevOps_Virtual_Internship,Mobile_App_Development_Virtual_Internship,Digital_Marketing_Virtual_Internship,Robotics_Virtual_Internship,Machine_Learning_Virtual_Internship,Embedded_Systems_Virtual_Internship
import nltk
nltk.download('stopwords')


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# Virtual Internship recommender which has data already loaded from Internships.py
def Virtual_Internship_recommender(internship_list):
    st.subheader("**Virtual Internships Recommendations 🌐**")
    c = 0
    rec_internships = []
    # Slider to choose the number of recommendations
    no_of_reco = st.slider('Choose Number of Internship Recommendations:', 1, 10, 5)
    random.shuffle(internship_list)
    for i_name, i_link in internship_list:
        c += 1
        st.markdown(f"({c}) [{i_name}]({i_link})")
        rec_internships.append(i_name)
        if c == no_of_reco:
            break
    return rec_internships

###### Database Stuffs ######


# sql connector
connection = pymysql.connect(host='localhost',user='root',password='admin',db='cv')
cursor = connection.cursor()


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon='./Logo/recommend.png',
)


###### Main function run() ######


def run():
    
    # (Logo, Heading, Sidebar etc)
    img = Image.open('./Logo/RESUM.png')
    st.image(img)
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '<b>Built with 🤍 by <a href="https://dnoobnerd.netlify.app/" style="text-decoration: none; color: #E2E5ECFF;">Gaurav Ghandat</a></b>' 
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.markdown('''
        <!-- site visitors -->

        <div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

        <noscript>
            <a href="https://www.freecounterstat.com" title="hit counter">
                <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter"> -->
            </a>
        </noscript>
    
        <p>Visitors <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    ''', unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en')
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy


        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.header("**Resume Analysis 🤘**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info 👀**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.subheader("**Skills Recommendation 💡**")
                
                ### Current Analyzed Skills
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                Software_Development_keyword = [{"programming_languages": ["Java", "Python", "JavaScript", "C++", "C#", "Ruby", "Swift", "Kotlin", "TypeScript", "PHP", "Go", "Rust"], "frameworks_and_libraries": ["React.js", "Angular", "Vue.js", "Django", "Flask", "Ruby on Rails", "Spring Boot", "ASP.NET", "Node.js", "Express.js"], "version_control_systems": ["Git", "GitHub", "GitLab", "Bitbucket"], "development_methodologies": ["Agile", "Scrum", "Kanban", "Waterfall", "Test-Driven Development (TDD)", "Continuous Integration (CI)", "Continuous Deployment (CD)", "DevOps"], "databases": ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Firebase", "Oracle DB", "Microsoft SQL Server", "Cassandra"], "development_tools": ["Docker", "Kubernetes", "Jenkins", "Travis CI", "Visual Studio Code", "IntelliJ IDEA", "PyCharm", "WebStorm", "Eclipse", "Sublime Text"], "apis_and_web_services": ["RESTful APIs", "GraphQL", "SOAP", "JSON", "XML", "OAuth", "OpenAPI", "Swagger"], "software_architecture": ["Microservices", "Monolithic Architecture", "Serverless Architecture", "Event-Driven Architecture", "MVC", "MVVM", "SOA"], "operating_systems_and_platforms": ["Linux", "Windows", "macOS", "Android", "iOS"], "testing_and_debugging": ["Unit Testing", "Integration Testing", "End-to-End (E2E) Testing", "JUnit", "Selenium", "Jest", "Mocha", "Cypress", "Postman", "PyTest"], "software_design_patterns": ["Singleton", "Factory Pattern", "Observer Pattern", "Adapter Pattern", "Dependency Injection"], "cloud_platforms": ["Amazon Web Services (AWS)", "Microsoft Azure", "Google Cloud Platform (GCP)", "Heroku", "DigitalOcean"], "mobile_development": ["Android SDK", "iOS SDK", "React Native", "Flutter", "Xamarin"], "versioning_and_deployment": ["Jenkins", "Travis CI/CD", "Ansible", "Terraform", "Puppet"]}]
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                cybersecurity_keyword = ['cybersecurity', 'security analyst', 'penetration testing', 'infosec', 'malware', 'phishing', 'ransomware', 'firewall', 'encryption', 'intrusion detection', 'vulnerability assessment', 'incident response', 'network security', 'data breach', 'zero trust', 'threat intelligence', 'authentication', 'access control', 'SIEM', 'social engineering', 'cloud security', 'IoT security', 'compliance']
                artificial_intelligence_keyword = ['Artificial Intelligence', 'Machine Learning', 'Deep Learning', 'Natural Language Processing', 'Computer Vision', 'Reinforcement Learning', 'Neural Networks', 'Supervised Learning', 'Unsupervised Learning', 'Generative Adversarial Networks', 'Transfer Learning', 'Feature Engineering', 'Bias and Fairness', 'Explainable AI', 'Autonomous Systems', 'Robotics', 'Edge AI', 'AI Ethics', 'Predictive Analytics']
                network_engineering_keyword = ["TCP/IP", "OSI Model", "Routing", "Switching", "VLAN", "BGP", "Subnetting", "DNS", "NAT", "Firewall", "VPN", "Ethernet", "Load Balancing", "DHCP", "SNMP", "LAN", "WAN", "QoS", "MPLS", "IPv6"]
                cloud_computing_keyword = ["IaaS", "PaaS", "SaaS", "Cloud Storage", "Virtualization", "Public Cloud", "Private Cloud", "Hybrid Cloud", "AWS", "Azure", "Google Cloud", "Kubernetes", "Containers", "Serverless", "Microservices", "DevOps", "Cloud Security", "Multi-Cloud", "Cloud Migration", "Edge Computing"]
                game_development_keyword = ["Game Engine", "Unity", "Unreal Engine", "3D Modeling", "2D Graphics", "Animation", "Game Design", "Level Design", "Artificial Intelligence", "Physics Simulation", "Scripting", "Gameplay Mechanics", "Multiplayer Networking", "User Interface (UI)", "Game Monetization", "Virtual Reality (VR)", "Augmented Reality (AR)", "Game Testing", "Asset Creation", "Shaders"]
                vr_ar_keyword = ["Virtual Reality", "Augmented Reality", "Immersion", "Simulation", "3D Environment", "Headset", "Haptic Feedback", "AR Glasses", "Mixed Reality", "User Experience", "Interactivity", "Spatial Computing"]
                Data_Science_keyword = ["Data Science", "Python", "R", "SQL", "Statistics", "Machine Learning", "Deep Learning", "Data Wrangling", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow", "Keras", "Big Data", "Spark", "Hadoop", "Data Analysis", "Data Visualization", "Tableau", "Power BI", "ETL", "Data Engineering"]
                Blockchain_Development_keyword = ["Blockchain", "Cryptocurrency", "Smart Contracts", "Solidity", "Ethereum", "Hyperledger", "Distributed Ledger Technology (DLT)", "Decentralized Applications (DApps)", "Consensus Algorithms", "Tokenomics", "Web3.js", "Truffle", "Ganache", "Cryptography", "Bitcoin", "IPFS", "Blockchain Security", "Decentralized Finance (DeFi)", "Layer 2 Solutions", "Blockchain Architecture"]
                DevOps_keyword = ["DevOps", "CI/CD", "Continuous Integration", "Continuous Deployment", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible", "Git", "AWS", "Azure", "Google Cloud", "Scripting", "Linux", "Bash", "Python", "Agile", "Monitoring", "CloudFormation", "Infrastructure as Code (IaC)", "Version Control", "Automation", "Configuration Management"]
                Mobile_App_Development_keyword = ["Mobile Development", "Android", "iOS", "Swift", "Kotlin", "Java", "Flutter", "React Native", "Mobile App Design", "Firebase", "SQLite", "APIs", "UI/UX", "App Store Deployment", "Hybrid Apps", "Mobile Optimization", "Mobile Security", "Android Studio", "Xcode"]
                Digital_Marketing_keyword = ["Digital Marketing", "SEO", "SEM", "Content Marketing", "Google Ads", "Google Analytics", "Email Marketing", "Social Media Marketing", "Keyword Research", "Copywriting", "PPC", "A/B Testing", "Conversion Rate Optimization", "Marketing Automation", "CRM", "Web Analytics", "Campaign Management", "Digital Strategy", "Social Media Platforms"]
                Robotics_keyword = ["Robotics", "Robot Operating System (ROS)", "C++", "Python", "Mechatronics", "Automation", "Sensors", "Actuators", "Control Systems", "Path Planning", "Kinematics", "Embedded Systems", "AI", "Simulation", "Computer Vision", "3D Modeling", "Hardware Design", "MATLAB", "Robotic Arms", "Autonomous Systems"]
                Embedded_Systems_keyword = ["Embedded Systems", "Microcontrollers", "C", "C++", "Assembly Language", "RTOS", "Embedded C", "IoT", "PCB Design", "Debugging Tools", "Low-Level Programming", "Firmware Development", "Hardware Security", "Embedded Linux", "Sensor Integration", "Actuators", "SPI/I2C", "CAN Protocol", "System Design"]
                Machine_Learning_keyword = ["Machine Learning", "Deep Learning", "Supervised Learning", "Unsupervised Learning", "Reinforcement Learning", "NLP", "Computer Vision", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Data Cleaning", "Feature Engineering", "Hyperparameter Tuning", "Model Evaluation", "Mathematics", "Statistics", "Algorithms"]
                Thermal_Engineering = ["Thermodynamics", "Heat Transfer", "Refrigeration", "Air Conditioning", "Power Plants"],
                Fluid_Mechanics = ["Hydrodynamics", "CFD", "Pipe Flow", "Open Channel Flow", "Pumps", "Turbines"],
                Robotics_and_Automation = ["Industrial Robotics", "Mechatronics", "PLC", "Control Systems", "Sensors"],
                Design_and_Manufacturing = ["SolidWorks", "AutoCAD", "CATIA", "CNC", "3D Printing", "Product Design"],
                Automobile_Engineering = ["Vehicle Dynamics", "Engine Design", "Automotive Electronics", "Chassis Design", "Emission Control"]
                Power_Systems = ["Grid Systems", "Transmission Lines", "Power Distribution", "Load Analysis", "Renewable Integration"],
                Control_Systems = ["PID Controllers", "Mathematical Modeling", "State Space", "Feedback Systems", "Automation"],
                Electrical_Machines = ["Transformers", "Motors", "Generators", "Induction Machines", "DC Machines"],
                Signal_Processing = ["Fourier Transform", "Wavelets", "Filtering", "Digital Signal Processing", "Spectral Analysis"],
                Renewable_Energy = ["Solar Power", "Wind Energy", "Battery Systems", "Hydropower", "Energy Storage"]
                Structural_Engineering = ["STAAD Pro", "RCC Design", "Steel Structures", "Earthquake Engineering", "Bridge Design"],
                Geotechnical_Engineering = ["Soil Mechanics", "Foundation Design", "Slope Stability", "Earth Retaining Structures"],
                Environmental_Engineering = ["Water Treatment", "Air Pollution Control", "Sustainability", "Solid Waste Management"],
                Transportation_Engineering = ["Traffic Analysis", "Pavement Design", "Highway Engineering", "Urban Planning"],
                Construction_Management = ["Project Scheduling", "Quantity Surveying", "Cost Estimation", "Construction Safety"]
                Embedded_Systems = ["Microcontrollers", "Arduino", "Raspberry Pi", "Real-Time Systems"],
                VLSI_Design = ["HDL", "FPGA", "ASIC", "Semiconductor Devices"],
                Digital_Signal_Processing = ["DSP Algorithms", "Filter Design", "Wavelets", "Image Processing"],
                Internet_of_Things = ["IoT Sensors", "MQTT", "Edge Computing", "Home Automation"],
                Telecommunications = ["Wireless Communication", "5G", "Optical Networks", "Satellite Communication"]
                Process_Engineering = ["Heat Exchangers", "Distillation", "Fluidized Beds", "Process Control"],
                Biochemical_Engineering = ["Fermentation", "Bioreactors", "Enzyme Technology"],
                Petroleum_and_Petrochemical_Engineering = ["Crude Oil Processing", "Natural Gas", "Downstream Operations"],
                Materials_Science = ["Polymers", "Composites", "Metallurgy", "Nanomaterials"]
                Aerodynamics = ["Flow Dynamics", "Aircraft Design", "Wind Tunnel Testing"],
                Propulsion_Systems = ["Jet Engines", "Rocket Engines", "Turbochargers"],
                Avionics = ["Flight Control Systems", "Navigation", "Radar Systems"],
                Spacecraft_Design = ["Orbital Mechanics", "Satellite Systems", "Space Propulsion"]
                Medical_Imaging = ["MRI", "CT Scans", "Ultrasound"],
                Biomaterials = ["Prosthetics", "Bioimplants", "Tissue Engineering"],
                Biomechanics = ["Rehabilitation Devices", "Ergonomics"],
                Healthcare_Device_Development = ["Wearable Technology", "Diagnostic Tools"]
                Waste_Management = ["Recycling", "Landfills", "Hazardous Waste"],
                Water_Resources_Engineering = ["Hydrology", "Water Treatment", "Irrigation"],
                Climate_Change_Mitigation = ["Carbon Capture", "Sustainability", "Environmental Policy"],
                Sustainable_Energy = ["Solar Energy", "Wind Energy", "Hydropower"]
                Lean_Manufacturing = ["5S", "Kanban", "Waste Reduction", "Just-in-Time"],
                Operations_Research = ["Linear Programming", "Optimization Models", "Simulation"],
                Supply_Chain_Management = ["Inventory Control", "Logistics Planning", "Demand Forecasting"],
                Quality_Control = ["Six Sigma", "Statistical Process Control", "ISO Standards"]
                Nanomaterials = ["Graphene", "Carbon Nanotubes", "Quantum Dots"],
                Nanofabrication = ["Electron Beam Lithography", "Thin Film Deposition"],
                Applications = ["Nanoelectronics", "Nanosensors", "Drug Delivery Systems"]
                Solar_Energy = ["PV Panel Installation", "Solar Cell Design", "Net Metering"],
                Wind_Energy = ["Wind Turbine Components", "Energy Yield Analysis", "Offshore Wind Farms"],
                Hydropower = ["Small Hydropower Plants", "Turbine Selection", "Hydraulic Design"],
                Energy_Storage = ["Battery Chemistry", "Energy Management Systems", "Grid Integration"]
                Metallurgy = ["Alloy Design", "Heat Treatment", "Phase Transformations", "Metal Testing"],
                Polymers = ["Polymer Synthesis", "Composite Materials", "Thermoplastics", "Elastomers"],
                Ceramics = ["Ceramic Processing", "Thermal Conductivity", "Piezoelectric Materials", "Refractories"],
                Nanomaterials = ["Nanoparticles", "Nanostructures", "Self-Assembly", "Functional Coatings"]
                Naval_Architecture = ["Ship Design", "Hydrostatics", "Stability Analysis", "Marine Hydrodynamics"],
                Marine_Machinery = ["Propulsion Systems", "Diesel Engines", "Turbomachinery", "Piping Systems"],
                Ocean_Engineering = ["Underwater Vehicles", "Ocean Energy", "Marine Structures", "Offshore Platforms"]
                Mine_Planning =["Geostatistics", "Mine Safety", "Open Pit Design", "Underground Mining"],
                Mineral_Processing = ["Crushing and Grinding", "Flotation", "Gravity Separation", "Dewatering"],
                Mining_Equipment = ["Drillng Machines", "Excavators", "Haul Trucks", "Automation in Mining"]
                Farm_Machinery = ["Tractor Design", "Irrigation Systems", "Harvesting Equipment", "Precision Agriculture"],
                Soil_Science = ["Soil Fertility", "Soil Erosion Control", "Soil Mechanics", "Soil Testing"],
                Food_Processing = ["Post-Harvest Technology", "Food Preservation", "Packaging Technology", "Cold Storage"]
                Textile_Manufacturing = ["Yarn Production", "Weaving", "Knitting", "Dyeing and Printing"],
                Textile_Materials = ["Natural Fibers", "Synthetic Fibers", "Blended Fabrics", "Non-Woven Materials"],
                Technical_Textiles = ["Geo-textiles", "Medical Textiles", "Smart Textiles", "Protective Clothing"]
                Reservoir_Engineering = ["Reservoir Simulation", "Enhanced Oil Recovery", "PVT Analysis", "Reservoir Management"],
                Drilling_Engineering = ["Drilling Fluids", "Directional Drilling", "Well Control", "Casing Design"],
                Production_Engineering = ["Well Stimulation", "Artificial Lift", "Production Optimization", "Subsea Systems"]
                Energy_Efficiency = ["Building Energy Management", "Smart Grids", "Energy Auditing", "Demand-Side Management"],
                Sustainable_Energy = ["Geothermal Energy", "Biomass", "Tidal Energy", "Fuel Cells"],
                Energy_Systems = ["Power Conversion", "Energy Policy", "Thermal Energy Storage", "Hybrid Energy Systems"]
                Electric_Vehicles = ["Battery Management Systems", "EV Charging Stations", "Electric Motors", "Power Electronics"],
                Autonomous_Vehicles = ["ADAS", "Lidar", "Sensor Fusion", "Autonomous Navigation"],
                Vehicle_Safety = ["Crash Analysis", "Airbag Systems", "Traction Control", "Braking Systems"]
                Industrial_IoT = ["Smart Sensors", "Edge Computing", "Digital Twins", "Predictive Maintenance"],
                Robotic_Process_Automation = ["Robotic Arms", "Motion Control", "Path Planning", "Industrial Robotics"],
                Automation_Tools = ["SCADA", "HMI", "DCS", "Programmable Logic Controllers (PLC)"]
                Optoelectronics = ["Laser Design", "Fiber Optics", "Photon Detectors", "LED Technology"],
                Optical_Communication = ["Waveguide Design", "Optical Amplifiers", "Free-Space Optics", "Optical Networks"],
                Imaging_Systems = ["Holography", "Microscopy", "Remote Sensing", "Infrared Imaging"]
                Nuclear_Reactor_Design = ["Thermal Reactors", "Fast Reactors", "Neutron Moderation", "Reactor Safety"],
                Radiation_Protection = ["Dosimetry", "Shielding Design", "Nuclear Waste Management", "Radiation Monitoring"],
                Fusion_Energy = ["Plasma Physics", "Tokamak Design", "Magnetic Confinement", "Fusion Materials"]
                Geophysics = ["Seismic Surveying", "Gravity and Magnetic Analysis", "Well Logging", "Geophysical Data Processing"],
                Hydrogeology = ["Groundwater Flow", "Aquifer Testing", "Contaminant Transport", "Hydrogeological Modeling"],
                Engineering_Geology = ["Rock Mechanics", "Slope Stability", "Site Investigation", "Geological Hazard Assessment"]
                Measurement_Systems = ["Sensors", "Transducers", "Signal Conditioning", "Data Acquisition Systems"],
                Process_Instrumentation = ["Flow Meters", "Pressure Sensors", "Temperature Controllers", "Analytical Instruments"],
                Control_Systems = ["PID Tuning", "Feedback Systems", "Process Control Loops", "SCADA Systems"]
                Aircraft_Maintenance = ["Airframe Repair", "Engine Overhaul", "Avionics Testing", "Maintenance Scheduling"],
                Flight_Mechanics = ["Performance Analysis", "Flight Dynamics", "Control Surfaces", "Aircraft Stability"],
                Airport_Management = ["Air Traffic Control", "Runway Design", "Aircraft Scheduling", "Passenger Services"]
                Extractive_Metallurgy = ["Ore Processing", "Hydrometallurgy", "Pyrometallurgy", "Electrometallurgy"],
                Physical_Metallurgy = ["Phase Diagrams", "Heat Treatment", "Mechanical Testing", "Failure Analysis"],
                Process_Metallurgy = ["Casting", "Rolling", "Forging", "Welding"]               
                Acoustics_Design = ["Noise Control", "Soundproofing", "Echo Reduction", "Building Acoustics"],
                Audio_Engineering = ["Signal Processing", "Microphone Arrays", "Speaker Design", "Room Acoustics"],
                Vibration_Analysis = ["Modal Analysis", "Damping Techniques", "Vibration Isolation", "Dynamic Testing"]
                Systems_Integration = ["Flight Software", "Payload Systems", "Spacecraft Operations"],
                Satellite_Technology = ["Remote Sensing", "Orbit Mechanics", "Telemetry Systems", "Ground Stations"],
                Aerospace_Materials = ["Lightweight Composites", "High-Temperature Alloys", "Corrosion Resistance"]
                Mechatronic_Systems = ["Motion Control", "Robotic Systems", "Microcontrollers", "Electro-Mechanical Design"],
                Automation = ["PLC Programming", "HMI Design", "Actuator Control", "Industrial Automation"],
                Sensor_Systems = ["Position Sensors", "Force Sensors", "IMUs", "Sensor Fusion"]
                Risk_Assessment = ["Hazard Identification", "Safety Audits", "Risk Mitigation Plans", "Emergency Response"],
                Industrial_Hygiene = ["Occupational Exposure", "Ventilation Systems", "Toxicology", "Noise Monitoring"],
                Sustainability = ["Green Building Practices", "Life Cycle Assessment", "Energy Efficiency Audits"]
                Subsea_Engineering = ["Pipeline Design", "Underwater Structures", "ROVs", "Subsea Control Systems"],
                Ship_Propulsion = ["Marine Engines", "Propeller Design", "Fuel Efficiency", "Emission Control"],
                Offshore_Platforms = ["Structural Design", "Platform Stability", "Wave Loading", "Mooring Systems"]
                Track_Engineering = ["Rail Alignment", "Track Maintenance", "Ballast Design", "Rail Welding"],
                Rolling_Stock = ["Train Dynamics", "Electric Locomotives", "Brake Systems", "Traction Systems"],
                Signal_and_Control = ["Automatic Train Control", "Interlocking Systems", "Train Scheduling"]
                Process_Safety = ["HAZOP Studies", "Risk-Based Inspections", "Safety Instrumented Systems"],
                Fire_Protection = ["Sprinkler Systems", "Fire Dynamics", "Explosion Prevention", "Emergency Planning"],
                Ergonomics = ["Workplace Design", "Human Factors Engineering", "Occupational Health"]
                Wireless_Communication = ["5G Networks", "MIMO Systems", "RF Planning", "Spectrum Management"],
                Optical_Communication = ["DWDM", "Fiber Optic Networks", "Photonic Devices", "Free Space Optics"],
                Urban_Infrastructure = ["Smart Cities", "Public Transport Systems", "Energy-Efficient Buildings"],
                Land_Use_Planning = ["Zoning Policies", "Geographic Information Systems (GIS)", "Urban Analytics"],
                Sustainable_Development = ["Carbon Neutral Cities", "Green Infrastructure", "Water Management"]
                Flight_Safety = ["Airworthiness", "Flight Data Analysis", "Incident Investigation", "Safety Protocols"],
                Regulatory_Compliance = ["ICAO Standards", "FAA Regulations", "EASA Guidelines", "Auditing"],
                Safety_Management_Systems = ["Risk Analysis", "Safety Culture", "Human Factors in Aviation"]
                Autonomous_Robots = ["SLAM Algorithms", "Path Planning", "Vision-Based Control", "AI Integration"],
                Industrial_Robots = ["Robot Arm Design", "Pick and Place Systems", "End Effector Design"],
                Humanoid_Robotics = ["Locomotion", "Kinematics", "Artificial Skin", "Emotion Recognition"]
                Hydrogen_Energy = ["Fuel Cells", "Electrolysis Systems", "Hydrogen Storage", "Energy Conversion"],
                Energy_Systems_Modeling = ["Energy Economics", "Renewable Resource Assessment", "System Optimization"],
                Hybrid_Renewable_Systems = ["Wind-Solar Integration", "Battery Storage", "Grid-Tied Systems"]
                Remote_Sensing = ["Satellite Imagery", "LiDAR", "Multispectral Analysis", "Image Classification"],
                Geographic_Information_Systems = ["Spatial Analysis", "Cartography", "Geospatial Databases"],
                Surveying = ["GPS Technology", "Total Station Operation", "Topographic Mapping"]
                Vehicle_Control_Systems = ["ECU Programming", "ADAS Development", "Drive-by-Wire Systems"],
                Infotainment_Systems = ["HMI Design", "CarPlay Integration", "Audio Systems Development"],
                Connected_Cars = ["Telematics", "Vehicle-to-Vehicle Communication (V2V)", "OTA Updates"]
                Water_Distribution_Systems = ["Pipeline Design", "Pressure Management", "Leak Detection"],
                Irrigation_Systems = ["Sprinkler Design", "Drip Irrigation", "Canal Systems"],
                Flood_Management = ["Flood Risk Assessment", "Floodplain Mapping", "Reservoir Operations"]
                Tunnel_Design = ["Rock Tunneling", "TBM (Tunnel Boring Machines)", "Support Systems"],
                Underground_Structures = ["Subway Stations", "Underground Storage", "Cavern Design"],
                Geotechnical_Analysis = ["Ground Settlement", "Slope Stability", "Soil-Structure Interaction"]
                Bioreactor_Design = ["Scale-Up Processes", "Batch Reactors", "Continuous Fermentation"],
                Downstream_Processing = ["Protein Purification", "Filtration Systems", "Chromatography"],
                Enzyme_Technology = ["Immobilization Techniques", "Catalysis", "Enzyme Kinetics"]
          
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''
                rec_internship = ''
                
                ### condition starts to check skills from keywords and predict field
                for i in resume_data['skills']:
                
                    #### Software Development recommendation
                    if i.lower() in Software_Development_keyword:
                        print(i.lower())
                        reco_field = 'Software Development'
                        st.success("** Our analysis says you are looking software Development Jobs.**")
                        recommended_skills = ["Java", "Python", "JavaScript", "C++", "React.js", "Node.js", "Git", "Agile", "MySQL", "MongoDB", "Docker", "Kubernetes", "AWS", "RESTful APIs", "Unit Testing", "CI/CD", "Linux", "MVC", "Microservices", "Selenium", "Flutter", "React Native", "Jenkins", "SQL", "NoSQL", "DevOps", "Cloud Computing", "Version Control"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(Software_Development_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Software_Development_Virtual_Internship)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Web_development_Virtual_Internship)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Android_Development_Virtual_Internship) 
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(IOS_Development_Virtual_Internship) 
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(UI_UX_Development_Virtual_Internship) 
                        break
                    
                    #### CyberSecurity Recommendation
                    elif i.lower() in cybersecurity_keyword:
                        print(i.lower())
                        reco_field = 'Cyber-Security'
                        st.success("** Our analysis says you are looking for Cyber Security Jobs **")
                        recommended_skills = ['Network Security', 'Ethical Hacking', 'Firewalls', 'Intrusion Detection','Malware Analysis', 'Risk Assessment', 'Incident Response', 'Cryptography', 'Security Compliance', 'Penetration Testing']
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost 🚀 the chances of getting a Job 💼</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(cybersecurity_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Cyber_Security_Virtual_Internship) 
                        break
                    
                    #### Artificial Intelligence Recommendation
                    elif i.lower() in artificial_intelligence_keyword:
                        print(i.lower())
                        reco_field = 'Artificial Intelligence'
                        st.success("** Our analysis says you are looking for AI Engineer, Machine Learning Engineer, Data Scientist   Jobs **")
                        recommended_skills = ['Python', 'R', 'TensorFlow', 'Keras', 'PyTorch', 'Scikit-learn', 'Data Preprocessing', 'Data Visualization', 'Statistical Analysis', 'Linear Algebra', 'Calculus', 'Model Evaluation', 'Hyperparameter Tuning', 'Natural Language Processing', 'Image Processing', 'Big Data Technologies', 'SQL', 'Cloud Computing', 'Version Control (Git)', 'Team Collaboration']
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost 🚀 the chances of getting a Job 💼</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(artificial_intelligence_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Artificial_Intelligence_Virtual_Internship) 
                        break 
                         
                    #### Network Engineering Recommendation
                    elif i.lower() in network_engineering_keyword:
                        print(i.lower())
                        reco_field = 'Network Engineering'
                        st.success("** Our analysis says you are looking for Network Architect, Network Security Engineer, Wireless Network Engineer Jobs **")
                        recommended_skills = ["Network Protocols", "Routing and Switching", "Network Security", "Firewall Management", "VPN Configuration", "Subnetting", "Network Monitoring", "Load Balancing", "Troubleshooting", "Cisco IOS", "Wireless Networks", "SDN", "Cloud Networking", "VoIP", "Network Automation"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost 🚀 the chances of getting a Job 💼</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(network_engineering_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Network_Engineering_Virtual_Internship) 
                        break
                    
                    #### Cloud Computing Recommendation                
                    elif i.lower() in cloud_computing_keyword:
                        print(i.lower())
                        reco_field = 'Cloud Computing'
                        st.success("** Our analysis says you are looking for Cloud Solutions Architect, DevOps Engineer, Systems Engineer   Jobs **")
                        recommended_skills = ["Cloud Architecture", "Cloud Security", "Containerization", "Virtualization", "Networking", "DevOps", "Serverless Computing", "Automation", "Cloud Storage Management", "Cloud Migration", "API Management", "Monitoring and Logging", "Kubernetes", "AWS Services", "Azure Services", "Google Cloud Services", "Data Management", "Disaster Recovery", "Multi-Cloud Management"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost 🚀 the chances of getting a Job 💼</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(cloud_computing_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Cloud_Computing_Virtual_Internship) 
                        break
                    
                    #### Game Development Recommendation
                    elif i.lower() in game_development_keyword:
                        print(i.lower())
                        reco_field = 'Game Development'
                        st.success("** Our analysis says you are looking for Game Developer, Game Designer, Graphics Programmer Jobs **")
                        recommended_skills = ["Proficiency in Game Engines", "C# Programming (for Unity)", "C++ Programming (for Unreal Engine)", "3D Modeling and Animation", "Game Design Principles", "Level Design", "Artificial Intelligence Programming", "Physics Simulation", "Multiplayer Networking", "Version Control (e.g., Git)", "User Interface Design", "Game Monetization Strategies", "Sound Design", "Scripting and Gameplay Programming", "Problem Solving and Critical Thinking", "Project Management"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost 🚀 the chances of getting a Job 💼</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(game_development_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Game_Development_Virtual_Internship) 
                        break
                    
                    #### Virtual Reality (VR) and Augmented Reality (AR) Recommendation
                    elif i.lower() in vr_ar_keyword:
                        print(i.lower())
                        reco_field = 'Virtual Reality (VR) and Augmented Reality (AR)'
                        st.success("** Our analysis says you are looking for VR Developer, AR Developer Jobs **")
                        recommended_skills = ["3D Modeling", "Game Development", "Programming (C#, C++, Python)", "VR/AR Frameworks (ARKit, ARCore)", "UI/UX Design", "Computer Vision", "Creativity", "Problem-Solving", "Collaboration", "Adaptability", "Communication", "Research Skills", "Project Management", "Testing and Debugging", "Trends in VR/AR", "Market Understanding"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost 🚀 the chances of getting a Job 💼</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(vr_ar_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Virtual_Reality_Augmented_Reality_Virtual_Internship) 
                        break
                    
                    #### Data Science recommendation
                    elif i.lower() in Data_Science_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Big Data", "Hadoop", "Spark", "Tableau", "Power BI", "Data Wrangling", "Data Visualization", "Machine Learning", "Deep Learning", "Statistics", "Matplotlib", "Seaborn", "EDA", "Keras", "Time Series Analysis", "Natural Language Processing (NLP)", "Predictive Modeling"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(Data_Science_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Data_Science_Virtual_Internship)
                        break
                    
                    #### Blockchain Development recommendation
                    elif i.lower() in Blockchain_Development_keyword:
                        print(i.lower())
                        reco_field = 'Blockchain Development'
                        st.success("** Our analysis says you are looking for Blockchain Development Jobs.**")
                        recommended_skills = ["Solidity", "Ethereum", "Hyperledger", "Smart Contracts", "Cryptography", "Blockchain Architecture", "Node.js", "Web3.js", "Truffle", "Ganache", "IPFS", "Consensus Algorithms", "DApps", "Blockchain Security", "Cryptocurrency", "Distributed Systems", "Decentralized Finance (DeFi)"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(blockchain_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Blockchain_Development_Virtual_Internship) 
                        break
                    
                    #### DevOps recommendation
                    elif i.lower() in DevOps_keyword:
                        print(i.lower())
                        reco_field = 'DevOps'
                        st.success("** Our analysis says you are looking for DevOps Jobs.**")
                        recommended_skills = ["Linux", "Docker", "Kubernetes", "CI/CD", "Jenkins", "Terraform", "Ansible", "AWS", "Azure", "Google Cloud", "Python", "Bash Scripting", "Monitoring Tools", "CloudFormation", "Git", "Networking", "Agile Methodologies", "DevOps Culture", "Cloud Security", "Automation", "Configuration Management"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='11')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(devops_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(DevOps_Virtual_Internship) 
                        break
                    
                    #### Mobile App Development recommendation
                    elif i.lower() in Mobile_App_Development_keyword:
                        print(i.lower())
                        reco_field = 'Mobile App Development'
                        st.success("** Our analysis says you are looking for Mobile App Development Jobs.**")
                        recommended_skills = ["Java", "Kotlin", "Swift", "React Native", "Flutter", "iOS Development", "Android Development", "Firebase", "SQLite", "UI/UX Design", "APIs", "Git", "Mobile Testing", "App Optimization", "App Store Deployment", "Hybrid Apps", "Mobile Security"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='12')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(mobile_app_development_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Mobile_App_Development_Virtual_Internship)
                        break
                    
                    #### Digital Marketing recommendation
                    elif i.lower() in Digital_Marketing_keyword:
                        print(i.lower())
                        reco_field = 'Digital Marketing'
                        st.success("** Our analysis says you are looking for Digital Marketing Jobs.**")
                        recommended_skills = ["SEO", "SEM", "Content Marketing", "Google Analytics", "Social Media Marketing", "Email Marketing", "Google Ads", "Copywriting", "Keyword Research", "Pay-Per-Click (PPC)", "A/B Testing", "Marketing Automation", "Campaign Management", "Web Analytics", "Conversion Rate Optimization (CRO)", "Customer Relationship Management (CRM)", "Digital Strategy"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='13')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(digital_marketing_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Digital_Marketing_Virtual_Internship) 
                        break

                    #### Robotics recommendation
                    elif i.lower() in Robotics_keyword:
                        print(i.lower())
                        reco_field = 'Robotics'
                        st.success("** Our analysis says you are looking for Robotics Jobs.**")
                        recommended_skills = ["Robot Operating System (ROS)", "C++", "Python", "Mechanical Design", "Kinematics", "Actuators", "Embedded Systems", "Control Systems", "Sensors", "Computer Vision", "Path Planning", "AI", "Simulation Tools", "Mathematics", "Automation", "PLC Programming", "Robot Programming", "3D Modeling"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='14')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(robotics_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Robotics_Virtual_Internship) 
                        break

                    #### Machine Learning recommendation
                    elif i.lower() in Machine_Learning_keyword:
                        print(i.lower())
                        reco_field = 'Machine Learning'
                        st.success("** Our analysis says you are looking for Machine Learning Jobs.**")
                        recommended_skills = ["Python", "R", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Machine Learning Algorithms", "Data Cleaning", "Feature Engineering", "Big Data", "NLP", "Deep Learning", "Model Evaluation", "Hyperparameter Tuning", "Mathematics", "Statistics", "Pandas", "NumPy", "Data Visualization"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='15')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(machine_learning_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Machine_Learning_Virtual_Internship) 
                        break

                    #### Embedded Systems recommendation
                    elif i.lower() in Embedded_Systems_keyword:
                        print(i.lower())
                        reco_field = 'Embedded Systems'
                        st.success("** Our analysis says you are looking for Embedded Systems Jobs.**")
                        recommended_skills = ["C", "C++", "Assembly Language", "Microcontrollers", "RTOS", "Embedded C", "IoT", "PCB Design", "Debugging Tools", "Sensor Integration", "Embedded Linux", "Firmware Development", "CAN Protocol", "SPI/I2C", "Low-Level Programming", "Electronics", "System Design", "Hardware Security"]
                        recommended_keyword = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System', value=recommended_skills, key='16')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(embedded_systems_course)
                        # Virtual Internship recommendation
                        rec_internship = Virtual_Internship_recommender(Embedded_Systems_Virtual_Internship) 
                        break
                    
                    #### Thermal Engineering recommendation
                    if i.lower() in Thermal_Engineering:
                       print(i.lower())
                       reco_field = 'Thermal Engineering'
                       st.success("** Our analysis says you are looking for Thermal Engineering Jobs.**")
                       recommended_skills = ["Thermodynamics", "Heat Transfer", "Refrigeration", "Air Conditioning", "Power Plants"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System',value=recommended_skills, key='thermal_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Fluid Mechanics recommendation
                    if i.lower() in Fluid_Mechanics:
                       print(i.lower())
                       reco_field = 'Fluid Mechanics'
                       st.success("** Our analysis says you are looking for Fluid Mechanics Jobs.**")
                       recommended_skills = ["Hydrodynamics", "CFD", "Pipe Flow", "Open Channel Flow", "Pumps", "Turbines"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='fluid_mechanics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Robotics and Automation recommendation
                    if i.lower() in Robotics_and_Automation:
                       print(i.lower())
                       reco_field = 'Robotics and Automation'
                       st.success("** Our analysis says you are looking for Robotics and Automation Jobs.**")
                       recommended_skills = ["Industrial Robotics", "Mechatronics", "PLC", "Control Systems", "Sensors"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.', 
                       text='Recommended skills generated from System', value=recommended_skills, key='robotics_automation')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Design and Manufacturing recommendation
                    if i.lower() in Design_and_Manufacturing:
                       print(i.lower())
                       reco_field = 'Design and Manufacturing'
                       st.success("** Our analysis says you are looking for Design and Manufacturing Jobs.**")
                       recommended_skills = ["SolidWorks", "AutoCAD", "CATIA", "CNC", "3D Printing", "Product Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='design_manufacturing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Automobile Engineering recommendation
                    if i.lower() in Automobile_Engineering:
                       print(i.lower())
                       reco_field = 'Automobile Engineering'
                       st.success("** Our analysis says you are looking for Automobile Engineering Jobs.**")
                       recommended_skills = ["Vehicle Dynamics", "Engine Design", "Automotive Electronics", "Chassis Design", "Emission Control"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='automobile_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Power Systems recommendation
                    if i.lower() in Power_Systems:
                       print(i.lower())
                       reco_field = 'Power Systems'
                       st.success("** Our analysis says you are looking for Power Systems Jobs.**")
                       recommended_skills = ["Grid Systems", "Transmission Lines", "Power Distribution", "Load Analysis", "Renewable Integration"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='power_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Control Systems recommendation
                    if i.lower() in Control_Systems:
                       print(i.lower())
                       reco_field = 'Control Systems'
                       st.success("** Our analysis says you are looking for Control Systems Jobs.**")
                       recommended_skills = ["PID Controllers", "Mathematical Modeling", "State Space", "Feedback Systems", "Automation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='control_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Electrical Machines recommendation
                    if i.lower() in Electrical_Machines:
                       print(i.lower())
                       reco_field = 'Electrical Machines'
                       st.success("** Our analysis says you are looking for Electrical Machines Jobs.**")
                       recommended_skills = ["Transformers", "Motors", "Generators", "Induction Machines", "DC Machines"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='electrical_machines')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Signal Processing recommendation
                    if i.lower() in Signal_Processing:
                       print(i.lower())
                       reco_field = 'Signal Processing'
                       st.success("** Our analysis says you are looking for Signal Processing Jobs.**")
                       recommended_skills = ["Fourier Transform", "Wavelets", "Filtering", "Digital Signal Processing", "Spectral Analysis"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='signal_processing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Renewable Energy recommendation
                    if i.lower() in Renewable_Energy:
                       print(i.lower())
                       reco_field = 'Renewable Energy'
                       st.success("** Our analysis says you are looking for Renewable Energy Jobs.**")
                       recommended_skills = ["Solar Power", "Wind Energy", "Battery Systems", "Hydropower", "Energy Storage"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='renewable_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Structural Engineering recommendation
                    if i.lower() in Structural_Engineering:
                       print(i.lower())
                       reco_field = 'Structural Engineering'
                       st.success("** Our analysis says you are looking for Structural Engineering Jobs.**")
                       recommended_skills = ["STAAD Pro", "RCC Design", "Steel Structures", "Earthquake Engineering", "Bridge Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='structural_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Geotechnical Engineering recommendation
                    if i.lower() in Geotechnical_Engineering:
                       print(i.lower())
                       reco_field = 'Geotechnical Engineering'
                       st.success("** Our analysis says you are looking for Geotechnical Engineering Jobs.**")
                       recommended_skills = ["Soil Mechanics", "Foundation Design", "Slope Stability", "Earth Retaining Structures"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='geotechnical_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Environmental Engineering recommendation
                    if i.lower() in Environmental_Engineering:
                       print(i.lower())
                       reco_field = 'Environmental Engineering'
                       st.success("** Our analysis says you are looking for Environmental Engineering Jobs.**")
                       recommended_skills = ["Water Treatment", "Air Pollution Control", "Sustainability", "Solid Waste Management"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='environmental_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break
                    
                    #### Transportation Engineering recommendation
                    if i.lower() in Transportation_Engineering:
                       print(i.lower())
                       reco_field = 'Transportation Engineering'
                       st.success("** Our analysis says you are looking for Transportation Engineering Jobs.**")
                       recommended_skills = ["Traffic Analysis", "Pavement Design", "Highway Engineering", "Urban Planning"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='transportation_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break
                    
                    #### Construction Management recommendation
                    if i.lower() in Construction_Management:
                       print(i.lower())
                       reco_field = 'Construction Management'
                       st.success("** Our analysis says you are looking for Construction Management Jobs.**")
                       recommended_skills = ["Project Scheduling", "Quantity Surveying", "Cost Estimation", "Construction Safety"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='construction_management')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Embedded Systems recommendation
                    if i.lower() in Embedded_Systems:
                       print(i.lower())
                       reco_field = 'Embedded Systems'
                       st.success("** Our analysis says you are looking for Embedded Systems Jobs.**")
                       recommended_skills = ["Microcontrollers", "Arduino", "Raspberry Pi", "Real-Time Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='embedded_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### VLSI Design recommendation
                    if i.lower() in VLSI_Design:
                       print(i.lower())
                       reco_field = 'VLSI Design'
                       st.success("** Our analysis says you are looking for VLSI Design Jobs.**")
                       recommended_skills = ["HDL", "FPGA", "ASIC", "Semiconductor Devices"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='vlsi_design')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Digital Signal Processing recommendation
                    if i.lower() in Digital_Signal_Processing:
                       print(i.lower())
                       reco_field = 'Digital Signal Processing'
                       st.success("** Our analysis says you are looking for Digital Signal Processing Jobs.**")
                       recommended_skills = ["DSP Algorithms", "Filter Design", "Wavelets", "Image Processing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='digital_signal_processing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Internet of Things (IoT) recommendation
                    if i.lower() in Internet_of_Things:
                       print(i.lower())
                       reco_field = 'Internet of Things'
                       st.success("** Our analysis says you are looking for Internet of Things Jobs.**")
                       recommended_skills = ["IoT Sensors", "MQTT", "Edge Computing", "Home Automation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='internet_of_things')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Telecommunications recommendation
                    if i.lower() in Telecommunications:
                       print(i.lower())
                       reco_field = 'Telecommunications'
                       st.success("** Our analysis says you are looking for Telecommunications Jobs.**")
                       recommended_skills = ["Wireless Communication", "5G", "Optical Networks", "Satellite Communication"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='telecommunications')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Process Engineering recommendation
                    if i.lower() in Process_Engineering:
                       print(i.lower())
                       reco_field = 'Process Engineering'
                       st.success("** Our analysis says you are looking for Process Engineering Jobs.**")
                       recommended_skills = ["Heat Exchangers", "Distillation", "Fluidized Beds", "Process Control"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='process_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Biochemical Engineering recommendation
                    if i.lower() in Biochemical_Engineering:
                       print(i.lower())
                       reco_field = 'Biochemical Engineering'
                       st.success("** Our analysis says you are looking for Biochemical Engineering Jobs.**")
                       recommended_skills = ["Fermentation", "Bioreactors", "Enzyme Technology"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='biochemical_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Petroleum and Petrochemical Engineering recommendation
                    if i.lower() in Petroleum_and_Petrochemical_Engineering:
                       print(i.lower())
                       reco_field = 'Petroleum and Petrochemical Engineering'
                       st.success("** Our analysis says you are looking for Petroleum and Petrochemical Engineering Jobs.**")
                       recommended_skills = ["Crude Oil Processing", "Natural Gas", "Downstream Operations"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='petroleum_petrochemical_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Materials Science recommendation
                    if i.lower() in Materials_Science:
                       print(i.lower())
                       reco_field = 'Materials Science'
                       st.success("** Our analysis says you are looking for Materials Science Jobs.**")
                       recommended_skills = ["Polymers", "Composites", "Metallurgy", "Nanomaterials"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='materials_science')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Aerodynamics recommendation
                    if i.lower() in Aerodynamics:
                       print(i.lower())
                       reco_field = 'Aerodynamics'
                       st.success("** Our analysis says you are looking for Aerodynamics Jobs.**")
                       recommended_skills = ["Flow Dynamics", "Aircraft Design", "Wind Tunnel Testing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='aerodynamics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Propulsion Systems recommendation
                    if i.lower() in Propulsion_Systems:
                       print(i.lower())
                       reco_field = 'Propulsion Systems'
                       st.success("** Our analysis says you are looking for Propulsion Systems Jobs.**")
                       recommended_skills = ["Jet Engines", "Rocket Engines", "Turbochargers"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='propulsion_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Avionics recommendation
                    if i.lower() in Avionics:
                       print(i.lower())
                       reco_field = 'Avionics'
                       st.success("** Our analysis says you are looking for Avionics Jobs.**")
                       recommended_skills = ["Flight Control Systems", "Navigation", "Radar Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='avionics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Spacecraft Design recommendation
                    if i.lower() in Spacecraft_Design:
                       print(i.lower())
                       reco_field = 'Spacecraft Design'
                       st.success("** Our analysis says you are looking for Spacecraft Design Jobs.**")
                       recommended_skills = ["Orbital Mechanics", "Satellite Systems", "Space Propulsion"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='spacecraft_design')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break
           
                    #### Medical Imaging recommendation
                    if i.lower() in Medical_Imaging:
                       print(i.lower())
                       reco_field = 'Medical Imaging'
                       st.success("** Our analysis says you are looking for Medical Imaging Jobs.**")
                       recommended_skills = ["MRI", "CT Scans", "Ultrasound"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='medical_imaging')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Biomaterials recommendation
                    if i.lower() in Biomaterials:
                       print(i.lower())
                       reco_field = 'Biomaterials'
                       st.success("** Our analysis says you are looking for Biomaterials Jobs.**")
                       recommended_skills = ["Prosthetics", "Bioimplants", "Tissue Engineering"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='biomaterials')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Biomechanics recommendation
                    if i.lower() in Biomechanics:
                       print(i.lower())
                       reco_field = 'Biomechanics'
                       st.success("** Our analysis says you are looking for Biomechanics Jobs.**")
                       recommended_skills = ["Rehabilitation Devices", "Ergonomics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='biomechanics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Healthcare Device Development recommendation
                    if i.lower() in Healthcare_Device_Development:
                       print(i.lower())
                       reco_field = 'Healthcare Device Development'
                       st.success("** Our analysis says you are looking for Healthcare Device Development Jobs.**")
                       recommended_skills = ["Wearable Technology", "Diagnostic Tools"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='healthcare_device_development')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Waste Management recommendation
                    if i.lower() in Waste_Management:
                       print(i.lower())
                       reco_field = 'Waste Management'
                       st.success("** Our analysis says you are looking for Waste Management Jobs.**")
                       recommended_skills = ["Recycling", "Landfills", "Hazardous Waste"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='waste_management')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Water Resources Engineering recommendation
                    if i.lower() in Water_Resources_Engineering:
                       print(i.lower())
                       reco_field = 'Water Resources Engineering'
                       st.success("** Our analysis says you are looking for Water Resources Engineering Jobs.**")
                       recommended_skills = ["Hydrology", "Water Treatment", "Irrigation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='water_resources_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Climate Change Mitigation recommendation
                    if i.lower() in Climate_Change_Mitigation:
                       print(i.lower())
                       reco_field = 'Climate Change Mitigation'
                       st.success("** Our analysis says you are looking for Climate Change Mitigation Jobs.**")
                       recommended_skills = ["Carbon Capture", "Sustainability", "Environmental Policy"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='climate_change_mitigation')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Sustainable Energy recommendation
                    if i.lower() in Sustainable_Energy:
                       print(i.lower())
                       reco_field = 'Sustainable Energy'
                       st.success("** Our analysis says you are looking for Sustainable Energy Jobs.**")
                       recommended_skills = ["Solar Energy", "Wind Energy", "Hydropower"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='sustainable_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Lean Manufacturing recommendation
                    if i.lower() in Lean_Manufacturing:
                       print(i.lower())
                       reco_field = 'Lean Manufacturing'
                       st.success("** Our analysis says you are looking for Lean Manufacturing Jobs.**")
                       recommended_skills = ["5S", "Kanban", "Waste Reduction", "Just-in-Time"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='lean_manufacturing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Operations Research recommendation
                    if i.lower() in Operations_Research:
                       print(i.lower())
                       reco_field = 'Operations Research'
                       st.success("** Our analysis says you are looking for Operations Research Jobs.**")
                       recommended_skills = ["Linear Programming", "Optimization Models", "Simulation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='operations_research')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Supply Chain Management recommendation
                    if i.lower() in Supply_Chain_Management:
                       print(i.lower())
                       reco_field = 'Supply Chain Management'
                       st.success("** Our analysis says you are looking for Supply Chain Management Jobs.**")
                       recommended_skills = ["Inventory Control", "Logistics Planning", "Demand Forecasting"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='supply_chain_management')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Quality Control recommendation
                    if i.lower() in Quality_Control:
                       print(i.lower())
                       reco_field = 'Quality Control'
                       st.success("** Our analysis says you are looking for Quality Control Jobs.**")
                       recommended_skills = ["Six Sigma", "Statistical Process Control", "ISO Standards"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='quality_control')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Nanomaterials recommendation
                    if i.lower() in Nanomaterials:
                       print(i.lower())
                       reco_field = 'Nanomaterials'
                       st.success("** Our analysis says you are looking for Nanomaterials Jobs.**")
                       recommended_skills = ["Graphene", "Carbon Nanotubes", "Quantum Dots"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='nanomaterials')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    
                    #### Nanofabrication recommendation
                    if i.lower() in Nanofabrication:
                       print(i.lower())
                       reco_field = 'Nanofabrication'
                       st.success("** Our analysis says you are looking for Nanofabrication Jobs.**")
                       recommended_skills = ["Electron Beam Lithography", "Thin Film Deposition"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='nanofabrication')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Applications of Nanotechnology recommendation
                    if i.lower() in Applications:
                       print(i.lower())
                       reco_field = 'Applications of Nanotechnology'
                       st.success("** Our analysis says you are looking for Applications of Nanotechnology Jobs.**")
                       recommended_skills = ["Nanoelectronics", "Nanosensors", "Drug Delivery Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='applications_nanotechnology')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Solar Energy recommendation
                    if i.lower() in Solar_Energy:
                       print(i.lower())
                       reco_field = 'Solar Energy'
                       st.success("** Our analysis says you are looking for Solar Energy Jobs.**")
                       recommended_skills = ["PV Panel Installation", "Solar Cell Design", "Net Metering"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='solar_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Wind Energy recommendation
                    if i.lower() in Wind_Energy:
                       print(i.lower())
                       reco_field = 'Wind Energy'
                       st.success("** Our analysis says you are looking for Wind Energy Jobs.**")
                       recommended_skills = ["Wind Turbine Components", "Energy Yield Analysis", "Offshore Wind Farms"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='wind_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Hydropower recommendation
                    if i.lower() in Hydropower:
                       print(i.lower())
                       reco_field = 'Hydropower'
                       st.success("** Our analysis says you are looking for Hydropower Jobs.**")
                       recommended_skills = ["Small Hydropower Plants", "Turbine Selection", "Hydraulic Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='hydropower')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Energy Storage recommendation
                    if i.lower() in Energy_Storage:
                       print(i.lower())
                       reco_field = 'Energy Storage'
                       st.success("** Our analysis says you are looking for Energy Storage Jobs.**")
                       recommended_skills = ["Battery Chemistry", "Energy Management Systems", "Grid Integration"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='energy_storage')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Metallurgy recommendation
                    if i.lower() in Metallurgy:
                       print(i.lower())
                       reco_field = 'Metallurgy'
                       st.success("** Our analysis says you are looking for Metallurgy Jobs.**")
                       recommended_skills = ["Alloy Design", "Heat Treatment", "Phase Transformations", "Metal Testing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='metallurgy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Polymers recommendation
                    if i.lower() in Polymers:
                       print(i.lower())
                       reco_field = 'Polymers'
                       st.success("** Our analysis says you are looking for Polymers Jobs.**")
                       recommended_skills = ["Polymer Synthesis", "Composite Materials", "Thermoplastics", "Elastomers"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='polymers')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Ceramics recommendation
                    if i.lower() in Ceramics:
                       print(i.lower())
                       reco_field = 'Ceramics'
                       st.success("** Our analysis says you are looking for Ceramics Jobs.**")
                       recommended_skills = ["Ceramic Processing", "Thermal Conductivity", "Piezoelectric Materials", "Refractories"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='ceramics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Naval Architecture recommendation
                    if i.lower() in Naval_Architecture:
                       print(i.lower())
                       reco_field = 'Naval Architecture'
                       st.success("** Our analysis says you are looking for Naval Architecture Jobs.**")
                       recommended_skills = ["Ship Design", "Hydrostatics", "Stability Analysis", "Marine Hydrodynamics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='naval_architecture')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Marine Machinery recommendation
                    if i.lower() in Marine_Machinery:
                       print(i.lower())
                       reco_field = 'Marine Machinery'
                       st.success("** Our analysis says you are looking for Marine Machinery Jobs.**")
                       recommended_skills = ["Propulsion Systems", "Diesel Engines", "Turbomachinery", "Piping Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='marine_machinery')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Ocean Engineering recommendation
                    if i.lower() in Ocean_Engineering:
                       print(i.lower())
                       reco_field = 'Ocean Engineering'
                       st.success("** Our analysis says you are looking for Ocean Engineering Jobs.**")
                       recommended_skills = ["Underwater Vehicles", "Ocean Energy", "Marine Structures", "Offshore Platforms"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='ocean_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Mine Planning recommendation
                    if i.lower() in Mine_Planning:
                       print(i.lower())
                       reco_field = 'Mine Planning'
                       st.success("** Our analysis says you are looking for Mine Planning Jobs.**")
                       recommended_skills = ["Geostatistics", "Mine Safety", "Open Pit Design", "Underground Mining"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='mine_planning')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Mineral Processing recommendation
                    if i.lower() in Mineral_Processing:
                       print(i.lower())
                       reco_field = 'Mineral Processing'
                       st.success("** Our analysis says you are looking for Mineral Processing Jobs.**")
                       recommended_skills = ["Crushing and Grinding", "Flotation", "Gravity Separation", "Dewatering"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='mineral_processing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Mining Equipment recommendation
                    if i.lower() in Mining_Equipment:
                       print(i.lower())
                       reco_field = 'Mining Equipment'
                       st.success("** Our analysis says you are looking for Mining Equipment Jobs.**")
                       recommended_skills = ["Drilling Machines", "Excavators", "Haul Trucks", "Automation in Mining"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='mining_equipment')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Farm Machinery recommendation
                    if i.lower() in Farm_Machinery:
                       print(i.lower())
                       reco_field = 'Farm Machinery'
                       st.success("** Our analysis says you are looking for Farm Machinery Jobs.**")
                       recommended_skills = ["Tractor Design", "Irrigation Systems", "Harvesting Equipment", "Precision Agriculture"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='farm_machinery')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Soil Science recommendation
                    if i.lower() in Soil_Science:
                       print(i.lower())
                       reco_field = 'Soil Science'
                       st.success("** Our analysis says you are looking for Soil Science Jobs.**")
                       recommended_skills = ["Soil Fertility", "Soil Erosion Control", "Soil Mechanics", "Soil Testing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='soil_science')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Food Processing recommendation
                    if i.lower() in Food_Processing:
                       print(i.lower())
                       reco_field = 'Food Processing'
                       st.success("** Our analysis says you are looking for Food Processing Jobs.**")
                       recommended_skills = ["Post-Harvest Technology", "Food Preservation", "Packaging Technology", "Cold Storage"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='food_processing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Textile Manufacturing recommendation
                    if i.lower() in Textile_Manufacturing:
                       print(i.lower())
                       reco_field = 'Textile Manufacturing'
                       st.success("** Our analysis says you are looking for Textile Manufacturing Jobs.**")
                       recommended_skills = ["Yarn Production", "Weaving", "Knitting", "Dyeing and Printing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='textile_manufacturing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Textile Materials recommendation
                    if i.lower() in Textile_Materials:
                       print(i.lower())
                       reco_field = 'Textile Materials'
                       st.success("** Our analysis says you are looking for Textile Materials Jobs.**")
                       recommended_skills = ["Natural Fibers", "Synthetic Fibers", "Blended Fabrics", "Non-Woven Materials"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='textile_materials')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Technical Textiles recommendation
                    if i.lower() in Technical_Textiles:
                       print(i.lower())
                       reco_field = 'Technical Textiles'
                       st.success("** Our analysis says you are looking for Technical Textiles Jobs.**")
                       recommended_skills = ["Geo-textiles", "Medical Textiles", "Smart Textiles", "Protective Clothing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='technical_textiles')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Reservoir Engineering recommendation
                    if i.lower() in Reservoir_Engineering:
                       print(i.lower())
                       reco_field = 'Reservoir Engineering'
                       st.success("** Our analysis says you are looking for Reservoir Engineering Jobs.**")
                       recommended_skills = ["Reservoir Simulation", "Enhanced Oil Recovery", "PVT Analysis", "Reservoir Management"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='reservoir_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Drilling Engineering recommendation
                    if i.lower() in Drilling_Engineering:
                       print(i.lower())
                       reco_field = 'Drilling Engineering'
                       st.success("** Our analysis says you are looking for Drilling Engineering Jobs.**")
                       recommended_skills = ["Drilling Fluids", "Directional Drilling", "Well Control", "Casing Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='drilling_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Production Engineering recommendation
                    if i.lower() in Production_Engineering:
                       print(i.lower())
                       reco_field = 'Production Engineering'
                       st.success("** Our analysis says you are looking for Production Engineering Jobs.**")
                       recommended_skills = ["Well Stimulation", "Artificial Lift", "Production Optimization", "Subsea Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='production_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Energy Efficiency recommendation
                    if i.lower() in Energy_Efficiency:
                       print(i.lower())
                       reco_field = 'Energy Efficiency'
                       st.success("** Our analysis says you are looking for Energy Efficiency Jobs.**")
                       recommended_skills = ["Building Energy Management", "Smart Grids", "Energy Auditing", "Demand-Side Management"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='energy_efficiency')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Sustainable Energy recommendation
                    if i.lower() in Sustainable_Energy:
                       print(i.lower())
                       reco_field = 'Sustainable Energy'
                       st.success("** Our analysis says you are looking for Sustainable Energy Jobs.**")
                       recommended_skills = ["Geothermal Energy", "Biomass", "Tidal Energy", "Fuel Cells"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='sustainable_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Energy Systems recommendation
                    if i.lower() in Energy_Systems:
                       print(i.lower())
                       reco_field = 'Energy Systems'
                       st.success("** Our analysis says you are looking for Energy Systems Jobs.**")
                       recommended_skills = ["Power Conversion", "Energy Policy", "Thermal Energy Storage", "Hybrid Energy Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='energy_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Electric Vehicles recommendation
                    if i.lower() in Electric_Vehicles:
                       print(i.lower())
                       reco_field = 'Electric Vehicles'
                       st.success("** Our analysis says you are looking for Electric Vehicles Jobs.**")
                       recommended_skills = ["Battery Management Systems", "EV Charging Stations", "Electric Motors", "Power Electronics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='electric_vehicles')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Autonomous Vehicles recommendation
                    if i.lower() in Autonomous_Vehicles:
                       print(i.lower())
                       reco_field = 'Autonomous Vehicles'
                       st.success("** Our analysis says you are looking for Autonomous Vehicles Jobs.**")
                       recommended_skills = ["ADAS", "Lidar", "Sensor Fusion", "Autonomous Navigation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='autonomous_vehicles')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Vehicle Safety recommendation
                    if i.lower() in Vehicle_Safety:
                       print(i.lower())
                       reco_field = 'Vehicle Safety'
                       st.success("** Our analysis says you are looking for Vehicle Safety Jobs.**")
                       recommended_skills = ["Crash Analysis", "Airbag Systems", "Traction Control", "Braking Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='vehicle_safety')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Industrial IoT recommendation
                    if i.lower() in Industrial_IoT:
                       print(i.lower())
                       reco_field = 'Industrial IoT'
                       st.success("** Our analysis says you are looking for Industrial IoT Jobs.**")
                       recommended_skills = ["Smart Sensors", "Edge Computing", "Digital Twins", "Predictive Maintenance"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='industrial_iot')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Robotic Process Automation recommendation
                    if i.lower() in Robotic_Process_Automation:
                       print(i.lower())
                       reco_field = 'Robotic Process Automation'
                       st.success("** Our analysis says you are looking for Robotic Process Automation Jobs.**")
                       recommended_skills = ["Robotic Arms", "Motion Control", "Path Planning", "Industrial Robotics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='robotic_process_automation')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Automation Tools recommendation
                    if i.lower() in Automation_Tools:
                       print(i.lower())
                       reco_field = 'Automation Tools'
                       st.success("** Our analysis says you are looking for Automation Tools Jobs.**")
                       recommended_skills = ["SCADA", "HMI", "DCS", "Programmable Logic Controllers (PLC)"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='automation_tools')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Optoelectronics recommendation
                    if i.lower() in Optoelectronics:
                       print(i.lower())
                       reco_field = 'Optoelectronics'
                       st.success("** Our analysis says you are looking for Optoelectronics Jobs.**")
                       recommended_skills = ["Laser Design", "Fiber Optics", "Photon Detectors", "LED Technology"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='optoelectronics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Optical Communication recommendation
                    if i.lower() in Optical_Communication:
                       print(i.lower())
                       reco_field = 'Optical Communication'
                       st.success("** Our analysis says you are looking for Optical Communication Jobs.**")
                       recommended_skills = ["Waveguide Design", "Optical Amplifiers", "Free-Space Optics", "Optical Networks"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='optical_communication')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Imaging Systems recommendation
                    if i.lower() in Imaging_Systems:
                       print(i.lower())
                       reco_field = 'Imaging Systems'
                       st.success("** Our analysis says you are looking for Imaging Systems Jobs.**")
                       recommended_skills = ["Holography", "Microscopy", "Remote Sensing", "Infrared Imaging"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='imaging_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Nuclear Reactor Design recommendation
                    if i.lower() in Nuclear_Reactor_Design:
                       print(i.lower())
                       reco_field = 'Nuclear Reactor Design'
                       st.success("** Our analysis says you are looking for Nuclear Reactor Design Jobs.**")
                       recommended_skills = ["Thermal Reactors", "Fast Reactors", "Neutron Moderation", "Reactor Safety"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='nuclear_reactor_design')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Radiation Protection recommendation
                    if i.lower() in Radiation_Protection:
                       print(i.lower())
                       reco_field = 'Radiation Protection'
                       st.success("** Our analysis says you are looking for Radiation Protection Jobs.**")
                       recommended_skills = ["Dosimetry", "Shielding Design", "Nuclear Waste Management", "Radiation Monitoring"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='radiation_protection')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Fusion Energy recommendation
                    if i.lower() in Fusion_Energy:
                       print(i.lower())
                       reco_field = 'Fusion Energy'
                       st.success("** Our analysis says you are looking for Fusion Energy Jobs.**")
                       recommended_skills = ["Plasma Physics", "Tokamak Design", "Magnetic Confinement", "Fusion Materials"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='fusion_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Geophysics recommendation
                    if i.lower() in Geophysics:
                       print(i.lower())
                       reco_field = 'Geophysics'
                       st.success("** Our analysis says you are looking for Geophysics Jobs.**")
                       recommended_skills = ["Seismic Surveying", "Gravity and Magnetic Analysis", "Well Logging", "Geophysical Data Processing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='geophysics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Hydrogeology recommendation
                    if i.lower() in Hydrogeology:
                       print(i.lower())
                       reco_field = 'Hydrogeology'
                       st.success("** Our analysis says you are looking for Hydrogeology Jobs.**")
                       recommended_skills = ["Groundwater Flow", "Aquifer Testing", "Contaminant Transport", "Hydrogeological Modeling"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='hydrogeology')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Engineering Geology recommendation
                    if i.lower() in Engineering_Geology:
                       print(i.lower())
                       reco_field = 'Engineering Geology'
                       st.success("** Our analysis says you are looking for Engineering Geology Jobs.**")
                       recommended_skills = ["Rock Mechanics", "Slope Stability", "Site Investigation", "Geological Hazard Assessment"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='engineering_geology')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Measurement Systems recommendation
                    if i.lower() in Measurement_Systems:
                       print(i.lower())
                       reco_field = 'Measurement Systems'
                       st.success("** Our analysis says you are looking for Measurement Systems Jobs.**")
                       recommended_skills = ["Sensors", "Transducers", "Signal Conditioning", "Data Acquisition Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='measurement_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Process Instrumentation recommendation
                    if i.lower() in Process_Instrumentation:
                       print(i.lower())
                       reco_field = 'Process Instrumentation'
                       st.success("** Our analysis says you are looking for Process Instrumentation Jobs.**")
                       recommended_skills = ["Flow Meters", "Pressure Sensors", "Temperature Controllers", "Analytical Instruments"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='process_instrumentation')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Environmental Engineering recommendation
                    if i.lower() in Environmental_Engineering:
                       print(i.lower())
                       reco_field = 'Environmental Engineering'
                       st.success("** Our analysis says you are looking for Environmental Engineering Jobs.**")
                       recommended_skills = ["Water Treatment", "Air Pollution Control", "Sustainability", "Solid Waste Management"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='environmental_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Transportation Engineering recommendation
                    if i.lower() in Transportation_Engineering:
                       print(i.lower())
                       reco_field = 'Transportation Engineering'
                       st.success("** Our analysis says you are looking for Transportation Engineering Jobs.**")
                       recommended_skills = ["Traffic Analysis", "Pavement Design", "Highway Engineering", "Urban Planning"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='transportation_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Construction Management recommendation
                    if i.lower() in Construction_Management:
                       print(i.lower())
                       reco_field = 'Construction Management'
                       st.success("** Our analysis says you are looking for Construction Management Jobs.**")
                       recommended_skills = ["Project Scheduling", "Quantity Surveying", "Cost Estimation", "Construction Safety"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='construction_management')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Embedded Systems recommendation
                    if i.lower() in Embedded_Systems:
                       print(i.lower())
                       reco_field = 'Embedded Systems'
                       st.success("** Our analysis says you are looking for Embedded Systems Jobs.**")
                       recommended_skills = ["Microcontrollers", "Arduino", "Raspberry Pi", "Real-Time Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='embedded_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Aircraft Maintenance recommendation
                    if i.lower() in Aircraft_Maintenance:
                       print(i.lower())
                       reco_field = 'Aircraft Maintenance'
                       st.success("** Our analysis says you are looking for Aircraft Maintenance Jobs.**")
                       recommended_skills = ["Airframe Repair", "Engine Overhaul", "Avionics Testing", "Maintenance Scheduling"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='aircraft_maintenance')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Flight Mechanics recommendation
                    if i.lower() in Flight_Mechanics:
                       print(i.lower())
                       reco_field = 'Flight Mechanics'
                       st.success("** Our analysis says you are looking for Flight Mechanics Jobs.**")
                       recommended_skills = ["Performance Analysis", "Flight Dynamics", "Control Surfaces", "Aircraft Stability"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='flight_mechanics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Airport Management recommendation
                    if i.lower() in Airport_Management:
                       print(i.lower())
                       reco_field = 'Airport Management'
                       st.success("** Our analysis says you are looking for Airport Management Jobs.**")
                       recommended_skills = ["Air Traffic Control", "Runway Design", "Aircraft Scheduling", "Passenger Services"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='airport_management')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Extractive Metallurgy recommendation
                    if i.lower() in Extractive_Metallurgy:
                       print(i.lower())
                       reco_field = 'Extractive Metallurgy'
                       st.success("** Our analysis says you are looking for Extractive Metallurgy Jobs.**")
                       recommended_skills = ["Ore Processing", "Hydrometallurgy", "Pyrometallurgy", "Electrometallurgy"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='extractive_metallurgy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Physical Metallurgy recommendation
                    if i.lower() in Physical_Metallurgy:
                       print(i.lower())
                       reco_field = 'Physical Metallurgy'
                       st.success("** Our analysis says you are looking for Physical Metallurgy Jobs.**")
                       recommended_skills = ["Phase Diagrams", "Heat Treatment", "Mechanical Testing", "Failure Analysis"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='physical_metallurgy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Process Metallurgy recommendation
                    if i.lower() in Process_Metallurgy:
                       print(i.lower())
                       reco_field = 'Process Metallurgy'
                       st.success("** Our analysis says you are looking for Process Metallurgy Jobs.**")
                       recommended_skills = ["Casting", "Rolling", "Forging", "Welding"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='process_metallurgy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Acoustics Design recommendation
                    if i.lower() in Acoustics_Design:
                       print(i.lower())
                       reco_field = 'Acoustics Design'
                       st.success("** Our analysis says you are looking for Acoustics Design Jobs.**")
                       recommended_skills = ["Noise Control", "Soundproofing", "Echo Reduction", "Building Acoustics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='acoustics_design')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Audio Engineering recommendation
                    if i.lower() in Audio_Engineering:
                       print(i.lower())
                       reco_field = 'Audio Engineering'
                       st.success("** Our analysis says you are looking for Audio Engineering Jobs.**")
                       recommended_skills = ["Signal Processing", "Microphone Arrays", "Speaker Design", "Room Acoustics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='audio_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Vibration Analysis recommendation
                    if i.lower() in Vibration_Analysis:
                       print(i.lower())
                       reco_field = 'Vibration Analysis'
                       st.success("** Our analysis says you are looking for Vibration Analysis Jobs.**")
                       recommended_skills = ["Modal Analysis", "Damping Techniques", "Vibration Isolation", "Dynamic Testing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='vibration_analysis')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Systems Integration recommendation
                    if i.lower() in Systems_Integration:
                       print(i.lower())
                       reco_field = 'Systems Integration'
                       st.success("** Our analysis says you are looking for Systems Integration Jobs.**")
                       recommended_skills = ["Flight Software", "Payload Systems", "Spacecraft Operations"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='systems_integration')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Satellite Technology recommendation
                    if i.lower() in Satellite_Technology:
                       print(i.lower())
                       reco_field = 'Satellite Technology'
                       st.success("** Our analysis says you are looking for Satellite Technology Jobs.**")
                       recommended_skills = ["Remote Sensing", "Orbit Mechanics", "Telemetry Systems", "Ground Stations"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='satellite_technology')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Aerospace Materials recommendation
                    if i.lower() in Aerospace_Materials:
                       print(i.lower())
                       reco_field = 'Aerospace Materials'
                       st.success("** Our analysis says you are looking for Aerospace Materials Jobs.**")
                       recommended_skills = ["Lightweight Composites", "High-Temperature Alloys", "Corrosion Resistance"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='aerospace_materials')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Mechatronic Systems recommendation
                    if i.lower() in Mechatronic_Systems:
                       print(i.lower())
                       reco_field = 'Mechatronic Systems'
                       st.success("** Our analysis says you are looking for Mechatronic Systems Jobs.**")
                       recommended_skills = ["Motion Control", "Robotic Systems", "Microcontrollers", "Electro-Mechanical Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='mechatronic_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Automation recommendation
                    if i.lower() in Automation:
                       print(i.lower())
                       reco_field = 'Automation'
                       st.success("** Our analysis says you are looking for Automation Jobs.**")
                       recommended_skills = ["PLC Programming", "HMI Design", "Actuator Control", "Industrial Automation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='automation')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Sensor Systems recommendation
                    if i.lower() in Sensor_Systems:
                       print(i.lower())
                       reco_field = 'Sensor Systems'
                       st.success("** Our analysis says you are looking for Sensor Systems Jobs.**")
                       recommended_skills = ["Position Sensors", "Force Sensors", "IMUs", "Sensor Fusion"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='sensor_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Risk Assessment recommendation
                    if i.lower() in Risk_Assessment:
                       print(i.lower())
                       reco_field = 'Risk Assessment'
                       st.success("** Our analysis says you are looking for Risk Assessment Jobs.**")
                       recommended_skills = ["Hazard Identification", "Safety Audits", "Risk Mitigation Plans", "Emergency Response"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='risk_assessment')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Industrial Hygiene recommendation
                    if i.lower() in Industrial_Hygiene:
                       print(i.lower())
                       reco_field = 'Industrial Hygiene'
                       st.success("** Our analysis says you are looking for Industrial Hygiene Jobs.**")
                       recommended_skills = ["Occupational Exposure", "Ventilation Systems", "Toxicology", "Noise Monitoring"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='industrial_hygiene')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Sustainability recommendation
                    if i.lower() in Sustainability:
                       print(i.lower())
                       reco_field = 'Sustainability'
                       st.success("** Our analysis says you are looking for Sustainability Jobs.**")
                       recommended_skills = ["Green Building Practices", "Life Cycle Assessment", "Energy Efficiency Audits"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='sustainability')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Subsea Engineering recommendation
                    if i.lower() in Subsea_Engineering:
                       print(i.lower())
                       reco_field = 'Subsea Engineering'
                       st.success("** Our analysis says you are looking for Subsea Engineering Jobs.**")
                       recommended_skills = ["Pipeline Design", "Underwater Structures", "ROVs", "Subsea Control Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='subsea_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Ship Propulsion recommendation
                    if i.lower() in Ship_Propulsion:
                       print(i.lower())
                       reco_field = 'Ship Propulsion'
                       st.success("** Our analysis says you are looking for Ship Propulsion Jobs.**")
                       recommended_skills = ["Marine Engines", "Propeller Design", "Fuel Efficiency", "Emission Control"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='ship_propulsion')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Offshore Platforms recommendation
                    if i.lower() in Offshore_Platforms:
                       print(i.lower())
                       reco_field = 'Offshore Platforms'
                       st.success("** Our analysis says you are looking for Offshore Platforms Jobs.**")
                       recommended_skills = ["Structural Design", "Platform Stability", "Wave Loading", "Mooring Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='offshore_platforms')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Track Engineering recommendation
                    if i.lower() in Track_Engineering:
                       print(i.lower())
                       reco_field = 'Track Engineering'
                       st.success("** Our analysis says you are looking for Track Engineering Jobs.**")
                       recommended_skills = ["Rail Alignment", "Track Maintenance", "Ballast Design", "Rail Welding"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='track_engineering')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Rolling Stock recommendation
                    if i.lower() in Rolling_Stock:
                       print(i.lower())
                       reco_field = 'Rolling Stock'
                       st.success("** Our analysis says you are looking for Rolling Stock Jobs.**")
                       recommended_skills = ["Train Dynamics", "Electric Locomotives", "Brake Systems", "Traction Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='rolling_stock')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Signal and Control recommendation
                    if i.lower() in Signal_and_Control:
                       print(i.lower())
                       reco_field = 'Signal and Control'
                       st.success("** Our analysis says you are looking for Signal and Control Jobs.**")
                       recommended_skills = ["Automatic Train Control", "Interlocking Systems", "Train Scheduling"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='signal_and_control')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Process Safety recommendation
                    if i.lower() in Process_Safety:
                       print(i.lower())
                       reco_field = 'Process Safety'
                       st.success("** Our analysis says you are looking for Process Safety Jobs.**")
                       recommended_skills = ["HAZOP Studies", "Risk-Based Inspections", "Safety Instrumented Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='process_safety')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Fire Protection recommendation
                    if i.lower() in Fire_Protection:
                       print(i.lower())
                       reco_field = 'Fire Protection'
                       st.success("** Our analysis says you are looking for Fire Protection Jobs.**")
                       recommended_skills = ["Sprinkler Systems", "Fire Dynamics", "Explosion Prevention", "Emergency Planning"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='fire_protection')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Ergonomics recommendation
                    if i.lower() in Ergonomics:
                       print(i.lower())
                       reco_field = 'Ergonomics'
                       st.success("** Our analysis says you are looking for Ergonomics Jobs.**")
                       recommended_skills = ["Workplace Design", "Human Factors Engineering", "Occupational Health"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='ergonomics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Wireless Communication recommendation
                    if i.lower() in Wireless_Communication:
                       print(i.lower())
                       reco_field = 'Wireless Communication'
                       st.success("** Our analysis says you are looking for Wireless Communication Jobs.**")
                       recommended_skills = ["5G Networks", "MIMO Systems", "RF Planning", "Spectrum Management"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='wireless_communication')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Optical Communication recommendation
                    if i.lower() in Optical_Communication:
                       print(i.lower())
                       reco_field = 'Optical Communication'
                       st.success("** Our analysis says you are looking for Optical Communication Jobs.**")
                       recommended_skills = ["DWDM", "Fiber Optic Networks", "Photonic Devices", "Free Space Optics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='optical_communication')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Urban Infrastructure recommendation
                    if i.lower() in Urban_Infrastructure:
                       print(i.lower())
                       reco_field = 'Urban Infrastructure'
                       st.success("** Our analysis says you are looking for Urban Infrastructure Jobs.**")
                       recommended_skills = ["Smart Cities", "Public Transport Systems", "Energy-Efficient Buildings"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='urban_infrastructure')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Land Use Planning recommendation
                    if i.lower() in Land_Use_Planning:
                       print(i.lower())
                       reco_field = 'Land Use Planning'
                       st.success("** Our analysis says you are looking for Land Use Planning Jobs.**")
                       recommended_skills = ["Zoning Policies", "Geographic Information Systems (GIS)", "Urban Analytics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='land_use_planning')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Sustainable Development recommendation
                    if i.lower() in Sustainable_Development:
                       print(i.lower())
                       reco_field = 'Sustainable Development'
                       st.success("** Our analysis says you are looking for Sustainable Development Jobs.**")
                       recommended_skills = ["Carbon Neutral Cities", "Green Infrastructure", "Water Management"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='sustainable_development')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Flight Safety recommendation
                    if i.lower() in Flight_Safety:
                       print(i.lower())
                       reco_field = 'Flight Safety'
                       st.success("** Our analysis says you are looking for Flight Safety Jobs.**")
                       recommended_skills = ["Airworthiness", "Flight Data Analysis", "Incident Investigation", "Safety Protocols"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='flight_safety')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Regulatory Compliance recommendation
                    if i.lower() in Regulatory_Compliance:
                       print(i.lower())
                       reco_field = 'Regulatory Compliance'
                       st.success("** Our analysis says you are looking for Regulatory Compliance Jobs.**")
                       recommended_skills = ["ICAO Standards", "FAA Regulations", "EASA Guidelines", "Auditing"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='regulatory_compliance')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Safety Management Systems recommendation
                    if i.lower() in Safety_Management_Systems:
                       print(i.lower())
                       reco_field = 'Safety Management Systems'
                       st.success("** Our analysis says you are looking for Safety Management Systems Jobs.**")
                       recommended_skills = ["Risk Analysis", "Safety Culture", "Human Factors in Aviation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='safety_management_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Autonomous Robots recommendation
                    if i.lower() in Autonomous_Robots:
                       print(i.lower())
                       reco_field = 'Autonomous Robots'
                       st.success("** Our analysis says you are looking for Autonomous Robots Jobs.**")
                       recommended_skills = ["SLAM Algorithms", "Path Planning", "Vision-Based Control", "AI Integration"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='autonomous_robots')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Industrial Robots recommendation
                    if i.lower() in Industrial_Robots:
                       print(i.lower())
                       reco_field = 'Industrial Robots'
                       st.success("** Our analysis says you are looking for Industrial Robots Jobs.**")
                       recommended_skills = ["Robot Arm Design", "Pick and Place Systems", "End Effector Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='industrial_robots')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Humanoid Robotics recommendation
                    if i.lower() in Humanoid_Robotics:
                       print(i.lower())
                       reco_field = 'Humanoid Robotics'
                       st.success("** Our analysis says you are looking for Humanoid Robotics Jobs.**")
                       recommended_skills = ["Locomotion", "Kinematics", "Artificial Skin", "Emotion Recognition"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='humanoid_robotics')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Hydrogen Energy recommendation
                    if i.lower() in Hydrogen_Energy:
                       print(i.lower())
                       reco_field = 'Hydrogen Energy'
                       st.success("** Our analysis says you are looking for Hydrogen Energy Jobs.**")
                       recommended_skills = ["Fuel Cells", "Electrolysis Systems", "Hydrogen Storage", "Energy Conversion"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='hydrogen_energy')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Energy Systems Modeling recommendation
                    if i.lower() in Energy_Systems_Modeling:
                       print(i.lower())
                       reco_field = 'Energy Systems Modeling'
                       st.success("** Our analysis says you are looking for Energy Systems Modeling Jobs.**")
                       recommended_skills = ["Energy Economics", "Renewable Resource Assessment", "System Optimization"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='energy_systems_modeling')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Hybrid Renewable Systems recommendation
                    if i.lower() in Hybrid_Renewable_Systems:
                       print(i.lower())
                       reco_field = 'Hybrid Renewable Systems'
                       st.success("** Our analysis says you are looking for Hybrid Renewable Systems Jobs.**")
                       recommended_skills = ["Wind-Solar Integration", "Battery Storage", "Grid-Tied Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='hybrid_renewable_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Remote Sensing recommendation
                    if i.lower() in Remote_Sensing:
                       print(i.lower())
                       reco_field = 'Remote Sensing'
                       st.success("** Our analysis says you are looking for Remote Sensing Jobs.**")
                       recommended_skills = ["Satellite Imagery", "LiDAR", "Multispectral Analysis", "Image Classification"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='remote_sensing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Geographic Information Systems recommendation
                    if i.lower() in Geographic_Information_Systems:
                       print(i.lower())
                       reco_field = 'Geographic Information Systems'
                       st.success("**Our analysis says you are looking for Geographic Information Systems Jobs.**")
                       recommended_skills = ["Spatial Analysis", "Cartography", "Geospatial Databases"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='geographic_information_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Surveying recommendation
                    if i.lower() in Surveying:
                       print(i.lower())
                       reco_field = 'Surveying'
                       st.success("**Our analysis says you are looking for Surveying Jobs.**")
                       recommended_skills = ["GPS Technology", "Total Station Operation", "Topographic Mapping"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='surveying')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Vehicle Control Systems recommendation
                    if i.lower() in Vehicle_Control_Systems:
                       print(i.lower())
                       reco_field = 'Vehicle Control Systems'
                       st.success("**Our analysis says you are looking for Vehicle Control Systems Jobs.**")
                       recommended_skills = ["ECU Programming", "ADAS Development", "Drive-by-Wire Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='vehicle_control_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Infotainment Systems recommendation
                    if i.lower() in Infotainment_Systems:
                       print(i.lower())
                       reco_field = 'Infotainment Systems'
                       st.success("**Our analysis says you are looking for Infotainment Systems Jobs.**")
                       recommended_skills = ["HMI Design", "CarPlay Integration", "Audio Systems Development"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='infotainment_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Connected Cars recommendation
                    if i.lower() in Connected_Cars:
                       print(i.lower())
                       reco_field = 'Connected Cars'
                       st.success("**Our analysis says you are looking for Connected Cars Jobs.**")
                       recommended_skills = ["Telematics", "Vehicle-to-Vehicle Communication (V2V)", "OTA Updates"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='connected_cars')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Water Distribution Systems recommendation
                    if i.lower() in Water_Distribution_Systems:
                       print(i.lower())
                       reco_field = 'Water Distribution Systems'
                       st.success("**Our analysis says you are looking for Water Distribution Systems Jobs.**")
                       recommended_skills = ["Pipeline Design", "Pressure Management", "Leak Detection"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='water_distribution_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Irrigation Systems recommendation
                    if i.lower() in Irrigation_Systems:
                       print(i.lower())
                       reco_field = 'Irrigation Systems'
                       st.success("**Our analysis says you are looking for Irrigation Systems Jobs.**")
                       recommended_skills = ["Sprinkler Design", "Drip Irrigation", "Canal Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='irrigation_systems')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Flood Management recommendation
                    if i.lower() in Flood_Management:
                       print(i.lower())
                       reco_field = 'Flood Management'
                       st.success("**Our analysis says you are looking for Flood Management Jobs.**")
                       recommended_skills = ["Flood Risk Assessment", "Floodplain Mapping", "Reservoir Operations"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='flood_management')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Tunnel Design recommendation
                    if i.lower() in Tunnel_Design:
                       print(i.lower())
                       reco_field = 'Tunnel Design'
                       st.success("**Our analysis says you are looking for Tunnel Design Jobs.**")
                       recommended_skills = ["Rock Tunneling", "TBM (Tunnel Boring Machines)", "Support Systems"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='tunnel_design')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Underground Structures recommendation
                    if i.lower() in Underground_Structures:
                       print(i.lower())
                       reco_field = 'Underground Structures'
                       st.success("**Our analysis says you are looking for Underground Structures Jobs.**")
                       recommended_skills = ["Subway Stations", "Underground Storage", "Cavern Design"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='underground_structures')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Geotechnical Analysis recommendation
                    if i.lower() in Geotechnical_Analysis:
                       print(i.lower())
                       reco_field = 'Geotechnical Analysis'
                       st.success("**Our analysis says you are looking for Geotechnical Analysis Jobs.**")
                       recommended_skills = ["Ground Settlement", "Slope Stability", "Soil-Structure Interaction"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='geotechnical_analysis')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Bioreactor Design recommendation
                    if i.lower() in Bioreactor_Design:
                       print(i.lower())
                       reco_field = 'Bioreactor Design'
                       st.success("**Our analysis says you are looking for Bioreactor Design Jobs.**")
                       recommended_skills = ["Scale-Up Processes", "Batch Reactors", "Continuous Fermentation"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='bioreactor_design')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Downstream Processing recommendation
                    if i.lower() in Downstream_Processing:
                       print(i.lower())
                       reco_field = 'Downstream Processing'
                       st.success("**Our analysis says you are looking for Downstream Processing Jobs.**")
                       recommended_skills = ["Protein Purification", "Filtration Systems", "Chromatography"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='downstream_processing')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break

                    #### Enzyme Technology recommendation
                    if i.lower() in Enzyme_Technology:
                       print(i.lower())
                       reco_field = 'Enzyme Technology'
                       st.success("**Our analysis says you are looking for Enzyme Technology Jobs.**")
                       recommended_skills = ["Immobilization Techniques", "Catalysis", "Enzyme Kinetics"]
                       recommended_keyword = st_tags(label='### Recommended skills for you.',
                       text='Recommended skills generated from System', value=recommended_skills, key='enzyme_technology')
                       st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job</h5>''', unsafe_allow_html=True)
                       break
         
                ## Resume Scorer & Resume Writing Tips
                st.subheader("**Resume Tips & Ideas 🥂**")
                resume_score = 0
                
                ### Predicting Whether these key points are added to the resume
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F80505FF;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F30707FF;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F50909FF;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F10A0AFF;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F30707FF;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F10909FF;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F30808FF;'>[-] Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F10E0EFF;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F30707FF;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #F10B0BFF;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.subheader("**Resume Score 📝**")
                
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )

                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### Score
                st.success('** Your Resume Writing Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        <p align="justify">
            Built with 🤍 by 
            <a href="https://dnoobnerd.netlify.app/" style="text-decoration: none; color: grey;">Gaurav Ghandat</a> through 
            <a href="https://www.linkedin.com/in/mrbriit/" style="text-decoration: none; color: grey;">T & P NEXUS</a>
        </p>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome admin ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
