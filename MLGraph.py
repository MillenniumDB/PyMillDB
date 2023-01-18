def GraphSAGE_embedding_generation(V, K, N, W, AGGREGATE, UPDATE, NORM):
    """
    Pseudo-code for GraphSAGE embedding generation
    
    Source: https://arxiv.org/pdf/1706.02216.pdf

    Args:
        V         (Array of nodes) : Array of graph nodes (with previously computed features)
        K         (Number)         : Depth of neighborhood aggregation
        N         (Function)       : Neighborhood function
        W         (Matrix)         : Weight matrix          (previously trained)
        AGGREGATE (Function)       : Aggregation function
        UPDATE    (Function)       : Update function
        NORM      (Function)       : Normalization function

    Returns:
        Array of arrays: Embedding of each node
    """
    # Initialize container
    h = [[ ] * len(V)] * (K + 1)
    # Initialize the first embedding without any aggregation
    h[0] = [v.features for v in V]
    for k in range(1, K + 1):
        for v in V:
            # Aggregate information to the neighborhood
            for nbr in N(v):
                h[k][nbr] = AGGREGATE(k)(h[k - 1][u] for u in N(v))
            # Update with the original feature with the neighborhood information
            h[k][v] = UPDATE(h[k - 1][v], h[k][N(v)])
        for v in V:
            # Normalize the embedding
            h[k][v] = NORM(h[k][v])
    # Return the final embedding
    return h[K]