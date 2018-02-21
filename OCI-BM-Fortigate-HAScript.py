#!/usr/bin/python2.7
#title           :OCI-BM-Fortigate-HAScript.py
#description     :Fortigate Active/Passive HA worker node script.
#author          :Vikram Gogte
#email           :vgogte@fortinet.com
#date            :02/21/2018
#version         :0.1
#usage           :python2.7 OCI-BM-Fortigate-HAScript.py
#notes           :The script will monitor Active Fortigate and failover to Passive Fortigate
#                :when ping to Active Fortigate Eth0 Interface fail and vice versa.
#                :This script will run on worker node in OCI environment.
#                :
#                :
#python_version  :2.7
#==============================================================================
# Create DEFAULT config at ~/.oci/config. More documentation located at 
# https://docs.us-phoenix-1.oraclecloud.com/Content/API/Concepts/sdkconfig.htm
#   SAMPLE FILE
'''
[DEFAULT]
user=user_ocid
fingerprint=9f:de:ba:51:0d:99:c6:aa:fa:1e:8d:b3:ca:44:a8:32
key_file =~/.oci/oci_api_key.pem
tenancy =tenancy_ocid
region =oci_region
log_requests = True
pass_phrase=mysecretphrase
'''

# Import the modules needed to run the script.

import string
import time
import os
import oci

# Fill in the variable details
# Fortigate outside private IP OCIDs
Instance1_outside_private_ocid=""   
Instance2_outside_private_ocid=""
# Fortigate inside private IP OCIDs
Instance1_inside_private_ocid=""
Instance2_inside_private_ocid="" 
# Floating Public IP OCID (Reserved)  
Reserved_Public_IP_ocid=""
# Fortigate Instance Display names in OCI
Instance1="FGT-A"
Instance2="FGT-B"
# Fortigate Outside private IPs
Instance1_outside_private_ip=""
Instance2_outside_private_ip=""
# RouteTable for subnet with next-hop as Fortigate
# This script covers for only one subnet. If there are more subnets, please add RouteTable OCID 
# for each subnet and modify script to update the route table.
RouteTable_ocid=""


def oci_authenticate():

    config = oci.config.from_file("~/.oci/config", "DEFAULT")
    compute = oci.core.compute_client.ComputeClient(config)
    network = oci.core.virtual_network_client.VirtualNetworkClient(config)

    return compute,network

def oci_update_default_route(network,route_table_id, private):
	
	route_table_details = oci.core.models.UpdateRouteTableDetails()
	route_rules = []
	route_rules.append(oci.core.models.RouteRule(
		cidr_block='0.0.0.0/0',
		network_entity_id=private
		)
	)

	route_table_details.route_rules = route_rules

	ip_details = oci.core.models.UpdatePublicIpDetails()
	ip_details.private_ip_id = private

	try: 
		request = network.update_route_table(route_table_id, route_table_details).data
		print "Route table "+str(request.display_name)+" updated"

	except Exception as e: 
		print "Failed to update the route rule. Exception: {}".format(e)
		sys.exit(1)

def oci_update_public_ip(network,Instance_outside_private_ocid):
    
    public_ip_details = network.get_public_ip(Reserved_Public_IP_ocid).data
    #print public_ip_details
    public_ip_details=oci.core.models.UpdatePublicIpDetails()
    public_ip_details.private_ip_id=Instance_outside_private_ocid

    try: 
        request = network.update_public_ip(Reserved_Public_IP_ocid, public_ip_details)
        #public_ip_details = network.get_public_ip(Reserved_Public_IP_ocid).data
        #print public_ip_details

    except Exception as e: 
		print "Failed to update the public IP. Exception: {}".format(e)
		sys.exit(1)

# Function to check the status of Active Fortigate by performing pings.
def oci_ping_check(Active_Fortigate,Active_Fortigate_IP):

    response=os.system("ping -c 1 " + Active_Fortigate_IP +"> /dev/null")
    if response == 0:
        ping_status = "ok"
    else:
        ping_status = "error"

    return ping_status

def main():

    ''' Initiating the OCI Enviroment using the parameters.
    Call oci_authenticate() to authenticate with Oracle Cloud and set the
    Cookie for making REST API calls.
    '''
    compute,network=oci_authenticate()

    Active_Fortigate = Instance1
    Active_Fortigate_IP = Instance1_outside_private_ip

    TRUE = 1
    LOOP = 0
    error_count = 0
    while TRUE == 1:
        ping_status = oci_ping_check(Active_Fortigate,Active_Fortigate_IP)
        if ping_status=='ok':
            print "Ping Check to Fortigate {} Eth0 IP {} is good.".format(Active_Fortigate,Active_Fortigate_IP)
            time.sleep(0.5)
        else:
            error_count = error_count + 1

            print "Ping Check to Fortigate {} Eth0 IP {} are Failing.".format(Active_Fortigate,Active_Fortigate_IP)
            ''' If the ping fails for 5 times, then switch the Public IP and Route Admin Distance on inside.
            '''
            if error_count >= 2:

                print "Ping checks to Active Fortigate failed. Failover triggered. Initiating Failover to Passive Fortigate."
                if Active_Fortigate == Instance1:
                    ''' If the Active Fortigate is Instance1, failover to Instance2 and set it as Active Fortigate.
                    '''
                    ''' Update the public IP by changing the private IP to Instance2 private IP OCID
                    '''
                    oci_update_public_ip(network,Instance2_outside_private_ocid)

                    '''Update the default route in the Route table by changing the next-hop as 
                        inside private of Instance1. For every subnet make a oci_update_default_route call 
                        with respective routetable ocid.
                    '''

                    oci_update_default_route(network,RouteTable_ocid,Instance2_inside_private_ocid)
               
                    error_count = 0
                    Active_Fortigate = Instance2
                    Active_Fortigate_IP = Instance2_outside_private_ip
                    print "After Failover, {} is now the Active Fortigate.".format(Active_Fortigate)

                else:
                    ''' If the Active Fortigate is Instance2, failover to Instance1 and set it as Active Fortigate.
                    '''
                    ''' Update the public IP by changing the private IP to Instance1 private IP OCID
                    '''
                    oci_update_public_ip(network,Instance1_outside_private_ocid)
                    
                    ''' Update the default route in the Route table by changing the next-hop as 
                        inside private of Instance1. For every subnet make a oci_update_default_route call
                        with respective routetable ocid.
                    ''' 
                    oci_update_default_route(network,RouteTable_ocid,Instance1_inside_private_ocid)
               
                    error_count = 0
                    Active_Fortigate = Instance1
                    Active_Fortigate_IP = Instance1_outside_private_ip

                    print "After Failover, {} is now the Active Fortigate.".format(Active_Fortigate)
    
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()