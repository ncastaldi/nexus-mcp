from typing import Literal
from schemas import CanonicalUser

IdentityConfidence = Literal["strong", "partial", "weak"]

def is_privileged_account(user: CanonicalUser) -> bool:
    """
    Determines whether this identity represents a privileged/admin account.

    Policy:
    - Privileged AD accounts live under OU=WheelsUsersPrivileged
    - These accounts are not expected to have mailboxes
    """
    return (
        user.source_system == "ActiveDirectory"
        and isinstance(user.source_id, str)
        and "OU=WheelsUsersPrivileged" in user.source_id
    )


def compute_identity_confidence(user: CanonicalUser) -> IdentityConfidence:
    """
    Derive confidence level for an identity, based on completeness
    and organizational policy.

    Confidence levels:
    - strong: complete for its account class
    - partial: usable but missing expected attributes
    - weak: insufficient signal for reliable identity use
    """

    privileged = is_privileged_account(user)

    missing = []

    # Always required
    if not user.username:
        missing.append("username")

    if not user.display_name:
        missing.append("display_name")

    # Email is required ONLY for non-privileged users
    if not privileged and not user.email:
        missing.append("email")

    if not missing:
        return "strong"

    if privileged:
        # Missing email alone is acceptable
        if missing == ["email"]:
            return "strong"
        if len(missing) <= 2:
            return "partial"
        return "weak"

    # Non-privileged users
    if len(missing) == 1:
        return "partial"

    return "weak"