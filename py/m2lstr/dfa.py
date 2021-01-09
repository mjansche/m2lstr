# Copyright 2020 the m2lstr Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Deterministic finite automata representations and operations."""

from abc import abstractmethod
import collections
import itertools
from typing import Container, Dict, FrozenSet, Hashable, Iterable, Iterator
from typing import List, Set, Tuple


Arc = collections.namedtuple(
    'Arc', ['symbol', 'pos', 'neg', 'nextstate'])


class RhoSymbol:
    def __str__(self):
        return 'ρ'


RHO_SYMBOL = RhoSymbol()


class SymbolToArcsMapping(Container, Iterable):
    """Abstract base class for a collection of arcs indexed by symbol."""

    @abstractmethod
    def __contains__(self, symbol) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator:
        raise NotImplementedError

    @abstractmethod
    def for_symbol(self, symbol) -> Iterable[Arc]:
        """Iterates over all arcs for the given symbol."""
        raise NotImplementedError

    def can_match(self, symbol) -> bool:
        """Indicates whether the symbol is mapped, possibly via fallback."""
        return symbol in self or RHO_SYMBOL in self

    def iterarcs(self) -> Iterator[Arc]:
        """Iterates over all arcs."""
        for symbol in self:
            yield from self.for_symbol(symbol)
        return


class DictionaryArcs(SymbolToArcsMapping):
    """Collection of arcs indexed by symbol that is backed by a dictionary."""

    def __init__(self, symbol_to_arcs: Dict[Hashable, List[Arc]]):
        self.symbol_to_arcs = symbol_to_arcs
        return

    def __contains__(self, symbol) -> bool:
        return symbol in self.symbol_to_arcs

    def __iter__(self) -> Iterator:
        return iter(self.symbol_to_arcs)

    def for_symbol(self, symbol) -> Iterable[Arc]:
        if symbol in self.symbol_to_arcs:
            return self.symbol_to_arcs[symbol]
        return self.symbol_to_arcs[RHO_SYMBOL]


class DFA:
    """Abstract base class for deterministic finite automata."""

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def final(self, state) -> bool:
        pass

    @abstractmethod
    def arcs_at(self, state) -> SymbolToArcsMapping:
        pass


class DefaultDFA(DFA):
    """Immutable default DFA implementation."""

    @staticmethod
    def builder():
        return DefaultBuilder()

    def __init__(self, start_state, final_states, arcs_at_state):
        self.start_state = start_state
        self.final_states = final_states
        self.arcs_at_state = arcs_at_state
        return

    def start(self):
        return self.start_state

    def final(self, state) -> bool:
        return state in self.final_states

    def arcs_at(self, state) -> SymbolToArcsMapping:
        return self.arcs_at_state[state]


def default_state_generator():
    """Default factory for generating new state identifiers."""
    state = 0
    while True:
        yield state
        state += 1
    return


class DefaultBuilder:
    """Builder for DefaultDFA."""

    def __init__(self, state_generator=default_state_generator()):
        self.state_generator = state_generator
        self.start_state = None
        self.final_states = set()
        self.arcs_at_state = {}
        return

    def add_state(self):
        state = next(self.state_generator)
        self.arcs_at_state[state] = {}
        return state

    def set_start(self, state):
        self.start_state = state
        return

    def set_final(self, state):
        self.final_states.add(state)
        return

    def add_arc(self, state, nextstate, symbol,
                pos=frozenset(), neg=frozenset()):
        arcs_for_symbol = self.arcs_at_state[state]
        if symbol not in arcs_for_symbol:
            arcs_for_symbol[symbol] = []
        arc_list = arcs_for_symbol[symbol]
        arc_list.append(Arc(symbol, pos, neg, nextstate))
        return

    def build(self):
        return DefaultDFA(
            self.start_state, self.final_states,
            {s: DictionaryArcs(a) for (s, a) in self.arcs_at_state.items()})


def intersect_arcs(left: Arc, right: Arc):
    """Yields the intersection of two arcs."""
    assert not left.pos & left.neg
    assert not right.pos & right.neg
    if left.symbol == right.symbol or right.symbol == RHO_SYMBOL:
        symbol = left.symbol
    elif left.symbol == RHO_SYMBOL:
        symbol = right.symbol
    else:
        return
    pos = left.pos | right.pos
    neg = left.neg | right.neg
    if pos & neg:
        return
    nextstate = left.nextstate, right.nextstate
    yield Arc(symbol, pos, neg, nextstate)
    return


class IntersectionArcs(SymbolToArcsMapping):
    """Collection of arcs indexed by symbol for the intersection of DFAs."""

    def __init__(self, left: SymbolToArcsMapping, right: SymbolToArcsMapping):
        self.left = left
        self.right = right
        symbols = {sym for sym in right if left.can_match(sym)}
        symbols |= {sym for sym in left if right.can_match(sym)}
        self.symbols = frozenset(symbols)
        return

    def __contains__(self, symbol) -> bool:
        return symbol in self.symbols

    def __iter__(self) -> Iterator:
        return iter(self.symbols)

    def for_symbol(self, symbol) -> Iterator[Arc]:
        for left_arc in self.left.for_symbol(symbol):
            for right_arc in self.right.for_symbol(symbol):
                yield from intersect_arcs(left_arc, right_arc)
        return


class IntersectionDFA(DFA):
    """Lazy intersection of two DFAs."""

    def __init__(self, left: DFA, right: DFA):
        self.left = left
        self.right = right
        return

    def start(self):
        return self.left.start(), self.right.start()

    def final(self, state) -> bool:
        left_state, right_state = state
        return self.left.final(left_state) and self.right.final(right_state)

    def arcs_at(self, state) -> SymbolToArcsMapping:
        left_state, right_state = state
        return IntersectionArcs(self.left.arcs_at(left_state),
                                self.right.arcs_at(right_state))


class ComplementDFA(DFA):
    """Lazy complement of a DFA."""

    def __init__(self, dfa: DFA):
        self.dfa = dfa
        return

    def start(self):
        return self.dfa.start()

    def final(self, state) -> bool:
        return not self.dfa.final(state)

    def arcs_at(self, state) -> SymbolToArcsMapping:
        return self.dfa.arcs_at(state)


class ProjectedArcs(SymbolToArcsMapping):
    """Collection of arcs indexed by symbol for the projection of a DFA."""

    def __init__(self, symbol_to_arcs: SymbolToArcsMapping, variable):
        self.symbol_to_arcs = symbol_to_arcs
        self.variable = variable
        return

    def __contains__(self, symbol) -> bool:
        return symbol in self.symbol_to_arcs

    def __iter__(self) -> Iterator:
        return iter(self.symbol_to_arcs)

    def for_symbol(self, symbol) -> Iterator[Arc]:
        for arc in self.symbol_to_arcs.for_symbol(symbol):
            if self.variable in arc.pos:
                assert self.variable not in arc.neg
                yield Arc(arc.symbol, arc.pos - {self.variable}, arc.neg,
                          arc.nextstate)
            elif self.variable in arc.neg:
                assert self.variable not in arc.pos
                yield Arc(arc.symbol, arc.pos, arc.neg - {self.variable},
                          arc.nextstate)
            else:
                yield arc
        return


class ProjectedNFA(DFA):
    """Lazy projection of a finite automaton."""

    def __init__(self, dfa: DFA, variable):
        self.dfa = dfa
        self.variable = variable
        return

    def start(self):
        return self.dfa.start()

    def final(self, state) -> bool:
        return self.dfa.final(state)

    def arcs_at(self, state) -> SymbolToArcsMapping:
        return ProjectedArcs(self.dfa.arcs_at(state), self.variable)


class DeterminizedArcs(SymbolToArcsMapping):
    """Collection of arcs indexed by symbol for a determinized FA."""

    def __init__(self, mappings: List[SymbolToArcsMapping]):
        self.mappings = mappings
        symbols: Set = set()
        for m in mappings:
            symbols.update(m)
        self.symbols = frozenset(symbols)
        return

    def __contains__(self, symbol) -> bool:
        return symbol in self.symbols

    def __iter__(self) -> Iterator:
        return iter(self.symbols)

    def for_symbol(self, symbol) -> Iterator[Arc]:
        # TODO: Handle RHO_SYMBOL properly.
        variables = set()
        for mapping in self.mappings:
            for arc in mapping.for_symbol(symbol):
                variables.update(arc.pos)
                variables.update(arc.neg)
        arcs: Dict[Tuple[FrozenSet, FrozenSet], Set] = {}
        for k in range(len(variables) + 1):
            for subset in itertools.combinations(variables, k):
                pos = frozenset(subset)
                neg = frozenset(variables - pos)
                arcs[pos, neg] = set()
        for mapping in self.mappings:
            for arc in mapping.for_symbol(symbol):
                for key in arcs:
                    pos, neg = key
                    if not pos & arc.neg and not neg & arc.pos:
                        arcs[pos, neg].add(arc.nextstate)
        for key in arcs:
            pos, neg = key
            yield Arc(symbol, pos, neg, frozenset(arcs[pos, neg]))
        return


class DeterminizedDFA(DFA):
    """Lazy determinization of a finite automaton."""

    def __init__(self, nfa):
        self.nfa = nfa
        return

    def start(self):
        return frozenset({self.nfa.start()})

    def final(self, state) -> bool:
        return any(self.nfa.final(s) for s in state)

    def arcs_at(self, state) -> SymbolToArcsMapping:
        return DeterminizedArcs([self.nfa.arcs_at(s) for s in state])


def transition(automaton, state, symbol):
    arcs = automaton.arcs_at(state).for_symbol(symbol)
    nextstates = {arc.nextstate for arc in arcs}
    assert len(nextstates) == 1
    return nextstates.pop()


def accepts(automaton: DFA, seq: Iterable) -> bool:
    """Checks if the DFA accepts the given sequence of symbols."""
    state = automaton.start()
    for symbol in seq:
        state = transition(automaton, state, symbol)
    return automaton.final(state)
