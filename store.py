from pymdb import FeatureStore, MDBClient

with MDBClient(host="127.0.0.1", port=8080) as client:
    fs = FeatureStore(client, "random")
    print(fs)
    fs.close()
