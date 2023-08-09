from ldap3 import Server, Connection, ALL
from snippies import db
import os

# AD Configuration
AD_SERVER = 'WDC01.woodleighschool.net'
AD_USERNAME = os.getenv("ADUSERNAME")
AD_PASSWORD = os.getenv("ADPASSWORD")
DOMAIN_BASE = 'DC=woodleighschool,DC=net'


def connect_to_ad():
    server = Server(AD_SERVER, get_info=ALL, use_ssl=True)
    conn = Connection(server, user=AD_USERNAME,
                      password=AD_PASSWORD, auto_bind=True)
    return conn


def edit_ad_user(user_identifier, action, db_row):
    conn = connect_to_ad()

    # Search for the user using their email
    conn.search(search_base=DOMAIN_BASE,
                search_filter=f'(sAMAccountName={user_identifier})',
                attributes=['cn', 'department'])

    if not conn.entries:
        print(f"Username '{user_identifier}' not found.")
        return

    user_dn = conn.entries[0].entry_dn
    user_department = conn.entries[0].department

    if action == "away":
        # add user to overseas access group
        conn.extend.microsoft.add_members_to_groups(
            user_dn, f'CN=Azure - Allow access when overseas (Travelling Users),OU=Office 365 and Azure AD,{DOMAIN_BASE}')
        # remove user from group that disables overseas access
        conn.extend.microsoft.remove_members_from_groups(
            user_dn, f'CN=Azure - Block Access to O365 if not in Australia,OU=Office 365 and Azure AD,{DOMAIN_BASE}')
        # add user to 2fa group
        conn.extend.microsoft.add_members_to_groups(
            user_dn, f'CN=Enable Office 365 MFA,OU=Office 365 and Azure AD,{DOMAIN_BASE}')
    elif action == "home":
        # add user to group that disables overseas access
        conn.extend.microsoft.add_members_to_groups(
            user_dn, f'CN=Azure - Block Access to O365 if not in Australia,OU=Office 365 and Azure AD,{DOMAIN_BASE}')
        # remove user from overseas access group
        conn.extend.microsoft.remove_members_from_groups(
            user_dn, f'CN=Azure - Allow access when overseas (Travelling Users),OU=Office 365 and Azure AD,{DOMAIN_BASE}')
        if user_department != "Staff":
            # remove students from 2fa group
            conn.extend.microsoft.remove_members_from_groups(
                user_dn, f'CN=Enable Office 365 MFA,OU=Office 365 and Azure AD,{DOMAIN_BASE}')

    conn.unbind()
    db.delete_record(db_row)
