import networkx as nx

# https://networkx.github.io/documentation/latest/_downloads/networkx_reference.pdf

'''
test version to find loops, then break them
topology is a triangle between Top-Middle-Bottom

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


#####
Nodes = {}

# Top Switch
Neighbors = {}
Neighbors["Neighbor 1"] = {}
Neighbors["Neighbor 1"]["Name"] = "Middle"
Neighbors["Neighbor 1"]["Management IP"] = "192.168.1.2"
Neighbors["Neighbor 1"]["Local Node Interface"] = "0/12"
Neighbors["Neighbor 1"]["Adjacent Node Interface"] = "0/21"
Neighbors["Neighbor 2"] = {}
Neighbors["Neighbor 2"]["Name"] = "Bottom"
Neighbors["Neighbor 2"]["Management IP"] = "192.168.1.3"
Neighbors["Neighbor 2"]["Local Node Interface"] = "0/13"
Neighbors["Neighbor 2"]["Adjacent Node Interface"] = "0/1"
Nodes["192.168.1.1"] = Neighbors

# Middle Switch
Neighbors = {}
Neighbors["Neighbor 1"] = {}
Neighbors["Neighbor 1"]["Name"] = "Top"
Neighbors["Neighbor 1"]["Management IP"] = "192.168.1.1"
Neighbors["Neighbor 1"]["Local Node Interface"] = "0/21"
Neighbors["Neighbor 1"]["Adjacent Node Interface"] = "0/12"
Neighbors["Neighbor 2"] = {}
Neighbors["Neighbor 2"]["Name"] = "Bottom"
Neighbors["Neighbor 2"]["Management IP"] = "192.168.1.3"
Neighbors["Neighbor 2"]["Local Node Interface"] = "0/23"
Neighbors["Neighbor 2"]["Adjacent Node Interface"] = "0/2"
Nodes["192.168.1.2"] = Neighbors

# Bottom Switch
Neighbors = {}
Neighbors["Neighbor 1"] = {}
Neighbors["Neighbor 1"]["Name"] = "Top"
Neighbors["Neighbor 1"]["Management IP"] = "192.168.1.1"
Neighbors["Neighbor 1"]["Local Node Interface"] = "0/1"
Neighbors["Neighbor 1"]["Adjacent Node Interface"] = "0/13"
Neighbors["Neighbor 2"] = {}
Neighbors["Neighbor 2"]["Name"] = "Middle"
Neighbors["Neighbor 2"]["Management IP"] = "192.168.1.2"
Neighbors["Neighbor 2"]["Local Node Interface"] = "0/2"
Neighbors["Neighbor 2"]["Adjacent Node Interface"] = "0/23"
Nodes["192.168.1.3"] = Neighbors

for node in Nodes:
    print(node)
    print(Nodes[node])
    print("\n")

#
# Adjacency List -> Tree
Edges = []
for node in Nodes:
    for neighbor in Nodes[node]:
        pair = (node, Nodes[node][neighbor]["Management IP"])
        Edges.append(pair)

print("\nEdges: ", Edges)

tree, all_edges = spanning_tree_from_edges(Edges)
print("\nTree: ", sorted(tree.edges()))

# find link in graph, but not in tree -> redundant link (loop)
missing_links = []
for e in all_edges:
    if e not in tree.edges():
        missing_links.append(e)

# create object that says which interface needs to be re-configured on which node
configIPs = {}
for link in missing_links:
    sIP, dIP = link  # start, destination IP addresses
    #print(sIP + " : " + dIP)

    for node in Nodes:
        if node == sIP:
            for neighbor in Nodes[node]:
                if Nodes[node][neighbor]["Management IP"] == dIP:
                    configIPs[sIP] = Nodes[node][neighbor]["Local Node Interface"]
                    configIPs[dIP] = Nodes[node][neighbor]["Adjacent Node Interface"]


# Trunk ports on these interfaces need to be re-configured on these nodes (by IP address)
print("\nConfig IPs: ", configIPs)






