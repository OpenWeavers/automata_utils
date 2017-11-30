from functools import reduce
import pygraphviz as pgv
import itertools
from collections import defaultdict
from finite_automata.fa import FA
from finite_automata.dfa import DFA


class ENFA(FA):
    def __init__(self, Q, Σ, δ_dict, q_0, F):
        def set_combi(s, r):
            for i in itertools.combinations(s, r):
                yield frozenset(i)

        self.P_Q = set(itertools.chain.from_iterable(set_combi(Q, r) for r in range(0, len(Q) + 1)))
        self.extra = {'ϵ'}
        assert set(δ_dict.keys()).intersection(Q) == Q
        assert all(
            set(δ_dict[d].keys()).intersection(Σ.union({'ϵ'})) == Σ.union({'ϵ'})
            and all(x in self.P_Q for x in δ_dict[d].values())
            for d in δ_dict)

        assert q_0 in Q
        assert F <= Q  # Subset or Equal
        FA.__init__(self, Q, Σ, δ_dict, q_0, F)

    def ϵClosure(self, q):
        res = frozenset({q})
        queue = [q]
        while queue:
            u = queue.pop(0)
            for v in self.δ(u, 'ϵ'):
                if v not in res:
                    res = res.union({v})
                    queue.append(v)
        return res

    def δ_set(self, Q, a):
        res = frozenset()
        for q in Q:
            res = res.union(self.δ(q, a))
        res = frozenset(map(lambda x: self.ϵClosure(x), res))
        res = reduce(lambda x, y: x.union(y), res, frozenset())
        return res

    def is_accepted(self, w):
        return reduce(self.δ_set, w, self.ϵClosure(self.q_0)).intersection(self.F) != frozenset()

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
        Q = {self.ϵClosure(self.q_0)}
        queue = [self.ϵClosure(self.q_0)]
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
        q_0 = self.ϵClosure(self.q_0)
        return DFA(Q, self.Σ, δ_dict, q_0, F)


if __name__ == '__main__':
    s_q = ['q' + str(x) for x in range(6)]
    s_sigma = ['+,-', '.', '0,1,...,9']
    s_delta = [
        [[1], [1], [], []],
        [[], [], [2], [1, 4]],
        [[], [], [], [3]],
        [[5], [], [], [3]],
        [[], [], [3], []],
        [[], [], [], []]
    ]
    # HORRIBLE LINES OF CODE BELOW
    '''s_delta = reduce(lambda xx, yy: {**xx, **yy}, list(map(lambda x: {x[0]: x[1]}, zip(s_q, map(
        lambda x: reduce(lambda p, q: {**p, **q},
                         list(map(lambda y: {y[0]: frozenset(['q' + str(z) for z in y[1]])}, zip(['ϵ'] + s_sigma, x)))),
        s_delta)))))'''
    # SIMPLIFIED VERSION ;)
    s_delta = dict(
        zip(s_q, list(map(lambda x: dict(zip(['ϵ'] + s_sigma, x)),
                          [[frozenset(['q' + str(z) for z in y]) for y in x] for x in s_delta]
                          )
                      )
            )
    )
    s = ENFA(set(s_q), set(s_sigma), s_delta, 'q0', {'q5'})
    print(s.is_accepted(map(lambda x: '+,-' if '+' in x or '-' in x else '0,1,...,9' if x.isdigit() else x, '-.23')))
    s = ENFA({'q0','q1'}, {'a', 'b'}, {'q0': dict(zip({'a', 'b', 'ϵ'}, [frozenset(), frozenset(), frozenset({'q1'})])),
                                     'q1': dict(zip({'a', 'b', 'ϵ'}, [frozenset(), frozenset(), frozenset()]))}, 'q0',
             set())
    s.draw('digit.png')
    s.to_dfa().draw('digitdfa.png')
