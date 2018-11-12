import re
import json
import paramiko
import time
import sys
import networkx as nx

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

# TO DO: read list of management IPs from text file instead of command line arguments

# read in list of ip addresses as argument
i=1
IPs = []
for arg in sys.argv:
	if i == 1:
		i = i + 1
		continue
	IPs.append(arg)

# Ask user which switch to make root
print("\nList of nodes by IP address: ", IPs)
root = input("\nSpecify root node by IP address: ")

# going to be sneaky and move 'root' to front of list
IPs.insert(0, IPs.pop(IPs.index(root)))
#print(IPs)

Nodes = {}
nodes_visited = {}

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
				Neighbors[neighbor_name]["Name"] = item2.split(": ")[1]
				i=i+1
			if "Interface: " in item2:
				Neighbors[neighbor_name]["Local Node Interface"] = item2.split("Interface: ")[1].split(",  Port ID (outgoing port): ")[0]
				Neighbors[neighbor_name]["Adjacent Node Interface"] = item2.split("Interface: ")[1].split(",  Port ID (outgoing port): ")[1]
			if "Native VLAN: " in item2:
				Neighbors[neighbor_name]["Local VLAN"] = item2.split("Native VLAN: ")[1]
				Neighbors[neighbor_name]["Adjacent VLAN"] = item2.split("Native VLAN: ")[1]
			if "IP address: " in item2:
				Neighbors[neighbor_name]["Management IP"] = item2.split("IP address: ")[1]

	Nodes[remoteIP] = Neighbors
	
	
	
#####
## Graph -> Tree
# initialize all to not visited


Edges = []
for node in Nodes:
	for neighbor in Nodes[node]:
		pair = (node, Nodes[node][neighbor]["Management IP"])
		Edges.append(pair)
	
#
print("\n#######################")
nodes_by_IP = []
for node in Nodes:
	print(node)
	nodes_by_IP.append(node)
	print(Nodes[node])
	print("\n")
print("#######################\n")
#print("\nEdges: ", Edges)
#print("\nNodes by IP address: ", nodes_by_IP)

tree, all_edges = spanning_tree_from_edges(Edges)
#print("\nTree: ", sorted(tree.edges()))
#print("\nAll edges: ", all_edges)


#
# get mapping of IP address and its local interfaces
ips2ifaces = {}
for node in Nodes:
	ifaces = []

	for neighbor in Nodes[node]:
		ifaces.append(Nodes[node][neighbor]["Local Node Interface"])

	ips2ifaces[node] = ifaces

#print("\nIPs to their interfaces: ", ips2ifaces)

##
# create mapping of IP address to device ID
ips2names = {}
names2ips = {}
for node in Nodes:
	for neighbor in Nodes[node]:
		name = Nodes[node][neighbor]["Name"]
		ip = Nodes[node][neighbor]["Management IP"]
		ips2names[ip] = name
		names2ips[name] = ip

#print("\nIPs to Names: ", ips2names)
#print("\nNames to IPs: ", names2ips)



# check which interfaces are missing
missing_links = []
for e in all_edges:
	if e not in tree.edges():
		missing_links.append(e)

#print("\nMissing Links: ", missing_links)

# create object of ip:iface that needs to be re-configured

configIPs = {}
for link in missing_links:
	sIP, dIP = link
	#print(sIP + " : " + dIP)

	for node in Nodes:
		if node == sIP:
			for neighbor in Nodes[node]:
				if Nodes[node][neighbor]["Management IP"] == dIP:
					configIPs[sIP] = Nodes[node][neighbor]["Local Node Interface"]
					configIPs[dIP] = Nodes[node][neighbor]["Adjacent Node Interface"]

print("\nConfig IPs: ", configIPs)

# re-configure trunk links -> take off vlan
for ip in configIPs:
	# ssh into svi
	username = "exam"
	password = "exam"
	handler = paramiko.SSHClient()
	handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		handler.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
	except Exception as e:
		print("\nException: ", str(e))
		continue

	shell = handler.invoke_shell()

	shell.send("terminal length 0\n")  # forces terminal to print everything; no space needed
	time.sleep(1)

	shell.send("enable\n")
	time.sleep(1)

	output = shell.recv(65535)
	output = output.decode("utf-8")
	print(output)

	# change interface configuration


