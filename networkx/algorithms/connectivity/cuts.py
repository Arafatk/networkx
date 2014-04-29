# -*- coding: utf-8 -*-
"""
Flow based cut algorithms
"""
# http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
# http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf
import itertools

import networkx as nx

# Define the default maximum flow function to use in all flow based
# connectivity algorithms. 
from networkx.algorithms.flow import edmonds_karp
from networkx.algorithms.flow import shortest_augmenting_path
from networkx.algorithms.flow.utils import build_residual_network
default_flow_func = edmonds_karp

from networkx.algorithms.connectivity.utils import (
    build_auxiliary_node_connectivity, build_auxiliary_edge_connectivity)

__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>'])

__all__ = ['minimum_st_node_cut',
           'minimum_node_cut',
           'minimum_st_edge_cut',
           'minimum_edge_cut']


def minimum_st_edge_cut(G, s, t, capacity='capacity', flow_func=None,
                        residual=None):
    """Returns the edges of the cut-set of a minimum (s, t)-cut.

    We use the max-flow min-cut theorem, i.e., the capacity of a minimum
    capacity cut is equal to the flow value of a maximum flow.

    Parameters
    ----------
    G : NetworkX graph
        Edges of the graph are expected to have an attribute called
        'capacity'. If this attribute is not present, the edge is
        considered to have infinite capacity.

    s : node
        Source node for the flow.

    t : node
        Sink node for the flow.

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See :meth:`node_connectivity` for
        details. The choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    residual : NetworkX DiGraph
        Residual network to compute maximum flow. If provided it will be
        reused instead of recreated. Default value: None.

    Returns
    -------
    cutset : set
        Set of edges that, if removed from the graph, will disconnect it

    Raises
    ------
    NetworkXUnbounded
        If the graph has a path of infinite capacity, all cuts have
        infinite capacity and the function raises a NetworkXError.

    See also
    --------
    :meth:`maximum_flow`
    :meth:`minimum_cut`
    :meth:`minimum_node_cut`
    :meth:`minimum_edge_cut`
    :meth:`stoer_wagner`
    :meth:`node_connectivity`
    :meth:`edge_connectivity`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edge('x','a', capacity = 3.0)
    >>> G.add_edge('x','b', capacity = 1.0)
    >>> G.add_edge('a','c', capacity = 3.0)
    >>> G.add_edge('b','c', capacity = 5.0)
    >>> G.add_edge('b','d', capacity = 4.0)
    >>> G.add_edge('d','e', capacity = 2.0)
    >>> G.add_edge('c','y', capacity = 2.0)
    >>> G.add_edge('e','y', capacity = 3.0)
    >>> cutset = nx.minimum_edge_cut(G, 'x', 'y')
    >>> sorted(cutset)
    [('c', 'y'), ('x', 'b')]
    >>> cut_value = nx.minimum_cut_value(G, 'x', 'y')
    >>> cut_value == sum(G[u][v]['capacity'] for u, v in cutset)
    True

    """
    if flow_func is None:
        flow_func = default_flow_func

    kwargs = dict(capacity=capacity, flow_func=flow_func, residual=residual)

    try:
        cut_value, partition = nx.minimum_cut(G, s, t, **kwargs)
        reachable, non_reachable = partition
        # Any edge in the original graph linking the two sets in the 
        # partition is part of the edge cutset
        cutset = set()
        for u, nbrs in ((n, G[n]) for n in reachable):
            cutset.update((u, v) for v in nbrs if v in non_reachable)
        return cutset

    except nx.NetworkXUnbounded:
        raise nx.NetworkXUnbounded("Infinite capacity path, no minimum cut.")


def minimum_st_node_cut(G, s, t, flow_func=None, aux_digraph=None,
                        mapping=None, residual=None):
    r"""Returns a set of nodes of minimum cardinality that disconnect source
    from target in G.

    This function returns the set of nodes of minimum cardinality that,
    if removed, would destroy all paths among source and target in G.

    Parameters
    ----------
    G : NetworkX graph

    s : node
        Source node.

    t : node
        Target node.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See :meth:`node_connectivity` for
        details. The choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    aux_digraph : NetworkX DiGraph
        Auxiliary digraph to compute flow based node connectivity. If None
        the auxiliary digraph is build. Default value: None.

    mapping : dict
        Dictionary with a mapping of node names in G and in the auxiliary
        digraph. Default value: None.

    residual : NetworkX DiGraph
        Residual network to compute maximum flow. If provided it will be
        reused instead of recreated. Default value: None.

    Returns
    -------
    cutset : set
        Set of nodes that, if removed, would destroy all paths between
        source and target in G.

    Examples
    --------
    >>> # Platonic icosahedral graph has node connectivity 5
    >>> G = nx.icosahedral_graph()
    >>> len(nx.minimum_st_node_cut(G, 0, 6))
    5

    If you need to compute local st cuts on several pairs of
    nodes in the same graph, it is recommended that you reuse the
    data structures that NetworkX uses for computing the maximum 
    flow and the node connectivity: the auxiliary digraph for
    node connectivity, and the residual network for maximum flow:

    >>> # Import the function for building the auxiliary digraph
    >>> from networkx.algorithms.connectivity.utils import (
    ...     build_auxiliary_node_connectivity)
    >>> H, mapping = build_auxiliary_node_connectivity(G)
    >>> # Import the function for building the resudual network
    >>> from networkx.algorithms.flow.utils import build_residual_network
    >>> R = build_residual_network(H, 'capacity')
    >>> # You can reuse them by passing them as parameters
    >>> kwargs = dict(aux_digraph=H, mapping=mapping, residual=R) 
    >>> len(nx.minimum_st_node_cut(G, 0, 6, **kwargs))
    5

    You can also use alternative flow algorithms for computing 
    node cuts. For instance, in dense networks the algorithm
    :meth:`shortest_augmenting_path` will usually perform better than
    the default :meth:`edmonds_karp` which is faster for sparse 
    network with highly skewed degree distributions:

    >>> len(nx.minimum_st_node_cut(G, 0, 6, flow_func=nx.shortest_augmenting_path))
    5

    Notes
    -----
    This is a flow based implementation of minimum node cut. The algorithm
    is based in solving a number of max-flow problems (ie local st-node
    connectivity, see :meth:`local_node_connectivity`) to determine the 
    capacity of the minimum cut on an auxiliary directed network that 
    corresponds to the minimum node cut of G. It handles both directed 
    and undirected graphs.

    This implementation is based on algorithm 11 in [1]_. We use the Ford
    and Fulkerson algorithm to compute max flow (see ford_fulkerson).

    See also
    --------
    :meth:`minimum_node_cut`
    :meth:`minimum_edge_cut`
    :meth:`stoer_wagner`
    :meth:`node_connectivity`
    :meth:`edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    if aux_digraph is None or mapping is None:
        H, mapping = build_auxiliary_node_connectivity(G)
    else:
        H = aux_digraph
    kwargs = dict(flow_func=flow_func, residual=residual)

    edge_cut = minimum_st_edge_cut(H, '%sB' % mapping[s], '%sA' % mapping[t],
                                   **kwargs)
    # Each node in the original graph maps to two nodes of the auxiliary graph
    node_cut = set(H.node[node]['id'] for edge in edge_cut for node in edge)
    return node_cut - set([s, t])


def minimum_node_cut(G, s=None, t=None, flow_func=None):
    r"""Returns a set of nodes of minimum cardinality that disconnects G.

    If source and target nodes are provided, this function returns the
    set of nodes of minimum cardinality that, if removed, would destroy
    all paths among source and target in G. If not, it returns a set
    of nodes of minimum cardinality that disconnects G.

    Parameters
    ----------
    G : NetworkX graph

    s : node
        Source node. Optional. Default value: None.

    t : node
        Target node. Optional. Default value: None.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See below for details. The
        choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    Returns
    -------
    cutset : set
        Set of nodes that, if removed, would disconnect G. If source
        and target nodes are provided, the set contians the nodes that
        if removed, would destroy all paths between source and target.

    Examples
    --------
    >>> # Platonic icosahedral graph has node connectivity 5
    >>> G = nx.icosahedral_graph()
    >>> len(nx.minimum_node_cut(G))
    5
    >>> # this is the minimum over any pair of non adjacent nodes
    >>> from itertools import combinations
    >>> for u,v in combinations(G, 2):
    ...     if v not in G[u]:
    ...         assert(len(nx.minimum_node_cut(G,u,v)) == 5)
    ...

    Notes
    -----
    This is a flow based implementation of minimum node cut. The algorithm
    is based in solving a number of max-flow problems (ie local st-node
    connectivity, see local_node_connectivity) to determine the capacity
    of the minimum cut on an auxiliary directed network that corresponds
    to the minimum node cut of G. It handles both directed and undirected
    graphs. This implementation is based on algorithm 11 in [1]_.

    You can use alternative flow algorithms for the underlying maximum
    flow computation. In dense networks the algorithm
    :meth:`shortest_augmenting_path` will usually perform better
    than the default :meth:`edmonds_karp`, which is faster for
    sparse networks with highly skewed degree distributions.

    See also
    --------
    :meth:`minimum_node_cut`
    :meth:`minimum_edge_cut`
    :meth:`stoer_wagner`
    :meth:`node_connectivity`
    :meth:`edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    # Local minimum node cut
    if s is not None and t is not None:
        if s not in G:
            raise nx.NetworkXError('node %s not in graph' % s)
        if t not in G:
            raise nx.NetworkXError('node %s not in graph' % t)
        return minimum_st_node_cut(G, s, t, flow_func=flow_func)

    # Global minimum node cut
    # Analog to the algoritm 11 for global node connectivity in [1]
    if G.is_directed():
        if not nx.is_weakly_connected(G):
            raise nx.NetworkXError('Input graph is not connected')
        iter_func = itertools.permutations
        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors_iter(v),
                                                  G.successors_iter(v)])
    else:
        if not nx.is_connected(G):
            raise nx.NetworkXError('Input graph is not connected')
        iter_func = itertools.combinations
        neighbors = G.neighbors_iter

    # Reuse the auxiliary digraph and the residual network
    H, mapping = build_auxiliary_node_connectivity(G)
    R = build_residual_network(H, 'capacity')
    kwargs = dict(flow_func=flow_func, aux_digraph=H, mapping=mapping,
                  residual=R)

    # Choose a node with minimum degree
    deg = G.degree()
    v = next(n for n, d in deg.items() if d == min(deg.values()))
    # Initial node cutset is all neighbors of the node with minimum degree
    min_cut = set(G[v])
    # compute st node cuts between v and all its non-neighbors nodes in G
    for w in set(G) - set(neighbors(v)) - set([v]):
        this_cut = minimum_st_node_cut(G, v, w, **kwargs)
        if len(min_cut) >= len(this_cut):
            min_cut = this_cut
    # Same for non adjacent pairs of neighbors of v
    for x,y in iter_func(neighbors(v),2):
        if y in G[x]:
            continue
        this_cut = minimum_st_node_cut(G, v, w, **kwargs)
        if len(min_cut) >= len(this_cut):
            min_cut = this_cut

    return min_cut

def minimum_edge_cut(G, s=None, t=None, flow_func=None):
    r"""Returns a set of edges of minimum cardinality that disconnects G.

    If source and target nodes are provided, this function returns the
    set of edges of minimum cardinality that, if removed, would break
    all paths among source and target in G. If not, it returns a set of
    edges of minimum cardinality that disconnects G.

    Parameters
    ----------
    G : NetworkX graph

    s : node
        Source node. Optional. Default value: None.

    t : node
        Target node. Optional. Default value: None.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See below for details. The
        choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    Returns
    -------
    cutset : set
        Set of edges that, if removed, would disconnect G. If source
        and target nodes are provided, the set contians the edges that
        if removed, would destroy all paths between source and target.

    Examples
    --------
    >>> # Platonic icosahedral graph has edge connectivity 5
    >>> G = nx.icosahedral_graph()
    >>> len(nx.minimum_edge_cut(G))
    5
    >>> # this is the minimum over any pair of nodes
    >>> from itertools import combinations
    >>> for u,v in combinations(G, 2):
    ...     assert(len(nx.minimum_edge_cut(G,u,v)) == 5)
    ...

    Notes
    -----
    This is a flow based implementation of minimum edge cut. For
    undirected graphs the algorithm works by finding a 'small' dominating
    set of nodes of G (see algorithm 7 in [1]_) and computing the maximum
    flow between an arbitrary node in the dominating set and the rest of
    nodes in it. This is an implementation of algorithm 6 in [1]_. For 
    directed graphs, the algorithm does n calls to the max flow function.
    It is an implementation of algorithm 8 in [1]_.

    You can use alternative flow algorithms for the underlying 
    maximum flow computation. In dense networks the algorithm 
    :meth:`shortest_augmenting_path` will usually perform better 
    than the default :meth:`edmonds_karp`, which is faster for 
    sparse networks with highly skewed degree distributions.

    See also
    --------
    :meth:`minimum_node_cut`
    :meth:`minimum_edge_cut`
    :meth:`stoer_wagner`
    :meth:`node_connectivity`
    :meth:`edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    # reuse auxiliary digraph and residual network
    H = build_auxiliary_edge_connectivity(G)
    R = build_residual_network(H, 'capacity')
    kwargs = dict(flow_func=flow_func, residual=R)

    # Local minimum edge cut if s and t are not None
    if s is not None and t is not None:
        if s not in G:
            raise nx.NetworkXError('node %s not in graph' % s)
        if t not in G:
            raise nx.NetworkXError('node %s not in graph' % t)
        return minimum_st_edge_cut(H, s, t, **kwargs)
    # Global minimum edge cut
    # Analog to the algoritm for global edge connectivity
    if G.is_directed():
        # Based on algorithm 8 in [1]
        if not nx.is_weakly_connected(G):
            raise nx.NetworkXError('Input graph is not connected')

        # Initial cutset is all edges of a node with minimum degree
        deg = G.degree()
        node = next(n for n,d in deg.items() if d==min(deg.values()))
        min_cut = G.edges(node)
        nodes = G.nodes()
        n = len(nodes)
        for i in range(n):
            try:
                this_cut = minimum_st_edge_cut(H, nodes[i], nodes[i+1], **kwargs)
                if len(this_cut) <= len(min_cut):
                    min_cut = this_cut
            except IndexError: # Last node!
                this_cut = minimum_st_edge_cut(H, nodes[i], nodes[0], **kwargs)
                if len(this_cut) <= len(min_cut):
                    min_cut = this_cut
        return min_cut

    else: # undirected
        # Based on algorithm 6 in [1]
        if not nx.is_connected(G):
            raise nx.NetworkXError('Input graph is not connected')

        # Initial cutset is all edges of a node with minimum degree
        deg = G.degree()
        node = next(n for n,d in deg.items() if d==min(deg.values()))
        min_cut = G.edges(node)
        # A dominating set is \lambda-covering
        # We need a dominating set with at least two nodes
        for node in G:
            D = nx.dominating_set(G, start_with=node)
            v = D.pop()
            if D:
                break
        else:
            # in complete graphs the dominating set will always be of one node
            # thus we return min_cut, which now contains the edges of a node
            # with minimum degree
            return min_cut
        for w in D:
            this_cut = minimum_st_edge_cut(H, v, w, **kwargs)
            if len(this_cut) <= len(min_cut):
                min_cut = this_cut

        return min_cut
