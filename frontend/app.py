import streamlit as st
import requests
import time
from config import BACKEND_URL

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="MELCO-Care",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. SESSION STATE INIT
if "user" not in st.session_state:
    st.session_state.user = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "high_contrast" not in st.session_state:
    st.session_state.high_contrast = False
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. HIGH CONTRAST TOGGLE (Top Right)
with st.container():
    col_spacer, col_toggle = st.columns([3, 1])
    with col_toggle:
        st.session_state.high_contrast = st.toggle("High Contrast", value=st.session_state.high_contrast)

# 4. DYNAMIC CSS GENERATION
if st.session_state.high_contrast:
    # --- HIGH CONTRAST THEME (Strict Black & Yellow) ---
    css = """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Global Background: Pure Black */
        .stApp { background-color: #000000 !important; color: #FFFF00 !important; }
        
        /* Containers: Black with thick Yellow Borders */
        .glass-card, .login-container {
            background: #000000 !important; 
            border: 3px solid #FFFF00 !important;
            border-radius: 0px !important; 
            padding: 20px; 
            margin-bottom: 20px; 
            box-shadow: none !important;
        }
        
        /* Typography: All Yellow, Bold, Monospace feel */
        h1, h2, h3, h4, h5, p, div, span, label, small {
            color: #FFFF00 !important; 
            font-family: 'Courier New', Courier, monospace !important;
            letter-spacing: 1px !important;
        }
        
        /* Chat Bubbles: High Visibility */
        .user-bubble {
            background-color: #000000 !important; 
            border: 2px solid #FFFF00 !important;
            color: #FFFF00 !important; 
            border-radius: 0px !important; 
            font-weight: bold;
            padding: 12px 18px;
            margin-bottom: 8px;
        }
        .bot-bubble {
            background-color: #FFFF00 !important; 
            border: 2px solid #FFFF00 !important;
            color: #000000 !important;
            border-radius: 0px !important; 
            font-weight: bold;
            padding: 12px 18px;
            margin-bottom: 8px;
        }
        
        /* --- BUTTON FIX: BLACK TEXT ON YELLOW BACKGROUND --- */
        div.stButton > button {
            background-color: #FFFF00 !important; 
            color: #000000 !important;
            border: 2px solid #FFFFFF !important;
            font-weight: 900 !important; 
            border-radius: 0px !important; 
            text-transform: uppercase;
        }
        div.stButton > button:hover {
            background-color: #FFFFFF !important; 
            color: #000000 !important; 
            border: 2px solid #FFFF00 !important;
        }
        div.stButton > button p {
            color: #000000 !important;
        }
        
        /* Inputs: Black Box, Yellow Text */
        input { 
            background-color: #000000 !important; 
            color: #FFFF00 !important; 
            border: 2px solid #FFFFFF !important; 
        }
        
        /* Status Dots: Simplified for contrast */
        .dot-green { background-color: #FFFF00; border: 1px solid #FFFF00; }
        .dot-yellow { background-color: #FFFF00; border: 1px dashed #FFFF00; }
        .dot-red { background-color: #000000; border: 1px solid #FFFF00; }
        
        /* Font Overrides for Brand */
        .brand-font { color: #FFFF00 !important; }
        .subtitle-font { color: #FFFF00 !important; }
    </style>
    """
else:
    # --- NORMAL THEME (Subtle Purple/White Gradient) ---
    css = """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Subtle Purple-White Gradient Background */
        .stApp {
            background: linear-gradient(180deg, #FFFFFF 0%, #F3E5F5 100%);
            background-attachment: fixed;
            font-family: 'Inter', sans-serif;
        }
        
        /* Login Container */
        .login-container {
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            padding-top: 20px;
            padding-bottom: 20px;
        }
        
        /* Glass Card Style */
        .glass-card {
            background: rgba(255, 255, 255, 0.90); 
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 16px; 
            padding: 24px; 
            box-shadow: 0 8px 32px rgba(100, 50, 150, 0.05);
            margin-bottom: 15px; 
            transition: transform 0.2s ease;
        }
        .glass-card:hover { transform: translateY(-2px); }
        
        /* Chat Bubbles */
        .user-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white;
            padding: 12px 18px; border-radius: 18px 18px 0 18px;
            margin-left: auto; max-width: 80%; margin-bottom: 8px;
            box-shadow: 0 4px 10px rgba(118, 75, 162, 0.2);
        }
        .bot-bubble {
            background-color: #ffffff; color: #333; padding: 12px 18px;
            border-radius: 18px 18px 18px 0; margin-right: auto; max-width: 80%;
            margin-bottom: 8px; border: 1px solid #e5e7eb;
        }
        
        /* Status Dots */
        .status-dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
        .dot-green { background-color: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
        .dot-yellow { background-color: #F59E0B; }
        .dot-red { background-color: #EF4444; }
        
        /* Gradient Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 12px 24px;
            border-radius: 8px; font-weight: 600; transition: all 0.3s ease;
        }
        div.stButton > button:hover { 
            box-shadow: 0 8px 15px rgba(118, 75, 162, 0.3); 
            transform: translateY(-1px); 
        }
        button[kind="secondary"] {
            background: transparent !important; border: 1px solid #764ba2 !important; color: #764ba2 !important;
        }
        
        /* Custom Font Class for Title */
        .brand-font {
            font-family: 'Neue Haas Grotesk Display', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: #333;
            margin-top: 15px;
            margin-bottom: 5px;
            text-transform: uppercase;
            font-size: 1.8rem;
        }
        .subtitle-font {
            font-family: 'Inter', sans-serif;
            color: #666;
            font-size: 0.95rem;
            font-weight: 400;
            margin-bottom: 20px;
        }
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

# ==========================================
#              LOGIN SCREEN
# ==========================================
if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # LOGO
        logo_cols = st.columns([1, 2, 1])
        with logo_cols[1]:
            try:
                st.image("logo.png", use_container_width=True) 
            except:
                st.markdown("<h1 style='text-align:center; color:#764ba2;'>🏥</h1>", unsafe_allow_html=True)
        
        # TEXT (Neue Haas Grotesk)
        st.markdown(
            """
            <div style="text-align: center;">
                <div class="brand-font">MELCO - CARE</div>
                <div class="subtitle-font">Autonomous Hospital Agent</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        user_input_id = st.text_input("Login ID", placeholder="Enter ID (e.g. p201, d101)", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("SECURE LOGIN", use_container_width=True, type="primary"):
            if not user_input_id:
                st.warning("Please enter a User ID")
            else:
                success = False
                attempts = 0
                max_retries = 2
                while attempts < max_retries and not success:
                    try:
                        resp = requests.post(f"{BACKEND_URL}/login", json={"user_id": user_input_id}, timeout=5)
                        data = resp.json()
                        if data.get("success"):
                            st.session_state.user = data["user"]
                            st.session_state.user_id = user_input_id
                            success = True
                            st.rerun()
                        else:
                            st.error(data.get("reason"))
                            break 
                    except requests.exceptions.RequestException:
                        attempts += 1
                        time.sleep(0.1)
                if not success and attempts == max_retries:
                    st.error("Server unavailable. Check connection.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
#              MAIN APP UI
# ==========================================
user = st.session_state.user
user_id = st.session_state.user_id
role = user.get("role", "patient")

with st.container():
    c_left, c_right = st.columns([3, 1])
    with c_left:
        st.markdown(f"<div style='font-size:1.4em; font-weight:700;'>Hello, {user.get('name')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.9em; opacity: 0.8;'>📍 {user.get('location', 'Unknown')}</div>", unsafe_allow_html=True)
    with c_right:
        if st.button("LOGOUT", type="secondary", use_container_width=True):
            st.session_state.user = None
            st.session_state.user_id = None
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ==========================================
#         PATIENT DASHBOARD
# ==========================================
if role == "patient":
    tab_chat, tab_apts, tab_meds = st.tabs(["💬 ASSISTANT", "📅 APPOINTMENTS", "💊 PHARMACY"])
    
    # ========== TAB 1: CHAT ==========
    with tab_chat:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            st.markdown('<div class="bot-bubble">I am your health assistant. How can I help you today?</div>', unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            formatted = msg["content"].replace("\\n", "\n").replace("\n", "<br>")
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">{formatted}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-bubble">{formatted}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("###")
        
        user_input = st.chat_input("Type your message...")
        
        # SCHEME MATCHER BUTTON (preserved from original)
        if st.button("💡 Find Government Schemes For My Diseases", use_container_width=True):
            payload = {
                "user_id": user_id,
                "message": "Find government health schemes for me — use my disease history in my profile.",
                "session_id": st.session_state.session_id,
            }
            try:
                resp = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
                data = resp.json()
                bot_reply = data.get("message", "No response from backend.")
                st.session_state.session_id = data.get("session_id", st.session_state.session_id)
            except Exception as e:
                bot_reply = f"Backend error: {e}"
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
        
        # Normal chat flow
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            payload = {
                "user_id": user_id,
                "message": user_input,
                "session_id": st.session_state.session_id,
            }
            
            try:
                resp = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
                data = resp.json()
                bot_reply = data.get("message", "No response from backend.")
            except Exception as e:
                bot_reply = f"Backend error: {e}"
                data = {"session_id": st.session_state.session_id}
            
            st.session_state.session_id = data.get("session_id", st.session_state.session_id)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()

    # ========== TAB 2: APPOINTMENTS ==========
    with tab_apts:
        try:
            appts = requests.get(f"{BACKEND_URL}/patient/appointments/{user_id}", timeout=15).json()
        except:
            appts = []
        
        if not appts:
            st.info("No active appointments.")
        else:
            for a in appts:
                if not isinstance(a, dict):
                    continue
                    
                status = a.get('status', 'pending')
                status_class = "dot-green" if status == 'accepted' else ("dot-red" if status == 'rejected' else "dot-yellow")
                final_diagnosis = a.get('final_disease', 'Pending')
                
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0;">👨‍⚕️ {a.get('doctor_name', 'Unknown')}</h4>
                        <span style="font-size:0.75em; font-weight:700; text-transform:uppercase; letter-spacing:1px;">
                            <span class="status-dot {status_class}"></span> {status}
                        </span>
                    </div>
                    <p style="margin:4px 0; font-size:0.9em; opacity: 0.8;">🏥 {a.get('hospital_name', 'Unknown')}</p>
                    <div style="margin-top:12px; padding-top:12px; border-top:1px solid rgba(128,128,128,0.2);">
                        <div style="display:flex; justify-content:space-between; font-size:0.9em;">
                            <span>🕒 {a.get('time', 'N/A')}</span>
                        </div>
                        <div style="margin-top:8px; font-size:0.9em;">
                            <span>🩺 <b>Final Diagnosis:</b> {final_diagnosis}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ========== TAB 3: PHARMACY ==========
    with tab_meds:
        try:
            res_resp = requests.get(f"{BACKEND_URL}/pharmacy/reservations/{user_id}", timeout=15)
            res_data = res_resp.json()
            reservations = res_data.get("reservations", [])
        except:
            reservations = []
        
        if not reservations:
            st.info("No active medicine reservations.")
        else:
            for r in reservations:
                if not isinstance(r, dict):
                    continue
                
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="margin:0;">💊 {r.get('medicine_name', 'Unknown')}</h4>
                        <span style="font-weight:bold;">
                            <span class="status-dot dot-yellow"></span> Reserved
                        </span>
                    </div>
                    <p style="margin:5px 0; font-size:0.9em; opacity: 0.8;">🏥 {r.get('hospital_name', 'N/A')}</p>
                    <p style="margin:5px 0; font-size:0.9em;">📦 Qty: {r.get('quantity', 1)}</p>
                    <p style="margin:5px 0; font-size:0.9em;">⏰ Pick up by: {r.get('expires_at', 'N/A')}</p>
                    <div style="font-size:0.8em; opacity: 0.6; margin-top:8px;">REF: #{r.get('id', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # CANCEL BUTTON (preserved from original)
                if st.button("❌ Cancel Reservation", key=f"cancel_{r.get('id')}"):
                    try:
                        cancel_resp = requests.post(
                            f"{BACKEND_URL}/pharmacy/cancel",
                            json={"reservation_id": r.get("id")},
                            timeout=10,
                        )
                        result = cancel_resp.json()
                        if result.get("success"):
                            st.success("Reservation cancelled!")
                            st.rerun()
                        else:
                            st.error(result.get("reason", "Failed to cancel."))
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==========================================
#         DOCTOR DASHBOARD
# ==========================================
elif role == "doctor":
    st.subheader("🩺 Patient Queue")
    
    try:
        appts = requests.get(f"{BACKEND_URL}/doctor/appointments/{user_id}", timeout=15).json()
    except:
        appts = []
    
    if not appts:
        st.success("No pending patients.")
    else:
        for a in appts:
            if not isinstance(a, dict):
                continue
            
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h3 style="margin:0;">🧑 {a.get('patient_name', 'Unknown')}</h3>
                        <small>ID: {a.get('patient_id', 'N/A')}</small>
                    </div>
                    <p style="margin:8px 0; font-size:0.9em;">🏥 {a.get('hospital_name', 'Unknown')}</p>
                    <p style="margin:8px 0; font-size:0.9em;">🕒 {a.get('time', 'N/A')}</p>
                    <div style="background:rgba(128,128,128,0.1); padding:12px; border-radius:8px; margin-top:12px;">
                        <span style="font-weight:600; font-size:0.9em;">📋 Symptoms reported:</span><br>
                        <span>{a.get('symptoms', 'Not provided')}</span>
                    </div>
                    <div style="margin-top:10px; font-size:0.85em;">Current Status: <b>{a.get('status', 'pending')}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                # STATUS UPDATE (preserved from original)
                status_options = ["pending", "accepted", "rejected", "completed"]
                current_status = a.get("status", "pending")
                if current_status not in status_options:
                    current_status = "pending"
                
                c1, c2 = st.columns(2)
                with c1:
                    new_status = st.selectbox(
                        "Update Status",
                        options=status_options,
                        index=status_options.index(current_status),
                        key=f"status_{a['id']}",
                    )
                with c2:
                    if st.button("✅ Update", key=f"update_{a['id']}", use_container_width=True):
                        if new_status != current_status:
                            try:
                                resp = requests.post(
                                    f"{BACKEND_URL}/doctor/decision",
                                    json={"appointment_id": a["id"], "decision": new_status},
                                    timeout=10,
                                )
                                result = resp.json()
                                if result.get("success"):
                                    st.success(f"Updated to {new_status}")
                                    st.rerun()
                                else:
                                    st.error(result.get("reason", "Failed to update."))
                            except Exception as e:
                                st.error(f"Failed to update: {e}")
                
                # FINAL DISEASE ASSIGNMENT (preserved from original)
                st.markdown("---")
                current_disease = a.get("final_disease", "")
                st.markdown(f"**Current Final Diagnosis:** {current_disease if current_disease else 'Not assigned'}")
                
                final_disease_input = st.text_input(
                    "Assign Final Disease/Diagnosis",
                    value=current_disease,
                    key=f"disease_{a['id']}",
                    placeholder="e.g., Viral Fever, Migraine, Hypertension"
                )
                
                if st.button("💾 Save Diagnosis", key=f"save_{a['id']}"):
                    if final_disease_input.strip():
                        try:
                            resp = requests.post(
                                f"{BACKEND_URL}/doctor/assign-disease",
                                json={
                                    "appointment_id": a["id"],
                                    "final_disease": final_disease_input.strip(),
                                    "patient_id": a.get("patient_id"),
                                },
                                timeout=10,
                            )
                            result = resp.json()
                            if result.get("success"):
                                st.success(f"✅ Diagnosis saved: {final_disease_input}")
                                st.rerun()
                            else:
                                st.error(result.get("reason", "Failed to save diagnosis."))
                        except Exception as e:
                            st.error(f"Failed to save diagnosis: {e}")
                    else:
                        st.warning("Please enter a diagnosis before saving.")
                
                st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
#         OTHER ROLES
# ==========================================
else:
    st.warning(
        f"Role '{role}' is not fully supported yet. "
        "Currently, only patients and doctors have dedicated dashboards."
    )
