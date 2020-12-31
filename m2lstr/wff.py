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

"""Well-formed formulas of Monadic Second-Order Logic over Strings."""


class Variable:
    """A first-order or second-order variable."""

    def __init__(self, name: str, order: int = 1):
        assert order in (1, 2)
        self.name = name
        self.order = order
        return

    ORDER_PRETTY = {1: '¹', 2: '²'}

    def order_pretty(self) -> str:
        return Variable.ORDER_PRETTY[self.order]

    def __repr__(self):
        return 'Variable({!r}, {!r})'.format(self.name, self.order)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        # type: ignore
        # NB: Abuse of operator overload for syntactic sugar.
        return Equal(self, other)

    def __ne__(self, other):
        # type: ignore
        # NB: Abuse of operator overload for syntactic sugar.
        return Not(Equal(self, other))

    def __lt__(self, other: 'Variable') -> 'WFF':
        return Less(self, other)

    def __gt__(self, other: 'Variable') -> 'WFF':
        return Less(other, self)

    def __le__(self, other: 'Variable') -> 'WFF':
        return Or(Less(self, other), Equal(self, other))

    def __ge__(self, other: 'Variable') -> 'WFF':
        return Or(Less(other, self), Equal(self, other))


class WFF:
    """Base class for well-formed formulas."""

    def __and__(self, other: 'WFF') -> 'WFF':
        return And(self, other)

    def __or__(self, other: 'WFF') -> 'WFF':
        return Or(self, other)

    def __invert__(self) -> 'WFF':
        return Not(self)


class Exists(WFF):
    """Existentially quantified formula."""

    def __init__(self, variable: 'Variable', wff: WFF):
        self.variable = variable
        self.wff = wff
        return

    def __repr__(self):
        return 'Exists({!r}, {!r})'.format(self.variable, self.wff)

    def __str__(self):
        return '∃{}{} {}'.format(
            self.variable.order_pretty(), self.variable, self.wff)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_exists(self)


class Forall(WFF):
    """Universally quantified formula."""

    def __init__(self, variable: Variable, wff: WFF):
        self.variable = variable
        self.wff = wff
        return

    def __repr__(self):
        return 'Forall({!r}, {!r})'.format(self.variable, self.wff)

    def __str__(self):
        return '∀{}{} {}'.format(
            self.variable.order_pretty(), self.variable, self.wff)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_forall(self)


class Not(WFF):
    """Logical negation of a propositional formula."""

    def __init__(self, wff: WFF):
        self.wff = wff
        return

    def __repr__(self):
        return 'Not({!r})'.format(self.wff)

    def __str__(self):
        return '¬{}'.format(self.wff)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_not(self)


class And(WFF):
    """Conjunction of two propositional formulas."""

    def __init__(self, left: WFF, right: WFF):
        self.left = left
        self.right = right
        return

    def __repr__(self):
        return 'And({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        return '[{} ∧ {}]'.format(self.left, self.right)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_and(self)


class If(WFF):
    """Material implication between two propositional formulas."""

    def __init__(self, left: WFF, right: WFF):
        self.left = left
        self.right = right
        return

    def __repr__(self):
        return 'If({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        return '[{} → {}]'.format(self.left, self.right)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_if(self)


class Or(WFF):
    """Disjunction of two propositional formulas."""

    def __init__(self, left: WFF, right: WFF):
        self.left = left
        self.right = right
        return

    def __repr__(self):
        return 'Or({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        return '[{} ∨ {}]'.format(self.left, self.right)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_or(self)


class ContainedIn(WFF):
    """Predicate formula asserting a containment relationship among positions.

    ContainedIn(x, Y) means x is an element of Y, also written as Y(x).
    ContainedIn(X, Y) means X is a subset of Y.
    """

    def __init__(self, left: Variable, right: Variable):
        assert right.order == 2
        self.left = left
        self.right = right
        return

    def __repr__(self):
        return 'ContainedIn({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        if self.left.order == 1:
            return '[{} ∈ {}]'.format(self.left, self.right)
        return '[{} ⊆ {}]'.format(self.left, self.right)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_contained_in(self)


class Equal(WFF):
    """Predicate formula asserting equality between two variables."""

    def __init__(self, left: Variable, right: Variable):
        self.left = left
        self.right = right
        return

    def __repr__(self):
        return 'Equal({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        return '[{} == {}]'.format(self.left, self.right)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_equal(self)


class Less(WFF):
    """Predicate formula asserting linear precedence among positions.

    [x < y] means position x precedes position y.
    [X < Y] means any position in X precedes any position in Y.
    [x < Y] means position x precedes any position in Y.
    [X < y] means any position in X precedes position y.
    """

    def __init__(self, left: Variable, right: Variable):
        self.left = left
        self.right = right
        return

    def __repr__(self):
        return 'Less({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        return '[{} < {}]'.format(self.left, self.right)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_less(self)


class Singleton(WFF):
    """Predicate formula asserting that a collection is a singleton."""

    def __init__(self, variable: Variable):
        self.variable = variable
        return

    def __repr__(self):
        return 'Singleton({!r})'.format(self.variable)

    def __str__(self):
        return 'Singleton({})'.format(self.variable)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_singleton(self)


class Symbol(WFF):
    """Predicate formula relating a position variable to a symbol.

    "a"(x) says that position x is labeled with the symbol "a".
    "a"(X) says that all positions in X are labeled with the symbol "a".
    """

    def __init__(self, symbol: str, variable: Variable):
        self.symbol = symbol
        self.variable = variable
        return

    def __repr__(self):
        return 'Symbol({!r}, {!r})'.format(self.symbol, self.variable)

    def __str__(self):
        return '"{}"({})'.format(self.symbol, self.variable)

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_symbol(self)


class Visitor:
    """Base class for recursively traversing well-formed formulas."""

    def visit_exists(self, formula: Exists):
        raise NotImplementedError

    def visit_forall(self, formula: Forall):
        raise NotImplementedError

    def visit_not(self, formula: Not):
        raise NotImplementedError

    def visit_and(self, formula: And):
        raise NotImplementedError

    def visit_if(self, formula: If):
        raise NotImplementedError

    def visit_or(self, formula: Or):
        raise NotImplementedError

    def visit_contained_in(self, formula: ContainedIn):
        raise NotImplementedError

    def visit_equal(self, formula: Equal):
        raise NotImplementedError

    def visit_less(self, formula: Less):
        raise NotImplementedError

    def visit_singleton(self, formula: Singleton):
        raise NotImplementedError

    def visit_symbol(self, formula: Symbol):
        raise NotImplementedError
