[Synopsis]

OCI Fortigate HA script is an automation for Fortigate Active/Passive design. 
The script will monitor the active Fortigate and will fail to Passive Fortigate when trigger condition is met.
During the failover, Public IP (Floating) is moved from Active Fortigate to Passive Fortigate. Also, 
routes in IPnetworks (trust or inside) adminDistance is changed such that they follow the Active Fortigate. 
This assures that traffic both directions inbound and outbound flows through the same Firewall.


[Pre-requisites]

-The script should be run on worker node in OCI environment. Worker node will linux instance (eg. ubuntu) and python2.7 installed. Also, python libraries listed should be installed.
-From the worker node, OCI environment needs to be reachable and also Fortigate Eth0 interfaces need to be reachable. 
-Fortigates will have Floating Public IP (Reserved) between the instances. So while deploying Fortigates "Public IP" select as none in OCI.
-Create a PublicIP in OCI  IPReservation. Active Fortigate Eth0 should be assigned the Floating Public IP.. 

[Example]

		    Floating Public IP             <<--- IPReservation in shared Network
			        | 
	  ____________________________
     |                            |    
     |Eth0                        |Eth0
	 |                            |
----------                    ----------
Fortigate1                    Fortigate2
----------                    ----------
     |                            |
	 |Eth1                        |Eth1
	 |                            |          
     ------------------------------
	                |
	 
	           Server Subnet
     
Server Subnet RouteTable will point to Fortigate which is Active meaning which has public IP attached to it. When the public IP swiches, the RouteTable will switch to other Fortigate as well.


***The script will work for the setup as described above. The script should be consumed as reference automation which would work in environment mentioned in the documentation and should not be considered as a product. 
***

[OCI Environment Parameter Requirements]

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


 

  
 