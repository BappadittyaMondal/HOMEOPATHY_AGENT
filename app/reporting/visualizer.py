"""
Simple Data-Visualization & SVG Component Engine (Phase 81).

Generates lightweight, mathematical, faithful inline SVG visualizations
for clinical and executive dashboards with zero JavaScript/Canvas/GPU overhead:
- Semicircular Vitality / Constitutional Reserve Gauge
- Objective NEWS2 Physiological Risk Gauge
- Simillimum Vector Space Candidate Ranking Bar Chart
- 4-Dimensional Miasmatic Simplex Radar Chart (Delta^3)
- Longitudinal Patient Vitality Trend Line
- High-Impact Clinical KPI Summary Cards
"""
import math
from typing import List, Optional, Dict, Any

from app.reporting.contracts import RenderedVisualAsset, VisualizationComponentType
from app.models.simillimum import RankedRemedyCandidate
from app.models.miasmatic import MiasmaticSimplexVector


class ClinicalVisualizer:
    """
    Pure-Python mathematical SVG rendering engine for clinical data visualization.
    Generates standards-compliant SVG XML with clean responsive viewboxes.
    """

    @staticmethod
    def generate_vitality_gauge(
        score: float,
        max_score: float = 10.0,
        label: str = "Vital Force & Susceptibility",
        width: int = 240,
        height: int = 150
    ) -> RenderedVisualAsset:
        """
        Renders a calibrated semicircular arc gauge for patient vitality tone.
        Color bands:
          - 1.0 - 3.5: Red (#EF4444) Low Reserve / Kent Obs 1 Risk
          - 3.5 - 6.5: Amber (#F59E0B) Moderate / Functional
          - 6.5 - 10.0: Green (#10B981) Robust Vital Force
        """
        clamped_score = max(1.0, min(float(score), float(max_score)))
        fraction = (clamped_score - 1.0) / (max_score - 1.0)
        # Semicircle angle from 180 deg (left) to 0 deg (right)
        angle_deg = 180.0 - (fraction * 180.0)
        angle_rad = math.radians(angle_deg)

        cx, cy, r = 120, 110, 80
        needle_len = 65
        nx = cx + needle_len * math.cos(angle_rad)
        ny = cy - needle_len * math.sin(angle_rad)

        # Determine color and qualitative status
        if clamped_score < 3.5:
            needle_color = "#EF4444"
            status_text = "LOW RESERVE"
            badge_bg = "#FEE2E2"
            badge_fg = "#991B1B"
        elif clamped_score < 6.5:
            needle_color = "#F59E0B"
            status_text = "MODERATE"
            badge_bg = "#FEF3C7"
            badge_fg = "#92400E"
        else:
            needle_color = "#10B981"
            status_text = "ROBUST"
            badge_bg = "#D1FAE5"
            badge_fg = "#065F46"

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" class="vitality-gauge-svg">
  <defs>
    <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#EF4444"/>
      <stop offset="30%" stop-color="#F59E0B"/>
      <stop offset="70%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
  </defs>
  <!-- Background Arc -->
  <path d="M 40,110 A 80,80 0 0,1 200,110" fill="none" stroke="#E2E8F0" stroke-width="14" stroke-linecap="round"/>
  <!-- Value Arc Gradient -->
  <path d="M 40,110 A 80,80 0 0,1 200,110" fill="none" stroke="url(#gauge-gradient)" stroke-width="14" stroke-linecap="round" stroke-dasharray="251.32" stroke-dashoffset="0"/>
  <!-- Needle -->
  <line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{needle_color}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="{cx}" cy="{cy}" r="6" fill="#1E293B"/>
  <circle cx="{cx}" cy="{cy}" r="2.5" fill="#FFFFFF"/>
  <!-- Readout Text -->
  <text x="{cx}" y="95" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="700" fill="#0F172A">{clamped_score:.1f}</text>
  <text x="{cx}" y="128" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="600" fill="#64748B">{label.upper()}</text>
  <!-- Status Badge -->
  <rect x="75" y="134" width="90" height="15" rx="4" fill="{badge_bg}"/>
  <text x="{cx}" y="145" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="700" fill="{badge_fg}">{status_text}</text>
</svg>"""

        return RenderedVisualAsset(
            component_type=VisualizationComponentType.GAUGE_VITALITY,
            title="Patient Vitality Gauge",
            svg_xml=svg,
            width_px=width,
            height_px=height,
            description=f"Vitality Score: {clamped_score:.1f}/10.0 ({status_text})"
        )

    @staticmethod
    def generate_news2_gauge(
        score: int,
        clinical_tier: str = "LOW",
        width: int = 240,
        height: int = 150
    ) -> RenderedVisualAsset:
        """
        Renders a calibrated NEWS2 Physiological Triage Gauge.
        Color bands:
          - 0 - 4: Green (#10B981) Low Risk / Outpatient Safe
          - 5 - 6: Amber (#F59E0B) Medium Risk / Urgent Review
          - 7+: Red (#DC2626) High Risk / Emergency Transfer Required
        """
        clamped_score = max(0, min(int(score), 20))
        fraction = clamped_score / 20.0
        angle_deg = 180.0 - (fraction * 180.0)
        angle_rad = math.radians(angle_deg)

        cx, cy, r = 120, 110, 80
        needle_len = 65
        nx = cx + needle_len * math.cos(angle_rad)
        ny = cy - needle_len * math.sin(angle_rad)

        if clamped_score >= 7 or clinical_tier in ["HIGH_CRITICAL", "CRITICAL"]:
            needle_color = "#DC2626"
            tier_label = "HIGH CRITICAL"
            badge_bg = "#FEE2E2"
            badge_fg = "#991B1B"
        elif clamped_score >= 5 or clinical_tier in ["MEDIUM", "URGENT"]:
            needle_color = "#F59E0B"
            tier_label = "MEDIUM RISK"
            badge_bg = "#FEF3C7"
            badge_fg = "#92400E"
        else:
            needle_color = "#10B981"
            tier_label = "LOW RISK"
            badge_bg = "#D1FAE5"
            badge_fg = "#065F46"

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" class="news2-gauge-svg">
  <!-- Track -->
  <path d="M 40,110 A 80,80 0 0,1 200,110" fill="none" stroke="#E2E8F0" stroke-width="14" stroke-linecap="round"/>
  <!-- Risk Zones -->
  <!-- 0-4 Low Green (approx 36 deg) -->
  <path d="M 40,110 A 80,80 0 0,1 68,48" fill="none" stroke="#10B981" stroke-width="14"/>
  <!-- 5-6 Medium Amber -->
  <path d="M 68,48 A 80,80 0 0,1 92,34" fill="none" stroke="#F59E0B" stroke-width="14"/>
  <!-- 7+ High Red -->
  <path d="M 92,34 A 80,80 0 0,1 200,110" fill="none" stroke="#DC2626" stroke-width="14"/>
  <!-- Needle -->
  <line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{needle_color}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="{cx}" cy="{cy}" r="6" fill="#1E293B"/>
  <circle cx="{cx}" cy="{cy}" r="2.5" fill="#FFFFFF"/>
  <!-- Numerical Readout -->
  <text x="{cx}" y="95" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="700" fill="#0F172A">NEWS2: {clamped_score}</text>
  <text x="{cx}" y="128" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="600" fill="#64748B">PHYSIOLOGICAL SAFETY</text>
  <!-- Tier Badge -->
  <rect x="70" y="134" width="100" height="15" rx="4" fill="{badge_bg}"/>
  <text x="{cx}" y="145" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="700" fill="{badge_fg}">{tier_label}</text>
</svg>"""

        return RenderedVisualAsset(
            component_type=VisualizationComponentType.GAUGE_NEWS2,
            title="NEWS2 Physiological Gauge",
            svg_xml=svg,
            width_px=width,
            height_px=height,
            description=f"NEWS2 Score: {clamped_score} ({tier_label})"
        )

    @staticmethod
    def generate_simillimum_bar_chart(
        candidates: List[Any],
        max_items: int = 5,
        width: int = 420,
        height: Optional[int] = None
    ) -> RenderedVisualAsset:
        """
        Renders a horizontal ranking bar chart showing candidate remedies,
        composite scores, and rubric coverage.
        """
        items = candidates[:max_items] if candidates else []
        row_height = 36
        chart_height = height or (55 + max(1, len(items)) * row_height)

        bar_svg_elements = []
        start_y = 45

        if not items:
            bar_svg_elements.append(
                f'<text x="210" y="60" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#64748B">No remedy candidates evaluated (ABSTAIN or Lockout)</text>'
            )
        else:
            for idx, cand in enumerate(items):
                y = start_y + (idx * row_height)
                name = getattr(cand, "remedy_name", f"Remedy {idx+1}")
                score = getattr(cand, "composite_score", 0.0)
                rubrics_cov = getattr(cand, "total_rubrics_covered", 0)
                rubrics_tot = getattr(cand, "patient_rubrics_total", 0)

                # Score bar calculation: max score 100 maps to 200px width
                bar_max_w = 190
                bar_w = max(4.0, (min(score, 100.0) / 100.0) * bar_max_w)

                is_primary = (idx == 0)
                bar_color = "#059669" if is_primary else "#3B82F6"
                badge_text = "SIMILLIMUM" if is_primary else f"RANK #{idx+1}"

                cov_str = f"{rubrics_cov}/{rubrics_tot}" if rubrics_tot > 0 else f"{rubrics_cov}"

                bar_row = f"""  <!-- Row {idx+1}: {name} -->
  <text x="15" y="{y + 14}" font-family="system-ui, sans-serif" font-size="11" font-weight="600" fill="#1E293B">{name}</text>
  <rect x="150" y="{y + 2}" width="{bar_max_w}" height="14" rx="3" fill="#F1F5F9"/>
  <rect x="150" y="{y + 2}" width="{bar_w:.1f}" height="14" rx="3" fill="{bar_color}"/>
  <text x="350" y="{y + 13}" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="#0F172A">{score:.1f}%</text>
  <text x="390" y="{y + 13}" font-family="system-ui, sans-serif" font-size="9" font-weight="500" fill="#64748B">({cov_str})</text>"""
                bar_svg_elements.append(bar_row)

        bars_body = "\n".join(bar_svg_elements)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {chart_height}" width="100%" height="auto" class="simillimum-bar-svg">
  <!-- Header -->
  <text x="15" y="22" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" fill="#0F172A">SIMILLIMUM VECTOR SPACE RANKING</text>
  <text x="15" y="36" font-family="system-ui, -apple-system, sans-serif" font-size="9.5" fill="#64748B">Composite Repertorial Rank (Density + Breadth + Mental Alignment)</text>
  <line x1="15" y1="40" x2="{width - 15}" y2="40" stroke="#E2E8F0" stroke-width="1"/>
{bars_body}
</svg>"""

        return RenderedVisualAsset(
            component_type=VisualizationComponentType.BAR_SIMILLIMUM_RANK,
            title="Simillimum Candidate Ranking",
            svg_xml=svg,
            width_px=width,
            height_px=chart_height,
            description=f"Top candidate: {getattr(items[0], 'remedy_name', 'None') if items else 'None'}"
        )

    @staticmethod
    def generate_miasmatic_radar(
        vector: Optional[MiasmaticSimplexVector],
        width: int = 260,
        height: int = 240
    ) -> RenderedVisualAsset:
        """
        Renders a 4-dimensional diamond/polar radar chart representing
        the Miasmatic Simplex (Delta^3): Psora, Sycosis, Syphilis, Tubercular.
        Coordinates are mathematically normalized to [0.0, 1.0].
        """
        cx, cy, max_r = 130, 120, 75

        # Extract values
        if vector:
            p = float(vector.psora)
            s = float(vector.sycosis)
            sy = float(vector.syphilis)
            t = float(vector.tubercular)
            dominant = str(getattr(vector, "dominant_miasm", "PSORA")).split(".")[-1]
        else:
            p, s, sy, t = 0.25, 0.25, 0.25, 0.25
            dominant = "UNSPECIFIED"

        # Coordinates for vertices on 4 axes:
        # Psora (Top, -Y): (cx, cy - max_r * p)
        # Sycosis (Right, +X): (cx + max_r * s, cy)
        # Syphilis (Bottom, +Y): (cx, cy + max_r * sy)
        # Tubercular (Left, -X): (cx - max_r * t, cy)
        p_x, p_y = cx, cy - (max_r * p)
        s_x, s_y = cx + (max_r * s), cy
        sy_x, sy_y = cx, cy + (max_r * sy)
        t_x, t_y = cx - (max_r * t), cy

        # Concentric guide rings (25%, 50%, 75%, 100%)
        rings = []
        for frac in [0.25, 0.50, 0.75, 1.0]:
            r_val = max_r * frac
            rings.append(
                f'<polygon points="{cx},{cy - r_val} {cx + r_val},{cy} {cx},{cy + r_val} {cx - r_val},{cy}" '
                f'fill="none" stroke="#E2E8F0" stroke-width="0.8" stroke-dasharray="2,2"/>'
            )
        rings_xml = "\n  ".join(rings)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" class="miasmatic-radar-svg">
  <!-- Title -->
  <text x="{cx}" y="18" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#0F172A">4D MIASMATIC SIMPLEX (&Delta;&sup3;)</text>
  <!-- Guide Rings -->
  {rings_xml}
  <!-- Cross Axes -->
  <line x1="{cx}" y1="{cy - max_r - 5}" x2="{cx}" y2="{cy + max_r + 5}" stroke="#CBD5E1" stroke-width="1"/>
  <line x1="{cx - max_r - 5}" y1="{cy}" x2="{cx + max_r + 5}" y2="{cy}" stroke="#CBD5E1" stroke-width="1"/>
  <!-- Axis Labels -->
  <text x="{cx}" y="{cy - max_r - 10}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="#4F46E5">PSORA ({p*100:.0f}%)</text>
  <text x="{cx + max_r + 8}" y="{cy + 3}" text-anchor="start" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="#059669">SYC ({s*100:.0f}%)</text>
  <text x="{cx}" y="{cy + max_r + 18}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="#DC2626">SYPH ({sy*100:.0f}%)</text>
  <text x="{cx - max_r - 8}" y="{cy + 3}" text-anchor="end" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="#D97706">TUB ({t*100:.0f}%)</text>
  <!-- Data Polygon -->
  <polygon points="{p_x:.1f},{p_y:.1f} {s_x:.1f},{s_y:.1f} {sy_x:.1f},{sy_y:.1f} {t_x:.1f},{t_y:.1f}"
           fill="#6366F1" fill-opacity="0.30" stroke="#4F46E5" stroke-width="2"/>
  <!-- Vertex Dots -->
  <circle cx="{p_x:.1f}" cy="{p_y:.1f}" r="3" fill="#4F46E5"/>
  <circle cx="{s_x:.1f}" cy="{s_y:.1f}" r="3" fill="#059669"/>
  <circle cx="{sy_x:.1f}" cy="{sy_y:.1f}" r="3" fill="#DC2626"/>
  <circle cx="{t_x:.1f}" cy="{t_y:.1f}" r="3" fill="#D97706"/>
  <!-- Dominant Badge -->
  <rect x="75" y="{height - 18}" width="110" height="15" rx="4" fill="#EEF2FF"/>
  <text x="{cx}" y="{height - 7}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="8.5" font-weight="700" fill="#4338CA">DOMINANT: {dominant}</text>
</svg>"""

        return RenderedVisualAsset(
            component_type=VisualizationComponentType.RADAR_MIASMATIC_SIMPLEX,
            title="Miasmatic Simplex Radar",
            svg_xml=svg,
            width_px=width,
            height_px=height,
            description=f"Dominant: {dominant} (P:{p:.2f}, Syc:{s:.2f}, Syph:{sy:.2f}, Tub:{t:.2f})"
        )

    @staticmethod
    def generate_longitudinal_trend(
        vitality_scores: List[float],
        encounter_dates: Optional[List[str]] = None,
        width: int = 360,
        height: int = 160
    ) -> RenderedVisualAsset:
        """
        Renders a longitudinal trend line of patient vitality across encounters.
        Calculates exact coordinates with zero data distortion.
        """
        scores = vitality_scores if vitality_scores else [5.0]
        padding_left = 35
        padding_right = 20
        padding_top = 35
        padding_bottom = 30

        plot_w = width - padding_left - padding_right
        plot_h = height - padding_top - padding_bottom

        min_val, max_val = 1.0, 10.0

        n = len(scores)
        points = []
        for i, val in enumerate(scores):
            x = padding_left + (i * (plot_w / max(1, n - 1))) if n > 1 else padding_left + (plot_w / 2)
            clamped_y = max(min_val, min(float(val), max_val))
            y = padding_top + (1.0 - ((clamped_y - min_val) / (max_val - min_val))) * plot_h
            points.append((x, y, clamped_y))

        # Build polyline string
        polyline_coords = " ".join([f"{x:.1f},{y:.1f}" for x, y, _ in points])

        # Build area polygon
        first_x, last_x = points[0][0], points[-1][0]
        baseline_y = padding_top + plot_h
        area_coords = f"{first_x:.1f},{baseline_y} " + polyline_coords + f" {last_x:.1f},{baseline_y}"

        # Direction assessment
        if n >= 2:
            delta = scores[-1] - scores[0]
            if delta > 0.5:
                direction_text = "IMPROVING"
                dir_color = "#10B981"
            elif delta < -0.5:
                direction_text = "DECLINING"
                dir_color = "#EF4444"
            else:
                direction_text = "STABLE"
                dir_color = "#3B82F6"
        else:
            direction_text = "BASELINE"
            dir_color = "#64748B"

        # Points SVG
        dots_svg = []
        for i, (x, y, val) in enumerate(points):
            dots_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2563EB" stroke="#FFFFFF" stroke-width="1.5"/>')
            dots_svg.append(f'<text x="{x:.1f}" y="{y - 7:.1f}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="#1E293B">{val:.1f}</text>')

        dots_xml = "\n  ".join(dots_svg)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" class="vitality-trend-svg">
  <defs>
    <linearGradient id="trend-fill" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <!-- Title -->
  <text x="{padding_left}" y="18" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#0F172A">LONGITUDINAL VITALITY TRAJECTORY</text>
  <!-- Direction Indicator -->
  <rect x="{width - 95}" y="8" width="75" height="15" rx="3" fill="#F1F5F9"/>
  <text x="{width - 57}" y="19" text-anchor="middle" font-family="system-ui, sans-serif" font-size="8.5" font-weight="700" fill="{dir_color}">{direction_text}</text>
  <!-- Grid Lines (10.0, 5.0, 1.0) -->
  <line x1="{padding_left}" y1="{padding_top}" x2="{width - padding_right}" y2="{padding_top}" stroke="#E2E8F0" stroke-width="0.8" stroke-dasharray="2,2"/>
  <text x="{padding_left - 5}" y="{padding_top + 3}" text-anchor="end" font-family="system-ui, sans-serif" font-size="8" fill="#94A3B8">10</text>
  <line x1="{padding_left}" y1="{padding_top + (plot_h / 2)}" x2="{width - padding_right}" y2="{padding_top + (plot_h / 2)}" stroke="#E2E8F0" stroke-width="0.8" stroke-dasharray="2,2"/>
  <text x="{padding_left - 5}" y="{padding_top + (plot_h / 2) + 3}" text-anchor="end" font-family="system-ui, sans-serif" font-size="8" fill="#94A3B8">5</text>
  <line x1="{padding_left}" y1="{baseline_y}" x2="{width - padding_right}" y2="{baseline_y}" stroke="#E2E8F0" stroke-width="0.8"/>
  <text x="{padding_left - 5}" y="{baseline_y + 3}" text-anchor="end" font-family="system-ui, sans-serif" font-size="8" fill="#94A3B8">1</text>
  <!-- Area & Line -->
  <polygon points="{area_coords}" fill="url(#trend-fill)"/>
  <polyline points="{polyline_coords}" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Data Points -->
  {dots_xml}
  <!-- Baseline axis label -->
  <text x="{width / 2}" y="{height - 6}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="8.5" fill="#64748B">Sequential Clinical Encounters ({n} Recorded)</text>
</svg>"""

        return RenderedVisualAsset(
            component_type=VisualizationComponentType.LINE_LONGITUDINAL_TREND,
            title="Longitudinal Vitality Trend",
            svg_xml=svg,
            width_px=width,
            height_px=height,
            description=f"Trajectory: {direction_text} across {n} encounters"
        )

    @staticmethod
    def generate_kpi_card(
        title: str,
        value: str,
        subtitle: str,
        color_hex: str = "#2563EB",
        badge: Optional[str] = None,
        width: int = 200,
        height: int = 85
    ) -> RenderedVisualAsset:
        """
        Renders a clean, high-impact clinical KPI stat card SVG.
        """
        badge_xml = ""
        if badge:
            badge_xml = f"""  <rect x="{width - 65}" y="10" width="55" height="14" rx="3" fill="#F1F5F9"/>
  <text x="{width - 37}" y="20" text-anchor="middle" font-family="system-ui, sans-serif" font-size="8" font-weight="700" fill="{color_hex}">{badge}</text>"""

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" class="kpi-card-svg">
  <rect x="2" y="2" width="{width - 4}" height="{height - 4}" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
  <line x1="2" y1="2" x2="6" y2="2" stroke="{color_hex}" stroke-width="4" stroke-linecap="round"/>
  <line x1="2" y1="2" x2="2" y2="{height - 2}" stroke="{color_hex}" stroke-width="4"/>
  <!-- Title -->
  <text x="14" y="22" font-family="system-ui, sans-serif" font-size="9" font-weight="600" fill="#64748B" letter-spacing="0.5">{title.upper()}</text>
{badge_xml}
  <!-- Value -->
  <text x="14" y="52" font-family="system-ui, sans-serif" font-size="20" font-weight="800" fill="{color_hex}">{value}</text>
  <!-- Subtitle -->
  <text x="14" y="70" font-family="system-ui, sans-serif" font-size="8.5" fill="#94A3B8">{subtitle}</text>
</svg>"""

        return RenderedVisualAsset(
            component_type=VisualizationComponentType.KPI_STAT_CARD,
            title=f"KPI: {title}",
            svg_xml=svg,
            width_px=width,
            height_px=height,
            description=f"{title}: {value} ({subtitle})"
        )
