from pymdb import Client
import pandas as pd

if __name__ == "__main__":
    # 1. Connect to MDB
    conn = Client("localhost", 8080)
    # 2. Query MDB
    try:
        result = conn.query("MATCH (?x) RETURN ?x LIMIT 100")
        df = result.to_dataframe()
        print(df)
    except Exception as e:
        print("Query error: ", e)
    conn.close()