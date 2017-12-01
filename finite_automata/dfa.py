from collections import defaultdict
from functools import reduce
import pygraphviz as pgv
from finite_automata.fa import FA


class DFA(FA):
    def __init__(self, Q, Σ, δ_dict, q_0, F):
        assert set(δ_dict.keys()).intersection(Q) == Q
        assert all(
            set(δ_dict[d].keys()).intersection(Σ) == Σ
            and all(x in Q for x in δ_dict[d].values())
            for d in δ_dict)
        assert q_0 in Q
        assert F <= Q  # Subset or Equal
        FA.__init__(self, Q, Σ, δ_dict, q_0, F)

    def rename(self, start=0):
        rename_dict = dict(zip(self.Q, {'q%s' % (start + i) for i in range(len(self.Q))}))

        def rename_func(x):
            return rename_dict[x]

        Q = set(map(rename_func, self.Q))
        q_0 = rename_func(self.q_0)
        F = set(map(rename_func, self.F))
        new_delta = defaultdict(dict)
        for q, A in self.δ_dict.items():
            for a in A:
                new_delta[rename_func(q)][a] = rename_func(self.δ_dict[q][a])
        return DFA(Q, self.Σ, new_delta, q_0, F)

    def is_accepted(self, w):
        return reduce(self.δ, w, self.q_0) in self.F

    def minimize(self):
        states = list(self.Q)
        alpha = list(self.Σ)
        initial_state = self.q_0
        final_states = list(self.F)

        # print(initial_state, states)

        a = {}

        for ele in states:
            a[ele] = []

        for ele in states:
            for alp in alpha:
                a[ele].append(self.δ_dict[ele][alp])

        mat = []
        for i in range(len(states) - 1):
            mat.append([0 for i in range(i + 1)])
            [mat[i].append(-1) for j in range(i + 1, len(states) - 1)]

        # final states position finder

        index_lst = [states.index(i) for i in final_states]

        for i in index_lst:
            for j in range(len(states) - 1):
                for k in range(j + 1):
                    if i - 1 == j and k not in index_lst:
                        mat[j][k] = 1
                    elif i == k and j + 1 not in index_lst:
                        mat[j][k] = 1

        # recursive defn. for looping through 'mat' till no operation was done

        flag = True
        while flag:
            flag3 = True
            for i in range(len(states) - 1):
                for j in range(i + 1):
                    if mat[i][j] == 0:
                        r = states[i + 1]
                        c = states[j]
                        t = 0
                        flag2 = True

                        while t < len(alpha) and flag2:

                            if a[r][t] != a[c][t]:
                                r1 = states.index(a[r][t]) - 1
                                c1 = states.index(a[c][t])

                                if c1 == len(states) - 1 or mat[r1][c1] == -1 or r1 == -1 or c1 == -1:
                                    r1, c1 = c1 - 1, r1 + 1

                                if mat[r1][c1] == 1:
                                    mat[i][j] = 1
                                    flag3 = False
                                    flag2 = False
                            t += 1

            if flag3:
                flag = False

        # equivalent pair finder

        pairs = []
        for i in range(len(states) - 1):
            for j in range(i + 1):
                if mat[i][j] == 0:
                    pairs.append((min(states[i + 1], states[j]), max(states[i + 1], states[j])))

        # transitive property applier (on pairs)

        i, j = 0, 0
        flag = True

        while flag:
            i, j = 0, 0
            flag = False
            while i < len(pairs):
                j = 0
                while j < len(pairs):
                    if i != j and len(set(pairs[i]).intersection(pairs[j])) > 0:
                        temp1 = set(pairs[i]).union(pairs[j])
                        pairs.pop(i)
                        if i > j:
                            pairs.pop(j)
                        else:
                            pairs.pop(j - 1)
                        pairs.append(temp1)
                        flag = True
                    j += 1
                i += 1

        # actual state to merged pairs

        tab_dict = {}

        for ele in states:
            flag = True
            for i in range(len(pairs)):
                if ele in pairs[i]:
                    tab_dict[ele] = sorted(list(pairs[i]))
                    flag = False
                    break
            if flag:
                tab_dict[ele] = [ele]

        # minimized table generation

        table = {}

        for ele in sorted(tab_dict):
            table[', '.join(tab_dict[ele])] = []
            for i in range(len(alpha)):
                table[', '.join(tab_dict[ele])].append(sorted(tab_dict[a[tab_dict[ele][0]][i]]))
                for j in range(1, len(tab_dict[ele])):
                    table[', '.join(tab_dict[ele])][i] = sorted(
                        set(table[', '.join(tab_dict[ele])][i]).union(tab_dict[a[tab_dict[ele][j]][i]]))

        # initial and final state(s) finder for minimised dfa

        fin_final = []
        fin_init = None
        for tab in table:
            if initial_state in tab:
                fin_init = tab
            [fin_final.append(tab) for fs in final_states if fs in tab]

        fin = {}
        for tab in sorted(table):
            strs = [', '.join(i) for i in table[tab]]
            fin[tab] = {}
            for alp in alpha:
                # print("{:<20}".format(tab) + ''.join("{:<20}".format(i) for _, i in enumerate(strs)))
                # print(strs)
                fin[tab][alp] = strs.pop(0)

        print("Minimized Successfully")

        return DFA(set(sorted(table)), set(alpha), fin, fin_init, set(fin_final))

    def draw(self, filename, prog='dot'):
        G = pgv.AGraph(directed=True, rankdir='LR')
        G.add_node('qi', shape='point')
        for q in self.Q:
            G.add_node(q, shape='oval', peripheries=2 if q in self.F else 1)
        G.add_edge('qi', self.q_0, label='start')
        for u in self.δ_dict:
            for a, v in self.δ_dict[u].items():
                label = G.get_edge(u, v).attr['label'] + ',' + a if G.has_edge(u, v) else a
                G.add_edge(u, v, label=label)
        G.draw(filename, format='png', prog=prog)

    def union(self, M):
        assert self.Σ == M.Σ
        Q = {(x, y) for x in self.Q for y in M.Q}
        delta_dict = {(x, y): {a: (self.δ(x, a), M.δ(y, a)) for a in self.Σ} for (x, y) in Q}
        F = {(x, y) for x in self.Q for y in M.Q if x in self.F or y in M.F}
        return DFA(Q, self.Σ, delta_dict, (self.q_0, M.q_0), F)

    def intersection(self, M):
        assert self.Σ == M.Σ
        Q = {(x, y) for x in self.Q for y in M.Q}
        delta_dict = {(x, y): {a: (self.δ(x, a), M.δ(y, a)) for a in self.Σ} for (x, y) in Q}
        F = {(x, y) for x in self.F for y in M.F}
        return DFA(Q, self.Σ, delta_dict, (self.q_0, M.q_0), F)

    def difference(self, M):
        assert self.Σ == M.Σ
        Q = {(x, y) for x in self.Q for y in M.Q}
        delta_dict = {(x, y): {a: (self.δ(x, a), M.δ(y, a)) for a in self.Σ} for (x, y) in Q}
        F = {(x, y) for x in self.F for y in M.F if x in self.F and y not in M.F}
        return DFA(Q, self.Σ, delta_dict, (self.q_0, M.q_0), F)

    def compliment(self):
        return DFA(self.Q, self.Σ, self.δ_dict, self.q_0, self.Q - self.F)

    def reduce(self):
        state_pairs = {frozenset({x, y}) for x in self.Q for y in self.Q if x != y}
        non_distinguishable_pairs = set()
        non_distinguishable_states = set()
        distinguishable_pairs = {x for x in state_pairs if len(set(x).intersection(self.F)) == 1}

        def is_distinguishable(pair):
            # Recursive Discovery of Distinguishable Pairs with Memory Function
            if len(pair) == 1:
                return False
            if pair in distinguishable_pairs:
                return True
            else:
                for a in self.Σ:
                    next_pair = frozenset(map(lambda x: self.δ(x, a), pair))
                    if is_distinguishable(next_pair):
                        distinguishable_pairs.update({pair})
                        return True
                return False

        for pair in state_pairs:
            if not is_distinguishable(pair):
                non_distinguishable_pairs.update({pair})
                non_distinguishable_states.update(pair)

        def transitive_closure(array):
            new_list = [frozenset(array.pop(0))]  # initialize first set with value of index `0`

            for item in array:
                for i, s in enumerate(new_list):
                    if any(x in s for x in item):
                        new_list[i] = new_list[i].union(item)
                        break
                else:
                    new_list.append(frozenset(item))
            return set(new_list)

        non_distinguishable_pairs = transitive_closure(list(non_distinguishable_pairs))

        Q = non_distinguishable_pairs.union({frozenset(x) for x in self.Q - non_distinguishable_states})
        delta_dict = defaultdict(dict)
        for q in Q:
            for a in self.Σ:
                delta_dict[q][a] = list({x for x in Q if x.intersection(set(map(lambda x:self.δ(x,a),q)))})[0]
        q_0 = [x for x in Q if self.q_0 in x][0]
        F = {x for x in Q if x.intersection(self.F)}
        print(Q, set(delta_dict[list(Q)[0]].values()), sep='\n')
        return DFA(Q, self.Σ, delta_dict, q_0, F)

    def to_enfa(self):
        from finite_automata.enfa import ENFA
        delta_dict = defaultdict(dict)
        for u in self.δ_dict:
            for a in self.δ_dict[u]:
                delta_dict[u][a] = frozenset({self.δ(u, a)})
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
    m.draw('dfa.png')
    print(m.is_accepted('aaaba'))
    n = DFA({'q0', 'q1'},
            {'a', 'b'},
            {'q0': {'a': 'q0', 'b': 'q1'},
             'q1': {'a': 'q1', 'b': 'q0'}
             },
            'q0',
            {'q0'})
    o = DFA({'C', 'D', 'E'},
            {0, 1},
            {'C': {0: 'D', 1: 'E'},
             'D': {0: 'D', 1: 'E'},
             'E': {0: 'C', 1: 'E'}},
            'C',
            {'C', 'D'})
    import string

    p_q = list(string.ascii_uppercase[:8])
    p_sigma = [0, 1]
    p_f = {'C'}
    p_q0 = 'A'
    p_delta = ['BF', 'GC', 'AC', 'CG', 'HF', 'CG', 'GE', 'GC']
    p_delta = [dict(zip(p_sigma, list(x))) for x in p_delta]
    p_delta = dict(zip(p_q, p_delta))
    p = DFA(set(p_q), set(p_sigma), p_delta, p_q0, p_f)
    p.draw('dfa.png')
    p.reduce().draw('dfa_minimized.png')
