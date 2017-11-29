import prettytable


class FA:
    def __init__(self, Q, Σ, 𝛿_dict, q_0, F):
        self.Q = Q
        self.Σ = Σ
        self.𝛿_dict = 𝛿_dict
        self.q_0 = q_0
        self.F = F
        self.extra = set()

    def 𝛿(self, q, a):
        return self.𝛿_dict[q][a]

    def __str__(self):
        desc = prettytable.PrettyTable(['Parameter', 'Value'])
        desc.add_row(["Q", "{%s}" % ', '.join(str(q) for q in self.Q)])
        desc.add_row(["Σ", "{%s}" % ', '.join(self.Σ)])
        desc.add_row(["q_0", str(self.q_0)])
        desc.add_row(["F", "{%s}" % ', '.join(str(f) for f in self.F)])
        if self.extra:
            desc.add_row(["Extra Symbols", self.extra])
        delta = prettytable.PrettyTable(['𝛿'] + list(self.Σ.union(self.extra)))
        for q in self.Q:
            delta.add_row([q] + [self.𝛿(q, a) for a in self.Σ.union(self.extra)])
        desc.add_row(["𝛿", str(delta)])
        return str(desc)
