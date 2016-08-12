# 
# Connect to a resource in a CloudShell reservation, 
#
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucseventhandler import UcsEventHandle
from ucsmsdk.mometa.ls.LsServer import LsServerConsts

# Define the service profile, and the blade to attach it to - if you don't
# want to hard code these, you can also pass them in as parameters to th driver
sp_dn ="org-root/ls-cloud"
Server_DN = "sys/chassis-2/blade-1"

# Based on the samples from the UCSMSDK repository
def sp_associate(handle, sp_dn, server_dn, wait_for_assoc_completion=True,
                 assoc_completion_timeout=20*60):
    """
    Associates a service profile to server
    Args:
        handle (UcsHandle)
        sp_dn (string): dn of service profile
        server_dn (string): dn of blade or rack
        wait_for_assoc_completion (bool): by default True. if Set to False,
                                         it will not monitor the completion of
                                         association.
        assoc_completion_timeout (number): wait timeout in seconds
    Returns:
        None
    Raises:
        ValueError: If LsServer is not present Or
                    ComputeBlade or ComputeRack not present Or
                    Service profile is already associated Or
    Example:
        sp_associate(handle, sp_dn="org-root/ls-chassis1-blade1",
                    server_dn="sys/chassis-1/blade-1")
    """
    from ucsmsdk.mometa.ls.LsBinding import LsBinding
    # check if sp exists
    sp = handle.query_dn(sp_dn)
    if sp is None:
        raise ValueError("Service profile '%s' does not exist." % sp_dn)
    # check if dn exists
    blade = handle.query_dn(server_dn)
    if blade is None:
        raise ValueError("Server '%s' does not exist." % server_dn)
    # check if sp is already associated with blade
    if sp.assoc_state == LsServerConsts.ASSOC_STATE_ASSOCIATED \
            and sp.pn_dn == server_dn:
        raise ValueError("Service Profile is already associated with Server %s"
                         "" % server_dn)
    # check if sp already has lsBinding with blade
    binding = handle.query_dn(sp_dn + "/pn")
    if binding is not None and binding.pn_dn == server_dn:
        raise ValueError("Service Profile is already administratively "
                         "associated with Server %s" % server_dn)
    mo = LsBinding(parent_mo_or_dn=sp_dn, pn_dn=server_dn,
                   restrict_migration="no")
    handle.add_mo(mo, modify_present=True)
    handle.commit()

if __name__ == "__main__":
    # connect to reservation
    # Replace:
    # 'username' with the name of the user who owns the reservation
    # 'password' with that user's password
    # 'domain' with the domain of the reservation
    # 'reservation_id' with the uuid of the reservation
    # 'server_address' with your cloudshell server 
    # 'resource_name' with the resource name (not hostname) of your UCS chassis
    dev_helpers.attach_to_cloudshell_as('username', 'password', 'domain', 'reservation_id', server_address='server_address', cloudshell_api_port='8029', resource_name='resource_name')

    # Populate resource, session, and connection so that we can use them later
    resource = helpers.get_resource_context_details()
    session = helpers.get_api_session()
    connection = helpers.get_connectivity_context_details()

    # Connect to the UCS chassis/emulator
    handle = UcsHandle(resource.address, resource.attributes['User'], resource.attributes['Password'])
    handle.login()

    sp_associate(handle, sp_dn, Server_DN)

    print handle.query_dn("org-root/ls-cloud/pn")
    print "Disconnecting."
    handle.logout()
    print "Command completed."
