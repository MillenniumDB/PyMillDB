from pymdb import Client

if __name__ == "__main__":
    conn = Client("localhost", 8080)
    conn.query("MATCH (n) RETURN n LIMIT 10")