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

"""Unit test for well-formed formulas."""

import unittest

from m2lstr import wff


class WffTest(unittest.TestCase):

    def test_repr(self):
        x = wff.Variable('x')
        f = wff.Forall(x, wff.Symbol('a', x))
        self.assertEqual(
            repr(f), "Forall(Variable('x', 1), Symbol('a', Variable('x', 1)))")
        return

    def test_str(self):
        x = wff.Variable('x')
        f = wff.Forall(x, wff.Symbol('a', x) | wff.Symbol('b', x))
        self.assertEqual(str(f), '∀¹x ["a"(x) ∨ "b"(x)]')
        y = wff.Variable('Y', 2)
        g = wff.Exists(y, x <= y)
        self.assertEqual(str(g), '∃²Y [[x < Y] ∨ [x == Y]]')
        return

    def test_simplify(self):
        x = wff.Variable('x')
        f = wff.Forall(x, wff.Symbol('a', x) | wff.Symbol('b', x))
        self.assertEqual(str(f), '∀¹x ["a"(x) ∨ "b"(x)]')
        g = wff.simplify(f)
        self.assertEqual(str(g), '¬∃²x [Singleton(x) ∧ [¬"a"(x) ∧ ¬"b"(x)]]')
        return


if __name__ == '__main__':
    unittest.main()
