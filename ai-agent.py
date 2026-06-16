import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from google import genai
from google.genai import types

# ── PAGE CONFIGURATION ───────────────────────────────────────────────────────
st.set_page_config(page_title="AI Data Agent - Enterprise BI", page_icon="📈", layout="wide")

# Custom CSS for Tab font size, spacing, and AI chat text output
st.markdown("""
    <style>
    /* AI chat text size */
    .big-chat-text {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    /* Enlarge text size on Streamlit Tabs */
    button[data-baseweb="tab"] div p {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 5px 10px !important;
    }
    /* Add margin between Tabs and the content below */
    .stTabs > div:nth-child(2) {
        margin-top: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ── SIDEBAR: CONFIGURATION ───────────────────────────────────────────────────
with st.sidebar:
    # --- COPYRIGHT ---
    st.markdown("### © RsydMathTech")
    st.markdown("---")
    
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    # --- HELPFUL LINK FOR API KEY ---
    st.caption("💡 **Need an API Key?**\nGet one for free at [Google AI Studio](https://aistudio.google.com/app/apikey).")
    
    # --- AUTO-TEST API KEY (MINIMUM TOKEN) ---
    if api_key:
        # Check so the API isn't hit continuously on every Streamlit refresh
        if "validated_api_key" not in st.session_state or st.session_state.get("current_api_key") != api_key:
            st.session_state.current_api_key = api_key
            
            with st.spinner("Checking API connection..."):
                try:
                    client = genai.Client(api_key=api_key)
                    # Lightweight test with 1 token limit to save quota
                    client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents="hi",
                        config=types.GenerateContentConfig(max_output_tokens=1)
                    )
                    st.session_state.validated_api_key = True
                except Exception as e:
                    st.session_state.validated_api_key = False
                    st.session_state.api_error_msg = str(e)
        
        # Display check results from memory (session_state)
        if st.session_state.get("validated_api_key"):
            st.success("✅ Valid API Key & Connected!")
        else:
            st.error("❌ Connection Failed! Check your API Key.")
            with st.expander("See Error Details"):
                st.code(st.session_state.get("api_error_msg", "Unknown Error"))

    st.markdown("---")
    uploaded_files = st.file_uploader("📁 Upload Datasets (Multiple CSVs allowed)", type=["csv"], accept_multiple_files=True)
    
    # --- LINKEDIN CREDITS ---
    st.markdown("---")
    st.markdown(
        "👨‍💻 **Muhammad Abdurrasyid Fahrurozi**<br>"
        "🔗 [LinkedIn Profile](https://id.linkedin.com/in/m-abdurrasyid)", 
        unsafe_allow_html=True
    )

st.title("📈 DataAgent AI — Enterprise Business Intelligence")
st.markdown("Automated BI system with Multi-Dataset support & Token-Efficient AI.")

# ── AUTO-HEURISTIC SCHEMA MAPPING ───────────────────────────────────────────
@st.cache_data(show_spinner=False)
def auto_detect_schema(df):
    mapping = {"date": None, "rev": None, "cost": None, "qty": None, "cat": None}
    kw_date = ['date', 'tanggal', 'time', 'waktu', 'month', 'bulan']
    kw_rev = ['revenue', 'sales', 'pendapatan', 'omset', 'total', 'amount']
    kw_cost = ['cost', 'biaya', 'cogs', 'hpp', 'modal', 'expense']
    kw_qty = ['quantity', 'qty', 'jumlah', 'volume']
    kw_cat = ['category', 'kategori', 'product', 'produk', 'item']

    for col in df.columns:
        c_low = str(col).lower()
        if not mapping["date"] and any(k in c_low for k in kw_date): mapping["date"] = col
        elif not mapping["rev"] and any(k in c_low for k in kw_rev) and pd.api.types.is_numeric_dtype(df[col]): mapping["rev"] = col
        elif not mapping["cost"] and any(k in c_low for k in kw_cost) and pd.api.types.is_numeric_dtype(df[col]): mapping["cost"] = col
        elif not mapping["qty"] and any(k in c_low for k in kw_qty) and pd.api.types.is_numeric_dtype(df[col]): mapping["qty"] = col
        elif not mapping["cat"] and any(k in c_low for k in kw_cat): mapping["cat"] = col

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not mapping["rev"] and len(num_cols) > 0: mapping["rev"] = num_cols[0]
    if not mapping["cost"] and len(num_cols) > 1: mapping["cost"] = num_cols[1]
    obj_cols = df.select_dtypes(include=['object']).columns.tolist()
    if not mapping["cat"] and obj_cols: mapping["cat"] = obj_cols[0]

    return mapping

# ── MAIN LOGIC ───────────────────────────────────────────────────────────────
if uploaded_files:
    dfs = {file.name: pd.read_csv(file) for file in uploaded_files}
    
    # ── DATASET SELECTION ──
    st.markdown("### 🎛️ Select Dataset for Main Dashboard:")
    selected_filename = st.selectbox("", list(dfs.keys()))
    main_df = dfs[selected_filename].copy()
    mapping = auto_detect_schema(main_df)
    
    # ── AUTO-RESET MEMORY ON FILE CHANGE ──
    # If a new dataset is selected or loaded, reset the chat state to clean old memories
    if "last_selected_file" not in st.session_state or st.session_state.last_selected_file != selected_filename:
        st.session_state.last_selected_file = selected_filename
        st.session_state.messages = [{
            "role": "assistant", 
            "content": f"Hello! I am your AI Data Agent. I have successfully loaded and optimized analysis for **{selected_filename}**. Ask me any analytical question!"
        }]
    
    # ── QUICK OVERVIEW CHART (AUTOMATIC) ──
    st.subheader("⚡ Quick Overview")
    with st.expander("Expand Quick Charts", expanded=True):
        q_col1, q_col2 = st.columns(2)
        
        with q_col1:
            if mapping["date"] and mapping["rev"]:
                main_df[mapping["date"]] = pd.to_datetime(main_df[mapping["date"]], errors='coerce')
                q_trend = main_df.dropna(subset=[mapping["date"]]).copy()
                q_trend['M'] = q_trend[mapping["date"]].dt.to_period('M').astype(str)
                q_trend_grp = q_trend.groupby('M')[mapping["rev"]].sum().reset_index()
                st.plotly_chart(px.line(q_trend_grp, x='M', y=mapping["rev"], title="Revenue Trend (Auto)"), use_container_width=True)
            else:
                st.info("Automation: Looking for Date & Revenue columns for trend...")

        with q_col2:
            if mapping["cat"] and mapping["rev"]:
                q_cat_grp = main_df.groupby(mapping["cat"])[mapping["rev"]].sum().reset_index().sort_values(by=mapping["rev"], ascending=False).head(10)
                st.plotly_chart(px.bar(q_cat_grp, x=mapping["rev"], y=mapping["cat"], orientation='h', title="Top Categories (Auto)"), use_container_width=True)
            else:
                st.info("Automation: Looking for Category & Revenue columns...")

    # Pre-processing P&L
    rev_col, cost_col = mapping["rev"], mapping["cost"]
    total_rev = main_df[rev_col].sum() if rev_col else 0
    total_cost = main_df[cost_col].sum() if cost_col else 0
    total_profit = total_rev - total_cost
    margin_pct = (total_profit / total_rev * 100) if total_rev > 0 else 0

    # ── TABS ──
    tab1, tab2, tab3, tab4 = st.tabs(["📊 P&L Dashboard", "🤖 AI Insights (Text Only)", "🗃️ Raw Data", "🛠️ Custom Chart Builder"])

    # --- TAB 1: EXECUTIVE DASHBOARD ---
    with tab1:
        with st.container(border=True):
            st.markdown("### 📈 Performance Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Total Revenue", f"{total_rev:,.0f}")
            c2.metric("📉 Total Cost", f"{total_cost:,.0f}")
            c3.metric("💎 Net Profit", f"{total_profit:,.0f}", f"{margin_pct:.1f}% Margin")
            
            st.markdown("---")
            if rev_col:
                st.plotly_chart(px.histogram(main_df, x=rev_col, title="Distribution of Revenue"), use_container_width=True)

    # --- TAB 2: AI INSIGHTS ---
    with tab2:
        with st.container(border=True):
            st.info("💡 Enter API Key in the sidebar. AI will provide text insights only (Token Efficient).")
            
            # Ensure the API key is truly valid before opening the chatbox
            is_valid_api = st.session_state.get("validated_api_key", False)
            
            if not api_key or not is_valid_api:
                st.warning("⚠️ Enter a valid Gemini API Key in the Sidebar to activate the AI Agent." if not api_key else "⚠️ Waiting for a valid API Key to initialize chat.")
            else:
                client = genai.Client(api_key=api_key)

                # Using a fixed-height container for scrollable chat area
                chat_container = st.container(height=500, border=True)
                
                with chat_container:
                    for msg in st.session_state.messages:
                        with st.chat_message(msg["role"]):
                            st.markdown(f"<div class='big-chat-text'>{msg['content']}</div>", unsafe_allow_html=True)

                if user_query := st.chat_input("Ask for analysis (Text only)..."):
                    st.session_state.messages.append({"role": "user", "content": user_query})
                    
                    with chat_container:
                        with st.chat_message("user"): 
                            st.markdown(f"<div class='big-chat-text'>{user_query}</div>", unsafe_allow_html=True)

                    with chat_container:
                        with st.chat_message("assistant"):
                            with st.spinner("Analyzing data..."):
                                try:
                                    sys_inst = """
                                    You are a Senior Business Analyst. 
                                    Language: English.
                                    
                                    STRICT RULES:
                                    1. DO NOT write any Python code blocks for charts (No Plotly, No Matplotlib).
                                    2. DO NOT use LaTeX formatting or '$' symbols.
                                    3. Provide your analysis in PLAIN TEXT and MARKDOWN tables only.
                                    4. If calculations are needed, explain them step-by-step in text.
                                    5. Focus on identifying trends, anomalies, and business recommendations based ONLY on the given context.
                                    """
                                    
                                    # ── TOKEN-EFFICIENT BACKGROUND AGGREGATION ──
                                    # Generate actual data aggregates dynamically so AI gets real metrics without parsing huge files
                                    agg_context = ""
                                    if mapping["cat"] and rev_col:
                                        if cost_col:
                                            # Create a tight, small text summary table of true categories
                                            cat_perf = main_df.groupby(mapping["cat"]).agg(
                                                Revenue=(rev_col, "sum"),
                                                Cost=(cost_col, "sum")
                                            )
                                            cat_perf["Profit"] = cat_perf["Revenue"] - cat_perf["Cost"]
                                            cat_perf["Margin_%"] = ((cat_perf["Profit"] / cat_perf["Revenue"]) * 100).round(2)
                                            agg_context += f"\nTrue Category Performance Breakdown:\n{cat_perf.to_string()}\n"
                                        else:
                                            cat_perf = main_df.groupby(mapping["cat"])[rev_col].sum().to_frame()
                                            agg_context += f"\nTrue Category Revenue Breakdown:\n{cat_perf.to_string()}\n"
                                    
                                    # Dynamically extract some unique values from any text object columns to prevent hallucinated labels
                                    obj_cols = main_df.select_dtypes(include=['object']).columns[:3]
                                    if len(obj_cols) > 0:
                                        agg_context += "\nSample Values Existing in Categorical Columns:\n"
                                        for col in obj_cols:
                                            uniques = main_df[col].dropna().unique()[:8]
                                            agg_context += f"- {col}: {list(uniques)}\n"

                                    summary_stats = main_df.describe().to_string()
                                    schema_info = f"Columns: {list(main_df.columns)}"
                                    
                                    # Merge static overview and precise aggregates into a robust, low-token context prompt
                                    full_prompt = f"Data Context:\n{schema_info}\n\nSummary Stats:\n{summary_stats}\n{agg_context}\nQuestion: {user_query}"

                                    response = client.models.generate_content(
                                        model='gemini-2.0-flash',
                                        contents=full_prompt,
                                        config=types.GenerateContentConfig(system_instruction=sys_inst, temperature=0.1)
                                    )
                                    
                                    res_text = response.text
                                    st.markdown(f"<div class='big-chat-text'>{res_text}</div>", unsafe_allow_html=True)
                                    st.session_state.messages.append({"role": "assistant", "content": res_text})
                                    
                                except Exception as e:
                                    st.error(f"Error: {e}")

    # --- TAB 3: DATA EXPLORER ---
    with tab3:
        with st.container(border=True):
            st.markdown("### 🗃️ Raw Data Explorer")
            st.dataframe(main_df, use_container_width=True)

    # --- TAB 4: MANUAL CHART BUILDER ---
    with tab4:
        with st.container(border=True):
            st.markdown("### 🛠️ Custom Chart Builder")
            bx, by, bt = st.columns(3)
            sel_x = bx.selectbox("X-Axis", main_df.columns, key="bx")
            sel_y = by.selectbox("Y-Axis", main_df.select_dtypes(include=[np.number]).columns, key="by")
            sel_t = bt.selectbox("Type", ["Bar", "Line", "Scatter", "Box"], key="bt")
            
            if st.button("Build Chart"):
                if sel_t == "Bar": fig = px.bar(main_df, x=sel_x, y=sel_y)
                elif sel_t == "Line": fig = px.line(main_df.sort_values(sel_x), x=sel_x, y=sel_y)
                elif sel_t == "Scatter": fig = px.scatter(main_df, x=sel_x, y=sel_y)
                else: fig = px.box(main_df, x=sel_x, y=sel_y)
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📁 Please upload dataset files to get started.")
