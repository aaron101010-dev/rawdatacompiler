import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import plotly.express as px
import io
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIG & PERFORMANCE ---
pd.set_option("styler.render.max_elements", 1000000)
st.set_page_config(page_title="Security Ranker Pro", layout="wide", page_icon="🛡️")

# --- 2. PROFESSIONAL ENTERPRISE UI THEMING ---
st.markdown("""
    <style>
    /* Global Background & Font */
    .stApp { background-color: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    /* Custom Card Styling */
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Header Section */
    .header-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        border-left: 8px solid #3b82f6;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; color: #1e293b; }
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding: 10px 20px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: #2563eb;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background: #1d4ed8; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
    
    /* Sidebar */
    .css-1639199 { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (KEEPING ORIGINAL LOGIC) ---
if 'monthly_db' not in st.session_state:
    st.session_state['monthly_db'] = pd.DataFrame()
if 'file_registry' not in st.session_state:
    st.session_state['file_registry'] = []
if 'processed_dates' not in st.session_state:
    st.session_state['processed_dates'] = set()

# --- 4. PROFESSIONAL PDF ENGINE (ORIGINAL CLASSES) ---
class PDFReport(FPDF):
    def add_secret_stamps(self, p_num):
        self.set_font("Arial", 'B', 8)
        self.set_text_color(170, 170, 170)
        self.text(95, 10, "SECRET")
        self.text(95, 287, "SECRET")
        self.set_font("Arial", '', 8)
        self.text(180, 287, f"Page {p_num} of 3")

def generate_pdf_report(df, start_date, end_date, sensor_id, dk, tk, uk, figs, dynamic_texts):
    pdf = PDFReport()
    # PAGE 1
    pdf.add_page()
    pdf.add_secret_stamps(1)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(29, 78, 216)
    pdf.cell(0, 15, "APPLIED THREAT INTELLIGENCE WEEKLY REPORT", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(100, 116, 139)
    date_str = f"Reporting Period: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    pdf.cell(0, 5, date_str, ln=True)
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    for label, val in [("OFFICE/LOCATION:", "Head Office"), ("SENSOR ID:", sensor_id), ("OPERATIONAL MODE:", "Observe Mode")]:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 7, label, 0)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 7, val, ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(0, 5, "A Shield in Protect mode will analyze and report on all traffic and kill anything unsafe. Observe mode will analyze and report on all traffic. Off Mode will not analyze nor report on any traffic, but will simply forward traffic.")
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, "DNS Responses", 0)
    pdf.cell(60, 10, "TCP Sessions", 0)
    pdf.cell(60, 10, "UDP Sessions", ln=True)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(60, 10, f"{dk:,} Kills", 0)
    pdf.cell(60, 10, f"{tk:,} Kills", 0)
    pdf.cell(60, 10, f"{uk:,} Kills", ln=True)
    pdf.ln(15)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(0, 4, "DNS Responses Killed - Number of Responses for High-Risk Host names and domain names killed.\nTCP Session Killed - Killed TCP requests to High-Risk endpoints.\nUDP Session Killed - Killed UDP Session Requests to High-Risk endpoints.")
    # PAGE 2
    pdf.add_page()
    pdf.add_secret_stamps(2)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(29, 78, 216)
    pdf.cell(0, 10, "Top Requested domain", ln=True)
    b1 = io.BytesIO(); figs[0].savefig(b1, format='png', dpi=150, bbox_inches='tight')
    pdf.image(b1, x=10, y=25, w=185)
    pdf.set_y(150); pdf.cell(0, 10, "Top Killed Domain", ln=True)
    b2 = io.BytesIO(); figs[1].savefig(b2, format='png', dpi=150, bbox_inches='tight')
    pdf.image(b2, x=10, y=165, w=185)
    # PAGE 3
    pdf.add_page()
    pdf.add_secret_stamps(3)
    pdf.set_font("Arial", 'B', 14); pdf.set_text_color(29, 78, 216); pdf.cell(0, 10, "TOP CATEGORIES", ln=True)
    b3 = io.BytesIO(); figs[2].savefig(b3, format='png', dpi=150, bbox_inches='tight')
    pdf.image(b3, x=10, y=25, w=90)
    pdf.set_xy(105, 30); pdf.set_font("Arial", '', 8); pdf.set_text_color(50, 50, 50); pdf.multi_cell(90, 4, dynamic_texts['cat_txt'])
    pdf.set_y(125); pdf.set_font("Arial", 'B', 14); pdf.set_text_color(29, 78, 216); pdf.cell(0, 10, "COUNTRIES VISITED", ln=True)
    b4 = io.BytesIO(); figs[3].savefig(b4, format='png', dpi=150, bbox_inches='tight')
    pdf.image(b4, x=10, y=140, w=185)
    pdf.set_y(235); pdf.set_font("Arial", '', 8); pdf.multi_cell(0, 4, dynamic_texts['country_txt'])
    return bytes(pdf.output(dest='S'))

# --- 5. CORE ENGINE (ORIGINAL LOGIC) ---
def process_excel_with_stats(file, selected_date):
    all_sheets_data = []
    status_text = st.empty()
    progress_bar = st.progress(0)
    xls = pd.ExcelFile(file, engine='openpyxl')
    total_sheets = len(xls.sheet_names)
    for i, sheet_name in enumerate(xls.sheet_names):
        status_text.text(f"Processing sheet: {sheet_name}...")
        progress_bar.progress((i + 1) / total_sheets)
        df = xls.parse(sheet_name)
        df.columns = df.columns.str.strip()
        if 'Status' not in df.columns: continue
        dev_col = 'Device Name' if 'Device Name' in df.columns else 'Device'
        if dev_col in df.columns: df.rename(columns={dev_col: 'Device Name'}, inplace=True)
        if 'Server Country' not in df.columns and 'Client Country' in df.columns:
            df.rename(columns={'Client Country': 'Server Country'}, inplace=True)
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce').fillna(0)
        
        if not st.session_state['monthly_db'].empty:
            history = st.session_state['monthly_db'][['Device Name', 'Domain']].drop_duplicates()
            history['Is_Repeat'] = True
            df = df.merge(history, on=['Device Name', 'Domain'], how='left')
            df['Is_Repeat'] = df['Is_Repeat'].fillna(False)
        else:
            df['Is_Repeat'] = False
        df['Processed_Date'] = pd.to_datetime(selected_date).date()
        all_sheets_data.append(df)
    progress_bar.empty()
    status_text.empty()
    return pd.concat(all_sheets_data, ignore_index=True) if all_sheets_data else pd.DataFrame()

# --- 6. SIDEBAR & HEADER ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1067/1067357.png", width=80)
    st.title("System Control")
    st.markdown("---")
    st.info(f"**Database Status:** {len(st.session_state['monthly_db'])} Log Entries")
    
    if st.session_state['file_registry']:
        st.subheader("📜 Recent Uploads")
        hist_df = pd.DataFrame(st.session_state['file_registry'])
        st.dataframe(hist_df[['filename', 'date']], use_container_width=True, hide_index=True)
    
    if st.button("🗑️ Wipe System Memory"):
        st.session_state['monthly_db'] = pd.DataFrame()
        st.session_state['file_registry'] = []
        st.rerun()

st.markdown("""
    <div class="header-banner">
        <h1 style='margin:0;'>Shield Raw Data Compiler</h1>
        <p style='margin:0; opacity: 0.8;'>Created By: Python Solutions OPC</p>
    </div>
    """, unsafe_allow_html=True)

# --- 7. TABS ---
t_entry, t_monthly, t_report = st.tabs(["📤 DATA INGESTION", "📊 RANKINGS", "📄 REPORT GENERATOR"])

with t_entry:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📥 Log Ingestion")
    c1, c2 = st.columns([1, 2])
    with c1:
        log_date = st.date_input("Processing Date", value=datetime.now())
    with c2:
        up_file = st.file_uploader("Upload Security Excel Export", type=["xlsx"])
    
    if up_file and st.button("🚀 PROCESS DATA"):
        new_df = process_excel_with_stats(up_file, log_date)
        st.session_state['monthly_db'] = pd.concat([st.session_state['monthly_db'], new_df], ignore_index=True)
        st.session_state['file_registry'].append({'filename': up_file.name, 'date': log_date, 'rows': len(new_df)})
        st.success("Successfully ingested log data.")
    st.markdown('</div>', unsafe_allow_html=True)

with t_monthly:
    if not st.session_state['monthly_db'].empty:
        db = st.session_state['monthly_db']
        db_blocked = db[db['Status'].astype(str).str.contains(r'(?i)blocked', na=False)]
        
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        f1, f2, f3 = st.columns([2, 2, 1])
        with f1: dr = st.date_input("Filter Date Range", [db['Processed_Date'].min(), db['Processed_Date'].max()])
        with f2: devs = sorted(db['Device Name'].unique().tolist()); sel_dev = st.selectbox("Select Sensor", ["ALL DEVICES"] + devs)
        with f3: lim = st.select_slider("Ranking Depth", options=[50, 100, 200, 500, 1000], value=200)
        
        mask = (db_blocked['Processed_Date'] >= dr[0])
        if len(dr) > 1: mask &= (db_blocked['Processed_Date'] <= dr[1])
        if sel_dev != "ALL DEVICES": mask &= (db_blocked['Device Name'] == sel_dev)
        
        res = db_blocked[mask].sort_values(['Count', 'Device Name'], ascending=[False, True]).head(lim).copy()
        res.index = range(1, len(res) + 1)
        
        st.dataframe(
            res.style.apply(lambda r: ['background-color: #fef2f2; border-left: 5px solid #ef4444; font-weight: bold']*len(r) if r.get('Is_Repeat', False) else ['']*len(r), axis=1), 
            use_container_width=True, height=500
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Waiting for data upload in the Ingestion tab.")

with t_report:
    if st.session_state['monthly_db'].empty:
        st.warning("No data available. Please upload logs first.")
    else:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        col_r1, col_r2 = st.columns(2)
        rep_range = col_r1.date_input("Reporting Period", [st.session_state['monthly_db']['Processed_Date'].min(), st.session_state['monthly_db']['Processed_Date'].max()])
        rep_dev = col_r2.selectbox("Target Sensor ID", sorted(st.session_state['monthly_db']['Device Name'].unique().tolist()))
        
        # --- NEW RFC FILTER TOGGLE ---
        exclude_rfc = st.toggle("Exclude Internal/Private Network Traffic (RFC1918)", value=True, help="Hides Private IPs, Localhost, and Internal Network ranges from the geographic charts.")

        mask = (st.session_state['monthly_db']['Processed_Date'] >= rep_range[0])
        if len(rep_range) > 1: mask &= (st.session_state['monthly_db']['Processed_Date'] <= rep_range[1])
        mask &= (st.session_state['monthly_db']['Device Name'] == rep_dev)
        df = st.session_state['monthly_db'][mask].copy()

        if not df.empty:
            blocked = df[df['Status'].astype(str).str.contains(r'(?i)blocked', na=False)]
            total_sum = int(blocked['Count'].sum())
            dk, tk = int(total_sum*0.46), int(total_sum*0.33); uk = total_sum - dk - tk

            # Dashboard Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("DNS Kills", f"{dk:,}")
            m2.metric("TCP Kills", f"{tk:,}")
            m3.metric("UDP Kills", f"{uk:,}")
            m4.metric("Total Count", f"{total_sum:,}")

            # Analytics (Original Logic/Plots)
            tr_data = df.groupby('Domain')['Count'].sum().nlargest(10).reset_index()
            tkill_data = blocked.groupby('Domain')['Count'].sum().nlargest(10).reset_index()
            
            # Matplotlib for PDF (Logic untouched)
            f1, a1 = plt.subplots(figsize=(10,5)); tr_data.set_index('Domain').plot(kind='bar', color='#2563eb', ax=a1); a1.ticklabel_format(style='plain', axis='y'); plt.xticks(rotation=45, ha='right'); plt.tight_layout()
            f2, a2 = plt.subplots(figsize=(10,5)); tkill_data.set_index('Domain').plot(kind='bar', color='#dc2626', ax=a2); a2.ticklabel_format(style='plain', axis='y'); plt.xticks(rotation=45, ha='right'); plt.tight_layout()

            risk_col = 'Risk Reason' if 'Risk Reason' in blocked.columns else 'Status'
            cat_data = blocked.copy()
            cat_data[risk_col] = cat_data[risk_col].fillna("Not Classified")
            cat_sum = cat_data.groupby(risk_col)['Count'].sum().sort_values(ascending=False).reset_index()
            f3, a3 = plt.subplots(figsize=(8,6)); labels = [str(x)[:20] for x in cat_sum[risk_col]]; w, t, at = a3.pie(cat_sum['Count'], autopct='%1.1f%%', colors=['#3b82f6','#ef4444','#10b981','#f59e0b']); a3.legend(w, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1)); plt.tight_layout()

            # --- GEOGRAPHIC LOGIC WITH RFC FILTER ---
            c_col = 'Server Country' if 'Server Country' in df.columns else 'Location'
            geo_df = df.copy()
            geo_blocked_df = blocked.copy()

            if exclude_rfc:
                rfc_patterns = ['Private', 'Local', 'Internal', 'Reserved', 'RFC', '192.168.', '10.', '172.']
                pattern = '|'.join(rfc_patterns)
                geo_df = geo_df[~geo_df[c_col].astype(str).str.contains(pattern, na=False, case=False)]
                geo_blocked_df = geo_blocked_df[~geo_blocked_df[c_col].astype(str).str.contains(pattern, na=False, case=False)]

            total_c = geo_df.groupby(c_col)['Count'].sum().nlargest(10)
            blocked_c = geo_blocked_df.groupby(c_col)['Count'].sum().reindex(total_c.index, fill_value=0)
            c_df = pd.DataFrame({'Total': total_c.values, 'Blocked': blocked_c.values}, index=total_c.index).reset_index()
            f4, a4 = plt.subplots(figsize=(12,6)); c_df.set_index(c_col).plot(kind='bar', ax=a4, color=['#2563eb','#dc2626']); a4.ticklabel_format(style='plain', axis='y'); plt.xticks(rotation=45, ha='right'); plt.tight_layout()

            # Dynamic Text (Respecting Geo Filter)
            cl = total_c.index.tolist()
            c1, c2, c3 = (cl[0] if len(cl)>0 else "N/A"), (cl[1] if len(cl)>1 else "N/A"), (cl[2] if len(cl)>2 else "N/A")
            country_txt = f"Connections originated from {c1}, {c2} and {c3}. {c1} shows volume of {int(total_c[0] if not total_c.empty else 0):,} queries."
            cat_txt = f"Traffic is primarily categorized as {cat_sum[risk_col][0] if not cat_sum.empty else 'N/A'}."

            # Dashboard Visuals
            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(px.bar(tr_data, x='Domain', y='Count', title="Top Domain Requests", color_discrete_sequence=['#2563eb']), use_container_width=True)
                st.plotly_chart(px.pie(cat_sum, values='Count', names=risk_col, title="Threat Categories", hole=.3), use_container_width=True)
            with col_chart2:
                st.plotly_chart(px.bar(tkill_data, x='Domain', y='Count', title="Top Domains Mitigated", color_discrete_sequence=['#dc2626']), use_container_width=True)
                st.plotly_chart(px.bar(c_df, x=c_col, y=['Total', 'Blocked'], barmode='group', title="Geographic Volume"), use_container_width=True)

            if st.button("🏗️ COMPILE EXECUTIVE PDF REPORT"):
                pdf_b = generate_pdf_report(df, rep_range[0], rep_range[1] if len(rep_range)>1 else rep_range[0], rep_dev, dk, tk, uk, [f1, f2, f3, f4], {'cat_txt': cat_txt, 'country_txt': country_txt})
                st.download_button("📥 DOWNLOAD PDF", pdf_b, f"Report_{rep_dev}.pdf", "application/pdf")
        st.markdown('</div>', unsafe_allow_html=True)
