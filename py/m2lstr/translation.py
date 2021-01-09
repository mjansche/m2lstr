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

"""Translation of well-formed formulas into finite automata."""

from typing import Iterable

from m2lstr import dfa
from m2lstr import wff


class TranslationVisitor(wff.Visitor):
    """Recursive translation of well-formed formulas into DFA."""
    # pylint: disable=abstract-method

    def __init__(self, alphabet: Iterable):
        self.alphabet = frozenset(alphabet)
        return

    def visit_exists(self, formula: wff.Exists) -> dfa.DFA:
        body_dfa = formula.body.accept(self)
        nfa = dfa.ProjectedNFA(body_dfa, formula.variable.name)
        return dfa.DeterminizedDFA(nfa)

    def visit_not(self, formula: wff.Not) -> dfa.DFA:
        body_dfa = formula.body.accept(self)
        return dfa.ComplementDFA(body_dfa)

    def visit_and(self, formula: wff.And) -> dfa.DFA:
        left_dfa = formula.left.accept(self)
        right_dfa = formula.right.accept(self)
        return dfa.IntersectionDFA(left_dfa, right_dfa)

    def visit_symbol(self, formula: wff.Symbol) -> dfa.DFA:
        return symbol_dfa(formula.symbol, formula.variable, self.alphabet)

    def visit_equal(self, formula: wff.Equal) -> dfa.DFA:
        return equal_dfa(formula.left, formula.right, self.alphabet)

    def visit_contained_in(self, formula: wff.ContainedIn) -> dfa.DFA:
        return contained_in_dfa(formula.left, formula.right, self.alphabet)

    def visit_singleton(self, formula: wff.Singleton) -> dfa.DFA:
        return singleton_dfa(formula.variable, self.alphabet)

    def visit_less(self, formula: wff.Less) -> dfa.DFA:
        return less_dfa(formula.left, formula.right, self.alphabet)


def universal_dfa(alphabet: Iterable) -> dfa.DFA:
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    builder.set_start(start)
    builder.set_final(start)
    for s in alphabet:
        builder.add_arc(start, start, s)
    return builder.build()


def symbol_dfa(symbol, variable: wff.Variable, alphabet: Iterable) -> dfa.DFA:
    assert symbol in alphabet
    var = variable.name
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    sink = builder.add_state()
    builder.set_start(start)
    builder.set_final(start)
    for s in alphabet:
        builder.add_arc(start, start, s, neg={var})
        nextstate = start if s == symbol else sink
        builder.add_arc(start, nextstate, s, pos={var})
        builder.add_arc(sink, sink, s)
    return builder.build()


def equal_dfa(left: wff.Variable, right: wff.Variable,
              alphabet: Iterable) -> dfa.DFA:
    x = left.name
    y = right.name
    if x == y:
        return universal_dfa(alphabet)
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    sink = builder.add_state()
    builder.set_start(start)
    builder.set_final(start)
    for s in alphabet:
        builder.add_arc(start, start, s, neg={x, y})
        builder.add_arc(start, start, s, pos={x, y})
        builder.add_arc(start, sink, s, pos={x}, neg={y})
        builder.add_arc(start, sink, s, pos={y}, neg={x})
        builder.add_arc(sink, sink, s)
    return builder.build()


def contained_in_dfa(left: wff.Variable, right: wff.Variable,
                     alphabet: Iterable) -> dfa.DFA:
    x = left.name
    y = right.name
    if x == y:
        return universal_dfa(alphabet)
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    sink = builder.add_state()
    builder.set_start(start)
    builder.set_final(start)
    for s in alphabet:
        builder.add_arc(start, start, s, neg={x})
        builder.add_arc(start, start, s, pos={x, y})
        builder.add_arc(start, sink, s, pos={x}, neg={y})
        builder.add_arc(sink, sink, s)
    return builder.build()


def singleton_dfa(variable: wff.Variable, alphabet: Iterable) -> dfa.DFA:
    var = variable.name
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    final = builder.add_state()
    sink = builder.add_state()
    builder.set_start(start)
    builder.set_final(final)
    for s in alphabet:
        builder.add_arc(start, start, s, neg={var})
        builder.add_arc(start, final, s, pos={var})
        builder.add_arc(final, final, s, neg={var})
        builder.add_arc(final, sink, s, pos={var})
        builder.add_arc(sink, sink, s)
    return builder.build()


def less_than_or_equal_dfa(left: wff.Variable, right: wff.Variable,
                           alphabet: Iterable) -> dfa.DFA:
    x = left.name
    y = right.name
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    final = builder.add_state()
    sink = builder.add_state()
    builder.set_start(start)
    builder.set_final(start)
    builder.set_final(final)
    for s in alphabet:
        builder.add_arc(start, start, s, neg={y})
        builder.add_arc(start, final, s, pos={y})
        builder.add_arc(final, final, s, neg={x})
        builder.add_arc(final, sink, s, pos={x})
        builder.add_arc(sink, sink, s)
    return builder.build()


def less_dfa(left: wff.Variable, right: wff.Variable,
             alphabet: Iterable) -> dfa.DFA:
    x = left.name
    y = right.name
    builder = dfa.DefaultDFA.builder()
    start = builder.add_state()
    final = builder.add_state()
    sink = builder.add_state()
    builder.set_start(start)
    builder.set_final(start)
    builder.set_final(final)
    for s in alphabet:
        builder.add_arc(start, sink,  s, pos={x, y})
        builder.add_arc(start, start, s, neg={x, y})
        builder.add_arc(start, start, s, pos={x}, neg={y})
        builder.add_arc(start, final, s, pos={y}, neg={x})
        builder.add_arc(final, final, s, neg={x})
        builder.add_arc(final, sink, s, pos={x})
        builder.add_arc(sink, sink, s)
    return builder.build()


def translate(formula: wff.WFF, alphabet: Iterable) -> dfa.DFA:
    simplified = wff.simplify(formula)
    visitor = TranslationVisitor(alphabet)
    return simplified.accept(visitor)
