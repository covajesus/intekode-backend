"""Domain enumerations — shared vocabulary across layers."""

from enum import StrEnum


class InspectionStatus(StrEnum):
    DRAFT = "draft"
    COMPLETED = "completed"


class ChecklistStatus(StrEnum):
    YES = "yes"
    NO = "no"
    NOT_APPLICABLE = "na"


class AircraftConfiguration(StrEnum):
    PASSENGER = "Passenger"
    FREIGHTER = "Freighter"


class MeasurementSystem(StrEnum):
    METRIC = "Metric"
    IMPERIAL = "Imperial"


class OrganizationRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"
