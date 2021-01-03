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

"""Unit test for translation of well-formed formulas into finite automata."""

import unittest

from m2lstr import dfa
from m2lstr import translation
from m2lstr import wff
from m2lstr.wff import Exists, Forall, Symbol


class TranslationTest(unittest.TestCase):

    def check_membership(self, a: dfa.DFA, accept, reject):
        for seq in accept:
            self.assertTrue(dfa.accepts(a, seq),
                            msg=f'should accept "{seq}"')
        for seq in reject:
            self.assertFalse(dfa.accepts(a, seq),
                             msg=f'should not accept "{seq}"')
        return

    def test_exists_trivial(self):
        alphabet = {'a', 'b'}
        x = wff.Variable('x')
        formula = Exists(x, x == x)  # pylint: disable=comparison-with-itself
        a = translation.translate(formula, alphabet)
        self.check_membership(a, {'a', 'b', 'aa', 'ab', 'ba', 'bb'}, {''})
        return

    def test_exists_symbol(self):
        alphabet = {'a', 'b'}
        x = wff.Variable('x')
        formula = Exists(x, Symbol('a', x))
        a = translation.translate(formula, alphabet)
        self.check_membership(a, {'a', 'ab', 'ba'}, {'', 'b', 'bb'})
        return

    def test_forall_symbol(self):
        alphabet = {'a', 'b'}
        x = wff.Variable('x')
        formula = Forall(x, Symbol('a', x))
        a = translation.translate(formula, alphabet)
        self.check_membership(a, {'', 'a', 'aa', 'aaa'}, {'b', 'ab', 'ba'})
        return

    def test_and(self):
        alphabet = {'a', 'b', 'c'}
        accept = {'ab', 'ba', 'abc', 'acb', 'bac', 'bca', 'cab', 'cba'}
        reject = {'', 'a', 'b', 'c', 'aa', 'ac', 'bb', 'bc', 'ca', 'cb', 'cc'}
        x = wff.Variable('x')
        y = wff.Variable('y')
        formula = Exists(x, Symbol('a', x)) & Exists(y, Symbol('b', y))
        a = translation.translate(formula, alphabet)
        self.check_membership(a, accept, reject)
        return

    def test_less(self):
        alphabet = {'a', 'b', 'c'}
        accept = {'ab', 'abc', 'acb', 'cab'}
        reject = {'', 'a', 'b', 'c',
                  'aa', 'ac', 'ba', 'bb', 'bc', 'ca', 'cb', 'cc',
                  'bac', 'bca', 'cba'}
        x = wff.Variable('x')
        y = wff.Variable('y')
        formula = Exists(
            x, Symbol('a', x) & Exists(y, Symbol('b', y) & (x < y)))
        a = translation.translate(formula, alphabet)
        self.check_membership(a, accept, reject)
        return

    def test_first(self):
        alphabet = {'a', 'b', 'c'}
        accept = {'a', 'aa', 'ab', 'ac'}
        reject = {'', 'b', 'c', 'ba', 'bb', 'bc', 'ca', 'cb', 'cc'}

        x = wff.Variable('x')
        y = wff.Variable('y')

        formula = Exists(x, Symbol('a', x) & ~Exists(y, y < x))
        a = translation.translate(formula, alphabet)
        self.check_membership(a, accept, reject)

        formula_2 = Exists(x, Symbol('a', x) & Forall(y, x <= y))
        a_2 = translation.translate(formula_2, alphabet)
        self.check_membership(a_2, accept, reject)
        return

    def test_last(self):
        alphabet = {'a', 'b', 'c'}
        accept = {'a', 'aa', 'ba', 'ca'}
        reject = {'', 'b', 'c', 'ab', 'bb', 'cb', 'ac', 'bc', 'cc'}

        x = wff.Variable('x')
        y = wff.Variable('y')

        formula = Exists(x, Symbol('a', x) & ~Exists(y, y > x))
        a = translation.translate(formula, alphabet)
        self.check_membership(a, accept, reject)

        formula_2 = Exists(x, Symbol('a', x) & Forall(y, x >= y))
        a_2 = translation.translate(formula_2, alphabet)
        self.check_membership(a_2, accept, reject)
        return


if __name__ == '__main__':
    unittest.main()
