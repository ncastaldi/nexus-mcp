# verify-disabled-accounts.ps1
# Returns the total number of disabled user accounts in Active Directory.

[CmdletBinding()]
param()

try {
    $disabled = Get-ADUser -Filter { Enabled -eq $false } -ErrorAction Stop
    $count = @($disabled).Count
    Write-Output "Disabled accounts: $count"
}
catch {
    Write-Error "Failed to query Active Directory: $_"
    exit 1
}
