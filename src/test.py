from pymilldb import GraphExplorer, MDBClient, Sampler

with MDBClient() as client:
    s = Sampler(client)
    ge = GraphExplorer(client)
    
    g = s.subgraph(1, [5])
    node_id = g.node_ids[0]
    print(node_id)
    print(ge.get_node(node_id))
