import streamlit as st
import pandas as pd
import plotly.express as px

# 1. STYLE CUSTOMIZATION: Define your app's look here
APP_THEME_COLOR = "#2E86C1"  # A professional blue
CHART_TEMPLATE = "plotly_white" # Options: "plotly_dark", "ggplot2", "seaborn"

st.set_page_config(page_title="Custom Patient Analysis", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('NYSDOH_sample.csv')
    
    # DATA CUSTOMIZATION: Cleaning Logic
    # We strip spaces and handle the '+' suffix for long stays
    df['Length of Stay'] = (
        df['Length of Stay']
        .astype(str)
        .str.replace(r'[^0-9]', '', regex=True)
    )
    df['Length of Stay'] = pd.to_numeric(df['Length of Stay'], errors='coerce')
    
    # CUSTOM FILTER: Remove outliers (e.g., stays longer than 365 days) if desired
    # df = df[df['Length of Stay'] <= 365] 
    
    return df.dropna(subset=['Length of Stay'])

try:
    df = load_data()

    # --- SIDEBAR CUSTOMIZATION ---
    st.sidebar.header("📊 Filter Settings")
    
    # Custom Sidebar Slider for Length of Stay range
    min_stay, max_stay = int(df["Length of Stay"].min()), int(df["Length of Stay"].max())
    stay_range = st.sidebar.slider(
        "Select Range of Stay (Days):", 
        min_stay, max_stay, (min_stay, max_stay)
    )

    age_groups = st.sidebar.multiselect(
        "Age Group:", options=sorted(df["Age Group"].unique()), default=df["Age Group"].unique()
    )

    # Applying Filters
    filtered_df = df[
        (df["Age Group"].isin(age_groups)) &
        (df["Length of Stay"].between(stay_range[0], stay_range[1]))
    ]

    # --- HEADER ---
    st.title("🏥 Customized Patient Dashboard")
    
    # --- METRICS CUSTOMIZATION ---
    # You can change how metrics look or what they calculate
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Avg Stay", f"{filtered_df['Length of Stay'].mean():.1f} Days")
    with m2:
        # Custom "Long Stay" metric: Patients staying > 10 days
        long_stays = len(filtered_df[filtered_df['Length of Stay'] > 10])
        st.metric("Long Stays (>10d)", long_stays)
    with m3:
        st.metric("Total Records", f"{len(filtered_df):,}")
    with m4:
        # Example: Percentage of filtered data vs total data
        pct = (len(filtered_df) / len(df)) * 100
        st.metric("% of Total Data", f"{pct:.1f}%")

    st.divider()

    # --- VISUALIZATION CUSTOMIZATION ---
    c1, c2 = st.columns(2)

    with c1:
        # CUSTOM HISTOGRAM: Changing color and adding a trend line (marginal box)
        st.subheader("Stay Distribution")
        fig_hist = px.histogram(
            filtered_df, 
            x="Length of Stay", 
            marginal="box", # Adds a box plot on top
            color_discrete_sequence=[APP_THEME_COLOR],
            template=CHART_TEMPLATE
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        # CUSTOM BAR CHART: Changing the color scale
        st.subheader("Stay by Admission Type")
        avg_adm = filtered_df.groupby("Type of Admission")["Length of Stay"].mean().reset_index()
        fig_bar = px.bar(
            avg_adm, 
            x="Type of Admission", 
            y="Length of Stay",
            color="Length of Stay", # Color bars by the value itself
            color_continuous_scale="Blues",
            template=CHART_TEMPLATE
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- DATA TABLE CUSTOMIZATION ---
    with st.expander("🔍 View/Download Filtered Data"):
        # Custom columns to show
        cols_to_show = st.multiselect("Select Columns:", df.columns.tolist(), default=["Age Group", "Gender", "Length of Stay"])
        st.dataframe(filtered_df[cols_to_show], use_container_width=True)
        
        # Add a download button for the customized data
        csv = filtered_df[cols_to_show].to_csv(index=False).encode('utf-8')
        st.download_button("Download filtered data as CSV", data=csv, file_name="custom_extract.csv", mime="text/csv")

except Exception as e:
    st.error(f"Please check your CSV file. Error: {e}")