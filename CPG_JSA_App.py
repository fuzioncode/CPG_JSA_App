# Unified Tab Routing for Leads and Mobile Techs
nav_options = ["🎙️ 1. Voice Briefing", "📝 2. Review JSA", "✍️ 3. QR / Crew Sign", "🚀 4. Drive Sync"]
default_nav_index = 2 if is_mobile_signer else 0

selected_tab = st.radio("JSA Portal Navigation:", nav_options, index=default_nav_index, horizontal=True, label_visibility="collapsed")
st.markdown("---")

if selected_tab == "🎙️ 1. Voice Briefing":
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

elif selected_tab == "📝 2. Review JSA":
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

elif selected_tab == "✍️ 3. QR / Crew Sign":
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

elif selected_tab == "🚀 4. Drive Sync":
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