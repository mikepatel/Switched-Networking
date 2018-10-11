#import re
#import json
import paramiko
import time
import sys

'''
Adjacent Node details:
1. hostname
2. local-interface number
3. local-interface vlan number
4. adjacent node's interface number
5. adjacent node's vlan number

'''

# read in list of ip addresses as argument
i=1
IPs = []
for arg in sys.argv:
	if i == 1:
		i = i + 1
		continue
	IPs.append(arg)

Nodes = {}
for remoteIP in IPs:
	#remoteIP = "169.254.231.151"
	username = "exam"
	password = "exam"
	handler = paramiko.SSHClient()
	handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		handler.connect(remoteIP, username=username, password=password, look_for_keys=False, allow_agent=False)
	except:
		print("\nInvalid IP given: " + remoteIP)
		continue
	#time.sleep(2)
	shell = handler.invoke_shell()
	#time.sleep(2)
	#output = shell.recv(65535)
	#print(output)
	shell.send("terminal length 0\n") #forces terminal to print everything; no space needed
	time.sleep(5)
	shell.send("show cdp neighbors detail\n")
	time.sleep(5)
	output = shell.recv(65535)
	#print(output)

	output = output.decode("utf-8")
	#print(output)

	Neighbors = {}
	i = 1
	neighbor_name = ""

	for neighbor in output.split("-------------------------\r\n"):
		for item2 in neighbor.split("\r\n"):
			if "Device ID" in item2:
				neighbor_name = "Neighbor " + str(i) + ": " + item2.split(": ")[1]
				Neighbors[neighbor_name] = {}
				i=i+1
			if "Interface: " in item2:
				Neighbors[neighbor_name]["Local Node Interface"] = item2.split("Interface: ")[1].split(",  Port ID (outgoing port): ")[0]
				Neighbors[neighbor_name]["Adjacent Node Interface"] = item2.split("Interface: ")[1].split(",  Port ID (outgoing port): ")[1]
			if "Native VLAN: " in item2:
				Neighbors[neighbor_name]["Local VLAN"] = item2.split("Native VLAN: ")[1]
				Neighbors[neighbor_name]["Adjacent VLAN"] = item2.split("Native VLAN: ")[1]			

	Nodes[remoteIP] = Neighbors
	# find hostname
	
#
print("\n#######################")
print(Nodes)
print("#######################")