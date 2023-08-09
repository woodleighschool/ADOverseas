from ldap3 import Server, Connection, ALL

# AD Configuration
AD_SERVER = '192.168.1.34'
AD_USERNAME = 'service_account@woodleigh.vic.edu.au'
AD_PASSWORD = '12345678abc!'
DOMAIN_BASE = 'DC=woodleigh,DC=vic,DC=edu,DC=au'


def connect_to_ad():
    server = Server(AD_SERVER, get_info=ALL)
    conn = Connection(server, user=AD_USERNAME,
                      password=AD_PASSWORD, auto_bind=True)
    return conn


def edit_ad_user(user_identifier, action):
    conn = connect_to_ad()

    # Search for the user using their email
    conn.search(search_base=DOMAIN_BASE,
                search_filter=f'(sAMAccountName={user_identifier})',
                attributes=['cn'])

    if not conn.entries:
        print(f"Username '{user_identifier}' not found.")
        return

    user_dn = conn.entries[0].entry_dn

    if action == "away":
        # add user to overseas access group
        conn.extend.microsoft.add_members_to_groups(
            user_dn, f'CN=Allow Overseas Access,OU=Groups,{DOMAIN_BASE}')
        # remove user from group that disables overseas access
        conn.extend.microsoft.remove_members_from_groups(
            user_dn, f'CN=Disable Overseas Access,OU=Groups,{DOMAIN_BASE}')
    elif action == "home":
        # add user to group that disables overseas access
        conn.extend.microsoft.remove_members_from_groups(
            user_dn, f'CN=Allow Overseas Access,OU=Groups,{DOMAIN_BASE}')
        # remove user from overseas access group
        conn.extend.microsoft.add_members_to_groups(
            user_dn, f'CN=Disable Overseas Access,OU=Groups,{DOMAIN_BASE}')

    conn.unbind()
