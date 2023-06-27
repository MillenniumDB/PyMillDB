from pymilldb import MDBClient, NodeIterator

with MDBClient() as client:
    it = NodeIterator(client, 100)
    for batch in it:
        print(batch)