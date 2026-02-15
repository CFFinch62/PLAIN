"""Tests for PLAIN to Python conversion."""

import unittest
from pathlib import Path

from plain_converter.converter.plain_to_python import PlainToPythonConverter

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestVariableConversion(unittest.TestCase):
    """Test variable declaration and assignment conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_var_integer(self):
        result = self.converter.convert('var x = 5')
        self.assertIn('x = 5', result.code)

    def test_var_string(self):
        result = self.converter.convert('var name = "Alice"')
        self.assertIn('name = "Alice"', result.code)

    def test_var_no_value(self):
        result = self.converter.convert('var count')
        self.assertIn('count = None', result.code)

    def test_fxd_constant(self):
        result = self.converter.convert('fxd MAX = 100')
        self.assertIn('MAX = 100', result.code)

    def test_assignment(self):
        result = self.converter.convert('var x = 5\nx = 10')
        self.assertIn('x = 10', result.code)

    def test_boolean_true(self):
        result = self.converter.convert('var flag = true')
        self.assertIn('flag = True', result.code)

    def test_boolean_false(self):
        result = self.converter.convert('var flag = false')
        self.assertIn('flag = False', result.code)

    def test_null(self):
        result = self.converter.convert('var val = null')
        self.assertIn('val = None', result.code)

    def test_float_value(self):
        result = self.converter.convert('var pi = 3.14')
        self.assertIn('pi = 3.14', result.code)


class TestTaskConversion(unittest.TestCase):
    """Test task (function) conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_simple_task(self):
        result = self.converter.convert('task Greet()\n    display("hello")')
        self.assertIn('def greet():', result.code)

    def test_task_with_params(self):
        result = self.converter.convert('task Add with (a, b)\n    display(a + b)')
        self.assertIn('def add(a, b):', result.code)

    def test_task_using_function(self):
        result = self.converter.convert('task Add using (a, b)\n    deliver a + b')
        self.assertIn('def add(a, b):', result.code)
        self.assertIn('return a + b', result.code)

    def test_deliver_to_return(self):
        result = self.converter.convert('task GetValue using ()\n    deliver 42')
        self.assertIn('return 42', result.code)

    def test_task_pascal_to_snake(self):
        result = self.converter.convert('task CalculateTotal using (a, b)\n    deliver a + b')
        self.assertIn('def calculate_total(a, b):', result.code)

    def test_main_guard_added(self):
        """Top-level calls should get wrapped in if __name__ guard."""
        result = self.converter.convert('task Main()\n    display("hi")\n\nMain()')
        self.assertIn('if __name__ == "__main__":', result.code)


class TestExpressionConversion(unittest.TestCase):
    """Test expression conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_string_concat_ampersand(self):
        result = self.converter.convert('var x = "hello" & " world"')
        self.assertIn('"hello" + " world"', result.code)

    def test_equality_operator(self):
        result = self.converter.convert('if x = 5\n    display("yes")')
        self.assertIn('x == 5', result.code)

    def test_not_equal(self):
        result = self.converter.convert('if x != 5\n    display("no")')
        self.assertIn('x != 5', result.code)

    def test_comparison_operators(self):
        result = self.converter.convert('if x > 5\n    display("big")')
        self.assertIn('x > 5', result.code)

    def test_and_operator(self):
        result = self.converter.convert('if x > 0 and x < 10\n    display("ok")')
        self.assertIn('x > 0 and x < 10', result.code)

    def test_or_operator(self):
        result = self.converter.convert('if x = 0 or x = 1\n    display("binary")')
        self.assertIn('x == 0 or x == 1', result.code)

    def test_not_operator(self):
        result = self.converter.convert('if not flag\n    display("no")')
        self.assertIn('not flag', result.code)

    def test_vstring_to_fstring(self):
        result = self.converter.convert('var msg = v"Hello {name}"')
        self.assertIn('f"Hello {name}"', result.code)

    def test_list_literal(self):
        result = self.converter.convert('var nums = [1, 2, 3]')
        self.assertIn('[1, 2, 3]', result.code)

    def test_table_literal(self):
        result = self.converter.convert('var t = {"a": 1, "b": 2}')
        self.assertIn('"a": 1', result.code)

    def test_negative_number(self):
        result = self.converter.convert('var x = -5')
        self.assertIn('x = -5', result.code)

    def test_index_expression(self):
        result = self.converter.convert('var x = nums[0]')
        self.assertIn('nums[0]', result.code)

    def test_dot_expression(self):
        result = self.converter.convert('var x = obj.field')
        self.assertIn('obj.field', result.code)


class TestControlFlowConversion(unittest.TestCase):
    """Test control flow conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_simple_if(self):
        result = self.converter.convert('if x > 0\n    display("positive")')
        self.assertIn('if x > 0:', result.code)

    def test_if_else(self):
        code = 'if x > 0\n    display("positive")\nelse\n    display("non-positive")'
        result = self.converter.convert(code)
        self.assertIn('if x > 0:', result.code)
        self.assertIn('else:', result.code)

    def test_if_with_then_keyword(self):
        code = 'if x = 0 then\n    display("zero")'
        result = self.converter.convert(code)
        self.assertIn('if x == 0:', result.code)

    def test_compound_condition_with_equals(self):
        code = 'if a = 1 and b = 2\n    display("match")'
        result = self.converter.convert(code)
        self.assertIn('a == 1 and b == 2', result.code)

    def test_counting_loop(self):
        code = 'loop i from 0 to 10\n    display(i)'
        result = self.converter.convert(code)
        self.assertIn('for i in range(0, 10 + 1):', result.code)

    def test_iteration_loop(self):
        code = 'loop item in items\n    display(item)'
        result = self.converter.convert(code)
        self.assertIn('for item in items:', result.code)

    def test_while_loop(self):
        code = 'loop x > 0\n    x = x - 1'
        result = self.converter.convert(code)
        self.assertIn('while x > 0:', result.code)

    def test_while_loop_with_equals(self):
        code = 'loop x = 0\n    display("zero")\n    exit'
        result = self.converter.convert(code)
        self.assertIn('while x == 0:', result.code)

    def test_exit_to_break(self):
        result = self.converter.convert('loop true\n    exit')
        self.assertIn('break', result.code)

    def test_continue_statement(self):
        result = self.converter.convert('loop i from 0 to 5\n    continue')
        self.assertIn('continue', result.code)

    def test_choose_true_pattern(self):
        code = ('choose true\n'
                '    choice x > 90\n'
                '        display("A")\n'
                '    choice x > 80\n'
                '        display("B")\n'
                '    default\n'
                '        display("C")')
        result = self.converter.convert(code)
        self.assertIn('if x > 90:', result.code)
        self.assertIn('elif x > 80:', result.code)
        self.assertIn('else:', result.code)

    def test_choose_value_pattern(self):
        code = ('choose grade\n'
                '    choice "A"\n'
                '        display("Excellent")\n'
                '    choice "B"\n'
                '        display("Good")\n'
                '    default\n'
                '        display("Other")')
        result = self.converter.convert(code)
        self.assertIn('if grade == "A":', result.code)
        self.assertIn('elif grade == "B":', result.code)


class TestErrorHandlingConversion(unittest.TestCase):
    """Test error handling conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_abort_to_raise(self):
        result = self.converter.convert('abort "something went wrong"')
        self.assertIn('raise Exception("something went wrong")', result.code)

    def test_attempt_handle(self):
        code = ('attempt\n'
                '    var x = risky_call()\n'
                'handle e\n'
                '    display(e)')
        result = self.converter.convert(code)
        self.assertIn('try:', result.code)
        self.assertIn('except Exception as e:', result.code)

    def test_attempt_handle_ensure(self):
        code = ('attempt\n'
                '    var x = 1\n'
                'handle e\n'
                '    display(e)\n'
                'ensure\n'
                '    display("done")')
        result = self.converter.convert(code)
        self.assertIn('try:', result.code)
        self.assertIn('except', result.code)
        self.assertIn('finally:', result.code)

    def test_safe_divide_with_then(self):
        """Test the formerly-buggy pattern: if b = 0 then."""
        code = ('task SafeDivide using (a, b)\n'
                '    if b = 0 then\n'
                '        abort "division by zero"\n'
                '    deliver a / b')
        result = self.converter.convert(code)
        self.assertIn('def safe_divide(a, b):', result.code)
        self.assertIn('if b == 0:', result.code)
        self.assertIn('raise Exception("division by zero")', result.code)
        self.assertIn('return a / b', result.code)
        self.assertEqual(result.errors, [])


class TestStdlibMapping(unittest.TestCase):
    """Test standard library function mapping."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_display_to_print(self):
        result = self.converter.convert('display("hello")')
        self.assertIn('print("hello")', result.code)

    def test_get_to_input(self):
        result = self.converter.convert('var x = get("Enter: ")')
        self.assertIn('input("Enter: ")', result.code)

    def test_length_to_len(self):
        result = self.converter.convert('var n = length(items)')
        self.assertIn('len(items)', result.code)

    def test_to_int(self):
        result = self.converter.convert('var n = to_int("5")')
        self.assertIn('int("5")', result.code)

    def test_to_string(self):
        result = self.converter.convert('var s = to_string(42)')
        self.assertIn('str(42)', result.code)

    def test_upper_method_from_function(self):
        """upper(s) should become s.upper()."""
        result = self.converter.convert('var x = upper(s)')
        self.assertIn('s.upper()', result.code)

    def test_trim_to_strip(self):
        """trim(s) should become s.strip()."""
        result = self.converter.convert('var x = trim(s)')
        self.assertIn('s.strip()', result.code)

    def test_starts_with_to_startswith(self):
        """starts_with(s, p) should become s.startswith(p)."""
        result = self.converter.convert('var x = starts_with(s, "hello")')
        self.assertIn('s.startswith("hello")', result.code)

    def test_ends_with_to_endswith(self):
        """ends_with(s, p) should become s.endswith(p)."""
        result = self.converter.convert('var x = ends_with(s, ".py")')
        self.assertIn('s.endswith(".py")', result.code)

    def test_join_arg_swap(self):
        """join(lst, sep) should become sep.join(lst)."""
        result = self.converter.convert('var x = join(items, ", ")')
        self.assertIn('", ".join(items)', result.code)

    def test_substring_special(self):
        """substring(s, start, end) should become s[start:end]."""
        result = self.converter.convert('var x = substring(s, 0, 3)')
        self.assertIn('s[0:3]', result.code)

    def test_contains_special(self):
        """contains(s, search) should become search in s."""
        result = self.converter.convert('var x = contains(s, "hello")')
        self.assertIn('"hello" in s', result.code)

    def test_is_int_type_check(self):
        """is_int(x) should become isinstance(x, int)."""
        result = self.converter.convert('var x = is_int(n)')
        self.assertIn('isinstance(n, int)', result.code)

    def test_sqr_special(self):
        """sqr(x) should become x ** 2."""
        result = self.converter.convert('var x = sqr(5)')
        self.assertIn('5 ** 2', result.code)

    def test_floor_imports_math(self):
        """floor(x) should become math.floor(x) with import."""
        result = self.converter.convert('var x = floor(3.7)')
        self.assertIn('math.floor(3.7)', result.code)
        self.assertIn('import math', result.code)

    def test_sqrt_imports_math(self):
        """sqrt(x) should become math.sqrt(x) with import."""
        result = self.converter.convert('var x = sqrt(16)')
        self.assertIn('math.sqrt(16)', result.code)
        self.assertIn('import math', result.code)

    def test_random_int_imports_random(self):
        """random_int(a, b) should become random.randint(a, b) with import."""
        result = self.converter.convert('var x = random_int(1, 10)')
        self.assertIn('random.randint(1, 10)', result.code)
        self.assertIn('import random', result.code)

    def test_append_method_from_function(self):
        """append(lst, x) should become lst.append(x)."""
        result = self.converter.convert('append(items, 5)')
        self.assertIn('items.append(5)', result.code)

    def test_has_key_special(self):
        """has_key(tbl, key) should become key in tbl."""
        result = self.converter.convert('var x = has_key(data, "name")')
        self.assertIn('"name" in data', result.code)

    def test_file_exists_imports_os(self):
        """file_exists(p) should become os.path.exists(p) with import."""
        result = self.converter.convert('var x = file_exists("test.txt")')
        self.assertIn('os.path.exists("test.txt")', result.code)
        self.assertIn('import os', result.code)


class TestSwapConversion(unittest.TestCase):
    """Test swap statement conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_swap(self):
        result = self.converter.convert('swap a, b')
        self.assertIn('a, b = b, a', result.code)


class TestCommentConversion(unittest.TestCase):
    """Test comment preservation."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_single_line_comment(self):
        result = self.converter.convert('rem: This is a comment')
        self.assertIn('# This is a comment', result.code)

    def test_comments_disabled(self):
        converter = PlainToPythonConverter(preserve_comments=False)
        result = converter.convert('rem: This is a comment')
        self.assertNotIn('#', result.code)

    def test_note_block_preserves_content(self):
        """note: block comments should preserve their text content."""
        code = 'note: First line\n    Second line\n    Third line\n\nvar x = 5'
        result = self.converter.convert(code)
        self.assertIn('# First line', result.code)
        self.assertIn('# Second line', result.code)
        self.assertIn('# Third line', result.code)

    def test_note_block_single_line(self):
        """note: with only one line of text."""
        code = 'note: Just one line\n\nvar x = 5'
        result = self.converter.convert(code)
        self.assertIn('# Just one line', result.code)

    def test_note_block_at_eof(self):
        """note: block at end of file should still preserve text."""
        code = 'var x = 5\nnote: End note\n    Final line.'
        result = self.converter.convert(code)
        self.assertIn('# End note', result.code)
        self.assertIn('# Final line.', result.code)

    def test_note_block_is_multiline_comment(self):
        """note: block should produce multiple # lines, not a docstring."""
        code = 'note: Line A\n    Line B\n\nvar x = 5'
        result = self.converter.convert(code)
        lines = result.code.splitlines()
        comment_lines = [l for l in lines if l.strip().startswith('#')]
        self.assertEqual(len(comment_lines), 2)

    def test_rem_and_note_together(self):
        """Both rem: and note: comments should be preserved."""
        code = 'rem: Single line\nnote: Block line 1\n    Block line 2\n\nvar x = 5'
        result = self.converter.convert(code)
        self.assertIn('# Single line', result.code)
        self.assertIn('# Block line 1', result.code)
        self.assertIn('# Block line 2', result.code)


class TestConversionResult(unittest.TestCase):
    """Test conversion result properties."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_success_result(self):
        result = self.converter.convert('var x = 5')
        self.assertTrue(result.success)
        self.assertEqual(result.errors, [])

    def test_stats_tracked(self):
        result = self.converter.convert('var x = 5\ndisplay(x)')
        self.assertIsNotNone(result.stats)


class TestFixtureIntegration(unittest.TestCase):
    """Integration tests using PLAIN fixture files."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_fixtures_exist(self):
        """Verify test fixtures are in place."""
        self.assertTrue((FIXTURES_DIR / "plain" / "hello.plain").exists())
        self.assertTrue((FIXTURES_DIR / "plain" / "fibonacci.plain").exists())
        self.assertTrue((FIXTURES_DIR / "plain" / "grade_calculator.plain").exists())

    def test_hello_conversion(self):
        code = (FIXTURES_DIR / "plain" / "hello.plain").read_text()
        result = self.converter.convert(code)
        self.assertTrue(result.success)
        self.assertIn('def main():', result.code)
        self.assertIn('print(greeting)', result.code)
        self.assertIn('f"Hello, {name}!"', result.code)

    def test_fibonacci_conversion(self):
        code = (FIXTURES_DIR / "plain" / "fibonacci.plain").read_text()
        result = self.converter.convert(code)
        self.assertTrue(result.success)
        self.assertIn('def fibonacci(n):', result.code)
        self.assertIn('return n', result.code)
        self.assertIn('return a + b', result.code)
        self.assertIn('if __name__ == "__main__":', result.code)

    def test_grade_calculator_conversion(self):
        code = (FIXTURES_DIR / "plain" / "grade_calculator.plain").read_text()
        result = self.converter.convert(code)
        self.assertTrue(result.success)
        self.assertIn('def get_grade(score):', result.code)
        self.assertIn('if score >= 90:', result.code)
        self.assertIn('return "A"', result.code)

    def test_generated_code_is_valid_python(self):
        """Verify the converted code is valid Python (can compile)."""
        for name in ['hello', 'fibonacci', 'grade_calculator']:
            code = (FIXTURES_DIR / "plain" / f"{name}.plain").read_text()
            result = self.converter.convert(code)
            try:
                compile(result.code, f"<{name}>", "exec")
            except SyntaxError as e:
                self.fail(f"{name}.plain produced invalid Python: {e}")


class TestTypeAnnotationConversion(unittest.TestCase):
    """Test type annotation conversion from PLAIN to Python."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_var_with_integer_type(self):
        result = self.converter.convert('var count as integer = 0')
        self.assertIn('count: int = 0', result.code)

    def test_var_with_string_type(self):
        result = self.converter.convert('var name as string = "Alice"')
        self.assertIn('name: str = "Alice"', result.code)

    def test_var_with_float_type(self):
        result = self.converter.convert('var pi as float = 3.14')
        self.assertIn('pi: float = 3.14', result.code)

    def test_var_with_boolean_type(self):
        result = self.converter.convert('var flag as boolean = true')
        self.assertIn('flag: bool = True', result.code)

    def test_var_with_list_type(self):
        result = self.converter.convert('var items as list = []')
        self.assertIn('items: list = []', result.code)

    def test_var_with_table_type(self):
        result = self.converter.convert('var data as table = {}')
        self.assertIn('data: dict = {}', result.code)

    def test_var_with_short_type(self):
        """Test abbreviated type names (int, str, flt, bln, lst, tbl)."""
        result = self.converter.convert('var x as int = 5')
        self.assertIn('x: int = 5', result.code)

    def test_var_with_type_no_value(self):
        result = self.converter.convert('var count as integer')
        self.assertIn('count: int', result.code)

    def test_var_without_type(self):
        """Vars without type annotation should work as before."""
        result = self.converter.convert('var x = 5')
        self.assertIn('x = 5', result.code)

    def test_fxd_with_type_uses_final(self):
        result = self.converter.convert('fxd MAX as integer = 100')
        self.assertIn('MAX: Final[int] = 100', result.code)
        self.assertIn('from typing import Final', result.code)

    def test_fxd_with_string_type(self):
        result = self.converter.convert('fxd NAME as string = "test"')
        self.assertIn('NAME: Final[str] = "test"', result.code)
        self.assertIn('from typing import Final', result.code)

    def test_fxd_without_type(self):
        """fxd without type should work as before (comment-based)."""
        result = self.converter.convert('fxd MAX = 100')
        self.assertIn('MAX = 100', result.code)
        self.assertIn('# constant', result.code)

    def test_task_with_typed_params(self):
        code = 'task Add using (a as integer, b as integer)\n    deliver a + b'
        result = self.converter.convert(code)
        self.assertIn('def add(a: int, b: int):', result.code)

    def test_task_with_mixed_params(self):
        """Some params typed, some not."""
        code = 'task Process with (name as string, value)\n    display(name)'
        result = self.converter.convert(code)
        self.assertIn('def process(name: str, value):', result.code)

    def test_task_without_typed_params(self):
        """Tasks without types should work as before."""
        code = 'task Add using (a, b)\n    deliver a + b'
        result = self.converter.convert(code)
        self.assertIn('def add(a, b):', result.code)

    def test_typed_code_is_valid_python(self):
        """Verify typed conversions produce valid Python."""
        code = ('var count as integer = 0\n'
                'fxd MAX as integer = 100\n'
                'var name as string = "test"\n'
                'task Add using (a as integer, b as integer)\n'
                '    deliver a + b')
        result = self.converter.convert(code)
        self.assertTrue(result.success)
        try:
            compile(result.code, "<typed>", "exec")
        except SyntaxError as e:
            self.fail(f"Typed conversion produced invalid Python: {e}")


class TestRecordConversion(unittest.TestCase):
    """Test PLAIN record → Python dataclass conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_simple_record(self):
        code = 'record Student:\n    name as string\n    age as integer'
        result = self.converter.convert(code)
        self.assertIn('@dataclasses.dataclass', result.code)
        self.assertIn('class Student:', result.code)
        self.assertIn('name: str', result.code)
        self.assertIn('age: int', result.code)

    def test_record_with_defaults(self):
        code = 'record Config:\n    width as integer = 800\n    height as integer = 600'
        result = self.converter.convert(code)
        self.assertIn('width: int = 800', result.code)
        self.assertIn('height: int = 600', result.code)

    def test_record_with_string_default(self):
        code = 'record Person:\n    name as string = "Unknown"'
        result = self.converter.convert(code)
        self.assertIn('name: str = "Unknown"', result.code)

    def test_record_inheritance(self):
        code = 'record GradStudent based on Student:\n    gpa as float = 3.0'
        result = self.converter.convert(code)
        self.assertIn('class GradStudent(Student):', result.code)
        self.assertIn('gpa: float = 3.0', result.code)

    def test_record_imports_dataclasses(self):
        code = 'record Point:\n    x as integer\n    y as integer'
        result = self.converter.convert(code)
        self.assertIn('import dataclasses', result.code)

    def test_record_multiple_types(self):
        code = 'record Item:\n    name as string\n    price as float\n    count as integer\n    active as boolean'
        result = self.converter.convert(code)
        self.assertIn('name: str', result.code)
        self.assertIn('price: float', result.code)
        self.assertIn('count: int', result.code)
        self.assertIn('active: bool', result.code)

    def test_record_short_types(self):
        code = 'record Data:\n    items as lst\n    lookup as tbl'
        result = self.converter.convert(code)
        self.assertIn('items: list', result.code)
        self.assertIn('lookup: dict', result.code)

    def test_record_produces_valid_python(self):
        code = 'record Student:\n    name as string\n    age as integer = 18'
        result = self.converter.convert(code)
        try:
            compile(result.code, "<record>", "exec")
        except SyntaxError as e:
            self.fail(f"Record conversion produced invalid Python: {e}")


class TestUseStatementConversion(unittest.TestCase):
    """Test PLAIN use: block → Python import conversion."""

    def setUp(self):
        self.converter = PlainToPythonConverter()

    def test_modules_simple_import(self):
        """modules: helpers → import helpers"""
        code = 'use:\n    modules:\n        helpers\n'
        result = self.converter.convert(code)
        self.assertIn('import helpers', result.code)

    def test_modules_dotted_path(self):
        """modules: mathlib.geometry → from mathlib import geometry"""
        code = 'use:\n    modules:\n        mathlib.geometry\n'
        result = self.converter.convert(code)
        self.assertIn('from mathlib import geometry', result.code)

    def test_tasks_import(self):
        """tasks: mathlib.arithmetic.Add → from mathlib.arithmetic import add"""
        code = 'use:\n    tasks:\n        mathlib.arithmetic.Add\n'
        result = self.converter.convert(code)
        self.assertIn('from mathlib.arithmetic import add', result.code)

    def test_tasks_simple_module(self):
        """tasks: helpers.Greet → from helpers import greet"""
        code = 'use:\n    tasks:\n        helpers.Greet\n'
        result = self.converter.convert(code)
        self.assertIn('from helpers import greet', result.code)

    def test_assemblies_skipped(self):
        """assemblies: should not produce any imports."""
        code = 'use:\n    assemblies:\n        mathlib\n        textlib\n'
        result = self.converter.convert(code)
        self.assertNotIn('import', result.code)

    def test_full_use_block(self):
        """Full use: block with all three sections."""
        code = ('use:\n'
                '    assemblies:\n'
                '        mathlib\n'
                '    modules:\n'
                '        helpers\n'
                '        mathlib.geometry\n'
                '    tasks:\n'
                '        mathlib.arithmetic.Add\n'
                '        helpers.Greet\n')
        result = self.converter.convert(code)
        self.assertIn('import helpers', result.code)
        self.assertIn('from mathlib import geometry', result.code)
        self.assertIn('from mathlib.arithmetic import add', result.code)
        self.assertIn('from helpers import greet', result.code)

    def test_module_qualified_call_snake_case(self):
        """Module-qualified calls should convert method to snake_case."""
        code = ('use:\n'
                '    modules:\n'
                '        helpers\n\n'
                'var result = helpers.AddNumbers(3, 4)\n')
        result = self.converter.convert(code)
        self.assertIn('helpers.add_numbers(3, 4)', result.code)

    def test_dotted_module_qualified_call(self):
        """Dotted module qualified calls should also convert."""
        code = ('use:\n'
                '    modules:\n'
                '        mathlib.geometry\n\n'
                'var area = geometry.CalculateArea(3, 4)\n')
        result = self.converter.convert(code)
        self.assertIn('geometry.calculate_area(3, 4)', result.code)

    def test_no_use_block_no_imports(self):
        """Code without use: block should have no user imports."""
        code = 'var x = 42\ndisplay(x)\n'
        result = self.converter.convert(code)
        # Should only have stdlib imports if any
        self.assertNotIn('import helpers', result.code)

    def test_task_direct_call_after_import(self):
        """Imported tasks should be callable directly."""
        code = ('use:\n'
                '    tasks:\n'
                '        mathlib.arithmetic.Add\n\n'
                'var x = Add(10, 5)\n')
        result = self.converter.convert(code)
        self.assertIn('from mathlib.arithmetic import add', result.code)
        # The call Add() should become add() via plain_task_to_python_func
        self.assertIn('add(10, 5)', result.code)


if __name__ == "__main__":
    unittest.main()
