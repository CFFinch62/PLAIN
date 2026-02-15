"""Tests for Python to PLAIN conversion."""

import unittest
from pathlib import Path

from plain_converter.converter.python_to_plain import PythonToPlainConverter

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestVariableDeclarations(unittest.TestCase):
    """Test variable declaration and assignment conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_simple_variable(self):
        result = self.converter.convert('x = 5')
        self.assertIn('var x = 5', result.code)

    def test_string_variable(self):
        result = self.converter.convert('name = "Alice"')
        self.assertIn('var name = "Alice"', result.code)

    def test_reassignment(self):
        result = self.converter.convert('x = 5\nx = 10')
        lines = result.code.strip().splitlines()
        self.assertIn('var x = 5', lines[0])
        self.assertIn('x = 10', lines[1])
        self.assertNotIn('var', lines[1])

    def test_constant_fxd(self):
        result = self.converter.convert('MAX_SIZE = 100')
        self.assertIn('fxd MAX_SIZE', result.code)

    def test_augmented_assign(self):
        result = self.converter.convert('x = 5\nx += 3')
        self.assertIn('x = x + 3', result.code)

    def test_boolean_constant(self):
        result = self.converter.convert('flag = True')
        self.assertIn('var flag = true', result.code)

    def test_none_constant(self):
        result = self.converter.convert('val = None')
        self.assertIn('var val = null', result.code)


class TestFunctionConversion(unittest.TestCase):
    """Test function definition conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_simple_function(self):
        result = self.converter.convert('def greet():\n    print("hello")')
        self.assertIn('task Greet()', result.code)

    def test_function_with_params(self):
        result = self.converter.convert('def add(a, b):\n    return a + b')
        self.assertIn('task Add using (a, b)', result.code)

    def test_procedure_with_params(self):
        result = self.converter.convert('def say(msg):\n    print(msg)')
        self.assertIn('task Say with (msg)', result.code)

    def test_return_as_deliver(self):
        result = self.converter.convert('def get_val():\n    return 42')
        self.assertIn('deliver 42', result.code)

    def test_docstring_as_comment(self):
        code = 'def foo():\n    """A function."""\n    pass'
        result = self.converter.convert(code)
        self.assertIn('rem: A function.', result.code)

    def test_multiline_docstring_as_note(self):
        """Multi-line docstrings should become note: blocks."""
        code = 'def foo():\n    """First line.\n\n    Second line.\n    """\n    pass'
        result = self.converter.convert(code)
        self.assertIn('note: First line.', result.code)
        self.assertIn('Second line.', result.code)

    def test_singleline_docstring_stays_rem(self):
        """Single-line docstrings should stay as rem:."""
        code = 'def bar():\n    """Just one line."""\n    pass'
        result = self.converter.convert(code)
        self.assertIn('rem: Just one line.', result.code)
        self.assertNotIn('note:', result.code)

    def test_standalone_multiline_string_as_note(self):
        """Module-level multi-line strings should become note: blocks."""
        code = '"""Module docs.\nWith more info."""\nx = 5'
        result = self.converter.convert(code)
        self.assertIn('note: Module docs.', result.code)
        self.assertIn('With more info.', result.code)

    def test_standalone_singleline_string_as_rem(self):
        """Module-level single-line strings should become rem:."""
        code = '"""Just a one-liner."""\nx = 5'
        result = self.converter.convert(code)
        self.assertIn('rem: Just a one-liner.', result.code)
        self.assertNotIn('note:', result.code)

    def test_snake_to_pascal(self):
        result = self.converter.convert('def my_func():\n    pass')
        self.assertIn('task MyFunc()', result.code)


class TestControlFlow(unittest.TestCase):
    """Test control flow conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter(prefer_choose=False)

    def test_simple_if(self):
        result = self.converter.convert('if x > 0:\n    y = 1')
        self.assertIn('if x > 0', result.code)

    def test_if_else(self):
        code = 'if x > 0:\n    y = 1\nelse:\n    y = 0'
        result = self.converter.convert(code)
        self.assertIn('if x > 0', result.code)
        self.assertIn('else', result.code)

    def test_if_elif_else(self):
        code = 'if x > 0:\n    y = 1\nelif x == 0:\n    y = 0\nelse:\n    y = -1'
        result = self.converter.convert(code)
        self.assertIn('if x > 0', result.code)
        self.assertIn('else if x == 0', result.code)

    def test_choose_mode(self):
        converter = PythonToPlainConverter(prefer_choose=True)
        code = ('if x == 1:\n    y = 1\nelif x == 2:\n    y = 2\n'
                'elif x == 3:\n    y = 3\nelse:\n    y = 0')
        result = converter.convert(code)
        self.assertIn('choose true', result.code)
        self.assertIn('choice x == 1', result.code)
        self.assertIn('default', result.code)

    def test_for_range(self):
        result = self.converter.convert('for i in range(10):\n    print(i)')
        self.assertIn('loop i from 0 to 9', result.code)

    def test_for_range_start_stop(self):
        result = self.converter.convert('for i in range(1, 5):\n    print(i)')
        self.assertIn('loop i from 1 to 4', result.code)

    def test_for_collection(self):
        result = self.converter.convert('for item in items:\n    print(item)')
        self.assertIn('loop item in items', result.code)

    def test_while_loop(self):
        result = self.converter.convert('while x > 0:\n    x -= 1')
        self.assertIn('loop x > 0', result.code)

    def test_while_true(self):
        result = self.converter.convert('while True:\n    pass')
        self.assertIn('loop', result.code)
        self.assertNotIn('loop true', result.code.lower().replace('loop\n', 'loop\n'))

    def test_break_as_exit(self):
        result = self.converter.convert('while True:\n    break')
        self.assertIn('exit', result.code)

    def test_continue(self):
        result = self.converter.convert('for i in range(10):\n    continue')
        self.assertIn('continue', result.code)


class TestErrorHandling(unittest.TestCase):
    """Test error handling conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_try_except(self):
        code = 'try:\n    x = 1\nexcept:\n    x = 0'
        result = self.converter.convert(code)
        self.assertIn('attempt', result.code)
        self.assertIn('handle', result.code)

    def test_try_except_finally(self):
        code = 'try:\n    x = 1\nexcept:\n    x = 0\nfinally:\n    cleanup()'
        result = self.converter.convert(code)
        self.assertIn('attempt', result.code)
        self.assertIn('handle', result.code)
        self.assertIn('ensure', result.code)

    def test_raise(self):
        code = 'raise ValueError("bad value")'
        result = self.converter.convert(code)
        self.assertIn('abort "bad value"', result.code)


class TestExpressions(unittest.TestCase):
    """Test expression conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_string_concat(self):
        result = self.converter.convert('x = "hello" + " world"')
        self.assertIn('&', result.code)

    def test_fstring_to_vstring(self):
        result = self.converter.convert('x = f"Hello {name}"')
        self.assertIn('v"Hello {name}"', result.code)

    def test_list_literal(self):
        result = self.converter.convert('x = [1, 2, 3]')
        self.assertIn('[1, 2, 3]', result.code)

    def test_dict_literal(self):
        result = self.converter.convert('x = {"a": 1, "b": 2}')
        self.assertIn('"a": 1', result.code)

    def test_not_operator(self):
        result = self.converter.convert('x = not True')
        self.assertIn('not true', result.code)

    def test_and_or(self):
        result = self.converter.convert('x = True and False')
        self.assertIn('true and false', result.code)

    def test_comparison(self):
        result = self.converter.convert('x = a >= b')
        self.assertIn('a >= b', result.code)


class TestStdlibMapping(unittest.TestCase):
    """Test standard library function mapping."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_print_to_display(self):
        result = self.converter.convert('print("hello")')
        self.assertIn('display("hello")', result.code)

    def test_input_to_get(self):
        result = self.converter.convert('x = input("prompt")')
        self.assertIn('get("prompt")', result.code)

    def test_len_to_length(self):
        result = self.converter.convert('x = len(items)')
        self.assertIn('length(items)', result.code)

    def test_int_to_to_int(self):
        result = self.converter.convert('x = int("5")')
        self.assertIn('to_int("5")', result.code)

    def test_str_to_to_string(self):
        result = self.converter.convert('x = str(42)')
        self.assertIn('to_string(42)', result.code)

    def test_method_append(self):
        result = self.converter.convert('items = []\nitems.append(1)')
        self.assertIn('append(items, 1)', result.code)

    def test_strip_to_trim(self):
        result = self.converter.convert('x = s.strip()')
        self.assertIn('trim(s)', result.code)

    def test_startswith_to_starts_with(self):
        result = self.converter.convert('x = s.startswith("hello")')
        self.assertIn('starts_with(s, "hello")', result.code)

    def test_endswith_to_ends_with(self):
        result = self.converter.convert('x = s.endswith(".py")')
        self.assertIn('ends_with(s, ".py")', result.code)

    def test_join_arg_swap(self):
        """sep.join(lst) should become join(lst, sep)."""
        result = self.converter.convert('x = ", ".join(items)')
        self.assertIn('join(items, ", ")', result.code)

    def test_upper_method(self):
        result = self.converter.convert('x = s.upper()')
        self.assertIn('upper(s)', result.code)

    def test_lower_method(self):
        result = self.converter.convert('x = s.lower()')
        self.assertIn('lower(s)', result.code)

    def test_replace_method(self):
        result = self.converter.convert('x = s.replace("a", "b")')
        self.assertIn('replace(s, "a", "b")', result.code)

    def test_split_method(self):
        result = self.converter.convert('x = s.split(",")')
        self.assertIn('split(s, ",")', result.code)

    def test_list_sort(self):
        result = self.converter.convert('items = [3, 1, 2]\nitems.sort()')
        self.assertIn('sort(items)', result.code)

    def test_list_reverse(self):
        result = self.converter.convert('items = [1, 2]\nitems.reverse()')
        self.assertIn('reverse(items)', result.code)

    def test_math_floor(self):
        """math.floor(x) should become floor(x)."""
        result = self.converter.convert('import math\nx = math.floor(3.7)')
        self.assertIn('floor(3.7)', result.code)

    def test_math_sqrt(self):
        """math.sqrt(x) should become sqrt(x)."""
        result = self.converter.convert('import math\nx = math.sqrt(16)')
        self.assertIn('sqrt(16)', result.code)

    def test_random_randint(self):
        """random.randint(a, b) should become random_int(a, b)."""
        result = self.converter.convert('import random\nx = random.randint(1, 10)')
        self.assertIn('random_int(1, 10)', result.code)


class TestClassConversion(unittest.TestCase):
    """Test class to record conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_simple_class_to_record(self):
        code = 'class Point:\n    x: int\n    y: int'
        result = self.converter.convert(code)
        self.assertIn('record Point:', result.code)
        self.assertIn('x as int', result.code)
        self.assertIn('y as int', result.code)

    def test_dataclass_to_record(self):
        code = 'from dataclasses import dataclass\n\n@dataclass\nclass Student:\n    name: str\n    age: int = 18'
        result = self.converter.convert(code)
        self.assertIn('record Student:', result.code)
        self.assertIn('name as string', result.code)
        self.assertIn('age as int = 18', result.code)

    def test_class_with_defaults(self):
        code = 'class Config:\n    width: int = 800\n    height: int = 600\n    title: str = "App"'
        result = self.converter.convert(code)
        self.assertIn('record Config:', result.code)
        self.assertIn('width as int = 800', result.code)
        self.assertIn('height as int = 600', result.code)
        self.assertIn('title as string = "App"', result.code)

    def test_class_with_init_to_record(self):
        code = 'class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y'
        result = self.converter.convert(code)
        self.assertIn('record Point:', result.code)
        self.assertIn('x as', result.code)
        self.assertIn('y as', result.code)

    def test_class_with_multiple_types(self):
        code = 'class Item:\n    name: str\n    price: float\n    count: int\n    active: bool'
        result = self.converter.convert(code)
        self.assertIn('name as string', result.code)
        self.assertIn('price as float', result.code)
        self.assertIn('count as int', result.code)
        self.assertIn('active as boolean', result.code)

    def test_class_with_list_dict_types(self):
        code = 'class Data:\n    items: list\n    lookup: dict'
        result = self.converter.convert(code)
        self.assertIn('items as list', result.code)
        self.assertIn('lookup as table', result.code)


class TestMainGuard(unittest.TestCase):
    """Test if __name__ == '__main__' handling."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_main_guard_stripped(self):
        code = 'def main():\n    pass\n\nif __name__ == "__main__":\n    main()'
        result = self.converter.convert(code)
        self.assertNotIn('__name__', result.code)
        # The body should still be emitted
        self.assertIn('Main()', result.code)


class TestConversionResult(unittest.TestCase):
    """Test conversion result properties."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_success_result(self):
        result = self.converter.convert('x = 1')
        self.assertTrue(result.success)
        self.assertFalse(result.has_warnings)

    def test_syntax_error(self):
        result = self.converter.convert('def ')
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)

    def test_stats_tracked(self):
        result = self.converter.convert('def foo():\n    return 1')
        self.assertIn('functions_converted', result.stats)
        self.assertEqual(result.stats['functions_converted'], 1)


class TestFixtureIntegration(unittest.TestCase):
    """Integration tests using fixture files."""

    def test_fixtures_exist(self):
        self.assertTrue((FIXTURES_DIR / "python" / "hello.py").exists())
        self.assertTrue((FIXTURES_DIR / "python" / "fibonacci.py").exists())
        self.assertTrue((FIXTURES_DIR / "python" / "grade_calculator.py").exists())

    def test_hello_conversion(self):
        converter = PythonToPlainConverter()
        source = (FIXTURES_DIR / "python" / "hello.py").read_text()
        result = converter.convert(source)
        self.assertTrue(result.success)
        self.assertIn('task Main()', result.code)
        self.assertIn('display(greeting)', result.code)
        self.assertIn('v"Hello, {name}', result.code)

    def test_fibonacci_conversion(self):
        converter = PythonToPlainConverter()
        source = (FIXTURES_DIR / "python" / "fibonacci.py").read_text()
        result = converter.convert(source)
        self.assertTrue(result.success)
        self.assertIn('task Fibonacci using (n)', result.code)
        self.assertIn('deliver n', result.code)
        self.assertIn('deliver a + b', result.code)

    def test_grade_calculator_conversion(self):
        converter = PythonToPlainConverter(prefer_choose=True)
        source = (FIXTURES_DIR / "python" / "grade_calculator.py").read_text()
        result = converter.convert(source)
        self.assertTrue(result.success)
        self.assertIn('choose true', result.code)
        self.assertIn('choice score >= 90', result.code)
        self.assertIn('deliver "A"', result.code)


class TestTypeAnnotationConversion(unittest.TestCase):
    """Test type annotation conversion from Python to PLAIN."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_annotated_int_variable(self):
        result = self.converter.convert('x: int = 5')
        self.assertIn('var x as int = 5', result.code)

    def test_annotated_str_variable(self):
        result = self.converter.convert('name: str = "Alice"')
        self.assertIn('var name as string = "Alice"', result.code)

    def test_annotated_float_variable(self):
        result = self.converter.convert('pi: float = 3.14')
        self.assertIn('var pi as float = 3.14', result.code)

    def test_annotated_bool_variable(self):
        result = self.converter.convert('flag: bool = True')
        self.assertIn('var flag as boolean = true', result.code)

    def test_annotated_list_variable(self):
        result = self.converter.convert('items: list = []')
        self.assertIn('var items as list = []', result.code)

    def test_annotated_dict_variable(self):
        result = self.converter.convert('data: dict = {}')
        self.assertIn('var data as table = {}', result.code)

    def test_annotation_only_no_value(self):
        result = self.converter.convert('count: int')
        self.assertIn('var count as int', result.code)

    def test_constant_annotation(self):
        """UPPER_CASE annotated vars should become fxd."""
        result = self.converter.convert('MAX_SIZE: int = 100')
        self.assertIn('fxd MAX_SIZE as int = 100', result.code)

    def test_generic_list_type(self):
        """List[int] should map to 'list' (PLAIN has no generics)."""
        result = self.converter.convert('from typing import List\nnums: List[int] = []')
        self.assertIn('var nums as list = []', result.code)

    def test_generic_dict_type(self):
        """Dict[str, int] should map to 'table'."""
        result = self.converter.convert('from typing import Dict\ndata: Dict[str, int] = {}')
        self.assertIn('var data as table = {}', result.code)

    def test_optional_type(self):
        """Optional[str] should map to inner type 'string'."""
        result = self.converter.convert('from typing import Optional\nname: Optional[str] = None')
        self.assertIn('var name as string', result.code)

    def test_final_type(self):
        """Final[int] should map to inner type 'int'."""
        result = self.converter.convert('from typing import Final\nMAX: Final[int] = 100')
        self.assertIn('fxd MAX as int = 100', result.code)

    def test_function_with_typed_params(self):
        code = 'def add(a: int, b: int) -> int:\n    return a + b'
        result = self.converter.convert(code)
        self.assertIn('task Add using (a as int, b as int)', result.code)

    def test_function_with_mixed_params(self):
        code = 'def greet(name: str, loud):\n    print(name)'
        result = self.converter.convert(code)
        self.assertIn('task Greet with (name as string, loud)', result.code)

    def test_function_without_typed_params(self):
        """Functions without types should work as before."""
        code = 'def add(a, b):\n    return a + b'
        result = self.converter.convert(code)
        self.assertIn('task Add using (a, b)', result.code)


class TestImportConversion(unittest.TestCase):
    """Test Python import → PLAIN use: block conversion."""

    def setUp(self):
        self.converter = PythonToPlainConverter()

    def test_stdlib_import_skipped(self):
        """stdlib imports should be skipped (handled by mapping)."""
        code = 'import math\nx = math.floor(3.7)'
        result = self.converter.convert(code)
        self.assertNotIn('use:', result.code)
        self.assertIn('floor(3.7)', result.code)

    def test_stdlib_from_import_skipped(self):
        """from-import of stdlib modules should be skipped."""
        code = 'from typing import List, Optional\nfrom dataclasses import dataclass'
        result = self.converter.convert(code)
        self.assertNotIn('use:', result.code)

    def test_import_module(self):
        """import module → use: modules: module"""
        code = 'import helpers\nresult = helpers.add_numbers(3, 4)'
        result = self.converter.convert(code)
        self.assertIn('use:', result.code)
        self.assertIn('modules:', result.code)
        self.assertIn('helpers', result.code)

    def test_from_import_becomes_tasks(self):
        """from module import name → use: tasks: module.Name"""
        code = 'from utils import format_date, parse_input'
        result = self.converter.convert(code)
        self.assertIn('use:', result.code)
        self.assertIn('tasks:', result.code)
        self.assertIn('utils.FormatDate', result.code)
        self.assertIn('utils.ParseInput', result.code)

    def test_from_submodule_import(self):
        """from module.sub import name → use: tasks: module.sub.Name"""
        code = 'from mathlib.arithmetic import add, subtract'
        result = self.converter.convert(code)
        self.assertIn('mathlib.arithmetic.Add', result.code)
        self.assertIn('mathlib.arithmetic.Subtract', result.code)

    def test_mixed_stdlib_and_non_stdlib(self):
        """stdlib imports skipped, non-stdlib converted."""
        code = 'import math\nfrom helpers import greet\nx = math.floor(1.5)\ngreet("hi")'
        result = self.converter.convert(code)
        self.assertIn('use:', result.code)
        self.assertIn('tasks:', result.code)
        self.assertIn('helpers.Greet', result.code)
        self.assertNotIn('modules:', result.code)  # math is stdlib

    def test_module_qualified_call_converted(self):
        """module.method() → module.PascalCase() in PLAIN."""
        code = 'import helpers\na = helpers.add_numbers(3, 4)\nb = helpers.format_name("alice")'
        result = self.converter.convert(code)
        self.assertIn('helpers.AddNumbers(3, 4)', result.code)
        self.assertIn('helpers.FormatName("alice")', result.code)

    def test_multiple_module_imports(self):
        """Multiple import statements → single use: block."""
        code = 'import helpers\nimport mathlib'
        result = self.converter.convert(code)
        # Should have one use: block with both modules
        self.assertEqual(result.code.count('use:'), 1)
        self.assertIn('helpers', result.code)
        self.assertIn('mathlib', result.code)

    def test_no_imports_no_use_block(self):
        """Code with no imports should have no use: block."""
        code = 'x = 42\nprint(x)'
        result = self.converter.convert(code)
        self.assertNotIn('use:', result.code)


if __name__ == "__main__":
    unittest.main()
