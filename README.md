# Scaler NPS Dashboard: A Strategic Analysis of Learner Feedback

An interactive Streamlit dashboard designed to audit, analyze, and provide strategic recommendations on learner Net Promoter Score (NPS) ticket data. This project moves beyond simple reporting to deliver actionable business insights.

**🚀 Live Demo:** [**https://utkarsh0723-scalar-nps-dashboard-dashboard-r8trmb.streamlit.app/**](https://utkarsh0723-scalar-nps-dashboard-dashboard-r8trmb.streamlit.app/)

---

## Problem Statement

The goal of this project was to analyze a dataset of learner feedback tickets to identify data quality issues, uncover high-impact strategic patterns, and propose a robust monitoring framework. The analysis needed to go beyond surface-level metrics to pinpoint the most critical issues affecting learner satisfaction and suggest concrete process improvements.

---

## Key Features & Analysis

This dashboard is built around the three core tasks of the assignment, providing a comprehensive solution.

### 1. Data Quality & Validation
* **Automated Audit:** The **"Data Quality Checks"** tab identifies and displays critical data issues, including missing values, duplicate tickets, logical inconsistencies between status/sub-status, and impossible timelines (e.g., tickets resolved before creation).
* **Actionable Recommendations:** For each identified issue, clear and specific **process improvement recommendations** are provided to prevent future data corruption at the source.

### 2. Strategic Pattern Analysis
* **Prioritization Matrix:** The **"Overview"** tab features a powerful "Strategic Issue Prioritisation" table that ranks issues not just by **frequency** (ticket volume) but also by **impact** (average NPS and resolution time).
* **"Single Biggest Fix":** Based on the prioritization matrix, the dashboard explicitly identifies and recommends the **single most impactful issue** to address for the greatest improvement in learner satisfaction.
* **Performance Tracking:** The dashboard includes dedicated tabs for analyzing **team performance**, visualizing **SLA breaches**, and understanding the **ticket flow** with an interactive Sankey diagram.

### 3. Monitoring & Automation
* **Root Cause Analysis:** The **"Root Cause Analysis"** tab uses a word cloud to quickly identify common themes within ticket remarks, allowing for a high-level understanding of learner complaints.
* **Automation Suggestions:** The project includes practical suggestions and a Python code example for **process automation**, such as auto-tagging tickets based on remark content to improve efficiency.

---

## Technology Stack

* **Language:** Python
* **Data Manipulation:** Pandas
* **Dashboarding:** Streamlit
* **Data Visualization:** Matplotlib, Seaborn, Plotly
* **Text Analysis:** WordCloud

---

## 🚀 How to Run Locally

Follow these steps to set up and run the project on your local machine.

### Prerequisites
* Python 3.8 or higher
* pip (Python package installer)

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME
