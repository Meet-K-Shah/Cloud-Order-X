"""Report Generator — produces PDF and Excel reports from order data."""
import io
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)


class ReportGenerator:
    BRAND_COLOR = colors.HexColor("#6366f1")
    HEADER_BG   = colors.HexColor("#f8fafc")

    # ── PDF ───────────────────────────────────────────────────────────────────
    def generate_pdf(self, orders: List[Dict[str, Any]], summary: Dict[str, Any]) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                topMargin=2*cm, bottomMargin=2*cm,
                                leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                     textColor=self.BRAND_COLOR, fontSize=22, spaceAfter=6)
        sub_style   = ParagraphStyle("Sub",   parent=styles["Normal"],
                                     textColor=colors.HexColor("#64748b"), fontSize=10, spaceAfter=18)
        section_style = ParagraphStyle("Section", parent=styles["Heading2"],
                                       textColor=colors.HexColor("#1e293b"), fontSize=13, spaceBefore=18, spaceAfter=8)

        elements = []

        # Header
        elements.append(Paragraph("CloudOrderX — Order Report", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", sub_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        elements.append(Spacer(1, 0.4*cm))

        # KPI summary table
        elements.append(Paragraph("Summary", section_style))
        kpi_data = [
            ["Metric", "Value"],
            ["Total Orders",       str(summary.get("totalOrders", 0))],
            ["Total Revenue",      f"${summary.get('totalRevenue', 0):,.2f}"],
            ["Avg Order Value",    f"${summary.get('averageOrderValue', 0):,.2f}"],
            ["Pending Orders",     str(summary.get("pendingOrders", 0))],
            ["Delivered Orders",   str(summary.get("deliveredOrders", 0))],
            ["Cancelled Orders",   str(summary.get("cancelledOrders", 0))],
        ]
        kpi_table = Table(kpi_data, colWidths=[9*cm, 7*cm])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  self.BRAND_COLOR),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  10),
            ("BACKGROUND",    (0, 1), (-1, -1), self.HEADER_BG),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, self.HEADER_BG]),
            ("FONTSIZE",      (0, 1), (-1, -1), 9),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.6*cm))

        # Orders table
        elements.append(Paragraph("Order Details", section_style))
        headers = ["Order #", "Customer", "Status", "Payment", "Total", "Date"]
        rows    = [headers]
        for o in orders[:200]:
            rows.append([
                o.get("orderNumber", ""),
                o.get("customer", {}).get("name", ""),
                o.get("status", ""),
                o.get("paymentStatus", ""),
                f"${float(o.get('totalAmount') or 0):,.2f}",
                (o.get("createdAt") or "")[:10],
            ])

        orders_table = Table(rows, colWidths=[3.5*cm, 4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        orders_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  self.BRAND_COLOR),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, self.HEADER_BG]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        elements.append(orders_table)

        doc.build(elements)
        buf.seek(0)
        return buf.read()

    # ── Excel ─────────────────────────────────────────────────────────────────
    def generate_excel(self, orders: List[Dict[str, Any]], summary: Dict[str, Any]) -> bytes:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            # Summary sheet
            summary_df = pd.DataFrame([
                {"Metric": "Total Orders",      "Value": summary.get("totalOrders", 0)},
                {"Metric": "Total Revenue",     "Value": summary.get("totalRevenue", 0)},
                {"Metric": "Avg Order Value",   "Value": summary.get("averageOrderValue", 0)},
                {"Metric": "Pending Orders",    "Value": summary.get("pendingOrders", 0)},
                {"Metric": "Delivered Orders",  "Value": summary.get("deliveredOrders", 0)},
                {"Metric": "Cancelled Orders",  "Value": summary.get("cancelledOrders", 0)},
            ])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Orders sheet
            if orders:
                orders_df = pd.DataFrame([{
                    "Order #":      o.get("orderNumber", ""),
                    "Customer":     o.get("customer", {}).get("name", ""),
                    "Email":        o.get("customer", {}).get("email", ""),
                    "Status":       o.get("status", ""),
                    "Payment":      o.get("paymentStatus", ""),
                    "Total ($)":    float(o.get("totalAmount") or 0),
                    "Items":        len(o.get("items", [])),
                    "Created At":   (o.get("createdAt") or "")[:10],
                } for o in orders])
                orders_df.to_excel(writer, sheet_name="Orders", index=False)

                # Revenue by month
                if summary.get("revenueByMonth"):
                    rev_df = pd.DataFrame([
                        {"Month": k, "Revenue ($)": v}
                        for k, v in summary["revenueByMonth"].items()
                    ])
                    rev_df.to_excel(writer, sheet_name="Revenue by Month", index=False)

        buf.seek(0)
        return buf.read()
