"""
==================
Depth-first search
==================

Basic algorithms for depth-first search and depth-limited search of a graph.

Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
by D. Eppstein, July 2004.
https://en.wikipedia.org/wiki/Depth-limited_search
"""
import networkx as nx
from collections import defaultdict
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>'])
__all__ = ['dfs_edges', 'dfs_tree',
           'dfs_predecessors', 'dfs_successors',
           'dfs_preorder_nodes','dfs_postorder_nodes',
           'dfs_labeled_edges']

def dfs_edges(G, source=None, search_depth=None):
    """Produce edges in a depth-first-search (DFS).

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    edges: generator
       A generator of edges in the depth-first-search.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(list(nx.dfs_edges(G,0)))
    [(0, 1), (1, 2)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    if source is None:
        # produce edges for all components
        nodes = G
    else:
        # produce edges for components with source
        nodes = [source]
    visited=set()
    if search_depth == None:
       search_depth = len(G)
    for start in nodes:
        if start in visited:
            continue
        visited.add(start)
        stack = [(start,search_depth,iter(G[start]))]
        while stack:
            parent,depth_now,children = stack[-1]
            if not depth_now >= 1:
                stack.pop()
                continue
            try:
                child = next(children)
                if child not in visited:
                    yield parent,child
                    visited.add(child)
                    stack.append((child,depth_now-1,iter(G[child])))
            except StopIteration:
                stack.pop()

def dfs_tree(G, source, search_depth=None):
    """Return oriented tree constructed from a depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    T : NetworkX DiGraph
       An oriented tree

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> T = nx.dfs_tree(G,0)
    >>> print(list(T.edges()))
    [(0, 1), (1, 2)]
    """
    T = nx.DiGraph()
    if source is None:
        T.add_nodes_from(G)
    else:
        T.add_node(source)
    T.add_edges_from(dfs_edges(G,source,search_depth))
    return T

def dfs_predecessors(G, source=None, search_depth=None):
    """Return dictionary of predecessors in depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    pred: dict
       A dictionary with nodes as keys and predecessor nodes as values.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(nx.dfs_predecessors(G,0))
    {1: 0, 2: 1}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    return dict((t,s) for s,t in dfs_edges(G,source=source,search_depth=search_depth))


def dfs_successors(G, source=None, search_depth=None):
    """Return dictionary of successors in depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    succ: dict
       A dictionary with nodes as keys and list of successor nodes as values.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(nx.dfs_successors(G,0))
    {0: [1], 1: [2]}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    d = defaultdict(list)
    for s,t in dfs_edges(G,source=source,search_depth=search_depth):
        d[s].append(t)
    return dict(d)


def dfs_postorder_nodes(G,source=None,search_depth=None):
    """Produce nodes in a depth-first-search post-ordering starting
    from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-first-search post-ordering.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(list(nx.dfs_postorder_nodes(G,0)))
    [2, 1, 0]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    post=(v for u,v,d in nx.dfs_labeled_edges(G,source=source,search_depth=search_depth)
          if d['dir']=='reverse')
    # potential modification: chain source to end of post-ordering
    # return chain(post,[source])
    return post


def dfs_preorder_nodes(G, source=None, search_depth=None):
    """Produce nodes in a depth-first-search pre-ordering starting
    from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-first-search pre-ordering.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(list(nx.dfs_preorder_nodes(G,0)))
    [0, 1, 2]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    pre=(v for u,v,d in nx.dfs_labeled_edges(G,source=source,search_depth=search_depth)
         if d['dir']=='forward')
    # potential modification: chain source to beginning of pre-ordering
    # return chain([source],pre)
    return pre


def dfs_labeled_edges(G, source=None, search_depth=None):
    """Produce edges in a depth-first-search (DFS) labeled by type.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    search_depth : length, optional
       Specify the maximum search depth.

    Returns
    -------
    edges: generator
       A generator of edges in the depth-first-search labeled with 'forward',
       'nontree', and 'reverse'.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> edges = (list(nx.dfs_labeled_edges(G,0)))

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    # Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    # by D. Eppstein, July 2004.
    if source is None:
        # produce edges for all components
        nodes = G
    else:
        # produce edges for components with source
        nodes = [source]
    visited = set()
    if search_depth == None:
       search_depth = len(G)
    for start in nodes:
        if start in visited:
            continue
        yield start,start,{'dir':'forward'}
        visited.add(start)
        stack = [(start,search_depth,iter(G[start]))]
        while stack:
            parent,depth_now,children = stack[-1]
            if not depth_now >= 1:
                stack.pop()
                continue
            try:
                child = next(children)
                if child in visited:
                    yield parent,child,{'dir':'nontree'}
                else:
                    yield parent,child,{'dir':'forward'}
                    visited.add(child)
                    stack.append((child,depth_now-1,iter(G[child])))
            except StopIteration:
                stack.pop()
                if stack:
                    yield stack[-1][0],parent,{'dir':'reverse'}
        yield start,start,{'dir':'reverse'}
