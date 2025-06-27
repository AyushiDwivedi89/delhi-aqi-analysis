import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from fpdf import FPDF

# Load CSV
df = pd.read_csv("delhi_aqi.csv")

# Preprocess
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['hour'] = df['date'].dt.hour
df['day'] = df['date'].dt.date

# Store charts in memory
chart_images = {}

def save_chart(name):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    chart_images[name] = buf
    plt.close()

# Chart 1: Daily PM2.5 & PM10
daily_avg = df.groupby('day')[['pm2_5', 'pm10']].mean()
plt.figure(figsize=(10, 5))
plt.plot(daily_avg.index, daily_avg['pm2_5'], label='PM2.5')
plt.plot(daily_avg.index, daily_avg['pm10'], label='PM10')
plt.title("Daily Average of PM2.5 and PM10")
plt.xlabel("Date")
plt.ylabel("Concentration (µg/m³)")
plt.legend()
save_chart("pm_trend")

# Chart 2: Monthly pollutant average
monthly_avg = df.groupby('month')[['pm2_5', 'pm10', 'no2', 'so2', 'co']].mean()
monthly_avg.plot(kind='bar', figsize=(10, 5))
plt.title("Monthly Average of Major Pollutants")
plt.xlabel("Month")
plt.ylabel("Concentration (µg/m³)")
save_chart("monthly_avg")

# Chart 3: Correlation heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(df[['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']].corr(), annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap of Pollutants")
save_chart("correlation")

# Chart 4: Hourly PM2.5
hourly_avg = df.groupby('hour')['pm2_5'].mean()
plt.figure(figsize=(8, 5))
sns.lineplot(x=hourly_avg.index, y=hourly_avg.values)
plt.title("Average PM2.5 by Hour of Day")
plt.xlabel("Hour")
plt.ylabel("PM2.5 (µg/m³)")
save_chart("hourly_pm25")

# Create PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title & Intro
pdf.set_font("Arial", 'B', 16)
pdf.cell(0, 10, "Air Quality Index (AQI) Analysis in Delhi", ln=True, align='C')

pdf.set_font("Arial", '', 12)
pdf.multi_cell(0, 10, """
This report presents an in-depth analysis of the Air Quality Index (AQI) in Delhi using hourly pollutant data. It highlights key insights, trends, and correlations to support public awareness and policy formulation.
""")

# Research Questions
pdf.set_font("Arial", 'B', 14)
pdf.cell(0, 10, "Research Questions:", ln=True)
pdf.set_font("Arial", '', 12)
pdf.multi_cell(0, 10, """
1. What are the trends of PM2.5 and PM10 over time?
2. How do pollution levels vary across months and hours?
3. What is the correlation between different pollutants?
4. Which times of day show the worst air quality levels?
""")

# Function to insert chart
def insert_chart(title, img_key):
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, title, ln=True)
    img_path = f"{img_key}.png"
    with open(img_path, 'wb') as f:
        f.write(chart_images[img_key].read())
    pdf.image(img_path, x=10, w=180)

# Add charts
insert_chart("Daily Trend of PM2.5 and PM10", "pm_trend")
insert_chart("Monthly Average of Major Pollutants", "monthly_avg")
insert_chart("Correlation Between Pollutants", "correlation")
insert_chart("Hourly Average PM2.5 Levels", "hourly_pm25")

# Conclusion
pdf.add_page()
pdf.set_font("Arial", 'B', 14)
pdf.cell(0, 10, "Conclusion and Recommendations", ln=True)
pdf.set_font("Arial", '', 12)
pdf.multi_cell(0, 10, """
The analysis reveals that PM2.5 and PM10 levels remain persistently high in Delhi, with noticeable peaks during winter months. Pollution is strongly correlated between particulate matter and gases like NO2 and CO.

Hourly trends show that air quality tends to worsen during late nights and early mornings, possibly due to low wind dispersion and vehicular emissions.

Recommendations:
- Implement stricter controls on vehicular emissions during peak pollution hours.
- Promote public transport and electric vehicle usage.
- Increase green cover and deploy air purifiers in critical zones.
- Launch awareness campaigns to reduce household pollution sources.
""")

# Save the PDF
pdf.output("Delhi_AQI_Analysis_Report.pdf")
print("✅ Report saved as: Delhi_AQI_Analysis_Report.pdf")
