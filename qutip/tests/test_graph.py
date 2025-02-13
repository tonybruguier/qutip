import os
import numpy as np
from numpy.testing import run_module_suite, assert_equal
import scipy.sparse as sp
from scipy.sparse.csgraph import breadth_first_order as BFO
import pytest

pwd = os.path.dirname(__file__)

from qutip import (rand_dm, graph_degree, breadth_first_search,
                   reverse_cuthill_mckee, tensor, destroy, qeye, sigmam,
                   liouvillian, maximum_bipartite_matching,
                   weighted_bipartite_matching, column_permutation)
from qutip.sparse import sp_permute, sp_bandwidth

def test_graph_degree():
    "Graph: Graph Degree"
    A = rand_dm(25, 0.1)
    with pytest.deprecated_call():
        deg = graph_degree(A.data)
    A = A.full()
    np_deg = []
    for k in range(25):
        num = 0
        inds = A[k, :].nonzero()[0]
        num = len(inds)
        if k in inds:
            num += 1
        np_deg.append(num)
    np.asarray(np_deg, dtype=int)
    assert_equal((deg - np_deg).all(), 0)


def test_graph_bfs():
    "Graph: Breadth-First Search"
    A = rand_dm(25, 0.5)
    A = A.data
    A.data = np.real(A.data)
    seed = np.random.randint(24)
    arr1 = BFO(A, seed)[0]
    with pytest.deprecated_call():
        arr2 = breadth_first_search(A, seed)[0]
    assert_equal((arr1 - arr2).all(), 0)


def test_graph_rcm_simple():
    "Graph: Reverse Cuthill-McKee Ordering (simple)"
    A = np.array([[1, 0, 0, 0, 1, 0, 0, 0],
                  [0, 1, 1, 0, 0, 1, 0, 1],
                  [0, 1, 1, 0, 1, 0, 0, 0],
                  [0, 0, 0, 1, 0, 0, 1, 0],
                  [1, 0, 1, 0, 1, 0, 0, 0],
                  [0, 1, 0, 0, 0, 1, 0, 1],
                  [0, 0, 0, 1, 0, 0, 1, 0],
                  [0, 1, 0, 0, 0, 1, 0, 1]], dtype=np.int32)
    A = sp.csr_matrix(A)
    with pytest.deprecated_call():
        perm = reverse_cuthill_mckee(A)
    ans = np.array([6, 3, 7, 5, 1, 2, 4, 0])
    assert_equal((perm - ans).all(), 0)


def test_graph_rcm_boost():
    "Graph: Reverse Cuthill-McKee Ordering (boost)"
    M = np.zeros((10, 10))
    M[0, [3, 5]] = 1
    M[1, [2, 4, 6, 9]] = 1
    M[2, [3, 4]] = 1
    M[3, [5, 8]] = 1
    M[4, 6] = 1
    M[5, [6, 7]] = 1
    M[6, 7] = 1
    M = M+M.T
    M = sp.csr_matrix(M, dtype=complex)
    with pytest.deprecated_call():
        perm = reverse_cuthill_mckee(M, 1)
    ans_perm = np.array([9, 7, 6, 4, 1, 5, 0, 2, 3, 8])
    assert_equal((perm - ans_perm).all(), 0)
    P = sp_permute(M, perm, perm)
    bw = sp_bandwidth(P)
    assert_equal(bw[2], 4)


def test_graph_rcm_qutip():
    "Graph: Reverse Cuthill-McKee Ordering (qutip)"
    kappa = 1
    gamma = 0.01
    g = 1
    wc = w0 = wl = 0
    N = 2
    E = 1.5
    a = tensor(destroy(N), qeye(2))
    sm = tensor(qeye(N), sigmam())
    H = (w0-wl)*sm.dag(
        )*sm+(wc-wl)*a.dag()*a+1j*g*(a.dag()*sm-sm.dag()*a)+E*(a.dag()+a)
    c_ops = [np.sqrt(2*kappa)*a, np.sqrt(gamma)*sm]
    L = liouvillian(H, c_ops)
    with pytest.deprecated_call():
        perm = reverse_cuthill_mckee(L.data)
    ans = np.array([12, 14, 4, 6, 10, 8, 2, 15, 0, 13, 7, 5, 9, 11, 1, 3])
    assert_equal(perm, ans)


def test_graph_maximum_bipartite_matching():
    "Graph: Maximum Bipartite Matching"
    A = sp.diags(np.ones(25), offsets=0, format='csc')
    perm = np.random.permutation(25)
    perm2 = np.random.permutation(25)
    B = sp_permute(A, perm, perm2)
    with pytest.deprecated_call():
        perm = maximum_bipartite_matching(B)
    C = sp_permute(B, perm, [])
    assert_equal(any(C.diagonal() == 0), False)


def test_graph_weighted_matching():
    "Graph: Weighted Bipartite Matching"
    A = sp.rand(25, 25, density=0.1, format='csc')
    a_len = len(A.data)
    A.data = np.ones(a_len)
    d = np.arange(0, 25) + 2
    B = sp.diags(d, offsets=0, format='csc')
    A = A+B
    perm = np.random.permutation(25)
    perm2 = np.random.permutation(25)
    B = sp_permute(A, perm, perm2)
    with pytest.deprecated_call():
        perm = weighted_bipartite_matching(B)
    C = sp_permute(B, perm, [])
    assert_equal(np.sum(A.diagonal()), np.sum(C.diagonal()))


def test_column_permutation():
    "Graph: Column Permutation"
    A = sp.rand(5, 5, 0.25, format='csc')
    with pytest.deprecated_call():
        perm = column_permutation(A)
    B = sp_permute(A, [], perm)
    counts = np.diff(B.indptr)
    assert_equal(np.all(np.argsort(counts) == np.arange(5)), True)


if __name__ == "__main__":
    run_module_suite()
