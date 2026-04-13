"""Centralised config — loaded from environment / .env file using pydantic-settings."""

from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ADConfig(BaseSettings):
    """Active Directory / LDAP configuration."""
    model_config = SettingsConfigDict(
        env_prefix="AD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    server: str = ""
    port: int = 389
    base_dn: str = ""
    user: str = ""
    password: str = ""
    use_ssl: bool = False


class EntraConfig(BaseSettings):
    """Microsoft Entra ID (Azure AD) configuration."""
    model_config = SettingsConfigDict(
        env_prefix="ENTRA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""


class IntuneConfig(BaseSettings):
    """Microsoft Intune configuration (falls back to Entra credentials)."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    intune_tenant_id: Optional[str] = Field(default=None, alias="INTUNE_TENANT_ID")
    intune_client_id: Optional[str] = Field(default=None, alias="INTUNE_CLIENT_ID")
    intune_client_secret: Optional[str] = Field(default=None, alias="INTUNE_CLIENT_SECRET")
    
    # Fallback to Entra credentials
    entra_tenant_id: Optional[str] = Field(default=None, alias="ENTRA_TENANT_ID")
    entra_client_id: Optional[str] = Field(default=None, alias="ENTRA_CLIENT_ID")
    entra_client_secret: Optional[str] = Field(default=None, alias="ENTRA_CLIENT_SECRET")
    
    @property
    def tenant_id(self) -> str:
        return self.intune_tenant_id or self.entra_tenant_id or ""
    
    @property
    def client_id(self) -> str:
        return self.intune_client_id or self.entra_client_id or ""
    
    @property
    def client_secret(self) -> str:
        return self.intune_client_secret or self.entra_client_secret or ""


class WorkdayConfig(BaseSettings):
    """Workday HCM API configuration."""
    model_config = SettingsConfigDict(
        env_prefix="WORKDAY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    base_url: str = ""
    tenant: str = ""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""


class HelixConfig(BaseSettings):
    """BMC Helix ITSM configuration."""
    model_config = SettingsConfigDict(
        env_prefix="HELIX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    base_url: str = ""
    username: str = ""
    password: str = ""


class LansweeperConfig(BaseSettings):
    """Lansweeper asset management API configuration."""
    model_config = SettingsConfigDict(
        env_prefix="LANSWEEPER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    api_url: str = "https://api.lansweeper.com/api/v2/graphql"
    application_id: str = ""
    application_secret: str = ""
    site_id: str = ""


class FedExConfig(BaseSettings):
    """FedEx shipping API configuration."""
    model_config = SettingsConfigDict(
        env_prefix="FEDEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    api_url: str = "https://apis.fedex.com"
    api_key: str = ""
    api_secret: str = ""
    account_number: str = ""


class ReportConfig(BaseSettings):
    """Report generation configuration."""
    model_config = SettingsConfigDict(
        env_prefix="REPORT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    output_dir: Path = Path("./reports")
    
    @field_validator("output_dir", mode="before")
    @classmethod
    def parse_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


class AuditConfig(BaseSettings):
    """SOC 2 audit log configuration.

    Controls:
      CC7.2  — System Monitoring: log_file is the append-only audit trail.
      CC6.1  — Logical Access: log_to_stderr enables SIEM/syslog forwarding.
    """
    model_config = SettingsConfigDict(
        env_prefix="AUDIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    log_file: Path = Field(default=Path("./logs/nexus_audit.jsonl"), alias="AUDIT_LOG_FILE")
    log_to_stderr: bool = Field(default=True, alias="AUDIT_LOG_STDERR")
    logging_enabled: bool = Field(default=True, alias="AUDIT_LOGGING_ENABLED")
    
    @field_validator("log_file", mode="before")
    @classmethod
    def parse_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    # Backwards compatibility alias
    @property
    def enabled(self) -> bool:
        return self.logging_enabled
