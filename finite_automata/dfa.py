import os
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

    def rename(self):
        rename_dict = dict(zip(self.Q, {'q%s' % i for i in range(len(self.Q))}))
        rename_func = lambda x: rename_dict[x]
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

        print(initial_state, states)

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

        # input dfa graph generation

        G = pgv.AGraph(directed=True, rankdir='LR')
        G.add_node('qi', shape='point')
        G.add_node(initial_state, color='red')
        G.add_edge('qi', initial_state)
        [G.add_node(fs, shape='doublecircle', color='green:green') for fs in final_states]
        for tab in sorted(a):
            labels = []
            temp = tab
            for i in range(len(alpha)):
                label = G.get_edge(tab, a[tab][i]).attr['label'] + ',' + alpha[i] if G.has_edge(tab, a[tab][i]) else \
                alpha[i]
                G.add_edge(tab, a[tab][i], label=label)

        G.write('in.dot')
        G.layout()
        G.draw('in.png', prog='dot')
        os.system('eog in.png')

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

        # minimised dfa (output) graph

        G = pgv.AGraph(directed=True, rankdir='LR')
        G.add_node(fin_init, color='red')
        G.add_node('qi', shape='point')
        G.add_edge('qi', fin_init, label='start')
        [G.add_node(fs, peripheries=2, color='green:green') for fs in fin_final]
        for tab in sorted(table):
            for i in range(len(alpha)):
                label = G.get_edge(tab, ', '.join(table[tab][i])).attr['label'] + ',' + alpha[i] if G.has_edge(tab,
                                                                                                               ', '.join(
                                                                                                                   table[
                                                                                                                       tab][
                                                                                                                       i])) else \
                alpha[i]
                G.add_edge(tab, ', '.join(table[tab][i]), label=label)

        # output minimised dfa's description

        print("Iniital state of minimal dfa: " + fin_init + '\n')
        print("Final state of minimal dfa: " + ', '.join(fin_final) + '\n')
        print("Minimal DFA transition table:\n\n")
        print("{:<20}".format('States') + ''.join("{:<20}".format(i) for _, i in enumerate(alpha)))

        for tab in sorted(table):
            strs = [', '.join(i) for i in table[tab]]
            print("{:<20}".format(tab) + ''.join("{:<20}".format(i) for _, i in enumerate(strs)))

        # print minimised (output) graph

        G.write('out.dot')
        G.layout()
        G.draw('out.png', prog='dot')
        os.system('eog out.png')

    def draw(self, filename):
        G = pgv.AGraph(directed=True, rankdir='LR')
        G.add_node('qi', shape='point')
        for q in self.Q:
            G.add_node(q, shape='oval', peripheries=2 if q in self.F else 1)
        G.add_edge('qi', self.q_0, label='start')
        for u in self.𝛿_dict:
            for a, v in self.𝛿_dict[u].items():
                label = G.get_edge(u, v).attr['label'] + ',' + a if G.has_edge(u, v) else a
                G.add_edge(u, v, label=label)
        G.draw(filename, format='png', prog='dot')


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
    m.minimize()
