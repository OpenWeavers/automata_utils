from functools import reduce
import pygraphviz as pgv
import itertools
from collections import defaultdict
from finite_automata.fa import FA
from finite_automata.dfa import DFA


class NFA(FA):
    def __init__(self, Q, Σ, δ_dict, q_0, F):
        def set_combi(s, r):
            for i in itertools.combinations(s, r):
                yield frozenset(i)

        self.P_Q = set(itertools.chain.from_iterable(set_combi(Q, r) for r in range(0, len(Q) + 1)))
        assert set(δ_dict.keys()).intersection(Q) == Q
        assert all(
            set(δ_dict[d].keys()).intersection(Σ) == Σ
            and all(x in self.P_Q for x in δ_dict[d].values())
            for d in δ_dict)
        assert q_0 in Q
        assert F <= Q  # Subset or Equal
        FA.__init__(self, Q, Σ, δ_dict, q_0, F)

    def δ_set(self, Q, a):
        res = frozenset()
        for q in Q:
            res = res.union(self.δ(q, a))
        return res

    def is_accepted(self, w):
        return reduce(self.δ_set, w, {self.q_0}).intersection(self.F) != frozenset()

    def draw(self, filename):
        G = pgv.AGraph(directed=True, rankdir='LR')
        G.add_node('qi', shape='point')
        for q in self.Q:
            G.add_node(q, shape='oval', peripheries=2 if q in self.F else 1)
        G.add_edge('qi', self.q_0, label='start')
        for u in self.δ_dict:
            for a, V in self.δ_dict[u].items():
                for v in V:
                    label = G.get_edge(u, v).attr['label'] + ',' + a if G.has_edge(u, v) else a
                    G.add_edge(u, v, label=label)
        G.draw(filename, format='png', prog='dot')

    def to_dfa(self):
        Q = {frozenset({self.q_0})}
        queue = [frozenset({self.q_0})]
        δ_dict = defaultdict(dict)
        while queue:
            current_state = queue.pop(0)
            for a in self.Σ:
                next_state = self.δ_set(current_state, a)
                δ_dict[current_state][a] = next_state
                if next_state not in Q:
                    Q = Q.union({next_state})
                    queue.append(next_state)
        F = {x for x in Q if x.intersection(self.F) != frozenset()}
        q_0 = frozenset({self.q_0})
        return DFA(Q, self.Σ, δ_dict, q_0, F)


if __name__ == '__main__':
    m = NFA({'q0', 'q1', 'q2'},
            {'a', 'b'},
            {'q0': {'a': frozenset({'q1', 'q0'}), 'b': frozenset({'q0'})},
             'q1': {'a': frozenset(), 'b': frozenset({'q2'})},
             'q2': {'a': frozenset(), 'b': frozenset()}
             },
            'q0',
            {'q2'})
    m.draw('nfa.png')
    m.to_dfa().rename().draw('dfa_*ab.png')
    m.is_accepted('aaaaaaababbabbab')
