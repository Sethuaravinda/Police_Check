
import streamlit as st  
import pandas as pd  
from sqlalchemy import create_engine  
import plotly.express as px  

# Connect to PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:sethu26@localhost:5432/secure_check")

#  Load data from DB
@st.cache_data
def load_data():
    query = "SELECT * FROM traffic_stops"
    return pd.read_sql(query, engine)

df = load_data()



#  Streamlit UI
st.set_page_config(page_title="SecureCheck Dashboard", layout="wide")
st.title("🚓 SecureCheck: Police Check Post Dashboard")
st.markdown("🔍 Real-time monitoring and insights for law enforcement operations.")
st.markdown(" ")

st.markdown("### 🚗 Vehicle Logs")
st.dataframe(df[['stopping_date', 'stop_time', 'vehicle_number', 'country_name']].head(10))

st.markdown("### ⚠️ Violation Summary")
violation_counts = df['violation'].value_counts().reset_index()
violation_counts.columns = ['Violation', 'Count']
fig = px.bar(violation_counts, x='Violation', y='Count', color='Violation', title='Top Violations')
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📝 Officer Outcomes (Reports Summary)")
officer_summary = df.groupby('stop_outcome').agg({
    'is_arrested': 'sum',
    'vehicle_number': 'count'
}).reset_index().rename(columns={
    'is_arrested': 'Total Arrests',
    'vehicle_number': 'Total Stops'
})
st.dataframe(officer_summary)

st.markdown(" ")

# 📊 Key Metrics
st.subheader("📈 Key Metrics")

total_stops = len(df)
total_arrests = df[df['is_arrested'] == True].shape[0]
total_warnings = df[df['stop_outcome'].str.lower() == 'warning'].shape[0]
drug_related = df[df['drugs_related_stop'] == True].shape[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("🚔 Total Police Stops", f"{total_stops:,}")
col2.metric("👮 Total Arrests", f"{total_arrests:,}")
col3.metric("⚠️ Total Warnings", f"{total_warnings:,}")
col4.metric("💊 Drug-Related Stops", f"{drug_related:,}")



st.markdown(" ")

# 📊  Insights Section
st.subheader("🧠 Insights")

# 1️⃣ Query Selector
query_options = [
    "Top 10 Drug-Related Vehicles",
    "Most Frequently Searched Vehicles",
    "Driver Age Group with Highest Arrest Rate",
    "Gender Distribution by Country",
    "Race + Gender with Highest Search Rate",
    "Time of Day with Most Traffic Stops",
    "Average Stop Duration by Violation",
    "Are Night Stops More Likely to Lead to Arrests?",
    "Violations with Most Searches or Arrests",
    "Most Common Violations (<25 Age)",
    "Rarely Resulting in Search or Arrest",
    "Countries with Highest Drug-Related Stops",
    "Arrest Rate by Country and Violation",
    "Most Stops with Search by Country"
]

selected_query = st.selectbox("Select a Query", query_options)

# 2️⃣ Query Map
query_map = {
    "Top 10 Drug-Related Vehicles": """
        SELECT vehicle_number
        FROM traffic_stops
        LIMIT 10;
    """,
    "Most Frequently Searched Vehicles": """
        SELECT vehicle_number, COUNT(*) AS search_count
        FROM traffic_stops
        WHERE search_conducted = TRUE
        GROUP BY vehicle_number
        ORDER BY search_count DESC
        LIMIT 10;
    """,
    "Driver Age Group with Highest Arrest Rate": """
        SELECT CASE 
            WHEN driver_age < 25 THEN '<25'
            WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
            WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
            ELSE '60+' END AS age_group,
            ROUND(100.0 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)/COUNT(*), 2) AS arrest_rate
        FROM traffic_stops
        GROUP BY age_group
        ORDER BY arrest_rate DESC;
    """,
    "Gender Distribution by Country": """
        SELECT country_name, driver_gender, COUNT(*) AS count
        FROM traffic_stops
        GROUP BY country_name, driver_gender
        ORDER BY country_name, driver_gender;
    """,
    "Race + Gender with Highest Search Rate": """
        SELECT driver_race, driver_gender,
            ROUND(100.0 * SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END)/COUNT(*), 2) AS search_rate
        FROM traffic_stops
        GROUP BY driver_race, driver_gender
        ORDER BY search_rate DESC
        LIMIT 5;
    """,
    "Time of Day with Most Traffic Stops": """
        SELECT EXTRACT(HOUR FROM stop_time::time) AS hour_of_day,
               COUNT(*) AS stop_count
        FROM traffic_stops
        GROUP BY hour_of_day
        ORDER BY stop_count DESC
        LIMIT 5;
    """,
    "Average Stop Duration by Violation": """
        SELECT violation, 
           ROUND(AVG(stop_duration_minutes)::numeric, 2) AS avg_duration_minutes
        FROM traffic_stops
        GROUP BY violation
        ORDER BY avg_duration_minutes DESC;
""",

    "Are Night Stops More Likely to Lead to Arrests?": """
        SELECT 
            CASE 
                WHEN EXTRACT(HOUR FROM stop_time::time) BETWEEN 19 AND 24 OR EXTRACT(HOUR FROM stop_time::time) < 5 
                THEN 'Night' ELSE 'Day' END AS time_period,
            ROUND(100.0 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)/COUNT(*), 2) AS arrest_rate
        FROM traffic_stops
        GROUP BY time_period;
    """,
    "Violations with Most Searches or Arrests": """
        SELECT violation,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS total_searches,
            SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests
        FROM traffic_stops
        GROUP BY violation
        ORDER BY total_searches DESC, total_arrests DESC
        LIMIT 10;
    """,
    "Most Common Violations (<25 Age)": """
        SELECT violation, COUNT(*) AS count
        FROM traffic_stops
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY count DESC
        LIMIT 5;
    """,
    "Rarely Resulting in Search or Arrest": """
        SELECT violation,
            COUNT(*) AS total,
            SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS searched,
            SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrested
        FROM traffic_stops
        GROUP BY violation
        HAVING SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) < 5
           AND SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) < 5
        ORDER BY total DESC
        LIMIT 10;
    """,
    "Countries with Highest Drug-Related Stops": """
        SELECT country_name, COUNT(*) AS drug_stops
        FROM traffic_stops
        WHERE drugs_related_stop = TRUE
        GROUP BY country_name
        ORDER BY drug_stops DESC;
    """,
    "Arrest Rate by Country and Violation": """
        SELECT country_name, violation,
            ROUND(100.0 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)/COUNT(*), 2) AS arrest_rate
        FROM traffic_stops
        GROUP BY country_name, violation
        ORDER BY arrest_rate DESC
        LIMIT 10;
    """,
    "Most Stops with Search by Country": """
        SELECT country_name, COUNT(*) AS search_count
        FROM traffic_stops
        WHERE search_conducted = TRUE
        GROUP BY country_name
        ORDER BY search_count DESC;
    """,
}

# 3️⃣ Run Button
if st.button("Run Query"):
    query = query_map.get(selected_query)
    if query:
        try:
            result_df = pd.read_sql(query, engine)
            st.success(f"✅ Showing results for: {selected_query}")
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Query failed: {e}")
    else:
        st.warning("⚠️ Invalid query selected.")


# 🧠 Advanced Complex Queries Section
st.subheader("🧠 Complex Insights")

complex_query_options = [
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops (Year, Month, Hour)",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, Race)",
    "Top 5 Violations with Highest Arrest Rates"
]

selected_complex_query = st.selectbox("Select a Complex Query", complex_query_options)

complex_query_map = {
    "Yearly Breakdown of Stops and Arrests by Country": """
        SELECT 
            country_name,
            EXTRACT(YEAR FROM stopping_date::date) AS year,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests
        FROM traffic_stops
        GROUP BY country_name, year
        ORDER BY country_name, year;
""",

    "Driver Violation Trends Based on Age and Race": """
        SELECT driver_race,
               CASE 
                   WHEN driver_age < 25 THEN '<25'
                   WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
                   WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                   ELSE '60+' END AS age_group,
               violation,
               COUNT(*) AS count
        FROM traffic_stops
        GROUP BY driver_race, age_group, violation
        ORDER BY count DESC
        LIMIT 10;
    """,
    "Time Period Analysis of Stops (Year, Month, Hour)": """
    SELECT 
        EXTRACT(YEAR FROM stopping_date::date) AS year,
        EXTRACT(MONTH FROM stopping_date::date) AS month,
        EXTRACT(HOUR FROM stop_time::time) AS hour,
        COUNT(*) AS total_stops
    FROM traffic_stops
    GROUP BY year, month, hour
    ORDER BY year, month, hour;
""",

    "Violations with High Search and Arrest Rates": """
        SELECT violation,
               COUNT(*) AS total_stops,
               ROUND(100.0 * SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END)/COUNT(*), 2) AS search_rate,
               ROUND(100.0 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)/COUNT(*), 2) AS arrest_rate
        FROM traffic_stops
        GROUP BY violation
        HAVING COUNT(*) > 10
        ORDER BY arrest_rate DESC, search_rate DESC;
    """,
    "Driver Demographics by Country (Age, Gender, Race)": """
        SELECT country_name, driver_gender, driver_race,
               ROUND(AVG(driver_age), 1) AS avg_age,
               COUNT(*) AS total_drivers
        FROM traffic_stops
        GROUP BY country_name, driver_gender, driver_race
        ORDER BY country_name, total_drivers DESC;
    """,
    "Top 5 Violations with Highest Arrest Rates": """
        SELECT violation,
               COUNT(*) AS total_stops,
               ROUND(100.0 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)/COUNT(*), 2) AS arrest_rate
        FROM traffic_stops
        GROUP BY violation
        HAVING COUNT(*) > 10
        ORDER BY arrest_rate DESC
        LIMIT 5;
    """
}

if st.button("Run Complex Query"):
    query = complex_query_map.get(selected_complex_query)
    if query:
        try:
            result_df = pd.read_sql(query, engine)
            st.success(f"✅ Showing results for: {selected_complex_query}")
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Complex query failed: {e}")
    else:
        st.warning("⚠️ No query found for your selection.")



st.markdown(" ")
st.markdown(" ")

st.subheader("🧾 Generate Stop Report Summary")

# 🧠 Select each value
driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
driver_gender = st.selectbox("Driver Gender", ["male", "female", "other"])
violation = st.selectbox("Violation", df['violation'].dropna().unique())
stop_time = st.time_input("Stop Time")  # returns time object
search_conducted = st.selectbox("Was a search conducted?", ["Yes", "No"])
stop_outcome = st.selectbox("Stop Outcome", df['stop_outcome'].dropna().unique())
stop_duration = st.selectbox("Stop Duration", {
    7.5: "0–15 minutes",
    23: "16–30 minutes",
    40: "30+ minutes",
    70: "60+ minutes"
}.values())
drugs_related = st.selectbox("Was it drug-related?", ["Yes", "No"])

# 🧾 Generate Summary
if st.button("Generate Summary"):
    summary = f"""
🚗 A {driver_age}-year-old {driver_gender} driver was stopped for **{violation}** violation at **{stop_time.strftime('%I:%M %p')}**.
{"A search was conducted" if search_conducted == "Yes" else "No search was conducted"}, and he received a **{stop_outcome}**.
The stop lasted **{stop_duration}** and was {"drug-related" if drugs_related == "Yes" else "not drug-related"}.
"""
    st.markdown(summary)
