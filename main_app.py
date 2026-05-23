import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Integrated IT Asset System", 
    page_icon="🖥️", 
    layout="wide"
)

# --- APP 1: DATA LOADING ---
@st.cache_data
def load_search_data():
    # Using path from App 1
    df = pd.read_csv(r"C:\Users\Abhishek\Downloads\Cleaned_Asset_Data_Unique_Names.csv")
    df.columns = df.columns.str.strip()
    df = df.fillna("") 
    return df

# --- APP 2: DATA LOADING ---
@st.cache_data
def load_dashboard_data():
    # Using path from App 2
    file_path = r"C:\Users\Abhishek\Downloads\converted_details.csv"
    raw_df = pd.read_csv(file_path, header=None)
    
    # Extract Department Name (Col 1), Total (Col 47), Tagged (Col 50), Not Tagged (Col 51)
    df = raw_df.iloc[3:, [1, 47, 50, 51]].copy()
    df.columns = ['Department', 'Total_Assets', 'Tagged', 'Not_Tagged']
    df = df.dropna(subset=['Department'])
    df = df[~df['Department'].str.contains("TOTAL", case=False, na=False)]
    
    for col in ['Total_Assets', 'Tagged', 'Not_Tagged']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

# --- APP 1 LOGIC (SEARCH PORTAL) ---
def run_search_portal():
    st.title("🖥️ Asset Tracking & Search Portal")
    st.markdown("Search for IT assets using Staff Name, Number, PC Model, or Department.")
    
    try:
        df = load_search_data()
    except Exception as e:
        st.error(f"Error loading Search Data: {e}")
        return

    # Auto-Detect Department Column
    if 'Deptt.' in df.columns: DEPT_COL = 'Deptt.'
    elif 'Deptt' in df.columns: DEPT_COL = 'Deptt'
    elif 'Department' in df.columns: DEPT_COL = 'Department'
    else:
        st.error("Could not find a Department column.")
        return

    # Sidebar Filters for Search Portal
    st.sidebar.header("🔍 Search Filters")
    departments = sorted([d for d in df[DEPT_COL].unique() if str(d).strip() != ""])
    dept_filter = st.sidebar.multiselect("Filter by Department", options=departments)

    # Search Feature
    search_query = st.text_input("🔍 Global Search", placeholder="Enter Name, Staff No, Host Name...")

    # Logic
    filtered_df = df.copy()
    if dept_filter:
        filtered_df = filtered_df[filtered_df[DEPT_COL].isin(dept_filter)]
    if search_query:
        desired_columns = ['Name', 'Staff No.', 'P. No.', 'HOST NAME', 'PC Model', 'PC Sl. No.']
        actual_search_columns = [col for col in desired_columns if col in filtered_df.columns]
        if actual_search_columns:
            mask = filtered_df[actual_search_columns].astype(str).apply(
                lambda x: x.str.contains(search_query, case=False, na=False)
            ).any(axis=1)
            filtered_df = filtered_df[mask]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Assets", len(df))
    col2.metric("Filtered Results", len(filtered_df))
    col3.metric("Unique Depts", df[DEPT_COL].nunique())

    tab1, tab2 = st.tabs(["📋 Data View", "📊 Analytics"])
    with tab1:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    with tab2:
        dept_counts = filtered_df[DEPT_COL].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Asset Count']
        st.bar_chart(dept_counts.set_index('Department'))

# --- APP 2 LOGIC (CYBER DASHBOARD) ---
def run_cyber_dashboard():
    # Inject Custom CSS for this view
    st.markdown("""
    <style>
        .stApp { background-color: #120b19; color: #00f2fe; }
        h1, h2, h3 { color: #00ffff !important; text-shadow: 0 0 5px #00ffff; }
        div[data-testid="metric-container"] {
            background-color: #1a2235; border: 1px solid #00ffff; border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🚀 CYBER-IT ASSET TRACKING SYSTEM")
    
    try:
        df = load_dashboard_data()
    except Exception as e:
        st.error(f"Error loading Dashboard Data: {e}")
        return

    search_query = st.sidebar.text_input("🔍 Search Department:", placeholder="e.g. AVIATION")
    filtered_df = df[df['Department'].str.contains(search_query, case=False, na=False)] if search_query else df

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Depts", len(filtered_df))
    col2.metric("Total Assets", filtered_df['Total_Assets'].sum())
    col3.metric("Tagged", filtered_df['Tagged'].sum())

    # Visuals
    fig = px.bar(filtered_df, x='Department', y=['Tagged', 'Not_Tagged'], barmode='group',
                 color_discrete_map={'Tagged': '#00ffff', 'Not_Tagged': '#ff0055'})
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ffff'))
    
    col_chart, col_table = st.columns([3, 2])
    with col_chart: st.plotly_chart(fig, use_container_width=True)
    with col_table: st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# --- MAIN NAVIGATION ---
st.sidebar.title("🖥️ Navigation")
page = st.sidebar.radio("Go to:", ["Search Portal", "Cyber Dashboard"])

if page == "Search Portal":
    run_search_portal()
else:
    run_cyber_dashboard()