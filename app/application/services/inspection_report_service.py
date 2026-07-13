"""Inspection PDF report builder — ReportLab layout for physical inspection reports."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.application.services.inspection_service import InspectionService
from app.infrastructure.persistence.models.inspection import Inspection

BRAND_NAVY = colors.HexColor("#0D3D5C")
BRAND_PRIMARY = colors.HexColor("#1A5F8A")
BRAND_LIGHT = colors.HexColor("#E8F4FB")
LIGHT_GRAY = colors.HexColor("#F3F6F9")
BORDER_GRAY = colors.HexColor("#D0D7DE")
MUTED = colors.HexColor("#5B6B7C")
WHITE = colors.white


class InspectionReportService:
    def __init__(self, inspection_service: InspectionService) -> None:
        self._inspections = inspection_service

    def build_pdf(self, organization_id: int, inspection_id: int) -> tuple[bytes, str]:
        inspection = self._inspections.get_inspection(organization_id, inspection_id)
        pdf_bytes = self._render(inspection)
        filename = self._filename(inspection)
        return pdf_bytes, filename

    def _filename(self, inspection: Inspection) -> str:
        slug = (inspection.registration or f"id-{inspection.id}").strip().replace(" ", "-")
        safe = "".join(ch for ch in slug if ch.isalnum() or ch in "-_")
        return f"inspection-report-{safe or inspection.id}.pdf"

    def _render(self, inspection: Inspection) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=22 * mm,
            bottomMargin=20 * mm,
            title=f"Physical Inspection Report #{inspection.id}",
            author="Aviation Inspection Cloud",
            subject=f"Aircraft {inspection.registration or inspection.id}",
        )
        styles = self._styles()
        story: list[Any] = []

        story.extend(self._cover(inspection, styles))
        story.append(Spacer(1, 2 * mm))
        story.append(
            HRFlowable(width="100%", thickness=0.8, color=BRAND_PRIMARY, spaceBefore=1 * mm, spaceAfter=2 * mm)
        )
        story.extend(self._component_serials(inspection, styles))
        story.extend(self._checklist(inspection, styles))
        story.extend(self._summary(inspection, styles))
        story.extend(self._discrepancies(inspection, styles))
        story.extend(self._signature(inspection, styles))

        registration = inspection.registration or f"ID-{inspection.id}"
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        def _on_page(canvas, doc_):
            self._draw_header_footer(canvas, doc_, registration, generated_at)

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
        return buffer.getvalue()

    def _draw_header_footer(self, canvas, doc, registration: str, generated_at: str) -> None:
        canvas.saveState()
        page_width, page_height = A4

        canvas.setFillColor(BRAND_NAVY)
        canvas.rect(0, page_height - 12 * mm, page_width, 12 * mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(16 * mm, page_height - 7.5 * mm, "AVIATION INSPECTION CLOUD")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(page_width - 16 * mm, page_height - 7.5 * mm, "Physical Inspection Report")

        canvas.setStrokeColor(BORDER_GRAY)
        canvas.setLineWidth(0.4)
        canvas.line(16 * mm, 12 * mm, page_width - 16 * mm, 12 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(16 * mm, 7 * mm, f"Confidential · {registration} · Generated {generated_at}")
        canvas.drawRightString(page_width - 16 * mm, 7 * mm, f"Page {doc.page}")
        canvas.restoreState()

    def _styles(self) -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "brand": ParagraphStyle(
                "Brand",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                textColor=BRAND_PRIMARY,
                spaceAfter=1 * mm,
            ),
            "title": ParagraphStyle(
                "ReportTitle",
                parent=base["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=18,
                textColor=BRAND_NAVY,
                spaceAfter=2 * mm,
                alignment=TA_LEFT,
            ),
            "subtitle": ParagraphStyle(
                "ReportSubtitle",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9,
                textColor=MUTED,
                spaceAfter=3 * mm,
            ),
            "section": ParagraphStyle(
                "SectionTitle",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                textColor=BRAND_NAVY,
                spaceBefore=5 * mm,
                spaceAfter=2 * mm,
            ),
            "subsection": ParagraphStyle(
                "SubsectionTitle",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                textColor=BRAND_PRIMARY,
                spaceBefore=3 * mm,
                spaceAfter=1.5 * mm,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=colors.black,
            ),
            "muted": ParagraphStyle(
                "Muted",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=8,
                textColor=MUTED,
            ),
            "badge": ParagraphStyle(
                "Badge",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=WHITE,
                alignment=TA_CENTER,
            ),
            "cell": ParagraphStyle(
                "Cell",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
            ),
            "cell_bold": ParagraphStyle(
                "CellBold",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=BRAND_NAVY,
            ),
            "meta_right": ParagraphStyle(
                "MetaRight",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=8,
                textColor=MUTED,
                alignment=TA_RIGHT,
            ),
        }

    def _cover(self, inspection: Inspection, styles: dict[str, ParagraphStyle]) -> list[Any]:
        status = (inspection.status or "draft").upper()
        status_color = colors.HexColor("#2E7D32") if status == "COMPLETED" else colors.HexColor("#ED6C02")

        badge = Table(
            [[Paragraph(status, styles["badge"])]],
            colWidths=[32 * mm],
        )
        badge.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), status_color),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        header = Table(
            [
                [
                    [
                        Paragraph("Aviation Inspection Cloud", styles["brand"]),
                        Paragraph("Physical Inspection Report", styles["title"]),
                        Paragraph(
                            f"Document No. PIR-{inspection.id:05d} · Official record",
                            styles["subtitle"],
                        ),
                    ],
                    badge,
                ]
            ],
            colWidths=[130 * mm, 35 * mm],
        )
        header.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT),
                    ("BOX", (0, 0), (-1, -1), 0.6, BRAND_PRIMARY),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        left_rows = [
            ["Registration", self._text(inspection.registration)],
            ["MSN", self._text(inspection.msn)],
            ["Aircraft model", self._text(inspection.aircraft_model)],
            ["Operator", self._text(inspection.operator)],
            ["Inspection date", self._date(inspection.inspection_date)],
            ["Revision", self._text(inspection.revision)],
            ["Configuration", self._text(inspection.configuration)],
        ]
        right_rows = [
            ["Total hours", self._text(inspection.total_hours)],
            ["Total cycles", self._text(inspection.total_cycles)],
            ["Location", self._text(inspection.location)],
            ["Facilities", self._text(inspection.facilities)],
            ["Performed by", self._text(inspection.performed_by)],
            ["Fuel on board (kg)", self._text(inspection.fuel_on_board_kg)],
            ["Measurement system", self._text(inspection.measurement_system)],
            ["Pictures available", self._text(inspection.pictures_available)],
        ]

        story: list[Any] = [
            header,
            Spacer(1, 4 * mm),
            Paragraph("Aircraft & inspection identification", styles["section"]),
            self._two_column_kv(left_rows, right_rows, styles),
        ]
        return story

    def _two_column_kv(
        self,
        left_rows: list[list[str]],
        right_rows: list[list[str]],
        styles: dict[str, ParagraphStyle],
    ) -> Table:
        max_len = max(len(left_rows), len(right_rows))
        data: list[list[Any]] = []
        for index in range(max_len):
            left = left_rows[index] if index < len(left_rows) else ["", ""]
            right = right_rows[index] if index < len(right_rows) else ["", ""]
            data.append(
                [
                    Paragraph(self._escape(left[0]), styles["cell_bold"]),
                    Paragraph(self._escape(left[1]), styles["cell"]),
                    Paragraph(self._escape(right[0]), styles["cell_bold"]),
                    Paragraph(self._escape(right[1]), styles["cell"]),
                ]
            )
        table = Table(data, colWidths=[35 * mm, 47 * mm, 38 * mm, 45 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
                    ("BACKGROUND", (2, 0), (2, -1), LIGHT_GRAY),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER_GRAY),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return table

    def _component_serials(
        self, inspection: Inspection, styles: dict[str, ParagraphStyle]
    ) -> list[Any]:
        story: list[Any] = [Paragraph("1. Component serial numbers", styles["section"])]
        serials = list(inspection.component_serials or [])
        if not serials:
            story.append(Paragraph("No component serial numbers recorded.", styles["muted"]))
            return story

        data = [
            [
                Paragraph("Component", styles["cell_bold"]),
                Paragraph("S/N Records", styles["cell_bold"]),
                Paragraph("S/N Installed", styles["cell_bold"]),
            ]
        ]
        for item in serials:
            data.append(
                [
                    Paragraph(self._escape(item.component_type), styles["cell"]),
                    Paragraph(self._escape(self._text(item.received_sn)), styles["cell"]),
                    Paragraph(self._escape(self._text(item.installed_sn)), styles["cell"]),
                ]
            )
        story.append(self._data_table(data, [45 * mm, 60 * mm, 60 * mm]))
        return story

    def _checklist(self, inspection: Inspection, styles: dict[str, ParagraphStyle]) -> list[Any]:
        story: list[Any] = [Paragraph("2. Checklist findings", styles["section"])]
        items = list(inspection.checklist_items or [])
        if not items:
            story.append(Paragraph("No checklist items recorded.", styles["muted"]))
            return story

        grouped: dict[tuple[str, str], list] = defaultdict(list)
        for item in items:
            grouped[(item.chapter or "", item.section or "")].append(item)

        for (chapter, section), section_items in sorted(
            grouped.items(), key=lambda pair: (pair[0][0], pair[0][1])
        ):
            heading = f"Chapter {chapter} — {section}" if chapter else section
            block: list[Any] = [Paragraph(self._escape(heading), styles["subsection"])]
            data = [
                [
                    Paragraph("Item", styles["cell_bold"]),
                    Paragraph("Status", styles["cell_bold"]),
                    Paragraph("Comments", styles["cell_bold"]),
                ]
            ]
            for item in section_items:
                data.append(
                    [
                        Paragraph(self._escape(item.item_label or item.item_key), styles["cell"]),
                        Paragraph(self._escape(self._status_label(item.status)), styles["cell"]),
                        Paragraph(self._escape(self._text(item.comments)), styles["cell"]),
                    ]
                )
            block.append(self._data_table(data, [90 * mm, 22 * mm, 53 * mm]))
            story.append(KeepTogether(block))
        return story

    def _summary(self, inspection: Inspection, styles: dict[str, ParagraphStyle]) -> list[Any]:
        story: list[Any] = [Paragraph("3. Summary & ratings", styles["section"])]
        story.append(
            self._kv_table(
                [["Overall aircraft rating", self._text(inspection.overall_rating)]],
                styles,
            )
        )
        story.append(Spacer(1, 2 * mm))

        ratings = self._parse_chapter_ratings(inspection.chapter_ratings)
        if ratings:
            story.append(Paragraph("Section ratings", styles["subsection"]))
            data = [
                [
                    Paragraph("Section", styles["cell_bold"]),
                    Paragraph("Rating", styles["cell_bold"]),
                ]
            ]
            for key, value in ratings.items():
                data.append(
                    [
                        Paragraph(self._escape(str(key)), styles["cell"]),
                        Paragraph(self._escape(self._text(value)), styles["cell"]),
                    ]
                )
            story.append(self._data_table(data, [110 * mm, 55 * mm]))
        else:
            story.append(Paragraph("No section ratings recorded.", styles["muted"]))

        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("General comments", styles["subsection"]))
        comments = self._text(inspection.summary_comments)
        story.append(Paragraph(self._escape(comments), styles["body"]))
        return story

    def _discrepancies(
        self, inspection: Inspection, styles: dict[str, ParagraphStyle]
    ) -> list[Any]:
        story: list[Any] = [Paragraph("4. Discrepancy register", styles["section"])]
        discrepancies = sorted(
            list(inspection.discrepancies or []),
            key=lambda item: item.item_number or 0,
        )
        if not discrepancies:
            story.append(Paragraph("No discrepancies recorded.", styles["muted"]))
            return story

        data = [
            [
                Paragraph("#", styles["cell_bold"]),
                Paragraph("Chapter", styles["cell_bold"]),
                Paragraph("Description", styles["cell_bold"]),
            ]
        ]
        for item in discrepancies:
            data.append(
                [
                    Paragraph(str(item.item_number), styles["cell"]),
                    Paragraph(self._escape(self._text(item.chapter)), styles["cell"]),
                    Paragraph(self._escape(self._text(item.description)), styles["cell"]),
                ]
            )
        story.append(self._data_table(data, [12 * mm, 45 * mm, 108 * mm]))
        return story

    def _signature(self, inspection: Inspection, styles: dict[str, ParagraphStyle]) -> list[Any]:
        story: list[Any] = [Paragraph("5. Authorization", styles["section"])]
        story.append(
            self._kv_table(
                [
                    ["Signed by", self._text(inspection.signed_by)],
                    ["Signature date", self._date(inspection.signed_date)],
                ],
                styles,
            )
        )
        story.append(Spacer(1, 8 * mm))
        story.append(
            Paragraph(
                "This document constitutes the official physical inspection report generated by Aviation Inspection Cloud.",
                styles["muted"],
            )
        )
        return story

    def _kv_table(self, rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
        data = [
            [
                Paragraph(self._escape(label), styles["cell_bold"]),
                Paragraph(self._escape(value), styles["cell"]),
            ]
            for label, value in rows
        ]
        table = Table(data, colWidths=[55 * mm, 110 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER_GRAY),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _data_table(self, data: list[list[Any]], col_widths: list[float]) -> Table:
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER_GRAY),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return table

    @staticmethod
    def _parse_chapter_ratings(raw: str | None) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return {}
        if isinstance(parsed, dict):
            return {str(k): v for k, v in parsed.items() if v not in (None, "")}
        return {}

    @staticmethod
    def _status_label(status: str | None) -> str:
        mapping = {"yes": "Yes", "no": "No", "na": "N/A"}
        if not status:
            return "—"
        return mapping.get(status.lower(), status)

    @staticmethod
    def _text(value: Any) -> str:
        if value is None or value == "":
            return "—"
        return str(value)

    @staticmethod
    def _date(value: Any) -> str:
        if not value:
            return "—"
        return value.isoformat() if hasattr(value, "isoformat") else str(value)

    @staticmethod
    def _escape(value: str) -> str:
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
