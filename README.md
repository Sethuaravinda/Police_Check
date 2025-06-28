
🔰 Project Title
SecureCheck: Real-Time Monitoring of Police Check Post Data

🧠 Objective
The goal of SecureCheck is to build a real-time, interactive dashboard that helps law enforcement agencies analyze traffic stop data, monitor violations, evaluate officer performance, and identify patterns in arrests, searches, and drug-related incidents.

📊 Tools & Technologies Used

| Component        | Technology         |
| ---------------- | ------------------ |
| UI Framework     | Streamlit (Python) |
| Database         | PostgreSQL         |
| Data Analysis    | Pandas, SQLAlchemy |
| Charts & Visuals | Plotly Express     |
| Backend Driver   | psycopg2           |
| Code Editor      | Visual Studio Code |


📂 Dataset
Source: traffic_stops_with_vehicle_number.csv (cleaned and processed)

Size: ~4000+ rows (depending on state data)

Columns: stop time, stop date, violation, outcome, search, arrest, vehicle number, driver info, etc.

⚙️ Implementation Details
🔹 1. Data Cleaning
Removed null-heavy columns

Filled missing values (e.g., search_type, driver_age)

Standardized time and date fields

Converted stop_duration into minutes for analysis

🔹 2. Database Insertion
Created a PostgreSQL database secure_check

Imported cleaned data into a table traffic_stops

Used SQLAlchemy and pandas.to_sql() for insertion

🔹 3. Dashboard Features
Key Metrics: Total stops, arrests, warnings, drug-related

Vehicle Logs: Display of recent traffic stop entries

Violation Summary: Violation type frequency with Plotly chart

Officer Reports: Summary based on outcomes and arrest activity

Advanced Insights: 15+ SQL-powered queries for deep data trends

Natural Language Summary: Converts selected stop data into a human-readable sentence

🔹 4. Complex SQL Queries Included
Violation trends by age, race, gender

Arrest and search rates by violation

Time of day/year/month patterns

Rare arrest/search violations

High-drug-stop locations

💡 Sample Use Case
A traffic supervisor can use SecureCheck to view all stops involving Speeding, identify vehicles with frequent drug-related stops, or analyze arrest patterns by country and violation. It also helps generate officer summary reports in natural language.

📈 Outcome
Highly interactive, real-time analytics dashboard

Intuitive UI for non-technical users

Fully database-driven for scalable performance

Extensible for officer assignment, location tracking, or AI insights

📌 Conclusion
SecureCheck offers a modern, data-powered solution for traffic enforcement analysis. It transforms raw stop data into actionable insights for safety and accountability. With its modular design, it can easily integrate with live law enforcement systems or be deployed as a public-facing transparency tool.



