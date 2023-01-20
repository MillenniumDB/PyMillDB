import pymdb

connection = pymdb.Connection(host="localhost", port="8080")

with connection.cursor() as cursor:
    query = "MATCH (Q10010)->(?y) RETURN ?y LIMIT 100"
    cursor.execute(query)

connection.close()