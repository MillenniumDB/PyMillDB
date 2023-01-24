# Cursor
1. ¿Qué output debería entregar cada método de path?

```python
class Cursor:
    def fetchall(self) -> list["Binding"]:
        pass

    def fetchone(self) -> "Binding":
        pass
```

# Neighbors
1. ¿Qué output debería entregar cada método de path?
2. ¿Node debe ser un ID o un nombre?

```python
def get_neighbors(node:      str | int,
                  edge_type: str = None,
                  direction: str = "outgoing" | "incoming" | "undirected") -> list[typeof(node)]:
    pass
def k_hop_neighbors(node:      str | int,
                    k: int,
                    edge_type: str = None,
                    direction: str = "outgoing" | "incoming" | "undirected") -> list[typeof(node)]:
    pass
```

# Paths
1. ¿Fijar source o target? (Variables abiertas)
2. ¿Qué output debería entregar cada método de path?
3. ¿Source y target deben ser ID o nombres?

```python
def get_path(source: str | int,
            target: str | int,
            propertyPath: str = None) -> "?":
    pass

def get_shortest_path(source: str | int,
                      target: str | int,
                      propertyPath: str = None) -> "?":
    pass

def get_k_shortest_path(source: str | int,
                        target: str | int,
                        k: int,
                        propertyPath: str = None) -> "?":
```

# Objetos
1. ¿Son necesarias estas clases?
2. Tal vez para `DESCRIBE(node)` ó `DESCRIBE(edge)`

```python
class Node:
    def __init__(self, id: int, name: str = None, properties: dict = None):
        pass

class Edge:
    def __init__(self, id: int, source: int, target: int, type: int = None, properties: dict = None):
        pass
```


```python
def get_node(name: str) -> "Node":
    pass
```