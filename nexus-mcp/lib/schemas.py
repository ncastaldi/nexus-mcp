"""Canonical data schemas for Nexus-MCP.

These pydantic models define normalized, system-agnostic representations
of domain objects (User, Device, Asset, Incident, etc.).

Every system adapter must transform its native API response into these
canonical formats, ensuring:
  • Type safety (str, int, bool validation)
  • Field normalization (e.g., email.lower())
  • Consistent field names across all systems
  • Clear validation errors when data is malformed

This pattern prevents fragile dict access and enables compile-time safety.
"""

from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal, Optional
from datetime import datetime
from enum import Enum


# ── User Identity Domain ──────────────────────────────────────────────────────

class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    DISABLED = "disabled"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class CanonicalUser(BaseModel):
    """Normalized user object across AD, Entra, and Workday.
    
    This is the "universal" user format. All system adapters must map
    their native response to this schema.
    """
    # Identity
    email: str = Field(description="Primary work email (normalized to lowercase)")
    employee_id: Optional[str] = Field(default=None, description="Employee ID from HR system")
    username: str = Field(description="Login username (sAMAccountName/UPN)")    
    
    # Profile
    display_name: str = Field(description="Full display name")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Organizational
    job_title: Optional[str] = None
    department: Optional[str] = None
    manager_email: Optional[str] = None
    office_location: Optional[str] = None
    
    # Status
    status: UserStatus = UserStatus.ACTIVE
    is_enabled: bool = True
    
    # Technical
    last_login: Optional[datetime] = None
    created_date: Optional[datetime] = None
    phone: Optional[str] = None
    
    # Source tracking
    source_system: Literal["ActiveDirectory", "Entra", "Workday"] = Field(
    description="System this data came from"
    )
    source_id: Optional[str] = Field(default=None, description="Native ID in source system")
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase for consistent comparison."""
        return v.lower().strip() if v else ""
    
    @field_validator('username')
    @classmethod
    def normalize_username(cls, v: Optional[str]) -> Optional[str]:
        """Normalize username to lowercase."""
        return v.lower().strip() if v else None

    model_config = ConfigDict(
        extra="forbid"  # Stops silent adapter drift
    )

# ── Device/Asset Domain ───────────────────────────────────────────────────────

class DeviceType(str, Enum):
    """Device categories."""
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    SERVER = "server"
    MOBILE = "mobile"
    TABLET = "tablet"
    VIRTUAL_MACHINE = "vm"
    UNKNOWN = "unknown"


class DeviceStatus(str, Enum):
    """Device operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"
    PENDING = "pending"


class CanonicalDevice(BaseModel):
    """Normalized device/asset object across Intune, Lansweeper, and Helix CMDB.
    
    Unified representation of physical/virtual compute assets.
    """
    # Identity
    hostname: str = Field(description="Device hostname/computer name")
    serial_number: Optional[str] = Field(default=None, description="Hardware serial number")
    asset_tag: Optional[str] = Field(default=None, description="Organization asset tag")
    
    # Classification
    device_type: DeviceType = DeviceType.UNKNOWN
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    
    # Assignment
    assigned_user_email: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    
    # Status
    status: DeviceStatus = DeviceStatus.ACTIVE
    is_compliant: Optional[bool] = None
    last_seen: Optional[datetime] = None
    enrollment_date: Optional[datetime] = None
    
    # Network
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    
    # Source tracking
    source_system: Literal["Intune", "Lansweeper", "Helix"] = Field(description="System this data came from")
    source_id: Optional[str] = Field(default=None, description="Native ID in source system")
    
    @field_validator('hostname')
    @classmethod
    def normalize_hostname(cls, v: str) -> str:
        """Normalize hostname to uppercase."""
        return v.upper().strip() if v else ""
    
    @field_validator('assigned_user_email')
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        """Normalize email to lowercase."""
        return v.lower().strip() if v else None
    
    @field_validator('serial_number', 'asset_tag')
    @classmethod
    def normalize_identifiers(cls, v: Optional[str]) -> Optional[str]:
        """Normalize serial/asset tag to uppercase."""
        return v.upper().strip() if v else None


# ── ITSM Domain ───────────────────────────────────────────────────────────────

class IncidentPriority(str, Enum):
    """Incident priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CanonicalIncident(BaseModel):
    """Normalized incident/ticket object from Helix ITSM.
    
    Represents service desk tickets and incidents.
    """
    # Identity
    incident_id: str = Field(description="Unique incident number (e.g., INC0001234)")
    
    # Content
    summary: str = Field(description="Short description/title")
    description: Optional[str] = Field(default=None, description="Full incident details")
    
    # Classification
    priority: IncidentPriority = IncidentPriority.MEDIUM
    status: IncidentStatus = IncidentStatus.NEW
    category: Optional[str] = None
    subcategory: Optional[str] = None
    
    # Assignment
    assigned_to: Optional[str] = None
    assigned_group: Optional[str] = None
    reported_by: Optional[str] = None
    
    # Timestamps
    created_date: datetime
    updated_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    
    # Source tracking
    source_system: Literal["helix"] = Field(description="System this data came from")
    source_id: Optional[str] = None


# ── Logistics Domain ──────────────────────────────────────────────────────────

class ShipmentStatus(str, Enum):
    """Package shipment status."""
    CREATED = "created"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
    CANCELLED = "cancelled"


class CanonicalShipment(BaseModel):
    """Normalized shipment object from FedEx API.
    
    Represents package tracking and delivery information.
    """
    # Identity
    tracking_number: str = Field(description="FedEx tracking number")
    
    # Status
    status: ShipmentStatus
    status_description: Optional[str] = None
    
    # Routing
    origin_city: Optional[str] = None
    origin_state: Optional[str] = None
    destination_city: Optional[str] = None
    destination_state: Optional[str] = None
    
    # Recipient
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None
    
    # Timestamps
    ship_date: Optional[datetime] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    
    # Package details
    weight_lbs: Optional[float] = None
    service_type: Optional[str] = None
    
    # Source tracking
    source_system: Literal["fedex"] = Field(description="System this data came from")
    source_id: Optional[str] = None


# ── Audit/Drift Domain ────────────────────────────────────────────────────────

class DriftType(str, Enum):
    """Types of cross-system discrepancies."""
    FIELD_MISMATCH = "field_mismatch"
    MISSING_IN_SYSTEM = "missing_in_system"
    STATUS_CONFLICT = "status_conflict"
    STALE_DATA = "stale_data"


class FieldDrift(BaseModel):
    """Represents a single field mismatch between two systems.
    
    Used by audit tools to report cross-system inconsistencies.
    """
    drift_type: DriftType = DriftType.FIELD_MISMATCH
    field_name: str = Field(description="Canonical field name (e.g., 'job_title')")
    
    # Source A
    system_a: str = Field(description="First system (e.g., 'Workday')")
    value_a: Optional[str] = Field(default=None, description="Value in system A")
    
    # Source B
    system_b: str = Field(description="Second system (e.g., 'Active Directory')")
    value_b: Optional[str] = Field(default=None, description="Value in system B")
    
    # Metadata
    severity: str = Field(default="medium", description="Impact level: low/medium/high")
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class UserDriftReport(BaseModel):
    """Aggregated drift report for a single user across all systems.
    
    Returned by audit_user_drift() tool.
    """
    email: str
    systems_checked: list[str]
    
    # System presence
    workday_found: bool
    ad_found: bool
    entra_found: bool
    
    # Drift summary
    discrepancy_count: int
    discrepancies: list[FieldDrift]
    
    # Timestamp
    audit_date: datetime = Field(default_factory=datetime.utcnow)
