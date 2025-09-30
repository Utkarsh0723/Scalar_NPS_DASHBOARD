import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.graph_objects as go

st.set_page_config(page_title="Scaler NPS Dashboard", layout="wide")

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        # It's best practice to use a relative path if the CSV is in the same folder
        df = pd.read_csv("Assignment Data_ NPS Tracker_2025 - Sheet1.csv")
    except FileNotFoundError:
        st.error("Error: The data file 'Assignment Data_ NPS Tracker_2025 - Sheet1.csv' was not found. Please make sure it's in the correct folder.")
        return pd.DataFrame()

    df['Created Date'] = pd.to_datetime(df['Created Date'])
    df['Resolved Date'] = pd.to_datetime(df['Resolved Date'])
    df['Resolution Time'] = (df['Resolved Date'] - df['Created Date']).dt.days
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
if not df.empty:
    issues_selected = st.sidebar.multiselect("Select Issues", options=df['Issue 2 - NPS'].unique(), default=df['Issue 2 - NPS'].unique())
    programs_selected = st.sidebar.multiselect("Select Programs", options=df['Program Name'].unique(), default=df['Program Name'].unique())
    filtered_df = df[(df['Issue 2 - NPS'].isin(issues_selected)) & (df['Program Name'].isin(programs_selected))]
else:
    filtered_df = pd.DataFrame(columns=df.columns)

# --- Dashboard Tabs ---
tabs = st.tabs([
    "Overview", "Team Performance", "Root Cause Analysis",
    "Ticket Flow Sankey", "SLA Breach Heatmap", "Data Quality Checks",
    "All Records", "Automation Suggestions"
])

# --- TAB 0: OVERVIEW (UPDATED FOR TASK 2) ---
with tabs[0]:
    st.header("Overview")
    st.write(f"Displaying insights for {filtered_df.shape[0]} tickets.")

    st.subheader("Strategic Issue Prioritisation")
    st.write("This table identifies critical issues by combining ticket volume (Frequency) with learner sentiment (NPS Impact) and operational drag (Resolution Time Impact).")

    if not filtered_df.empty:
        issue_summary = filtered_df.groupby('Issue 2 - NPS').agg(
            Ticket_Count=('Ticket No', 'count'),
            Avg_NPS_Rating=('NPS Rating', 'mean'),
            Avg_Resolution_Time_Days=('Resolution Time', 'mean')
        ).reset_index()

        issue_summary = issue_summary.sort_values(by='Ticket_Count', ascending=False)
        issue_summary['Avg_NPS_Rating'] = issue_summary['Avg_NPS_Rating'].round(2)
        issue_summary['Avg_Resolution_Time_Days'] = issue_summary['Avg_Resolution_Time_Days'].round(2)

        st.dataframe(
            issue_summary,
            use_container_width=True,
            column_config={
                "Ticket_Count": st.column_config.ProgressColumn(
                    "Ticket Count (Frequency)",
                    format="%f",
                    min_value=0,
                    # FIX 1: Convert numpy.int64 to standard python int
                    max_value=int(issue_summary['Ticket_Count'].max()),
                ),
                "Avg_NPS_Rating": st.column_config.ProgressColumn(
                    "Avg NPS (Impact)",
                    format="⭐ %.2f",
                    min_value=0,
                    max_value=10,
                )
            }
        )
    else:
        st.warning("No data to display based on current filters.")

    st.subheader("💡 Recommendation: The Single Biggest Fix")
    st.info("""
    **Analysis:** Based on the data, **'Projects & Assignment Related Concern (NPS)'** is the most critical issue.

    * **Frequency:** It consistently has one of the highest ticket volumes.
    * **Impact:** It suffers from a significantly low average NPS rating and a high average resolution time compared to other issues.

    **Conclusion:** Focusing resources on improving the project and assignment experience (e.g., clearer instructions, better TA feedback, realistic deadlines) would provide the largest positive impact on learner satisfaction and reduce operational load.
    """)

# --- TAB 1: TEAM PERFORMANCE ---
with tabs[1]:
    st.header("Team Performance")
    if not filtered_df.empty:
        team_performance = filtered_df.groupby('Assigned To')['Resolution Time'].mean().sort_values()
        st.subheader("Average Resolution Time by Team Member")
        st.bar_chart(team_performance)

        st.subheader("Resolution Time Distribution by Team Member")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=filtered_df, x='Assigned To', y='Resolution Time', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No data to display.")


# --- TAB 2: ROOT CAUSE ANALYSIS ---
with tabs[2]:
    st.header("Root Cause Analysis")
    if not filtered_df['Ticket All Remarks'].dropna().empty:
        remarks_str = ' '.join(filtered_df['Ticket All Remarks'].dropna().astype(str))
        wordcloud = WordCloud(background_color='white', max_words=100, width=800, height=400).generate(remarks_str)
        st.subheader("Ticket Remarks Word Cloud")
        fig_wc, ax_wc = plt.subplots()
        ax_wc.imshow(wordcloud, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)
    else:
        st.warning("No remarks available for word cloud.")

# --- TAB 3: TICKET FLOW SANKEY ---
with tabs[3]:
    st.header("Ticket Flow Sankey Diagram")
    if not filtered_df.empty:
        def prepare_sankey(df):
            df_sankey = df[['Issue 2 - NPS', 'Program Name', 'Assigned To', 'Status']].copy().dropna()
            if df_sankey.empty:
                return [], [], [], []
            labels = pd.concat([df_sankey[col] for col in df_sankey.columns]).unique().tolist()
            label_to_idx = {label: i for i, label in enumerate(labels)}
            def make_links(src_col, tgt_col):
                links_df = df_sankey.groupby([src_col, tgt_col]).size().reset_index(name='count')
                source = links_df[src_col].map(label_to_idx)
                target = links_df[tgt_col].map(label_to_idx)
                value = links_df['count']
                return source.tolist(), target.tolist(), value.tolist()
            s1, t1, v1 = make_links('Issue 2 - NPS', 'Program Name')
            s2, t2, v2 = make_links('Program Name', 'Assigned To')
            s3, t3, v3 = make_links('Assigned To', 'Status')
            return labels, s1 + s2 + s3, t1 + t2 + t3, v1 + v2 + v3
        labels, source, target, value = prepare_sankey(filtered_df)
        if labels:
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels),
                link=dict(source=source, target=target, value=value))])
            fig.update_layout(title_text="Ticket Flow", font_size=10)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough data to generate a Sankey diagram.")
    else:
        st.warning("No data to display.")

# --- TAB 4: SLA BREACH HEATMAP ---
with tabs[4]:
    st.header("SLA Breach Heatmap")
    SLA_THRESHOLD = 3
    if 'Created Date' in filtered_df.columns and not filtered_df.empty:
        df_sla = filtered_df.dropna(subset=['Created Date', 'Resolution Time', 'Assigned To']).copy()
        df_sla['SLA Breach'] = df_sla['Resolution Time'] > SLA_THRESHOLD
        df_sla['Week'] = df_sla['Created Date'].dt.to_period('W').apply(lambda r: r.start_time.strftime('%Y-%m-%d'))
        sml_table = df_sla.groupby(['Assigned To', 'Week'])['SLA Breach'].sum().unstack(fill_value=0)
        
        if not sml_table.empty:
            plt.figure(figsize=(14, 6))
            sns.heatmap(sml_table, cmap="Reds", linewidths=0.5, linecolor='lightgray', annot=True, fmt='g')
            plt.title("SLA Breaches Heatmap by Team and Week")
            plt.xlabel("Week")
            plt.ylabel("Team Member")
            st.pyplot(plt.gcf())
        else:
            st.warning("Not enough data to generate SLA Breach Heatmap.")
    else:
        st.warning("No data to display.")

# --- TAB 5: DATA QUALITY CHECKS (UPDATED FOR TASK 1) ---
with tabs[5]:
    st.header("Data Quality Checks")

    missing_critical = filtered_df[filtered_df[['Created Date', 'Resolved Date', 'Assigned To', 'Status']].isnull().any(axis=1)]
    st.subheader("Tickets with Missing Critical Information")
    st.write(f"Count: {missing_critical.shape[0]}")
    st.dataframe(missing_critical)

    duplicates = filtered_df[filtered_df.duplicated(subset=['Ticket No'], keep=False)]
    st.subheader("Duplicate Ticket Records")
    st.write(f"Count: {duplicates.shape[0]}")
    st.dataframe(duplicates)

    inconsistent_status = filtered_df[
        ((filtered_df['Status'] == 'Completed') & (filtered_df['Sub Status'] != 'Success')) |
        ((filtered_df['Status'] == 'Escalated') & (~filtered_df['Sub Status'].isin(['Pending Customer', 'In Progress']))) |
        ((filtered_df['Status'] == 'Open') & (filtered_df['Sub Status'] == 'Success'))
    ]
    st.subheader("Status and Sub-status Logical Inconsistencies")
    st.write(f"Count: {inconsistent_status.shape[0]}")
    st.dataframe(inconsistent_status)

    resolved_before_created = filtered_df[filtered_df['Resolved Date'] < filtered_df['Created Date']]
    st.subheader("Tickets with Resolution Date Before Created Date")
    st.write(f"Count: {resolved_before_created.shape[0]}")
    st.dataframe(resolved_before_created)

    st.divider()

    st.subheader("Process Improvement Recommendations")
    st.markdown("""
    Based on the audit, the following process improvements are recommended to prevent future data inconsistencies:

    **1. For Duplicate Tickets:**
    * **Problem:** Duplicate ticket numbers can corrupt analytics and make it impossible to track a specific issue's history.
    * **Recommendation:** **Enforce Uniqueness on `Ticket No`**.
    * **Rule:** The `Ticket No` column in the database should be set as a **Primary Key or have a Unique Constraint**. This will make it systemically impossible to create two tickets with the same ID.

    **2. For Missing Critical Information:**
    * **Problem:** Key fields are missing, preventing proper tracking of accountability (`Assigned To`), performance (`Resolved Date`), and status.
    * **Recommendation:** Implement **mandatory fields** in the ticketing system and use **automation**.
    * **Automation:** The `Resolved Date` should be **automatically populated** by the system when an agent changes the ticket `Status` to "Completed". This eliminates manual error.

    **3. For Status/Sub-status Inconsistencies:**
    * **Problem:** The ticket lifecycle is unclear, allowing for contradictory states (e.g., 'Open' and 'Success').
    * **Recommendation:** Enforce **status-based logic** in the system's backend.
    * **Rule:** The available `Sub Status` options should be dynamically filtered based on the selected `Status` to prevent invalid combinations.

    **4. For `Resolved Date` before `Created Date`:**
    * **Problem:** Impossible timelines corrupt all resolution time metrics.
    * **Recommendation:** Introduce a **database-level validation rule**.
    * **Rule:** Implement a `CHECK` constraint (e.g., `CHECK (Resolved_Date >= Created_Date)`) that prevents the system from saving a record with this logical error.
    """)

# --- TAB 6: ALL RECORDS ---
with tabs[6]:
    st.header("All Ticket Records")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

# --- TAB 7: AUTOMATION SUGGESTIONS ---
with tabs[7]:
    st.header("Process Automation Suggestions")
    st.write("""
    Here are some automation ideas to improve operational efficiency:
    - Automated ticket tagging using keyword matching or NLP.
    - Real-time SLA breach alerts with email/Slack notifications.
    - Scheduled data quality audits with automatic anomaly detection.
    - Automated escalation of pending tickets via chatbot integrations.
    """)

    st.subheader("Example: Auto Ticket Tagging")
    
    def auto_tag_ticket(remark):
        remark = str(remark).lower()
        if 'placement' in remark:
            return 'Placement Related'
        elif 'project' in remark or 'assignment' in remark:
            return 'Project Related'
        elif 'support' in remark or 'ta' in remark:
            return 'Support Related'
        else:
            return 'General'
            
    if not filtered_df.empty:
        df_tagged = filtered_df.copy()
        df_tagged['Auto Tag'] = df_tagged['Ticket All Remarks'].apply(auto_tag_ticket)
        st.write(df_tagged[['Ticket No', 'Ticket All Remarks', 'Auto Tag']].head(10))
    else:
        st.warning("No data to tag.")