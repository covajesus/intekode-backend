"""Static inspection template provider — Factory for checklist metadata."""

from app.application.dto.inspection import InspectionTemplateDTO
from app.resources.checklist_template import (
    CHAPTER_RATINGS,
    CHECKLIST_TEMPLATE,
    DEFAULT_COMPONENTS,
    OVERALL_RATINGS,
    SECTION_RATINGS,
)


class InspectionTemplateFactory:
    @staticmethod
    def build() -> InspectionTemplateDTO:
        return InspectionTemplateDTO(
            checklist=CHECKLIST_TEMPLATE,
            default_components=DEFAULT_COMPONENTS,
            chapter_ratings=CHAPTER_RATINGS,
            overall_ratings=OVERALL_RATINGS,
            section_ratings=SECTION_RATINGS,
        )
