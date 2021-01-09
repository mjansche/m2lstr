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

"""Various examples of m2lstr formulas."""

import unittest

from m2lstr import dfa
from m2lstr import translation
from m2lstr import wff
from m2lstr.wff import Exists, Symbol


class TranslationTest(unittest.TestCase):

    def check_membership(self, a: dfa.DFA, accept, reject):
        for seq in accept:
            self.assertTrue(dfa.accepts(a, seq),
                            msg=f'should accept "{seq}"')
        for seq in reject:
            self.assertFalse(dfa.accepts(a, seq),
                             msg=f'should not accept "{seq}"')
        return

    def test_example_1(self):
        """Second and second-to-last symbol is 'b'."""
        alphabet = {'a', 'b'}
        accept = {'bb', 'aba', 'abb', 'bba', 'bbb', 'abba', 'ababa', 'abaaaba'}
        reject = {'', 'a', 'b', 'aa', 'ab', 'ba', 'aaa', 'aab', 'baa', 'bab'}
        x = wff.Variable('x')
        y = wff.Variable('y')
        z = wff.Variable('z')
        formula_1 = Exists(x, ~Exists(y, y < x) &
                           Exists(y, (x < y) & ~Exists(z, (x < z) & (z < y)) &
                                  Symbol('b', y)))
        formula_2 = Exists(x, ~Exists(y, x < y) &
                           Exists(y, (y < x) & ~Exists(z, (y < z) & (z < x)) &
                                  Symbol('b', y)))
        formula = formula_1 & formula_2
        a = translation.translate(formula, alphabet)
        self.check_membership(a, accept, reject)
        return


if __name__ == '__main__':
    unittest.main()
