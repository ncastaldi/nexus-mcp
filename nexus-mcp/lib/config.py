"""Centralised config — loaded from environment / .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (nexus-mcp/)
load_dotenv(Path(__file__).parent.parent / ".env")


class ADConfig:
    server: str = os.getenv("AD_SERVER", "")
    port: int = int(os.getenv("AD_PORT", "389"))
    base_dn: str = os.getenv("AD_BASE_DN", "")
    user: str = os.getenv("AD_USER", "")
    password: str = os.getenv("AD_PASSWORD", "")
    use_ssl: bool = os.getenv("AD_USE_SSL", "false").lower() == "true"


class EntraConfig:
    tenant_id: str = os.getenv("ENTRA_TENANT_ID", "")
    client_id: str = os.getenv("ENTRA_CLIENT_ID", "")
    client_secret: str = os.getenv("ENTRA_CLIENT_SECRET", "")


class IntuneConfig:
    tenant_id: str = os.getenv("INTUNE_TENANT_ID") or os.getenv("ENTRA_TENANT_ID", "")
    client_id: str = os.getenv("INTUNE_CLIENT_ID") or os.getenv("ENTRA_CLIENT_ID", "")
    client_secret: str = os.getenv("INTUNE_CLIENT_SECRET") or os.getenv("ENTRA_CLIENT_SECRET", "")


class WorkdayConfig:
    base_url: str = os.getenv("WORKDAY_BASE_URL", "")
    tenant: str = os.getenv("WORKDAY_TENANT", "")
    client_id: str = os.getenv("WORKDAY_CLIENT_ID", "")
    client_secret: str = os.getenv("WORKDAY_CLIENT_SECRET", "")
    refresh_token: str = os.getenv("WORKDAY_REFRESH_TOKEN", "")


class HelixConfig:
    base_url: str = os.getenv("HELIX_BASE_URL", "")
    username: str = os.getenv("HELIX_USERNAME", "")
    password: str = os.getenv("HELIX_PASSWORD", "")


class LansweeperConfig:
    api_url: str = os.getenv("LANSWEEPER_API_URL", "https://api.lansweeper.com/api/v2/graphql")
    application_id: str = os.getenv("LANSWEEPER_APPLICATION_ID", "")
    application_secret: str = os.getenv("LANSWEEPER_APPLICATION_SECRET", "")
    site_id: str = os.getenv("LANSWEEPER_SITE_ID", "")


class FedExConfig:
    api_url: str = os.getenv("FEDEX_API_URL", "https://apis.fedex.com")
    api_key: str = os.getenv("FEDEX_API_KEY", "")
    api_secret: str = os.getenv("FEDEX_API_SECRET", "")
    account_number: str = os.getenv("FEDEX_ACCOUNT_NUMBER", "")


class ReportConfig:
    output_dir: Path = Path(os.getenv("REPORT_OUTPUT_DIR", "./reports"))


class AuditConfig:
    """SOC 2 audit log configuration.

    Controls:
      CC7.2  — System Monitoring: log_file is the append-only audit trail.
      CC6.1  — Logical Access: log_to_stderr enables SIEM/syslog forwarding.
    """
    log_file: Path = Path(os.getenv("AUDIT_LOG_FILE", "./logs/nexus_audit.jsonl"))
    log_to_stderr: bool = os.getenv("AUDIT_LOG_STDERR", "true").lower() == "true"
    enabled: bool = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
