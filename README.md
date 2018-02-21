# OCI-BM-Solutions
OCI-BM-Fortigate-HAScript.py

[Synopsis]

OCI Fortigate HA script is an automation for Fortigate Active/Passive design. 
The script will monitor the active Fortigate and will fail to Passive Fortigate when trigger condition is met.
During the failover, Public IP (Floating) is moved from Active Fortigate to Passive Fortigate. Also, 
routetable for inside subnets changed to next-hop (trust or inside) such that they follow the Active Fortigate. 
This assures that traffic both directions inbound and outbound flows through the same Firewall.


