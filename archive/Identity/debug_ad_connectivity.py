"""
Debug script to diagnose AD connectivity and find the correct username.
"""
import asyncio
import logging
import sys
from ad_adapter import ActiveDirectoryIdentityBackend

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

async def diagnose():
    backend = ActiveDirectoryIdentityBackend(
        username='cnathan',
        password='*********',
        timeout_seconds=30.0
    )
    
    print('=' * 60)
    print('ACTIVE DIRECTORY CONNECTIVITY DIAGNOSTICS')
    print('=' * 60)
    print()
    
    # Test 1: Basic connectivity - Get domain info
    print('📡 Test 1: Verifying AD connectivity...')
    domain_result = await backend._run_powershell(
        'Get-ADDomain | Select-Object DNSRoot,NetBIOSName | ConvertTo-Json -Compress'
    )
    if domain_result.get('success'):
        print(f'✅ Connected to domain: {domain_result["data"]}')
    else:
        print(f'❌ Domain connection failed: {domain_result.get("error")[:200]}')
        print('\n⚠️  Cannot proceed - AD not reachable or credentials invalid')
        return
    
    print()
    
    # Test 2: Get the authenticated user's info
    print('👤 Test 2: Identifying authenticated user...')
    whoami_result = await backend._run_powershell(
        'Get-ADUser -Identity $env:USERNAME -Properties samAccountName,DisplayName,mail | Select-Object samAccountName,DisplayName,mail | ConvertTo-Json -Compress'
    )
    if whoami_result.get('success'):
        print(f'✅ Your AD identity: {whoami_result["data"]}')
    else:
        print(f'⚠️  Could not resolve $env:USERNAME: {whoami_result.get("error")[:200]}')
    
    print()
    
    # Test 3: List some users to verify queries work
    print('📋 Test 3: Listing sample users (first 5)...')
    sample_result = await backend._run_powershell(
        'Get-ADUser -Filter * -Properties samAccountName | Select-Object -First 5 samAccountName | ConvertTo-Json -Compress'
    )
    if sample_result.get('success'):
        print(f'✅ Sample users found: {sample_result["data"]}')
    else:
        print(f'❌ Query failed: {sample_result.get("error")[:200]}')
    
    print()
    
    # Test 4: Search for users with partial name match (fixed syntax)
    print('🔍 Test 4: Searching for users matching "nathan"...')
    search_result = await backend._run_powershell(
        'Get-ADUser -Filter {samAccountName -like "*nathan*"} -Properties samAccountName,DisplayName | Select-Object samAccountName,DisplayName | ConvertTo-Json -Compress'
    )
    if search_result.get('success'):
        if search_result['data']:
            print(f'✅ Found matches: {search_result["data"]}')
        else:
            print('⚠️  No users found matching "*nathan*"')
    else:
        print(f'❌ Search failed: {search_result.get("error")[:200]}')
    
    print()
    
    # Test 5: Try common username variations
    print('🔍 Test 5: Testing common username variations...')
    variations = ['castn1', 'cnathan', 'nathan', 'cory.nathan', 'nathan.cory']
    for username in variations:
        result = await backend.get_user(username)
        status = '✅ FOUND' if result else '❌ Not found'
        print(f'  {status}: {username}')
    
    print()
    print('=' * 60)
    print('RECOMMENDATION:')
    print('If Test 1 passed but no users found, your account may not have')
    print('permission to read AD users. Check with your AD admin.')
    print('=' * 60)

if __name__ == '__main__':
    try:
        asyncio.run(diagnose())
    except KeyboardInterrupt:
        print('\n\n⚠️  Interrupted by user')
        sys.exit(1)
    except Exception as e:
        print(f'\n\n❌ Fatal error: {e}')
        sys.exit(1)
