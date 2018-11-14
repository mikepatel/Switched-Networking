import re
import json
import paramiko
import time
import sys
import networkx as nx
import os

# https://networkx.github.io/documentation/latest/_downloads/networkx_reference.pdf

'''
This comment is outdated as additions have been made to Adjacent Node details
Adjacent Node details:
1. hostname
2. local-interface number
3. local-interface vlan number
4. adjacent node's interface number
5. adjacent node's vlan number

'''

'''
TO DO:
# TO DO: read list of management IPs from text file instead of command line arguments
# check enable passwords on switches
# check ssh image
# check ssh configured
# show int trunk to get vlan info for interfaces
# prompt user for root per vlan

'''


# fn that takes in list of edge pairs, and
# returns a kruskal mst
def spanning_tree_from_edges(edges):
	graph = nx.Graph()

	for n1, n2 in edges:
		graph.add_edge(n1, n2)

	graph_edges = graph.edges()
	spanning_tree = nx.minimum_spanning_tree(graph)

	return spanning_tree, graph_edges


##
# read in list of ip addresses from file
ip_file = os.path.join(os.getcwd(), "577_ip_list.txt")
IPs = []
with open(ip_file, "r+") as f:
    for line in f:
        IPs.append(line.strip())


'''
# read in list of ip addresses as argument
i=1
IPs = []
for arg in sys.argv:
	if i == 1:
		i = i + 1
		continue
	IPs.append(arg)
'''


#print(root)


#print(IPs)

Nodes = {}
nodes_visited = {}
vlan_list = []

for remoteIP in IPs:
	#remoteIP = "169.254.231.151"
	username = "exam"
	password = "exam"
	handler = paramiko.SSHClient()
	handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		handler.connect(remoteIP, username=username, password=password, look_for_keys=False, allow_agent=False)
	except Exception as e:
		print("\nException: ", str(e))
		print("\nInvalid IP given: " + remoteIP)
		continue
	#time.sleep(2)
	shell = handler.invoke_shell()
	#time.sleep(2)
	#output = shell.recv(65535)
	#print(output)
	shell.send("terminal length 0\n")  # forces terminal to print everything; no space needed
	time.sleep(1)
	shell.send("show cdp neighbors detail\n")
	time.sleep(1)
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
				Neighbors[neighbor_name]["Name"] = item2.split(": ")[1]
				i=i+1
			if "Interface: " in item2:
				Neighbors[neighbor_name]["Local Node Interface"] = item2.split("Interface: ")[1].split(",  Port ID (outgoing port): ")[0]
				Neighbors[neighbor_name]["Adjacent Node Interface"] = item2.split("Interface: ")[1].split(",  Port ID (outgoing port): ")[1]

			'''
			if "Native VLAN: " in item2:
				Neighbors[neighbor_name]["Local VLAN"] = item2.split("Native VLAN: ")[1]
				Neighbors[neighbor_name]["Adjacent VLAN"] = item2.split("Native VLAN: ")[1]
			'''

			if "IP address: " in item2:
				Neighbors[neighbor_name]["Management IP"] = item2.split("IP address: ")[1]

	Nodes[remoteIP] = Neighbors


	shell.send("show int trunk\n")
	time.sleep(2)

	output = shell.recv(65535)
	output = output.decode("utf-8")
	##print("\n@@")
	#print(output)
	x = output.split("Vlans allowed on trunk")
	x = str(x[1])
	x = x.strip("\r\n").split("\r\n\r\nPort")
	x = str(x[0])
	x = x.split("\r\n")
	vlans = []
	for y in x:
		y = y.split("       ")
		vlans.append(y[1])

	vlan_list.append(vlans[0])

	for neighbor in Nodes[remoteIP]:
		Nodes[remoteIP][neighbor]["Local VLAN"] = vlans[0]
		Nodes[remoteIP][neighbor]["Adjacent VLAN"] = vlans[0]


	
#####
#print("\n@@")
vlan_list = vlan_list[0]
vlan_list = str(vlan_list).split(",")
#print(vlan_list)

root_IPs = {}
for v in vlan_list:
	print("\n##################################################################")
	print("\n##################################################################")
	print("\n##################################################################")
	print("\nList of nodes by IP address: ", IPs)
	row = {}
	copy_IPs = []
	for i in IPs:
		copy_IPs.append(i)

	#print(copy_IPs)

	x = "\nFor vlan " + str(v) + ", specify root node by IP address: "
	root = input(x)

	row["ip"] = root
	copy_IPs.insert(0, copy_IPs.pop(copy_IPs.index(root)))
	#print(copy_IPs)
	row["order"] = copy_IPs

	root_IPs[v] = row

	Edges = []
	for ip in copy_IPs:
		node = ip
		for neighbor in Nodes[node]:
			pair = (node, Nodes[node][neighbor]["Management IP"])
			Edges.append(pair)

	print("\nEdges: ", Edges)

	tree, all_edges = spanning_tree_from_edges(Edges)
	print("\nTree: (start_node, dest_node) ", sorted(tree.edges()))

	# ssh
	# ssh into svi
	username = "exam"
	password = "exam"
	handler = paramiko.SSHClient()
	handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		handler.connect(root, username=username, password=password, look_for_keys=False, allow_agent=False)
	except Exception as e:
		print("\nException: ", str(e))
		continue

	shell = handler.invoke_shell()

	shell.send("terminal length 0\n")  # forces terminal to print everything; no space needed
	time.sleep(1)

	# enable
	shell.send("en\n")
	shell.send("exam\n")  # enable password

	# before configuration
	print("\nBEFORE CONFIG")
	command = "show spanning-tree vlan " + str(v) + "\n"
	shell.send(command)
	time.sleep(1)

	output = shell.recv(65535)
	output = output.decode("utf-8")
	print(output)

	# configure
	shell.send("conf t\n")
	time.sleep(1)

	command = "spanning-tree vlan " + str(v) + " root primary\n"
	shell.send(command)
	time.sleep(1)

	shell.send("end\n")
	time.sleep(5)

	# after configuration
	print("\n####################")
	print("\nAFTER CONFIG")
	command = "show spanning-tree vlan " + str(v) + "\n"
	shell.send(command)
	time.sleep(1)

	output = shell.recv(65535)
	output = output.decode("utf-8")
	print(output)

