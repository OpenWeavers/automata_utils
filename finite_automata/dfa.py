from collections import defaultdict
from functools import reduce
import pygraphviz as pgv
from finite_automata.fa import FA


class DFA(FA):
    def __init__(self, Q, Σ, 𝛿_dict, q_0, F):
        assert set(𝛿_dict.keys()).intersection(Q) == Q
        assert all(
            set(𝛿_dict[d].keys()).intersection(Σ) == Σ
            and all(x in Q for x in 𝛿_dict[d].values())
            for d in 𝛿_dict)
        assert q_0 in Q
        assert F <= Q  # Subset or Equal
        FA.__init__(self, Q, Σ, 𝛿_dict, q_0, F)

    def rename(self, start=0):
        rename_dict = dict(zip(self.Q, {'q%s' % (start + i) for i in range(len(self.Q))}))

        def rename_func(x):
            return rename_dict[x]

        Q = set(map(rename_func, self.Q))
        q_0 = rename_func(self.q_0)
        F = set(map(rename_func, self.F))
        new_delta = defaultdict(dict)
        for q, A in self.𝛿_dict.items():
            for a in A:
                new_delta[rename_func(q)][a] = rename_func(self.𝛿_dict[q][a])
        return DFA(Q, self.Σ, new_delta, q_0, F)

    def is_accepted(self, w):
        return reduce(self.𝛿, w, self.q_0) in self.F

    def draw(self, filename, prog='dot'):
        G = pgv.AGraph(directed=True, rankdir='LR')
        G.add_node('qi', shape='point')
        for q in self.Q:
            G.add_node(q, shape='oval', peripheries=2 if q in self.F else 1)
        G.add_edge('qi', self.q_0, label='start')
        for u in self.𝛿_dict:
            for a, v in self.𝛿_dict[u].items():
                label = G.get_edge(u, v).attr['label'] + ',' + a if G.has_edge(u, v) else a
                G.add_edge(u, v, label=label)
        G.draw(filename, format='png', prog=prog)

    def union(self, M):
        assert self.Σ == M.Σ
        Q = {(x, y) for x in self.Q for y in M.Q}
        delta_dict = {(x, y): {a: (self.𝛿(x, a), M.𝛿(y, a)) for a in self.Σ} for (x, y) in Q}
        F = {(x, y) for x in self.Q for y in M.Q if x in self.F or y in M.F}
        return DFA(Q, self.Σ, delta_dict, (self.q_0, M.q_0), F)

    def intersection(self, M):
        assert self.Σ == M.Σ
        Q = {(x, y) for x in self.Q for y in M.Q}
        delta_dict = {(x, y): {a: (self.𝛿(x, a), M.𝛿(y, a)) for a in self.Σ} for (x, y) in Q}
        F = {(x, y) for x in self.F for y in M.F}
        return DFA(Q, self.Σ, delta_dict, (self.q_0, M.q_0), F)

    def difference(self, M):
        assert self.Σ == M.Σ
        Q = {(x, y) for x in self.Q for y in M.Q}
        delta_dict = {(x, y): {a: (self.𝛿(x, a), M.𝛿(y, a)) for a in self.Σ} for (x, y) in Q}
        F = {(x, y) for x in self.F for y in M.F if x in self.F and y not in M.F}
        return DFA(Q, self.Σ, delta_dict, (self.q_0, M.q_0), F)

    def to_enfa(self):
        from finite_automata.enfa import ENFA
        delta_dict = defaultdict(dict)
        for u in self.𝛿_dict:
            for a in self.𝛿_dict[u]:
                delta_dict[u][a] = frozenset({self.𝛿(u, a)})
            delta_dict[u]['ϵ'] = frozenset()
        return ENFA(self.Q, self.Σ, delta_dict, self.q_0, self.F)


if __name__ == '__main__':
    m = DFA({'q0', 'q1'},
            {'a', 'b'},
            {'q0': {'a': 'q1', 'b': 'q0'},
             'q1': {'a': 'q0', 'b': 'q1'}
             },
            'q0',
            {'q0'})
    n = DFA({'q0', 'q1'},
            {'a', 'b'},
            {'q0': {'a': 'q0', 'b': 'q1'},
             'q1': {'a': 'q1', 'b': 'q0'}
             },
            'q0',
            {'q0'})
