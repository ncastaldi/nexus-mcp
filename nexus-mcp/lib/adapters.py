"""System adapters for transforming native API responses into canonical schemas.

Each adapter class knows how to:
  1. Parse the system-specific response format
  2. Extract relevant fields using system-specific field names
  3. Transform into the canonical pydantic model
  4. Handle missing/null values gracefully

This isolates format complexity to adapter layer, keeping business logic clean.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Any
from schemas import (
    CanonicalUser, UserStatus,
    CanonicalDevice, DeviceType, DeviceStatus,
    CanonicalIncident, IncidentPriority, IncidentStatus,
    CanonicalShipment, ShipmentStatus,
)


# ── Helper Functions ──────────────────────────────────────────────────────────

def _get(data: dict | None, *keys: str, default: Any = None) -> Any:
    """Safely navigate nested dict paths. Returns default if any key is missing."""
    if data is None:
        return default
    
    obj = data
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key)
            if obj is None:
                return default
        else:
            return default
    return obj if obj is not None else default


def _parse_iso_date(value: str | None) -> Optional[datetime]:
    """Parse ISO 8601 datetime string. Returns None if parsing fails."""
    if not value:
        return None
    try:
        # Handle common formats: 2024-01-15T10:30:00Z or 2024-01-15T10:30:00.123Z
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        return datetime.fromisoformat(value)
    except (ValueError, AttributeError):
        return None


def _parse_timestamp(value: str | int | None) -> Optional[datetime]:
    """Parse Windows AD timestamp (e.g., 132876543210000000) to datetime."""
    if not value:
        return None
    try:
        # AD timestamps are 100-nanosecond intervals since 1601-01-01
        if isinstance(value, str) and len(value) > 10:
            timestamp_int = int(value)
            windows_epoch = datetime(1601, 1, 1)
            return windows_epoch + timedelta(microseconds=timestamp_int / 10)
        return None
    except (ValueError, TypeError):
        return None


def _normalize_bool(value: Any) -> bool:
    """Normalize various boolean representations."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'active', 'enabled')
    if isinstance(value, int):
        return value != 0
    return False


# ── Active Directory Adapters ─────────────────────────────────────────────────

class ADUserAdapter:
    """Transform Active Directory user objects into CanonicalUser."""
    
    @staticmethod
    def to_canonical(ad_user: dict) -> CanonicalUser:
        """Convert AD LDAP user dict to canonical format.
        
        Example AD fields:
          sAMAccountName, displayName, mail, department, title, manager,
          employeeID, userAccountControl, lastLogonTimestamp, whenCreated
        """
        # Parse account status from userAccountControl (512=enabled, 514=disabled)
        uac_raw = _get(ad_user, "userAccountControl", "512")
        uac = str(uac_raw) if uac_raw else "512"
        
        # Check if disabled (514 or has bit 2 set)
        is_disabled = False
        try:
            uac_int = int(uac)
            is_disabled = uac == "514" or (uac_int & 2) != 0
        except (ValueError, TypeError):
            # If parsing fails, assume enabled
            is_disabled = False
        
        status = UserStatus.DISABLED if is_disabled else UserStatus.ACTIVE
        
        # Parse manager DN to email (extract cn= from DN string)
        manager_dn = _get(ad_user, "manager", "")
        manager_email = None
        if manager_dn and "cn=" in manager_dn.lower():
            # Extract CN from "CN=John Doe,OU=Users,DC=corp,DC=com"
            cn_part = manager_dn.split(',')[0].replace('CN=', '').replace('cn=', '')
            # This is a simplification; in reality we'd need to look up the manager's email
            manager_email = None  # Would require a separate AD lookup
        
        return CanonicalUser(
            email=_get(ad_user, "mail", default=""),
            employee_id=_get(ad_user, "employeeID"),
            username=_get(ad_user, "sAMAccountName"),
            display_name=_get(ad_user, "displayName", default="Unknown"),
            first_name=_get(ad_user, "givenName"),
            last_name=_get(ad_user, "sn"),
            job_title=_get(ad_user, "title"),
            department=_get(ad_user, "department"),
            manager_email=manager_email,
            office_location=_get(ad_user, "physicalDeliveryOfficeName"),
            status=status,
            is_enabled=not is_disabled,
            last_login=_parse_iso_date(_get(ad_user, "lastLogonTimestamp")),
            created_date=_parse_iso_date(_get(ad_user, "whenCreated")),
            phone=_get(ad_user, "telephoneNumber"),
            source_system="ActiveDirectory",
            source_id=_get(ad_user, "dn"),
        )


# ── Microsoft Entra ID Adapters ───────────────────────────────────────────────

class EntraUserAdapter:
    """Transform Entra ID (Azure AD) user objects into CanonicalUser."""
    
    @staticmethod
    def to_canonical(entra_user: dict) -> CanonicalUser:
        """Convert Entra Graph API user dict to canonical format.
        
        Example Entra fields:
          id, displayName, userPrincipalName, mail, jobTitle, department,
          accountEnabled, createdDateTime, signInActivity
        """
        # Parse status
        is_enabled = _get(entra_user, "accountEnabled", default=True)
        status = UserStatus.ACTIVE if is_enabled else UserStatus.DISABLED
        
        # Parse last sign-in from signInActivity object
        last_login = None
        sign_in_activity = _get(entra_user, "signInActivity", default={})
        if isinstance(sign_in_activity, dict):
            last_login = _parse_iso_date(_get(sign_in_activity, "lastSignInDateTime"))
        
        return CanonicalUser(
            email=_get(entra_user, "mail") or _get(entra_user, "userPrincipalName", default=""),
            employee_id=_get(entra_user, "employeeId"),
            username=_get(entra_user, "userPrincipalName"),
            display_name=_get(entra_user, "displayName", default="Unknown"),
            first_name=_get(entra_user, "givenName"),
            last_name=_get(entra_user, "surname"),
            job_title=_get(entra_user, "jobTitle"),
            department=_get(entra_user, "department"),
            manager_email=None,  # Would require separate Graph API call to /manager
            office_location=_get(entra_user, "officeLocation"),
            status=status,
            is_enabled=is_enabled,
            last_login=last_login,
            created_date=_parse_iso_date(_get(entra_user, "createdDateTime")),
            phone=_get(entra_user, "mobilePhone") or _get(entra_user, "businessPhones", 0),
            source_system="Entra",
            source_id=_get(entra_user, "id"),
        )


# ── Workday Adapters ──────────────────────────────────────────────────────────

class WorkdayWorkerAdapter:
    """Transform Workday HCM worker objects into CanonicalUser."""
    
    @staticmethod
    def to_canonical(wd_worker: dict) -> CanonicalUser:
        """Convert Workday API worker dict to canonical format.
        
        Example Workday structure:
          id, descriptor (full name), primaryWorkEmail, employeeID,
          primaryJob { jobProfile { descriptor }, businessUnit { descriptor } }
        """
        # Extract job details from nested primaryJob object
        primary_job = _get(wd_worker, "primaryJob", default={})
        job_title = _get(primary_job, "jobProfile", "descriptor")
        department = _get(primary_job, "businessUnit", "descriptor")
        manager_ref = _get(primary_job, "manager", default={})
        manager_email = _get(manager_ref, "primaryWorkEmail")
        
        # Workday status from employeeStatus field
        status_str = _get(wd_worker, "employeeStatus", default="Active")
        if "terminated" in status_str.lower():
            status = UserStatus.TERMINATED
        elif "inactive" in status_str.lower():
            status = UserStatus.DISABLED
        else:
            status = UserStatus.ACTIVE
        
        return CanonicalUser(
            email=_get(wd_worker, "primaryWorkEmail", default=""),
            employee_id=_get(wd_worker, "employeeID"),
            username=None,  # Workday doesn't have username concept
            display_name=_get(wd_worker, "descriptor", default="Unknown"),
            first_name=_get(wd_worker, "firstName"),
            last_name=_get(wd_worker, "lastName"),
            job_title=job_title,
            department=department,
            manager_email=manager_email,
            office_location=_get(wd_worker, "location", "descriptor"),
            status=status,
            is_enabled=status == UserStatus.ACTIVE,
            last_login=None,  # Workday doesn't track login times
            created_date=_parse_iso_date(_get(wd_worker, "hireDate")),
            phone=_get(wd_worker, "primaryWorkPhone"),
            source_system="Workday",
            source_id=_get(wd_worker, "id"),
        )


# ── Intune Adapters ───────────────────────────────────────────────────────────

class IntuneDeviceAdapter:
    """Transform Intune managed device objects into CanonicalDevice."""
    
    @staticmethod
    def to_canonical(intune_device: dict) -> CanonicalDevice:
        """Convert Intune Graph API device dict to canonical format.
        
        Example Intune fields:
          id, deviceName, serialNumber, operatingSystem, osVersion,
          manufacturer, model, complianceState, lastSyncDateTime,
          userPrincipalName, enrolledDateTime
        """
        # Map Intune device types
        os_name = _get(intune_device, "operatingSystem", "").lower()
        if "windows" in os_name:
            device_type = DeviceType.LAPTOP if "laptop" in os_name else DeviceType.DESKTOP
        elif "ios" in os_name or "iphone" in os_name:
            device_type = DeviceType.MOBILE
        elif "ipad" in os_name:
            device_type = DeviceType.TABLET
        else:
            device_type = DeviceType.UNKNOWN
        
        # Parse compliance
        compliance = _get(intune_device, "complianceState", "")
        is_compliant = compliance.lower() == "compliant"
        
        # Parse status
        is_managed = _get(intune_device, "managementState", "") == "managed"
        status = DeviceStatus.ACTIVE if is_managed else DeviceStatus.INACTIVE
        
        return CanonicalDevice(
            hostname=_get(intune_device, "deviceName", default="UNKNOWN"),
            serial_number=_get(intune_device, "serialNumber"),
            asset_tag=None,  # Intune doesn't have asset tags
            device_type=device_type,
            os_name=_get(intune_device, "operatingSystem"),
            os_version=_get(intune_device, "osVersion"),
            manufacturer=_get(intune_device, "manufacturer"),
            model=_get(intune_device, "model"),
            assigned_user_email=_get(intune_device, "userPrincipalName"),
            department=None,  # Would need to look up user's department
            location=None,
            status=status,
            is_compliant=is_compliant,
            last_seen=_parse_iso_date(_get(intune_device, "lastSyncDateTime")),
            enrollment_date=_parse_iso_date(_get(intune_device, "enrolledDateTime")),
            ip_address=None,  # Not available in Intune API
            mac_address=_get(intune_device, "wiFiMacAddress") or _get(intune_device, "ethernetMacAddress"),
            source_system="Intune",
            source_id=_get(intune_device, "id"),
        )


# ── Lansweeper Adapters ───────────────────────────────────────────────────────

class LansweeperAssetAdapter:
    """Transform Lansweeper asset objects into CanonicalDevice."""
    
    @staticmethod
    def to_canonical(ls_asset: dict) -> CanonicalDevice:
        """Convert Lansweeper GraphQL asset dict to canonical format.
        
        Example Lansweeper structure:
          assetBasicInfo { name, type, serialNumber, manufacturer, model },
          assetCustom { location, department },
          assetBasicInfo { lastSeen, firstSeen },
          networkAddress { ip, mac }
        """
        # Parse device type from Lansweeper type field
        ls_type = _get(ls_asset, "assetBasicInfo", "type", "").lower()
        if "server" in ls_type:
            device_type = DeviceType.SERVER
        elif "laptop" in ls_type or "notebook" in ls_type:
            device_type = DeviceType.LAPTOP
        elif "desktop" in ls_type or "workstation" in ls_type:
            device_type = DeviceType.DESKTOP
        elif "vm" in ls_type or "virtual" in ls_type:
            device_type = DeviceType.VIRTUAL_MACHINE
        else:
            device_type = DeviceType.UNKNOWN
        
        # Extract network info
        network = _get(ls_asset, "networkAddress", {})
        ip = _get(network, "ip") if isinstance(network, dict) else None
        mac = _get(network, "mac") if isinstance(network, dict) else None
        
        return CanonicalDevice(
            hostname=_get(ls_asset, "assetBasicInfo", "name", default="UNKNOWN"),
            serial_number=_get(ls_asset, "assetBasicInfo", "serialNumber"),
            asset_tag=_get(ls_asset, "assetCustom", "assetTag"),
            device_type=device_type,
            os_name=_get(ls_asset, "operatingSystem", "name"),
            os_version=_get(ls_asset, "operatingSystem", "version"),
            manufacturer=_get(ls_asset, "assetBasicInfo", "manufacturer"),
            model=_get(ls_asset, "assetBasicInfo", "model"),
            assigned_user_email=_get(ls_asset, "assetCustom", "assignedUser"),
            department=_get(ls_asset, "assetCustom", "department"),
            location=_get(ls_asset, "assetCustom", "location"),
            status=DeviceStatus.ACTIVE,  # Lansweeper tracks active assets
            is_compliant=None,  # Not tracked by Lansweeper
            last_seen=_parse_iso_date(_get(ls_asset, "assetBasicInfo", "lastSeen")),
            enrollment_date=_parse_iso_date(_get(ls_asset, "assetBasicInfo", "firstSeen")),
            ip_address=ip,
            mac_address=mac,
            source_system="Lansweeper",
            source_id=_get(ls_asset, "assetBasicInfo", "assetId"),
        )


# ── Export Convenience ────────────────────────────────────────────────────────

__all__ = [
    "ADUserAdapter",
    "EntraUserAdapter",
    "WorkdayWorkerAdapter",
    "IntuneDeviceAdapter",
    "LansweeperAssetAdapter",
]
