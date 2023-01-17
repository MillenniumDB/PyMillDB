# Cursor
1. ¿Qué output debería entregar cada método de path?

```python
class Cursor:
    def fetchAll(self) -> list["Binding"]:
        pass

    def fetchOne(self) -> "Binding":
        pass
```

# Neighbors
1. ¿Qué output debería entregar cada método de path?
2. ¿Node debe ser un ID o un nombre?

```python
def getNeighbors(node:      str | int,
                 edge_type: str = None,
                 direction: str = "outgoing" | "incoming" | "undirected") -> list[typeof(node)]:
    pass
def kHopNeighbors(node:      str | int,
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
def getPath(source: str | int,
            target: str | int,
            propertyPath: str = None) -> "?":
    pass

def getShortestPath(source: str | int,
                    target: str | int,
                    propertyPath: str = None) -> "?":
    pass

def getKShortestPath(source: str | int,
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