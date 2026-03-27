import asyncio
import sys
sys.path.insert(0, '.')

from ad_adapter import ActiveDirectoryIdentityBackend

async def main():
    backend = ActiveDirectoryIdentityBackend()
    
    # Manually call the low-level PowerShell method to see raw output
    command = """
        $filter = "Enabled -eq $False"
        $users = @(Get-ADUser -Filter $filter -Properties DisplayName, SamAccountName, Enabled -ErrorAction Stop)
        
        $debug_before_sort = @{
            count_before = $users.Count
            has_user_before = ($null -ne $users[0])
        }
        
        if ($users.Count -gt 0) {
            $debug_before_sort.sam_before = $users[0].SamAccountName
        }
        
        $users = $users | Sort-Object SamAccountName
        $users = @($users)
        
        $debug_after_sort = @{
            count_after = $users.Count
            has_user_after = ($null -ne $users[0])
        }
        
        if ($users.Count -gt 0) {
            $debug_after_sort.sam_after = $users[0].SamAccountName
        }
        
        @{
            before_sort = $debug_before_sort
            after_sort = $debug_after_sort
        } | ConvertTo-Json -Compress -Depth 3
    """
    
    result = await backend._run_powershell(command, {"test": "debug"})
    
    print("=== PowerShell Result ===")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    print(f"Data length: {len(result['data']) if result['data'] else 0}")
    print("=== Raw Data ===")
    print(result['data'])

asyncio.run(main())
