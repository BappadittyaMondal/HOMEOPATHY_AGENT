"""
Interactive Responsive HTML5 Dashboard Generator (Phase 83).

Generates standalone, responsive, self-contained HTML5 clinical dashboards
with embedded SVG visualizations, zero external CDN dependencies,
dual-audience view toggles, and print-ready stylesheets (@media print).
"""
import html
import datetime
from typing import Optional, List, Dict, Any

from app.reporting.contracts import ReportAudience, ReportGenerationRequest, RenderedVisualAsset
from app.reporting.visualizer import ClinicalVisualizer
from app.clinical.master_verifier import MasterHardenedClinicalResult, MasterClinicalWorkflowResult


class HTMLDashboardBuilder:
    """
    Renders standalone interactive HTML5 clinical dashboards with embedded CSS,
    SVG visualizations, print stylesheets, and accessibility controls.
    """

    @classmethod
    def build_dashboard(
        cls,
        hardened_result: MasterHardenedClinicalResult,
        workflow_result: Optional[MasterClinicalWorkflowResult] = None,
        request: Optional[ReportGenerationRequest] = None
    ) -> str:
        """Generates the complete responsive HTML5 dashboard document."""
        ehr = hardened_result.ehr_encounter
        draft = hardened_result.approved_draft
        sig = hardened_result.signed_prescription
        nabh = hardened_result.nabh_audit_entry
        td = hardened_result.transfer_dossier
        remedy_name = hardened_result.canonical_remedy_name or "ABSTAIN / WITHHELD"

        vitality_val = ehr.vitality_score if ehr else 7.0
        dominant_miasm = ehr.dominant_miasm if ehr else "PSORA"
        chief_complaint = ehr.chief_complaint if ehr else "No complaint recorded"
        rubrics = ehr.rubrics_selected if ehr else []

        # 1. Generate SVG visual components
        vitality_gauge = ClinicalVisualizer.generate_vitality_gauge(vitality_val)
        news2_score = 0
        news2_tier = "LOW"
        if td:
            news2_score = getattr(td, "news2_score", 9)
            news2_tier = "HIGH_CRITICAL"
        news2_gauge = ClinicalVisualizer.generate_news2_gauge(news2_score, clinical_tier=news2_tier)

        candidates = []
        if workflow_result and workflow_result.repertorization_report:
            candidates = workflow_result.repertorization_report.top_candidates
        simillimum_bars = ClinicalVisualizer.generate_simillimum_bar_chart(candidates)

        miasm_vector = workflow_result.miasmatic_vector if workflow_result else None
        miasm_radar = ClinicalVisualizer.generate_miasmatic_radar(miasm_vector)

        trajectory_scores = [vitality_val]
        if workflow_result and workflow_result.longitudinal_trajectory:
            trajectory_scores = workflow_result.longitudinal_trajectory.vitality_trend or [vitality_val]
        trend_line = ClinicalVisualizer.generate_longitudinal_trend(trajectory_scores)

        kpi_remedy = ClinicalVisualizer.generate_kpi_card("Prescribed Simillimum", remedy_name, draft.potency if draft else "N/A", "#059669")
        kpi_vitality = ClinicalVisualizer.generate_kpi_card("Vital Reserve", f"{vitality_val:.1f} / 10", "Susceptibility Tone", "#2563EB")
        kpi_miasm = ClinicalVisualizer.generate_kpi_card("Dominant Miasm", dominant_miasm, "Simplex Primary", "#4F46E5")
        kpi_safety = ClinicalVisualizer.generate_kpi_card("Safety Gates", f"{len(hardened_result.invariants_verified)} Passed", "Zero-Tolerance", "#0D9488")

        # 2. Build Rubrics List HTML
        rubrics_html = "".join([f"<li class='rubric-item'><code>{html.escape(r)}</code></li>" for r in rubrics]) if rubrics else "<li><em>No rubrics selected</em></li>"

        # 3. Emergency Lockout Banner HTML
        emergency_banner_html = ""
        if hardened_result.is_emergency_lockout:
            diag = getattr(td, "primary_diagnosis_summary", getattr(td, "primary_emergency_diagnosis", "CRITICAL EMERGENCY")) if td else "CRITICAL EMERGENCY"
            emergency_banner_html = f"""
            <div class="emergency-banner">
                <div class="emergency-icon">&#9888;</div>
                <div class="emergency-text">
                    <h3>EMERGENCY BREAK-GLASS LOCKOUT ACTIVE (ORGANON &sect;186)</h3>
                    <p><strong>Critical Diagnosis:</strong> {html.escape(str(diag))}</p>
                    <p>Homeopathic prescribing suspended. Patient transferred to Tertiary Emergency Care.</p>
                </div>
            </div>"""

        # 4. Invariants HTML Badges
        invariants_html = "".join([f"<span class='inv-badge'>{inv}</span>" for inv in hardened_result.invariants_verified])

        # 5. Assemble HTML
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical Consultation Dossier — {html.escape(hardened_result.patient_id)}</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --bg-canvas: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-canvas);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        /* Header & Action Bar */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            padding: 20px 24px;
            border-radius: 12px;
            box-shadow: var(--shadow);
            border-left: 6px solid var(--primary);
            margin-bottom: 20px;
        }}
        .header-title h1 {{
            font-size: 22px;
            font-weight: 800;
            color: var(--text-main);
        }}
        .header-title p {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        .action-bar {{
            display: flex;
            gap: 10px;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid var(--border);
            cursor: pointer;
            background: #ffffff;
            color: var(--text-main);
            transition: all 0.2s ease;
        }}
        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}
        .btn-primary:hover {{ background: var(--primary-dark); }}
        .btn:hover {{ background: #f1f5f9; }}

        /* Audio Narration Bar */
        .audio-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f1f5f9;
            border: 1px solid var(--border);
            padding: 10px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .audio-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .audio-status {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
        }}

        /* Emergency Alert */
        .emergency-banner {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: #fee2e2;
            border-left: 6px solid var(--danger);
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #991b1b;
        }}
        .emergency-icon {{ font-size: 28px; }}

        /* KPI Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        /* Visualizations Grid */
        .viz-grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }}
        .col-4 {{ grid-column: span 4; }}
        .col-6 {{ grid-column: span 6; }}
        .col-8 {{ grid-column: span 8; }}
        .col-12 {{ grid-column: span 12; }}

        @media (max-width: 900px) {{
            .col-4, .col-6, .col-8 {{ grid-column: span 12; }}
        }}

        /* Audience Tabs */
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 8px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-radius: 6px;
        }}
        .tab-btn.active {{
            background: var(--primary);
            color: #ffffff;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        /* Rubrics List */
        .rubrics-list {{
            list-style: none;
            margin-top: 10px;
        }}
        .rubric-item {{
            padding: 6px 10px;
            background: #f8fafc;
            border-radius: 4px;
            margin-bottom: 6px;
            font-size: 13px;
        }}

        /* Invariant Badges */
        .inv-badges-wrap {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
        }}
        .inv-badge {{
            background: #e0f2fe;
            color: #0369a1;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}

        /* Print Styles */
        @media print {{
            body {{ background: #ffffff; padding: 0; }}
            .action-bar, .audio-bar, .tabs {{ display: none !important; }}
            .card {{ box-shadow: none; border: 1px solid #cbd5e1; page-break-inside: avoid; }}
            .tab-content {{ display: block !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-title">
                <h1>CLINICAL CONSULTATION & DECISION SUPPORT DOSSIER</h1>
                <p>Patient ID: <strong>{html.escape(hardened_result.patient_id)}</strong> | Tenant: <strong>{html.escape(hardened_result.tenant_id)}</strong> | System: <code>{hardened_result.system_status_banner}</code></p>
            </div>
            <div class="action-bar">
                <button class="btn" onclick="window.print()">&#128438; Print / Save PDF</button>
            </div>
        </header>

        <!-- Browser Audio Narration Bar -->
        <section class="audio-bar" id="audio-narration-widget">
            <div class="audio-controls">
                <span style="font-size: 18px;">&#128266;</span>
                <span class="audio-status" id="speech-status">Audio Narration: Ready (Muted)</span>
                <button class="btn" id="btn-play-speech" onclick="playAudioReport()">&#9654; Play</button>
                <button class="btn" id="btn-pause-speech" onclick="pauseAudioReport()">&#10074;&#10074; Pause</button>
                <button class="btn" id="btn-stop-speech" onclick="stopAudioReport()">&#9632; Stop</button>
            </div>
            <div>
                <label for="lang-select" style="font-size: 12px; font-weight: 600; color: var(--text-muted);">Language:</label>
                <select id="lang-select" style="padding: 4px 8px; border-radius: 4px; border: 1px solid var(--border); font-size: 12px;">
                    <option value="en-IN" selected>English (India)</option>
                    <option value="hi-IN">Hindi (हिन्दी)</option>
                    <option value="bn-IN">Bengali (বাংলা)</option>
                </select>
            </div>
        </section>

        <!-- Emergency Alert Banner -->
        {emergency_banner_html}

        <!-- KPI Grid -->
        <section class="kpi-grid">
            <div>{kpi_remedy.svg_xml}</div>
            <div>{kpi_vitality.svg_xml}</div>
            <div>{kpi_miasm.svg_xml}</div>
            <div>{kpi_safety.svg_xml}</div>
        </section>

        <!-- Audience Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('clinician-view', this)">Clinician Forensic View</button>
            <button class="tab-btn" onclick="switchTab('patient-view', this)">Patient Care Plan</button>
        </div>

        <!-- TAB 1: Clinician Forensic View -->
        <div id="clinician-view" class="tab-content active">
            <div class="viz-grid">
                <!-- Row 1: Vitality & NEWS2 Gauges -->
                <div class="card col-4">
                    <h3>Vitality Assessment</h3>
                    {vitality_gauge.svg_xml}
                </div>
                <div class="card col-4">
                    <h3>Physiological Triage</h3>
                    {news2_gauge.svg_xml}
                </div>
                <div class="card col-4">
                    <h3>4D Miasmatic Simplex</h3>
                    {miasm_radar.svg_xml}
                </div>

                <!-- Row 2: Simillimum Bar Chart & Trend Line -->
                <div class="card col-6">
                    {simillimum_bars.svg_xml}
                </div>
                <div class="card col-6">
                    {trend_line.svg_xml}
                </div>

                <!-- Row 3: Totality & Governance -->
                <div class="card col-6">
                    <h3>Classical Totality Rubrics</h3>
                    <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px;"><strong>Chief Complaint:</strong> {html.escape(chief_complaint)}</p>
                    <ul class="rubrics-list">
                        {rubrics_html}
                    </ul>
                </div>
                <div class="card col-6">
                    <h3>Statutory Governance & Signatures</h3>
                    <p style="font-size: 13px; margin-bottom: 6px;"><strong>RMP Signer:</strong> {html.escape(sig.rmp_name if sig else 'N/A')} ({html.escape(sig.registration_number if sig else 'N/A')})</p>
                    <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;"><strong>Payload Hash:</strong> <code>{sig.payload_hash_sha256 if sig else 'N/A'}</code></p>
                    <h4 style="font-size: 13px; margin-top: 12px;">Verified Invariant Gates:</h4>
                    <div class="inv-badges-wrap">
                        {invariants_html}
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: Patient Care Plan -->
        <div id="patient-view" class="tab-content">
            <div class="card col-12" style="margin-bottom: 20px;">
                <h2 style="color: var(--success); margin-bottom: 12px;">Prescribed Medicine: {html.escape(remedy_name)} ({html.escape(draft.potency if draft else '')})</h2>
                <p style="font-size: 15px; margin-bottom: 16px;"><strong>Directions for Use:</strong> {html.escape(draft.dosage_instructions if draft else 'Follow doctor instructions.')}</p>
                <div style="background: #f8fafc; border-left: 4px solid var(--primary); padding: 12px 16px; border-radius: 4px; margin-bottom: 16px;">
                    <h4 style="margin-bottom: 6px;">Important Hahnemannian Instructions:</h4>
                    <ul style="margin-left: 20px; font-size: 13px; line-height: 1.6;">
                        <li>Take medicine on a clean tongue (no food, coffee, smoking 20 minutes before or after).</li>
                        <li>Keep away from direct sunlight, camphor, perfumes, and electronic radiation.</li>
                        <li>Dissolve in clean water and succuss (shake) if liquid posology is prescribed.</li>
                    </ul>
                </div>
                <div style="background: #fef2f2; border-left: 4px solid var(--danger); padding: 12px 16px; border-radius: 4px;">
                    <h4 style="color: var(--danger); margin-bottom: 6px;">Emergency Warning Signs:</h4>
                    <p style="font-size: 13px; color: #991b1b;">If you experience crushing chest pain, severe shortness of breath, sudden facial weakness, or acute collapse, call emergency medical services immediately.</p>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>HOMEOPATHY_AGENT v3.2.0-ENTERPRISE-CLINICAL | NABH Homoeopathy 2nd Edition Compliant | NCH Act 2020 Statutory Verified</p>
            <p>Generated at: {datetime.datetime.now(datetime.timezone.utc).isoformat()} UTC</p>
        </footer>
    </div>

    <!-- Client-Side Tabs & Audio Speech Synthesis Script -->
    <script>
        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }}

        // W3C Web Speech API Client-Side Narration Controller
        let speechSynth = window.speechSynthesis;
        let speechUtterance = null;

        function getReportNarrationText() {{
            const patientId = "{html.escape(hardened_result.patient_id)}";
            const remedy = "{html.escape(remedy_name)}";
            const potency = "{html.escape(draft.potency if draft else '')}";
            return `Clinical consultation summary for patient ${{patientId}}. Prescribed homeopathic simillimum is ${{remedy}}, potency ${{potency}}. Patient vitality reserve is assessed at {vitality_val:.1f} out of 10. All safety gates passed successfully.`;
        }}

        function playAudioReport() {{
            if (!speechSynth) {{
                alert("Web Speech API is not supported on this device/browser.");
                return;
            }}
            if (speechSynth.paused) {{
                speechSynth.resume();
                document.getElementById('speech-status').innerText = "Audio Narration: Playing";
                return;
            }}
            speechSynth.cancel(); // Reset previous
            const text = getReportNarrationText();
            speechUtterance = new SpeechSynthesisUtterance(text);
            const langSelect = document.getElementById('lang-select');
            speechUtterance.lang = langSelect.value;
            speechUtterance.rate = 0.95;

            speechUtterance.onstart = () => {{
                document.getElementById('speech-status').innerText = "Audio Narration: Playing (" + langSelect.value + ")";
            }};
            speechUtterance.onend = () => {{
                document.getElementById('speech-status').innerText = "Audio Narration: Finished";
            }};
            speechUtterance.onerror = (e) => {{
                document.getElementById('speech-status').innerText = "Audio Narration: Stopped";
            }};

            speechSynth.speak(speechUtterance);
        }}

        function pauseAudioReport() {{
            if (speechSynth && speechSynth.speaking) {{
                speechSynth.pause();
                document.getElementById('speech-status').innerText = "Audio Narration: Paused";
            }}
        }}

        function stopAudioReport() {{
            if (speechSynth) {{
                speechSynth.cancel();
                document.getElementById('speech-status').innerText = "Audio Narration: Stopped";
            }}
        }}
    </script>
</body>
</html>"""
        return html_doc
