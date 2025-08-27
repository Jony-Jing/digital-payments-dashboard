🏦 Digital Payments Dashboard

An interactive Streamlit dashboard analyzing and visualizing digital payment trends in Malaysia.
This project leverages data published by Bank Negara Malaysia (BNM) to understand cashless adoption,
transaction growth, and infrastructure readiness across the country.

🔗 Live Demo: Coming Soon
📊 Data Source: Bank Negara Malaysia - Payment Statistics

🚀 Features

✅ Modern dark-themed dashboard
✅ Interactive year filtering
✅ KPIs for key insights at a glance
✅ Clean visualizations using Plotly & Matplotlib
✅ Professional, minimal, and user-friendly design

📊 Data Overview

The dashboard uses processed datasets derived from Bank Negara Malaysia's Payment Statistics:

T1 → E-payments per capita (BNM Table 7.1)

T2 → Total transaction volume & value (BNM Table 7.2)

T5 → POS & ATM terminals per 1,000 population (BNM Table 7.5)

📌 Data Source:
Bank Negara Malaysia. (2025). Payment Statistics. Retrieved from
https://www.bnm.gov.my/payment-statistics

📈 Insights & Key Findings

After analyzing the data, here are some key insights:

📌 Cashless adoption is accelerating — E-payments per capita grew significantly between 2021 and 2023.

📌 POS terminal density is improving — The number of POS terminals per 1,000 people increased steadily, supporting Malaysia’s cashless economy goals.

📌 ATM usage is declining — Reflecting a shift towards digital-first payments.

📌 COVID-19 accelerated digital payments — There's a visible spike in adoption right after the pandemic years.

These findings highlight Malaysia’s rapid shift towards a cashless economy, creating opportunities for fintech innovation and digital financial services.

🧠 Techniques & Cool Features Used

Some techniques and optimizations applied in this project:

Data Cleaning & Transformation

Standardized datasets with inconsistent year ranges

Unified naming conventions for consistent filtering

Interactive Dashboard Design

Used Streamlit for fast UI prototyping

Dynamic filtering with synchronized KPIs and charts

Advanced Visualization

Built hover-enabled, animated Plotly graphs

Added modern dark-theme styling for professional aesthetics

Custom Year Synchronization

Automatically detects common year ranges across datasets

Greys-out missing data in charts for better user clarity

🛠️ Challenges Faced

During development, I encountered and solved several challenges:

🔹 Inconsistent Year Ranges

Different datasets (T1, T2, T5) had mismatched year coverage

Solved by creating common year synchronization to ensure consistent filtering

🔹 Multiple Metrics with Different Scales

Transaction counts, POS density, and ATM numbers vary greatly

Solved by designing separate KPI cards and scalable visualizations

🔹 Making It Portfolio-Ready

Ensured dashboard is clean, interactive, and non-overwhelming

Added subtle hover animations for a polished UX

## 🛠️ Installation

Clone this repository:

```bash
https://github.com/Jony-Jing/digital-payments-dashboard.git
```
Install dependencies:
```
pip install -r requirements.txt
```
```
streamlit run dashboard.py
```
🌍 Deployment

This dashboard is deployed via Streamlit Community Cloud for public access.
Check it out live here: Live Demo

📌 Tech Stack

Language: Python

Framework: Streamlit

Data Viz: Plotly, Matplotlib, Seaborn

Data Processing: Pandas, NumPy
```
📸 Screenshots
```
👨‍💻 Author:
Jony Jing
💼 Data Management & Analytics (Master’s)
📧 Contact: jonyjing0620@gmail.com

🌐 Portfolio: your-portfolio-link.com
