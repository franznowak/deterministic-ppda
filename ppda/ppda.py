import random
from fractions import Fraction
from collections import defaultdict as dd
from ppda.base.symbol import Sym, BOT
from ppda.base.string import String
from enum import IntEnum, unique

# States
Q_INIT = 0
Q_FINAL = -1

@unique
class Action(IntEnum):
    NOOP = 0
    POP = 1

class PPDA:
    """Implements deterministic probabilistic PDA"""
    def __init__(
            self, 
            Σ={Sym("a"), Sym("b"), Sym("c")},
            Γ={BOT, Sym("0"), Sym("1")},
            seed: int = 42
            ):
        # DEFINITION
        # A deterministc probabilistic pushdown automaton is a 5-tuple <Q, Γ, Σ, δ, p> where
        # • Q is a set of states;
        # • Γ is an alphabet of stack symbols
        # • Σ is an alphabet of symbols;
        # • δ is a transition function Q × Γ x Σ -> Q x Action × Γ U {NONE};
        # • p is a normalised weighting function Q x Γ x Σ -> ℚ.

        self.Σ = Σ # alphabet
        self.Γ = Γ # stack alphabet
        self.Q = {Q_INIT, Q_FINAL} # set of states

        self.δ = {} # transition function
        self.p = dd(lambda: Fraction(0,1)) # weighting function

        self.stack = [BOT] # stack of the PPDA
        self.q = Q_INIT # current state

        random.seed(seed)

    @property
    def γ(self):
        """Returns the current top stack symbol"""
        return self.stack[-1]
    
    @property
    def normalized(self):
        """Returns true iff the PPDA is correctly locally normalized"""
        for q in self.Q.difference({Q_FINAL}):
            for γ in self.Γ:
                w = Fraction(0,1)
                present = False
                for sym in self.Σ:
                    if (q, γ, sym) in self.δ:
                        present = True
                    w += self.p[q, γ, sym]
                if present and w != Fraction(1,1):
                    print(q, γ, w)
                    return False
        return True

    def reset(self):
        """Resets the PPDA to its initial state"""
        self.stack = [BOT]
        self.q = Q_INIT
        
    def add(self, q1, γ1, sym, q2, a, γ2, w):
        """Adds a new transition to the transition and weighting functions"""
        self.Σ.add(sym)
        self.Γ.add(γ1)
        self.Γ.add(γ2)
        self.Q.add(q1)
        self.Q.add(q2)

        self.δ[q1, γ1, sym] = q2, a, γ2
        self.p[q1, γ1, sym] = w

    def step(self, sym):
        """Performs a computation step in the PPDA"""
        w = self.p[self.q, self.γ, sym]
        if w == Fraction(0,1):
            return w
        q2, a, γ2 = self.δ[self.q, self.γ, sym]
        if a == Action.POP:
            assert self.γ != BOT, "tried to pop empty stack"
            self.stack.pop()
        if γ2 is not None:
            self.stack.append(γ2)
        self.q = q2
        return w

    def accept(self, y):
        """Returns the weight of a given string in the PPDA"""
        y = String(y)
        self.reset()
        w = Fraction(1,1)
        for sym in y:
            w *= self.step(sym)
        return w
    
    def generate(self):
        """Generates a random string according to the PPDAs probability distribution"""
        self.reset()
        w = Fraction(1,1)
        output = String([])
        while True:
            sym = self._sample()
            output.append(sym)
            w *= self.step(sym)

            if self.q == Q_FINAL:
                return str(output), w
            
    def _sample(self):
        """Samples a random symbol given the current state and stack"""
        r = random.random()
        q = Fraction(0,1)

        assert self.normalized, "ppda δ not probabilistic"

        for sym in self.Σ:
            q += self.p[self.q, self.γ, sym]
            if q >= r:
                return sym
