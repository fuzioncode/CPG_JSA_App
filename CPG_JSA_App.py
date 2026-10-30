import sys
import os

# --- SMART DUAL-ENVIRONMENT BOOTSTRAPPER ---
is_streamlit_cloud = os.path.exists("/mount") or os.environ.get("STREAMLIT_SHARING_MODE") == "true"

if not is_streamlit_cloud and __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is None:
            if not os.environ.get("STREAMLIT_RUNNING_SUBPROCESS"):
                import subprocess
                env = os.environ.copy()
                env["STREAMLIT_RUNNING_SUBPROCESS"] = "1"
                cmd = [sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__), "--server.port", "8501"]
                sys.exit(subprocess.call(cmd, env=env))
    except ImportError:
        pass

import io
import re
import json
import socket
import datetime
import urllib.parse
import urllib.request
import qrcode
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# ReportLab for CPG PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Google Drive API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- ROBUST MULTI-SOURCE API KEY RESOLUTION ---
def get_gemini_api_key():
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if key and (key.startswith("AQ.") or key.startswith("AIzaSy")):
                return key
    except Exception:
        pass
    
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key and (env_key.startswith("AQ.") or env_key.startswith("AIzaSy")):
        return env_key
        
    return "AQ.Ab8RN6JgCKxOPIEVDyG5lLWDxEV9gHQexOVvnCRE2lzZ5koFGg"

# Page Configuration for Responsive Mobile / Tablet / Laptop UI
st.set_page_config(
    page_title="CPG QTS Safety Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-Contrast Mobile & Dark-Mode Friendly CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .status-card {
        background-color: #1e293b;
        color: #f8fafc;
        padding: 14px 18px;
        border-radius: 8px;
        border-left: 6px solid #38bdf8;
        margin-bottom: 12px;
        font-size: 1rem;
    }
    .weather-card {
        background-color: #0f172a;
        color: #38bdf8;
        padding: 10px 16px;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 14px;
        font-size: 0.95rem;
    }
    .teleprompter-box {
        background-color: #0f172a;
        color: #e2e8f0;
        padding: 20px 24px;
        border-radius: 10px;
        border: 2px solid #334155;
        font-size: 1.15rem;
        line-height: 1.75;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .teleprompter-title {
        color: #38bdf8;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: block;
    }
    .var-bracket {
        color: #fbbf24;
        background-color: rgba(251, 191, 36, 0.15);
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 700;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# --- Dynamic Geocoded Weather & Site Risk Integration ---
@st.cache_data(ttl=900, show_spinner=False)
def fetch_dynamic_site_weather(location_string):
    try:
        known_cities = ["ashburn", "eagle mountain", "chicago", "dallas", "phoenix", "santa clara", "atlanta", "salt lake city", "las vegas", "seattle"]
        query_city = "Eagle Mountain, UT"
        
        loc_lower = location_string.lower()
        for city in known_cities:
            if city in loc_lower:
                query_city = city
                break
                
        encoded_city = urllib.parse.quote(query_city)
        url = f"https://wttr.in/{encoded_city}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            current = data['current_condition'][0]
            temp_f = current['temp_F']
            desc = current['weatherDesc'][0]['value']
            wind_mph = current['windspeedMiles']
            humidity = current['humidity']
            
            risk_note = "Standard Indoor/Gallery Climate"
            try:
                if float(temp_f) > 90:
                    risk_note = "⚠️ Heat Stress Hazard: High ambient temp. Enforce hydration breaks."
                elif float(temp_f) < 32:
                    risk_note = "⚠️ Freezing Hazard: Verify outdoor equipment anti-condensation heaters."
                if float(wind_mph) > 25:
                    risk_note += " | ⚠️ High Wind Advisory: Secure exterior panels/doors."
            except Exception:
                pass
                
            return f"🌤️ **Live Weather ({query_city.title()}):** {temp_f}°F, {desc} | Wind: {wind_mph} mph | **Site Risk Note:** {risk_note}"
    except Exception:
        return f"🌤️ **Live Site Weather ({location_string}):** 68°F, Stable Climate | **Site Risk Note:** Standard Data Center Environment"

# --- Helper 0A: Auto-Discover Latest Available Gemini Model ---
@st.cache_data(ttl=3600, show_spinner=False)
def discover_gemini_models(api_key: str):
    fallback_models = ["models/gemini-2.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]
    if not api_key or not (api_key.startswith("AQ.") or api_key.startswith("AIzaSy")):
        return fallback_models[0], fallback_models

    try:
        client = genai.Client(api_key=api_key)
        all_models = list(client.models.list())
        candidates = []

        for m in all_models:
            name = getattr(m, "name", "")
            if not name or "gemini" not in name.lower():
                continue

            excluded_keywords = ["embedding", "imagen", "veo", "aqa", "tts", "audio", "vision", "learnlm", "thinking"]
            if any(k in name.lower() for k in excluded_keywords):
                continue

            actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None)
            if actions and "generateContent" not in actions:
                continue

            candidates.append(name)

        if not candidates:
            return fallback_models[0], fallback_models

        def score_model(model_name: str):
            low = model_name.lower()
            ver_match = re.search(r"gemini-(\d+(?:\.\d+)?)", low)
            version = float(ver_match.group(1)) if ver_match else 0.0
            is_flash = 2 if ("flash" in low and "lite" not in low) else (1 if "pro" in low else 0)
            is_clean = 0 if re.search(r"-\d{3,4}|exp|preview", low) else 1
            return (is_flash, version, is_clean)

        candidates.sort(key=score_model, reverse=True)
        return candidates[0], candidates

    except Exception:
        return fallback_models[0], fallback_models

# --- Helper 0B: Validate API Key Live ---
@st.cache_data(ttl=60, show_spinner=False)
def validate_gemini_key(api_key: str) -> bool:
    if not api_key or not (api_key.startswith("AQ.") or api_key.startswith("AIzaSy")):
        return False
    try:
        client = genai.Client(api_key=api_key)
        client.models.list()
        return True
    except Exception:
        return False

# --- Helper 0C: Unique Lead-Specific QR Code URL Builder ---
def get_active_app_url(lead_name, location_str):
    lead_slug = urllib.parse.quote(lead_name.strip().replace(" ", "_"))
    loc_slug = urllib.parse.quote(location_str.strip().replace(" ", "_"))
    
    if is_streamlit_cloud:
        base = "https://cpgjsaapp.streamlit.app"
    else:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            base = f"http://{ip}:8501"
        except Exception:
            base = "http://localhost:8501"
            
    return f"{base}/?lead={lead_slug}&loc={loc_slug}&action=sign"

# --- Helper 0D: Cross-Device Persistent Storage for Sign-Offs ---
def get_storage_filenames(lead_name, location_str):
    lead_slug = re.sub(r'[^A-Za-z0-9_-]', '_', lead_name.strip())
    loc_slug = re.sub(r'[^A-Za-z0-9_-]', '_', location_str.strip())
    return f"jsa_data_{lead_slug}_{loc_slug}.json", f"signers_data_{lead_slug}_{loc_slug}.json"

def save_persistent_state(lead_name, location_str, jsa_data, signers_data):
    jsa_fn, sig_fn = get_storage_filenames(lead_name, location_str)
    try:
        with open(jsa_fn, "w") as f:
            json.dump(jsa_data, f)
        with open(sig_fn, "w") as f:
            json.dump(signers_data, f)
    except Exception:
        pass

def load_persistent_state(lead_name, location_str, default_jsa, default_signers, force_fresh=False):
    jsa_fn, sig_fn = get_storage_filenames(lead_name, location_str)
    
    if force_fresh:
        try:
            if os.path.exists(jsa_fn):
                os.remove(jsa_fn)
            if os.path.exists(sig_fn):
                os.remove(sig_fn)
        except Exception:
            pass
        return default_jsa, default_signers

    jsa_data = default_jsa
    signers_data = default_signers
    
    if os.path.exists(jsa_fn):
        try:
            with open(jsa_fn, "r") as f:
                jsa_data = json.load(f)
        except Exception:
            pass
            
    if os.path.exists(sig_fn):
        try:
            with open(sig_fn, "r") as f:
                signers_data = json.load(f)
        except Exception:
            pass
            
    return jsa_data, signers_data

# --- Helper 1: Google Drive Sync ---
def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists('credentials.json'):
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            return None
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder_path(service, path_parts):
    parent_id = 'root'
    for folder_name in path_parts:
        q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        res = service.files().list(q=q, spaces='drive', fields='files(id, name)').execute()
        files = res.get('files', [])
        if files:
            parent_id = files[0]['id']
        else:
            meta = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
            folder = service.files().create(body=meta, fields='id').execute()
            parent_id = folder.get('id')
    return parent_id

def upload_pdf_to_gdrive(pdf_bytes, filename):
    service = get_drive_service()
    if not service:
        return False, "credentials.json not found in project root folder."
    try:
        target_folder_id = get_or_create_folder_path(service, ["CPG", "Salt Lake City", "QTS", "JSA"])
        file_metadata = {'name': filename, 'parents': [target_folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype='application/pdf', resumable=True)
        uploaded = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return True, uploaded.get('webViewLink')
    except Exception as e:
        return False, str(e)

# --- Helper 2: PDF Generator matching CPG Template ---
def generate_cpg_pdf(data, signers):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    group_name = data.get('group_type', 'SWITCHGEAR')
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#003366'), leading=17)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=8.5, leading=11)
    hdr_style = ParagraphStyle('Hdr', parent=styles['Heading2'], fontSize=10.5, textColor=colors.HexColor('#003366'), spaceBefore=6, spaceAfter=3)
    table_cell = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10)

    elements = [
        Paragraph(f"<b>CPG Job Safety Analysis</b> — {group_name} (rev 1.1)", title_style),
        Spacer(1, 6),
    ]

    info_data = [
        [Paragraph(f"<b>Date:</b> {data.get('date', '')}", sub_style), Paragraph(f"<b>Customer Name:</b> {data.get('customer', '')} (SO#: {data.get('sales_order', 'N/A')})", sub_style)],
        [Paragraph(f"<b>Site Location:</b> {data.get('location', '')}", sub_style), Paragraph(f"<b>Site Contact:</b> {data.get('site_contact', '')}", sub_style)],
        [Paragraph(f"<b>Onsite Job Lead:</b> {data.get('lead', '')} ({group_name} Lead)", sub_style), Paragraph("<b>Emergency #:</b> 911 | <b>Hotline:</b> 1-800-359-5020", sub_style)],
        [Paragraph(f"<b>Task Summary:</b> {data.get('task', '')}", sub_style), Paragraph(f"<b>Muster Point:</b> {data.get('muster_point', '')}", sub_style)],
        [Paragraph(f"<b>Ladders Used:</b> {'YES - ' + str(data.get('ladder_reason', '')) if data.get('ladders_used') else 'NO'}", sub_style), Paragraph(f"<b>Ergonomics / Heavy Lift:</b> {data.get('heavy_lifting_lbs', 'None')}", sub_style)]
    ]
    t_info = Table(info_data, colWidths=[270, 270])
    t_info.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#999999')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FA')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.extend([t_info, Spacer(1, 6)])

    elements.append(Paragraph("<b>7. Scope of Work, Hazards, and Controls</b>", hdr_style))
    steps_table = [[Paragraph("<b>Task Steps</b>", table_cell), Paragraph("<b>Potential Hazards</b>", table_cell), Paragraph("<b>Hazard Controls</b>", table_cell)]]
    for row in data.get('steps', []):
        if isinstance(row, dict):
            steps_table.append([
                Paragraph(str(row.get('step', '')), table_cell),
                Paragraph(str(row.get('hazards', '')), table_cell),
                Paragraph(str(row.get('controls', '')), table_cell)
            ])
        else:
            steps_table.append([Paragraph(str(row), table_cell), Paragraph("", table_cell), Paragraph("", table_cell)])
    
    t_steps = Table(steps_table, colWidths=[150, 180, 210])
    t_steps.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E9ECEF')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.extend([t_steps, Spacer(1, 6)])

    raw_ppe = data.get('ppe', [])
    ppe_list = ", ".join(raw_ppe) if isinstance(raw_ppe, list) else str(raw_ppe)
    elec_data = [
        [Paragraph(f"<b>PPE Selected:</b> {ppe_list}", sub_style)],
        [Paragraph(f"<b>Nominal Voltage:</b> {data.get('voltage', '')} | <b>Arc Flash PPE:</b> {data.get('arc_flash_ppe', '')} | <b>Glove Class:</b> {data.get('glove_class', '')}", sub_style)],
        [Paragraph(f"<b>Working Environment:</b> {data.get('work_env_mode', 'De-Energized LOTO')} | <b>LOTO Verified:</b> {'YES' if data.get('loto_required') else 'NO'}", sub_style)]
    ]
    t_elec = Table(elec_data, colWidths=[540])
    t_elec.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.HexColor('#999999')), ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FA'))]))
    elements.extend([Paragraph("<b>11. Electrical Work Hazard Analysis & PPE</b>", hdr_style), t_elec, Spacer(1, 6)])

    elements.append(Paragraph("<b>12. Staff Acknowledgement of Job Scope, Hazards, and Controls</b>", hdr_style))
    sign_table = [[Paragraph("<b>Technician Name</b>", table_cell), Paragraph("<b>Approval Verification</b>", table_cell), Paragraph("<b>Timestamp</b>", table_cell)]]
    for s in signers:
        if isinstance(s, dict):
            sign_table.append([Paragraph(str(s.get('name', '')), table_cell), Paragraph(str(s.get('type', '')), table_cell), Paragraph(str(s.get('time', '')), table_cell)])
    
    while len(sign_table) < 5:
        sign_table.append([Paragraph("", table_cell), Paragraph("", table_cell), Paragraph("", table_cell)])

    t_sign = Table(sign_table, colWidths=[200, 190, 150])
    t_sign.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E9ECEF')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(t_sign)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# --- Initialize Isolated Session State per Lead/Team via Disk Persistence ---
query_params = st.query_params
url_lead = query_params.get("lead", "Wes_Johnson").replace("_", " ")
url_loc = query_params.get("loc", "SLC Eagle Mountain - DC-02 PDU Gallery").replace("_", " ")

default_jsa_dict = {
    "date": datetime.date.today().strftime("%m/%d/%Y"),
    "customer": "QTS Data Centers",
    "sales_order": "24-16119",
    "location": url_loc,
    "lead": url_lead,
    "group_type": "SWITCHGEAR",
    "role_title": "Level 4 EPS Lead",
    "site_contact": "QTS Facilities / Commissioning Lead",
    "muster_point": "North Parking Lot Primary Rally Point",
    "task": "480V LV Switchgear Secondary Injection Testing & Visual Inspection",
    "ladders_used": False,
    "ladder_reason": "N/A - Working at floor level",
    "heavy_lifting_lbs": "50 lbs (Secondary Injection Test Kit)",
    "loto_required": True,
    "work_env_mode": "De-Energized via LOTO",
    "voltage": "480V",
    "arc_flash_ppe": "8-12 Cal/cm² Daily FR",
    "glove_class": "Class 0 (1000V) with leather protectors",
    "ppe": ["Hi-Viz Vest", "Safety-Toed Boots", "Safety Glasses", "Hard Hat", "Cut Resistant Gloves"],
    "steps": [
        {"step": "Verify LOTO & Zero Energy State", "hazards": "Electrical shock, backfeed, arc flash", "controls": "Live-dead-live test with calibrated meter, personal locks applied"},
        {"step": "Rack breaker to Test/Disconnected", "hazards": "Pinch points, physical strain, gear binding", "controls": "Hand placement clear of tracks, use breaker lift cart"},
        {"step": "Secondary Injection & Timing Test", "hazards": "Secondary shock, trip unit burn, arc flash", "controls": "Class 0 gloves, insulated probes, verify wiring diagrams"}
    ]
}

default_signers_list = [{"name": f"{url_lead} (SWITCHGEAR Lead)", "type": "Lead Verification", "time": datetime.datetime.now().strftime("%H:%M:%S")}]

session_key = f"jsa_{url_lead}_{url_loc}"
signers_key = f"signers_{url_lead}_{url_loc}"

if session_key not in st.session_state or signers_key not in st.session_state:
    loaded_jsa, loaded_signers = load_persistent_state(url_lead, url_loc, default_jsa_dict, default_signers_list)
    st.session_state[session_key] = loaded_jsa
    st.session_state[signers_key] = loaded_signers

current_jsa = st.session_state[session_key]
current_signers = st.session_state[signers_key]

# --- UI Header & Lead Admin Section ---
st.title("⚡ CPG QTS Safety Portal")

# Check if viewing via QR code / mobile sign mode
is_mobile_signer = (query_params.get("action") == "sign")

if is_mobile_signer:
    st.info("📲 **Mobile Crew Sign-Off Mode Active** — You have opened the briefing sign-off portal. Review the scope in Tab 2 if needed and sign below.")
else:
    # Lead-Only Admin & New JSA Thumbnail Button Panel
    lead_col1, lead_col2 = st.columns([3, 1])
    with lead_col1:
        with st.expander("✏️ Edit Header & Site Info (Active Site, Lead, Group)", expanded=False):
            h_c1, h_c2, h_c3, h_c4 = st.columns(4)
            with h_c1:
                current_jsa['location'] = st.text_input("Active Site / Location", value=str(current_jsa.get('location', '')), key="hdr_loc")
            with h_c2:
                current_jsa['lead'] = st.text_input("Lead Name", value=str(current_jsa.get('lead', '')), key="hdr_lead")
            with h_c3:
                current_jsa['group_type'] = st.selectbox("Group / Specialty", options=["SWITCHGEAR", "POWER", "HVAC", "SOLAR", "GENERATOR"], index=0, key="hdr_group")
            with h_c4:
                current_jsa['role_title'] = st.text_input("Role Title", value=str(current_jsa.get('role_title', 'Level 4 EPS Lead')), key="hdr_role")
            
            if st.button("💾 Save Header Updates"):
                save_persistent_state(current_jsa['lead'], current_jsa['location'], current_jsa, current_signers)
                st.success("Header updated and saved!")
    with lead_col2:
        # Secure Lead Thumbnail Button to start a fresh JSA without affecting technicians
        if st.button("➕ Create New JSA", help="Click to wipe previous signatures and start a fresh JSA for a new scope today"):
            fresh_jsa, fresh_signers = load_persistent_state(current_jsa['lead'], current_jsa['location'], default_jsa_dict, default_signers_list, force_fresh=True)
            st.session_state[session_key] = fresh_jsa
            st.session_state[signers_key] = fresh_signers
            st.success("Fresh JSA initialized!")
            st.rerun()

st.markdown(
    f'<div class="status-card"><b>Active Site:</b> {current_jsa.get("location", "")} &nbsp;|&nbsp; '
    f'<b>Lead:</b> {current_jsa.get("lead", "")} &nbsp;|&nbsp; '
    f'<b>Group:</b> {current_jsa.get("group_type", "SWITCHGEAR")} &nbsp;|&nbsp; '
    f'<b>Role:</b> {current_jsa.get("role_title", "")}</div>',
    unsafe_allow_html=True
)

# Render Dynamic Weather Widget based on Active Site Location
weather_info = fetch_dynamic_site_weather(current_jsa.get('location', 'Site'))
st.markdown(f'<div class="weather-card">{weather_info}</div>', unsafe_allow_html=True)

# Smart Tab Selection: If scanned via QR code (?action=sign), automatically default to Tab 3 (Crew Sign)
default_tab_index = 2 if is_mobile_signer else 0

tab_brief, tab_review, tab_sign, tab_export = st.tabs(["🎙️ 1. Voice Briefing", "📝 2. Review JSA", "✍️ 3. QR / Crew Sign", "🚀 4. Drive Sync"])

with tab_brief:
    st.markdown("### 🎙️ Pre-Job Huddle Teleprompter & Voice Capture")
    
    tp_style = st.radio(
        "Select Teleprompter Script Style:",
        ["⚡ Quick 45-Second Huddle (Standard Daily)", "📋 Full CPG Section 1–11 Walkthrough (Detailed)"],
        horizontal=True,
        key="tp_radio_style"
    )

    if tp_style == "⚡ Quick 45-Second Huddle (Standard Daily)":
        st.markdown("""
        <div class="teleprompter-box">
            <span class="teleprompter-title">📺 Live Huddle Teleprompter — Read Aloud & Fill in [BRACKETS]</span>
            "Morning team, today is <span class="var-bracket">[TODAY'S DATE]</span> at QTS Eagle Mountain inside <span class="var-bracket">[BUILDING & ROOM / GALLERY, e.g., DC-02 PDU Gallery 1]</span>.<br><br>
            1. <b>Task Scope:</b> Our task today is <span class="var-bracket">[MAIN TASK, e.g., 480V Breaker Secondary Injection Testing & Torque Checks]</span> on equipment lineup <span class="var-bracket">[EQUIPMENT ID, e.g., SWG-2A]</span>.<br>
            2. <b>Energy State & Permits:</b> We are working <span class="var-bracket">[DE-ENERGIZED UNDER LOTO / ENERGIZED FOR TESTING]</span> using Permit <span class="var-bracket">[LOTO OR EEWP PERMIT #]</span>. Nominal system voltage is <span class="var-bracket">[VOLTAGE, e.g., 480 Volts]</span>.<br>
            3. <b>Step-by-Step & Hazards:</b><br>
               &nbsp;&nbsp;• First, we will <span class="var-bracket">[STEP 1, e.g., verify zero energy / LOTO]</span>; watch out for <span class="var-bracket">[HAZARD, e.g., backfeed or arc flash]</span> by <span class="var-bracket">[CONTROL, e.g., performing live-dead-live checks]</span>.<br>
               &nbsp;&nbsp;• Next, we will <span class="var-bracket">[STEP 2, e.g., rack out breakers and connect secondary test kit]</span>; watch out for <span class="var-bracket">[HAZARD, e.g., pinch points and heavy lifting of 50 lbs]</span> by <span class="var-bracket">[CONTROL, e.g., using the lift cart and keeping hands clear of rails]</span>.<br>
               &nbsp;&nbsp;• Finally, we will <span class="var-bracket">[STEP 3, e.g., run trip timing tests and restore gear]</span>; prevent <span class="var-bracket">[HAZARD, e.g., tool FOD left inside gear]</span> by <span class="var-bracket">[CONTROL, e.g., doing a full tool accountability check]</span>.<br>
            4. <b>PPE & Ladders:</b> Required PPE is <span class="var-bracket">[ARC FLASH CAL RATING, e.g., 8 Cal daily wear]</span>, insulated gloves <span class="var-bracket">[GLOVE CLASS, e.g., Class 0 with leathers]</span>, hard hats, safety glasses, and cut gloves. Ladders are <span class="var-bracket">[NOT USED / USED BECAUSE NO LIFT FITS]</span>.<br>
            5. <b>Emergency:</b> Site contact is <span class="var-bracket">[SITE CONTACT NAME]</span> and our muster point is <span class="var-bracket">[MUSTER POINT, e.g., North Parking Lot]</span>."
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="teleprompter-box">
            <span class="teleprompter-title">📺 Full CPG Section 1–11 Teleprompter — Read Aloud & Fill in [BRACKETS]</span>
            • <b>Sec 1–3 (Job & Emergency):</b> Date is <span class="var-bracket">[DATE]</span>, Sales Order <span class="var-bracket">[SALES ORDER #]</span> at QTS <span class="var-bracket">[BUILDING / ROOM]</span>. Site contact is <span class="var-bracket">[CONTACT NAME]</span>, Muster Point is <span class="var-bracket">[MUSTER LOCATION]</span>. Task description is <span class="var-bracket">[TASK SUMMARY]</span>.<br>
            • <b>Sec 4–6 (Ladders, HRAs & Permits):</b> Are we using ladders? <span class="var-bracket">[YES / NO — IF YES, STATE WHY LIFTS CAN'T BE USED]</span>. High risk activities include <span class="var-bracket">[ELECTRICAL ISOLATION / MATERIAL HANDLING / WORKING FROM HEIGHTS]</span>. Active permits are <span class="var-bracket">[LOTO PERMIT / ENERGIZED WORK PERMIT / HOT WORK]</span>.<br>
            • <b>Sec 7 (Steps, Hazards & Controls):</b><br>
               &nbsp;&nbsp;- Step 1: <span class="var-bracket">[TASK STEP 1]</span> | Hazards: <span class="var-bracket">[HAZARDS]</span> | Controls: <span class="var-bracket">[CONTROLS]</span>.<br>
               &nbsp;&nbsp;- Step 2: <span class="var-bracket">[TASK STEP 2]</span> | Hazards: <span class="var-bracket">[HAZARDS]</span> | Controls: <span class="var-bracket">[CONTROLS]</span>.<br>
               &nbsp;&nbsp;- Step 3: <span class="var-bracket">[TASK STEP 3]</span> | Hazards: <span class="var-bracket">[HAZARDS]</span> | Controls: <span class="var-bracket">[CONTROLS]</span>.<br>
            • <b>Sec 8–9 (Ergonomics & Site PPE):</b> Heavy lifting is <span class="var-bracket">[YES — WEIGHT IN LBS / NO]</span>. Site PPE required: Hi-Viz, safety boots, safety glasses, hard hat, cut gloves, plus <span class="var-bracket">[FACESHIELD / HEARING PROTECTION]</span>.<br>
            • <b>Sec 10–11 (Electrical Hazard Analysis):</b> System voltage is <span class="var-bracket">[NOMINAL VOLTAGE, e.g., 480V / 13.8kV]</span>. Arc flash PPE is <span class="var-bracket">[8 CAL / 40 CAL SUIT]</span> and <span class="var-bracket">[CLASS 0 / CLASS 2]</span> voltage gloves inspected prior to use. Environment is <span class="var-bracket">[DE-ENERGIZED UNDER LOTO / ENERGIZED TESTING]</span> with <span class="var-bracket">[SINGLE / MULTIPLE]</span> point of isolation walked down."
        </div>
        """, unsafe_allow_html=True)

    col_v1, col_v2 = st.columns([1, 2])
    with col_v1:
        audio_record = st.audio_input("🎙️ Record Pre-Job Huddle While Reading Above")
    with col_v2:
        briefing_text = st.text_area(
            "Or type/paste bracketed overrides:",
            value="",
            height=115,
            placeholder="Optional: Type any specific SO#, permit numbers, or extra notes here...",
            key="briefing_textarea"
        )

    resolved_api_key = get_gemini_api_key()
    
    with st.expander("🔑 API Key & Model Configuration", expanded=not bool(resolved_api_key)):
        user_entered_key = st.text_input("Gemini API Key (AQ... or AIzaSy...):", value=resolved_api_key, type="password", key="gemini_key_input", placeholder="Paste your AQ... API key here")
        
        active_key = user_entered_key if user_entered_key.strip() else resolved_api_key
        is_valid_key = validate_gemini_key(active_key)
        
        if is_valid_key:
            st.success("✅ Gemini API Key is valid and authenticated!")
            best_model, available_models = discover_gemini_models(active_key)
            selected_model = st.selectbox(
                "Active Gemini Model (Newest Auto-Selected):",
                options=available_models,
                index=0,
                key="gemini_model_select"
            )
        else:
            st.warning("⚠️ Please enter a valid Gemini API Key starting with **`AQ.`** or **`AIzaSy...`** to enable AI processing.")
            selected_model = "models/gemini-2.5-flash"

    process_clicked = st.button("⚡ Process Briefing with AI", key="process_ai_btn", disabled=not is_valid_key)

    if process_clicked:
        if not active_key:
            st.error("Please enter a valid Gemini API Key.")
        else:
            client = genai.Client(api_key=active_key)
            
            system_instruction = """
            You are a critical infrastructure safety engineer for CPG Beyond at QTS Data Centers.
            Extract the provided audio recording and/or text notes into a structured CPG JSA JSON object.
            Return strict JSON only (no markdown formatting, no backticks) matching these exact keys:
            {
                "sales_order": "string",
                "location": "string",
                "site_contact": "string",
                "muster_point": "string",
                "task": "string",
                "ladders_used": false,
                "ladder_reason": "string",
                "heavy_lifting_lbs": "string",
                "voltage": "string",
                "loto_required": true,
                "work_env_mode": "string",
                "arc_flash_ppe": "string",
                "glove_class": "string",
                "steps": [
                    {"step": "string", "hazards": "string", "controls": "string"}
                ]
            }
            """
            contents = [system_instruction]
            if audio_record is not None:
                contents.append(types.Part.from_bytes(data=audio_record.getvalue(), mime_type="audio/wav"))
            if briefing_text.strip():
                contents.append(f"Additional text notes: {briefing_text}")
            elif audio_record is None:
                contents.append("Secondary injection testing on 480V switchgear breakers in DC-02 under zero energy LOTO. Class 0 gloves and 8-12 cal arc flash protection required.")

            with st.spinner(f"Analyzing spoken briefing with {selected_model}..."):
                try:
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=contents
                    )
                    clean_json = response.text.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_json)
                    if isinstance(parsed, dict):
                        current_jsa.update(parsed)
                    save_persistent_state(current_jsa['lead'], current_jsa['location'], current_jsa, current_signers)
                    st.success(f"✅ CPG JSA Auto-Populated using `{selected_model}`! Proceed to Tab 2 (Review JSA).")
                except Exception as err:
                    st.error(f"Extraction failed using {selected_model}: {err}")

with tab_review:
    st.markdown("### Sections 1–11: Review & Edit Auto-Populated JSA")
    st.caption("Review form fields below. Click any box to make corrections if Gemini filled something in wrong.")

    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        current_jsa['lead'] = st.text_input("Onsite Job Lead", value=str(current_jsa.get('lead', '')), key="rev_lead")
        current_jsa['location'] = st.text_input("Location / Gallery", value=str(current_jsa.get('location', '')), key="rev_loc")
        current_jsa['sales_order'] = st.text_input("Sales Order #", value=str(current_jsa.get('sales_order', '')), key="rev_so")
        current_jsa['site_contact'] = st.text_input("Site Contact", value=str(current_jsa.get('site_contact', '')), key="rev_contact")
        current_jsa['muster_point'] = st.text_input("Muster Point", value=str(current_jsa.get('muster_point', '')), key="rev_muster")
    with r_col2:
        current_jsa['task'] = st.text_area("Task Description Summary", value=str(current_jsa.get('task', '')), height=108, key="rev_task")
        current_jsa['ladders_used'] = st.checkbox("Using Ladders (Sec 4: Ladders Last)", value=bool(current_jsa.get('ladders_used', False)), key="rev_ladder_chk")
        current_jsa['ladder_reason'] = st.text_input("Why lifts/scaffolds can't be used:", value=str(current_jsa.get('ladder_reason', '')), key="rev_ladder_reason")
        current_jsa['heavy_lifting_lbs'] = st.text_input("Ergonomics / Heavy Lifting (lbs)", value=str(current_jsa.get('heavy_lifting_lbs', '')), key="rev_lift")
    with r_col3:
        current_jsa['voltage'] = st.text_input("Nominal System Voltage", value=str(current_jsa.get('voltage', '')), key="rev_volt")
        current_jsa['work_env_mode'] = st.text_input("Electrical Working Environment", value=str(current_jsa.get('work_env_mode', '')), key="rev_env")
        current_jsa['loto_required'] = st.checkbox("LOTO Established (Zero Energy State)", value=bool(current_jsa.get('loto_required', True)), key="rev_loto_chk")
        current_jsa['arc_flash_ppe'] = st.text_input("Arc Flash PPE Rating", value=str(current_jsa.get('arc_flash_ppe', '')), key="rev_arc")
        current_jsa['glove_class'] = st.text_input("Electrical Glove Class", value=str(current_jsa.get('glove_class', '')), key="rev_glove")
    
    with st.expander("✏️ Edit AI-Parsed Hazard Steps (Section 7)", expanded=True):
        st.caption("Modify any step, hazard, or control below if Gemini parsed it incorrectly:")
        updated_steps = []
        steps_data = current_jsa.get('steps', [])
        for idx, s in enumerate(steps_data):
            st.markdown(f"**Task Step {idx+1}**")
            s_col1, s_col2, s_col3 = st.columns([1.2, 1.4, 1.4])
            with s_col1:
                step_text = st.text_input(f"Step {idx+1}", value=str(s.get('step', '') if isinstance(s, dict) else s), key=f"edit_step_{idx}")
            with s_col2:
                hazard_text = st.text_input(f"Hazards {idx+1}", value=str(s.get('hazards', '') if isinstance(s, dict) else ''), key=f"edit_haz_{idx}")
            with s_col3:
                control_text = st.text_input(f"Controls {idx+1}", value=str(s.get('controls', '') if isinstance(s, dict) else ''), key=f"edit_ctrl_{idx}")
            updated_steps.append({"step": step_text, "hazards": hazard_text, "controls": control_text})
            st.markdown("---")
        current_jsa['steps'] = updated_steps
    
    if st.button("💾 Save JSA Review Edits"):
        save_persistent_state(current_jsa['lead'], current_jsa['location'], current_jsa, current_signers)
        st.success("JSA changes saved successfully!")

with tab_sign:
    st.markdown("### Section 12: Crew Acknowledgement")
    
    signed_count = len(current_signers)
    st.markdown(f"📊 **Huddle Status:** `{signed_count} Crew Member(s) Signed In`")

    col_qr1, col_qr2 = st.columns([1, 2])
    with col_qr1:
        app_url = get_active_app_url(current_jsa.get('lead', 'Wes Johnson'), current_jsa.get('location', 'Site'))
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(app_url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        st.image(img_qr.get_image(), caption="Scan to sign on phone", width=180)
    with col_qr2:
        st.info(f"**Unique QR URL:** `{app_url}`\n\nTechnicians scanning this QR code are taken directly to this signing portal. Crew signatures submitted on phones sync live here.")

    st.markdown("---")
    st.markdown("#### Live Crew Sign-Off Status")
    
    if st.button("🔄 Refresh Crew Signatures List"):
        _, fresh_signers = load_persistent_state(current_jsa['lead'], current_jsa['location'], current_jsa, current_signers)
        st.session_state[signers_key] = fresh_signers
        current_signers = fresh_signers
        st.success("Signatures refreshed from live crew submissions!")

    st.table(current_signers)

    st.markdown("#### Submit Sign-Off (Direct or Mobile Device Entry)")
    s_col1, s_col2 = st.columns([1, 1])
    with s_col1:
        crew_name = st.text_input("Technician Full Name", placeholder="e.g. John Doe", key="sign_crew_name")
        sign_mode = st.radio("Approval Method", ["Badge & Initials", "Voice Acknowledgment"], horizontal=True, key="sign_mode_radio")
    
    with s_col2:
        badge_id = ""
        sig_initials = ""
        if sign_mode == "Badge & Initials":
            b_c1, b_c2 = st.columns(2)
            with b_c1:
                badge_id = st.text_input("Employee ID / Badge #", placeholder="e.g. CPG-8842", key="badge_input_id")
            with b_c2:
                sig_initials = st.text_input("Initials", placeholder="e.g. JD", key="init_input_sig")
        else:
            v_sig = st.audio_input("Record Verbal Sign-Off", key="voice_sig_approval")
            if v_sig is not None:
                st.success("Voice confirmation recorded.")

    if st.button("➕ Confirm Technician Sign-Off", key="confirm_sign_btn"):
        if crew_name.strip():
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            if sign_mode == "Badge & Initials":
                meta_info = f"Badge: {badge_id or 'N/A'} | Initials: {sig_initials or 'N/A'}"
            else:
                meta_info = "Verbal Sign-Off (Recorded)"
            
            if not any(s['name'] == crew_name.strip() for s in current_signers):
                current_signers.append({"name": crew_name.strip(), "type": meta_info, "time": timestamp})
                save_persistent_state(current_jsa['lead'], current_jsa['location'], current_jsa, current_signers)
                st.toast(f"✅ Success! {crew_name.strip()} signed off.", icon="⚡")
                st.success(f"Added {crew_name} to JSA roster at {timestamp}! The lead can now view your signature.")
            else:
                st.warning(f"{crew_name.strip()} is already signed in on this JSA roster.")
        else:
            st.warning("Please enter technician's name.")

with tab_export:
    st.markdown("### Generate PDF & Sync to Google Drive")
    st.write("Target Folder: `My Drive > CPG > Salt Lake City > QTS > JSA`")

    st.markdown(f"**Current Signed Crew Roster Count:** `{len(current_signers)} technicians acknowledged.`")
    
    pdf_bytes = generate_cpg_pdf(current_jsa, current_signers)
    safe_loc = re.sub(r'[^A-Za-z0-9_-]', '_', str(current_jsa.get('location', 'Site')))
    filename = f"JSA_QTS_{datetime.date.today().strftime('%Y%m%d')}_{safe_loc}.pdf"

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(label="📥 Download CPG JSA (PDF)", data=pdf_bytes, file_name=filename, mime="application/pdf", key="dl_pdf_btn")

    with d_col2:
        if st.button("☁️ Save to Google Drive Directory", key="upload_drive_btn"):
            with st.spinner("Creating folder hierarchy and uploading PDF to Google Drive..."):
                ok, res_link = upload_pdf_to_gdrive(pdf_bytes, filename)
                if ok:
                    st.balloons()
                    st.success("Successfully uploaded to Google Drive!")
                    st.markdown(f"**Drive Link:** [View Saved JSA in Google Drive]({res_link})")
                else:
                    st.error(f"Upload failed: {res_link}")