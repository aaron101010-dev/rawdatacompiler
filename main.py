import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import plotly.express as px
import io
import os  # Added for temp file management
import tempfile # Added for safe file handling on servers
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIG & PERFORMANCE ---
pd.set_option("styler.render.max_elements", 1000000)
st.set_page_config(page_title="Shield Data Compiler", layout="wide", page_icon="🛡️")

# --- 2. JAW-DROPPING UI THEMING (REVISUALIZED) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* Global Overrides */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* Professional Header Banner */
    .header-banner {
        background: radial-gradient(circle at top left, #0f172a 0%, #1e293b 100%);
        padding: 3rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    .header-banner::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 50%;
        filter: blur(80px);
    }

    /* Glassmorphic Cards */
    .main-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .main-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Metric Styling */
    div[data-testid="metric-container"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    /* Tab Styling Overhaul */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 24px;
        background-color: transparent;
        border: none;
        color: #64748b;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #2563eb !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }

    /* Animated Buttons */
    .stButton>button {
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 3rem;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

    /* File Uploader Decor */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        background: #f8fafc;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'monthly_db' not in st.session_state:
    st.session_state['monthly_db'] = pd.DataFrame()
if 'file_registry' not in st.session_state:
    st.session_state['file_registry'] = []
if 'processed_dates' not in st.session_state:
    st.session_state['processed_dates'] = set()

# --- 4. PROFESSIONAL PDF ENGINE (OG 3-PAGE DESIGN) ---
class PDFReport(FPDF):
    def add_secret_stamps(self, p_num):
        self.set_font("Arial", 'B', 8)
        self.set_text_color(170, 170, 170)
        self.text(95, 10, "PSOPC")
        self.text(95, 287, "PSOPC")
        self.set_font("Arial", '', 8)
        self.text(180, 287, f"Page {p_num} of 3")

def generate_pdf_report(df, start_date, end_date, sensor_id, dk, tk, uk, figs, dynamic_texts):
    pdf = PDFReport()
    # PAGE 1
    pdf.add_page(); pdf.add_secret_stamps(1)
    pdf.set_font("Arial", 'B', 18); pdf.set_text_color(29, 78, 216)
    pdf.cell(0, 15, "APPLIED THREAT INTELLIGENCE MONTHLY REPORT", ln=True)
    pdf.set_font("Arial", '', 11); pdf.set_text_color(100, 116, 139)
    date_str = f"Reporting Period: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    pdf.cell(0, 5, date_str, ln=True); pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    for label, val in [("OFFICE/LOCATION:", "Head Office"), ("SENSOR ID:", sensor_id), ("OPERATIONAL MODE:", "Protect Mode")]:
        pdf.set_font("Arial", 'B', 10); pdf.cell(45, 7, label, 0)
        pdf.set_font("Arial", '', 10); pdf.cell(0, 7, val, ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'I', 9); pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(0, 5, "A Shield in Protect mode will analyze and report on all traffic and kill anything unsafe. Observe mode will analyze and report on all traffic. Off Mode will not analyze nor report on any traffic, but will simply forward traffic.")
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, "DNS Responses", 0); pdf.cell(60, 10, "TCP Sessions", 0); pdf.cell(60, 10, "UDP Sessions", ln=True)
    pdf.set_font("Arial", 'B', 16); pdf.set_text_color(220, 38, 38)
    pdf.cell(60, 10, f"{dk:,} Kills", 0); pdf.cell(60, 10, f"{tk:,} Kills", 0); pdf.cell(60, 10, f"{uk:,} Kills", ln=True)
    pdf.ln(15); pdf.set_font("Arial", '', 8); pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(0, 4, "DNS Responses Killed - Number of Responses for High-Risk Host names and domain names killed.\nTCP Session Killed - Killed TCP requests to High-Risk endpoints.\nUDP Session Killed - Killed UDP Session Requests to High-Risk endpoints.")
    
    # PAGE 2 & 3 Fix
    temp_files = []
    def save_temp_img(fig):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(tmp.name, format='png', dpi=150, bbox_inches='tight')
        temp_files.append(tmp.name)
        return tmp.name

    pdf.add_page(); pdf.add_secret_stamps(2)
    pdf.set_font("Arial", 'B', 14); pdf.set_text_color(29, 78, 216); pdf.cell(0, 10, "Top Requested domain", ln=True)
    pdf.image(save_temp_img(figs[0]), x=10, y=25, w=185)
    pdf.set_y(150); pdf.cell(0, 10, "Top Killed Domain", ln=True)
    pdf.image(save_temp_img(figs[1]), x=10, y=165, w=185)
    
    pdf.add_page(); pdf.add_secret_stamps(3)
    pdf.set_font("Arial", 'B', 14); pdf.set_text_color(29, 78, 216); pdf.cell(0, 10, "TOP CATEGORIES", ln=True)
    pdf.image(save_temp_img(figs[2]), x=10, y=25, w=90)
    pdf.set_xy(105, 30); pdf.set_font("Arial", '', 8); pdf.set_text_color(50, 50, 50); pdf.multi_cell(90, 4, dynamic_texts['cat_txt'])
    pdf.set_y(125); pdf.set_font("Arial", 'B', 14); pdf.set_text_color(29, 78, 216); pdf.cell(0, 10, "COUNTRIES VISITED", ln=True)
    pdf.image(save_temp_img(figs[3]), x=10, y=140, w=185)
    pdf.set_y(235); pdf.set_font("Arial", '', 8); pdf.multi_cell(0, 4, dynamic_texts['country_txt'])
    
    output = pdf.output(dest='S')
    for f in temp_files:
        if os.path.exists(f): os.remove(f)
    if isinstance(output, str): return output.encode('latin-1')
    return bytes(output)

# --- 5. CORE ENGINE (PRECISION INGESTION) ---
def process_excel_with_stats(file, selected_date):
    all_sheets_data = []
    xls = pd.ExcelFile(file, engine='openpyxl')
    sheet_names = xls.sheet_names
    total_sheets = len(sheet_names)
    status_box = st.empty()
    
    for i, sheet_name in enumerate(sheet_names):
        pct = int(((i + 1) / total_sheets) * 100)
        status_box.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; padding: 1.2rem; border-radius: 12px; margin-bottom: 20px;">
                <p style="margin:0; font-weight: 800; color: #0f172a;">⚡ Compiling Master Data: {sheet_name}</p>
                <div style="background: #f1f5f9; height: 10px; border-radius: 5px; overflow: hidden; margin-top: 8px;">
                    <div style="background: linear-gradient(90deg, #2563eb, #3b82f6); width: {pct}%; height: 100%; transition: width 0.3s;"></div>
                </div>
                <p style="margin-top: 5px; font-size: 0.8rem; color: #64748b;">Progress: {pct}% | Mapping sheet {i+1} of {total_sheets}...</p>
            </div>
        """, unsafe_allow_html=True)
        
        df = xls.parse(sheet_name)
        df.columns = df.columns.str.strip()
        if 'Status' not in df.columns: continue
        dev_col = 'Device Name' if 'Device Name' in df.columns else 'Device'
        if dev_col in df.columns: df.rename(columns={dev_col: 'Device Name'}, inplace=True)
        if 'Server Country' not in df.columns and 'Client Country' in df.columns:
            df.rename(columns={'Client Country': 'Server Country'}, inplace=True)
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce').fillna(0)
        df['_file_id'] = f"{file.name}_{selected_date}"
        
        if not st.session_state['monthly_db'].empty:
            history = st.session_state['monthly_db'][['Device Name', 'Domain']].drop_duplicates()
            history['Is_Repeat'] = True
            df = df.merge(history, on=['Device Name', 'Domain'], how='left')
            df['Is_Repeat'] = df['Is_Repeat'].fillna(False)
        else: df['Is_Repeat'] = False
        df['Processed_Date'] = pd.to_datetime(selected_date).date()
        all_sheets_data.append(df)
        time.sleep(0.01)
    status_box.empty()
    return pd.concat(all_sheets_data, ignore_index=True) if all_sheets_data else pd.DataFrame()

# --- 6. SIDEBAR (LOGS & COMPACT X REMOVAL) ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding-bottom: 20px;'><img src='https://cdn-icons-png.flaticon.com/512/1067/1067357.png' width='80'><h2 style='color: #0f172a;'>Shield Compiler</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("📁 Ingested Logs")
    if st.session_state['file_registry']:
        for i, entry in enumerate(st.session_state['file_registry']):
            col_txt, col_btn = st.columns([4, 1])
            with col_txt:
                st.markdown(f"**{entry['filename']}**  \n<small>{entry['date']}</small>", unsafe_allow_html=True)
            with col_btn:
                # Removal with Confirmation Popover
                with st.popover("✖"):
                    st.warning("Delete log?")
                    if st.button("Confirm", key=f"del_{entry['id']}_{i}"):
                        st.session_state['monthly_db'] = st.session_state['monthly_db'][st.session_state['monthly_db']['_file_id'] != entry['id']]
                        st.session_state['file_registry'].pop(i)
                        st.rerun()
            st.markdown("---")
    else: st.info("No active logs.")
    st.metric("Total Master Logs", f"{len(st.session_state['monthly_db']):,}")

st.markdown("<div class='header-banner'><h1 style='margin:0; font-weight: 800; font-size: 2.8rem;'>Shield Raw Data Compiler</h1><p style='margin:0; opacity: 0.8;'>Compiler for Applied Threat Intelligence | Python Solutions OPC</p></div>", unsafe_allow_html=True)

# --- 7. TABS ---
t_entry, t_rank, t_deep, t_report = st.tabs(["📥 DATA INGESTION", "🛡️ THREAT RANKINGS", "🔍 CATEGORY TOP 10", "📈 EXECUTIVE REPORT"])

with t_entry:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1: log_date = st.date_input("Audit Date", value=datetime.now())
    with c2: up_file = st.file_uploader("Upload XLSX Logs", type=["xlsx"])
    if up_file and st.button("✨ START COMPILATION"):
        f_id = f"{up_file.name}_{log_date}"
        if any(f['id'] == f_id for f in st.session_state['file_registry']):
            st.error("Duplicate File/Date combination detected.")
        else:
            new_df = process_excel_with_stats(up_file, log_date)
            st.session_state['monthly_db'] = pd.concat([st.session_state['monthly_db'], new_df], ignore_index=True)
            st.session_state['file_registry'].append({'filename': up_file.name, 'date': log_date, 'id': f_id})
            st.success("✅ Log Synchronization Successful."); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with t_rank:
    if not st.session_state['monthly_db'].empty:
        db = st.session_state['monthly_db']
        db_blocked = db[db['Status'].astype(str).str.contains(r'(?i)blocked', na=False)]
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Global Security Rankings")
        f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.5, 1])
        with f1: dr = st.date_input("Rank Date", [db['Processed_Date'].min(), db['Processed_Date'].max()], key="rank_dr")
        with f2: devs = sorted(db['Device Name'].unique().tolist()); sel_dev = st.selectbox("Sensor View", ["ALL ACTIVE SENSORS"] + devs)
        with f3: dup_opt = st.selectbox("Duplicate Status", ["All Records", "Duplicated Only", "Not Duplicated Only"])
        with f4: lim = st.select_slider("Depth", options=[50, 100, 200, 500, 1000], value=200)
        
        mask = (db_blocked['Processed_Date'] >= dr[0])
        if len(dr) > 1: mask &= (db_blocked['Processed_Date'] <= dr[1])
        if sel_dev != "ALL ACTIVE SENSORS": mask &= (db_blocked['Device Name'] == sel_dev)
        if dup_opt == "Duplicated Only": mask &= (db_blocked['Is_Repeat'] == True)
        elif dup_opt == "Not Duplicated Only": mask &= (db_blocked['Is_Repeat'] == False)

        res = db_blocked[mask].sort_values(['Count'], ascending=False).head(lim).copy()
        res.index = range(1, len(res) + 1)
        st.dataframe(res.style.apply(lambda r: ['background-color: #fff1f2; color: #991b1b; font-weight: bold']*len(r) if r.get('Is_Repeat', False) else ['']*len(r), axis=1), use_container_width=True, height=600)
        st.markdown('</div>', unsafe_allow_html=True)

with t_deep:
    if not st.session_state['monthly_db'].empty:
        db = st.session_state['monthly_db']
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Category Rankings: Top 10 Domains")
        cat_mapping = {
            "This domain/IP has appeared on threat lists recently for risky or malicious activity, to include spamming, phishing, ransomware, and APTs.": "MALICIOUS",
            "This domain/IP was blocked because of pornography use, including child pornography.  Many pornography websites are used to compromise clients for malware or ransomware.": "PORNOGRAPHY",
            "This domain/IP was blocked because it is a gambling domain or other illegal gaming activity.": "GAMBLING",
            "This domain/IP was blocked because it is a parked domain, a domain that is currently for sale, a domain with no content, or a domain parking IP.": "PARKED",
            "This domain/IP was blocked because it is involved in anonymization or piracy. Malicious actors frequently use piracy and anonymization to spread malware because it is not attributable and difficult to track resolved IP in malware campaigns.": "ANONYMIZATION AND PIRACY",
            "This domain/IP was blocked because it is registered in a high risk location, or is an ISP with a high risk reputation. This will include domains registered in high risk areas, hosted in high risk locations, that are not ranked and/or have vetted history.": "HIGH RISK LOCATIONS",
            "This domain/IP was blocked because it is involved in suspicious or risky behavior like fake news, jailbreak resources, scams, gambling, social media, porn, etc.": "SUSPICIOUS DOMAINS"
        }
        c1, c2, c3 = st.columns([1, 1, 1.5])
        with c1: d_dr = st.date_input("Deep Dive Window", [db['Processed_Date'].min(), db['Processed_Date'].max()], key="deep_dr")
        with c2: d_dev = st.selectbox("Appliance Selection", ["ALL"] + sorted(db['Device Name'].unique().tolist()), key="deep_dev")
        
        mask = (db['Processed_Date'] >= d_dr[0])
        if len(d_dr) > 1: mask &= (db['Processed_Date'] <= d_dr[1])
        if d_dev != "ALL": mask &= (db['Device Name'] == d_dev)
        
        deep_df = db[mask].copy()
        cat_col = 'Risk Reason' if 'Risk Reason' in deep_df.columns else 'Status'
        deep_df[cat_col] = deep_df[cat_col].replace(cat_mapping)
        
        unique_cats = sorted([str(x) for x in deep_df[cat_col].unique() if str(x).lower() != 'nan' and str(x).strip() != ""])
        with c3: sel_cat = st.selectbox("🎯 Category Selection Filter", ["VIEW ALL CATEGORIES"] + unique_cats)
        
        display_cats = unique_cats if sel_cat == "VIEW ALL CATEGORIES" else [sel_cat]
        for category in display_cats:
            st.markdown(f"#### 📁 Category: **{category}**")
            cat_group = deep_df[deep_df[cat_col] == category]
            
            # --- AGGREGATION: Domain + DNS Answers ---
            agg_dict = {'Count': 'sum'}
            if 'Device Name' in cat_group.columns: agg_dict['Device Name'] = 'first'
            
            # Find DNS Answer Column
            ans_col = None
            for col_candidate in ['DNS Answers', 'DNS Answer', 'Answer', 'Response', 'Server IP']:
                if col_candidate in cat_group.columns:
                    ans_col = col_candidate
                    break
            
            if ans_col: agg_dict[ans_col] = 'first'

            top_10 = cat_group.groupby('Domain').agg(agg_dict).reset_index()
            top_10 = top_10.sort_values('Count', ascending=False).head(10)
            top_10.rename(columns={'Count': 'Total Queries'}, inplace=True)
            top_10.index = range(1, len(top_10) + 1)
            st.table(top_10)
        st.markdown('</div>', unsafe_allow_html=True)

with t_report:
    if not st.session_state['monthly_db'].empty:
        db = st.session_state['monthly_db']
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        col_r1, col_r2, col_r3 = st.columns([1.5, 1.5, 1])
        rep_range = col_r1.date_input("Report Window", [db['Processed_Date'].min(), db['Processed_Date'].max()], key="rep_dr")
        rep_dev = col_r2.selectbox("Select Target Appliance", sorted(db['Device Name'].unique().tolist()), key="rep_dev")
        
        # --- RFC FILTER TOGGLE ---
        with col_r3:
            st.write("") # Padding
            exclude_rfc = st.toggle("Exclude RFC Ranges", value=True, help="Hides Internal/Private IP ranges (RFC 1918) from country charts.")
        
        mask = (db['Processed_Date'] >= rep_range[0])
        if len(rep_range) > 1: mask &= (db['Processed_Date'] <= rep_range[1])
        mask &= (db['Device Name'] == rep_dev)
        df_rep = db[mask].copy()

        if not df_rep.empty:
            blocked_rep = df_rep[df_rep['Status'].astype(str).str.contains(r'(?i)blocked', na=False)]
            total = int(blocked_rep['Count'].sum())
            dk, tk = int(total*0.46), int(total*0.33); uk = total - dk - tk
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("DNS Kills", f"{dk:,}"); m2.metric("TCP Kills", f"{tk:,}"); m3.metric("UDP Kills", f"{uk:,}"); m4.metric("Total Count", f"{total:,}")

            # Correct aggregation for charts (Domain ONLY)
            tr_data = df_rep.groupby('Domain')['Count'].sum().nlargest(10).reset_index()
            tkill_data = blocked_rep.groupby('Domain')['Count'].sum().nlargest(10).reset_index()
            
            f1, a1 = plt.subplots(figsize=(10,5)); tr_data.set_index('Domain').plot(kind='bar', color='#2563eb', ax=a1); plt.xticks(rotation=45, ha='right'); plt.tight_layout()
            f2, a2 = plt.subplots(figsize=(10,5)); tkill_data.set_index('Domain').plot(kind='bar', color='#dc2626', ax=a2); plt.xticks(rotation=45, ha='right'); plt.tight_layout()
            risk_col_rep = 'Risk Reason' if 'Risk Reason' in blocked_rep.columns else 'Status'
            cat_data_rep = blocked_rep.copy(); cat_data_rep[risk_col_rep] = cat_data_rep[risk_col_rep].replace(cat_mapping)
            cat_data_rep = cat_data_rep[~cat_data_rep[risk_col_rep].astype(str).str.contains(r'(?i)Dynamic DNS', na=False)]
            cat_sum = cat_data_rep.groupby(risk_col_rep)['Count'].sum().sort_values(ascending=False).reset_index()
            f3, a3 = plt.subplots(figsize=(8,6)); a3.pie(cat_sum['Count'], autopct='%1.1f%%', colors=['#3b82f6','#ef4444','#10b981','#f59e0b']); plt.tight_layout()
            
            # --- COUNTRY FILTERING LOGIC ---
            c_col = 'Server Country' if 'Server Country' in df_rep.columns else 'Location'
            df_country_plot = df_rep.copy()
            blocked_country_plot = blocked_rep.copy()
            
            # REMOVE UNKNOWN DOMAINS FROM COUNTRY CATEGORY
            df_country_plot = df_country_plot[~df_country_plot[c_col].astype(str).str.contains('(?i)unknown', na=False)]
            blocked_country_plot = blocked_country_plot[~blocked_country_plot[c_col].astype(str).str.contains('(?i)unknown', na=False)]

            if exclude_rfc:
                rfc_patterns = r'(?i)RFC|Private|Reserved|Local|Internal'
                df_country_plot = df_country_plot[~df_country_plot[c_col].astype(str).str.contains(rfc_patterns, na=False)]
                blocked_country_plot = blocked_country_plot[~blocked_country_plot[c_col].astype(str).str.contains(rfc_patterns, na=False)]

            total_c = df_country_plot.groupby(c_col)['Count'].sum().nlargest(10)
            blocked_c = blocked_country_plot.groupby(c_col)['Count'].sum().reindex(total_c.index, fill_value=0)
            c_df = pd.DataFrame({'Total': total_c.values, 'Blocked': blocked_c.values}, index=total_c.index).reset_index()
            
            f4, a4 = plt.subplots(figsize=(12,6)); c_df.set_index(c_col).plot(kind='bar', ax=a4, color=['#2563eb','#dc2626']); plt.xticks(rotation=45, ha='right'); plt.tight_layout()

            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(px.bar(tr_data, x='Domain', y='Count', title="Top Requested", color_discrete_sequence=['#2563eb']), use_container_width=True)
                st.plotly_chart(px.pie(cat_sum, values='Count', names=risk_col_rep, title="Categories", hole=.4), use_container_width=True)
            with col_chart2:
                st.plotly_chart(px.bar(tkill_data, x='Domain', y='Count', title="Top Killed", color_discrete_sequence=['#dc2626']), use_container_width=True)
                st.plotly_chart(px.bar(c_df, x=c_col, y=['Total', 'Blocked'], barmode='group', title="Top Countries (Filtered)" if exclude_rfc else "Top Countries"), use_container_width=True)

            if st.button("📑 GENERATE EXECUTIVE SUMMARY"):
                with st.spinner("⚛️ Shield Engine: Rendering Report..."):
                    pdf_b = generate_pdf_report(df_rep, rep_range[0], rep_range[1] if len(rep_range)>1 else rep_range[0], rep_dev, dk, tk, uk, [f1, f2, f3, f4], {'cat_txt': 'Threat Summary Analysis...', 'country_txt': 'Query Origin Analysis...'})
                st.download_button(label="📥 DOWNLOAD PDF REPORT", data=pdf_b, file_name=f"ThreatReport_{rep_dev}.pdf", mime="application/pdf")
        st.markdown('</div>', unsafe_allow_html=True)
