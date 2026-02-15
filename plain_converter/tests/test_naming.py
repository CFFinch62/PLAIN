"""Tests for naming convention conversion utilities."""

import unittest
from plain_converter.utils.naming import (
    detect_case_style,
    to_snake_case,
    to_pascal_case,
    to_camel_case,
    to_upper_snake_case,
    add_type_prefix,
    strip_type_prefix,
    python_func_to_plain_task,
    plain_task_to_python_func,
)


class TestDetectCaseStyle(unittest.TestCase):
    def test_snake_case(self):
        self.assertEqual(detect_case_style("my_function"), "snake_case")
        self.assertEqual(detect_case_style("calculate_sum"), "snake_case")
        self.assertEqual(detect_case_style("x"), "snake_case")

    def test_pascal_case(self):
        self.assertEqual(detect_case_style("MyFunction"), "PascalCase")
        self.assertEqual(detect_case_style("CalculateSum"), "PascalCase")

    def test_camel_case(self):
        self.assertEqual(detect_case_style("myVariable"), "camelCase")
        self.assertEqual(detect_case_style("calculateSum"), "camelCase")

    def test_upper_snake_case(self):
        self.assertEqual(detect_case_style("MAX_VALUE"), "UPPER_SNAKE_CASE")
        self.assertEqual(detect_case_style("PI"), "UPPER_SNAKE_CASE")

    def test_empty_string(self):
        self.assertEqual(detect_case_style(""), "unknown")


class TestToSnakeCase(unittest.TestCase):
    def test_from_pascal_case(self):
        self.assertEqual(to_snake_case("MyFunction"), "my_function")
        self.assertEqual(to_snake_case("CalculateSum"), "calculate_sum")

    def test_from_camel_case(self):
        self.assertEqual(to_snake_case("myVariable"), "my_variable")
        self.assertEqual(to_snake_case("calculateSum"), "calculate_sum")

    def test_from_upper_snake_case(self):
        self.assertEqual(to_snake_case("MAX_VALUE"), "max_value")

    def test_already_snake_case(self):
        self.assertEqual(to_snake_case("already_snake"), "already_snake")

    def test_single_word(self):
        self.assertEqual(to_snake_case("main"), "main")
        self.assertEqual(to_snake_case("Main"), "main")

    def test_empty_string(self):
        self.assertEqual(to_snake_case(""), "")


class TestToPascalCase(unittest.TestCase):
    def test_from_snake_case(self):
        self.assertEqual(to_pascal_case("my_function"), "MyFunction")
        self.assertEqual(to_pascal_case("calculate_sum"), "CalculateSum")

    def test_from_camel_case(self):
        self.assertEqual(to_pascal_case("myVariable"), "MyVariable")

    def test_from_upper_snake_case(self):
        self.assertEqual(to_pascal_case("MAX_VALUE"), "MaxValue")

    def test_already_pascal_case(self):
        self.assertEqual(to_pascal_case("MyFunction"), "MyFunction")

    def test_single_word(self):
        self.assertEqual(to_pascal_case("main"), "Main")

    def test_empty_string(self):
        self.assertEqual(to_pascal_case(""), "")


class TestToCamelCase(unittest.TestCase):
    def test_from_snake_case(self):
        self.assertEqual(to_camel_case("my_function"), "myFunction")

    def test_from_pascal_case(self):
        self.assertEqual(to_camel_case("MyFunction"), "myFunction")

    def test_single_word(self):
        self.assertEqual(to_camel_case("main"), "main")


class TestToUpperSnakeCase(unittest.TestCase):
    def test_from_snake_case(self):
        self.assertEqual(to_upper_snake_case("max_value"), "MAX_VALUE")

    def test_from_pascal_case(self):
        self.assertEqual(to_upper_snake_case("MyFunction"), "MY_FUNCTION")

    def test_from_camel_case(self):
        self.assertEqual(to_upper_snake_case("myVariable"), "MY_VARIABLE")


class TestTypePrefix(unittest.TestCase):
    def test_add_type_prefix(self):
        self.assertEqual(add_type_prefix("count", "integer"), "intCount")
        self.assertEqual(add_type_prefix("name", "string"), "strName")
        self.assertEqual(add_type_prefix("is_valid", "boolean"), "blnIsValid")
        self.assertEqual(add_type_prefix("price", "float"), "fltPrice")
        self.assertEqual(add_type_prefix("items", "list"), "lstItems")
        self.assertEqual(add_type_prefix("data", "table"), "tblData")

    def test_add_unknown_type_prefix(self):
        self.assertEqual(add_type_prefix("value", "unknown_type"), "value")

    def test_strip_type_prefix(self):
        self.assertEqual(strip_type_prefix("intCount"), ("count", "integer"))
        self.assertEqual(strip_type_prefix("strName"), ("name", "string"))
        self.assertEqual(strip_type_prefix("blnIsValid"), ("isValid", "boolean"))
        self.assertEqual(strip_type_prefix("fltPrice"), ("price", "float"))

    def test_strip_no_prefix(self):
        self.assertEqual(strip_type_prefix("myVar"), ("myVar", None))
        self.assertEqual(strip_type_prefix("count"), ("count", None))

    def test_strip_false_positive(self):
        # "string" starts with "str" but 'i' is lowercase
        self.assertEqual(strip_type_prefix("string"), ("string", None))
        self.assertEqual(strip_type_prefix("integer"), ("integer", None))


class TestFuncTaskConversion(unittest.TestCase):
    def test_python_to_plain(self):
        self.assertEqual(python_func_to_plain_task("my_function"), "MyFunction")
        self.assertEqual(python_func_to_plain_task("main"), "Main")
        self.assertEqual(python_func_to_plain_task("calculate_sum"), "CalculateSum")

    def test_plain_to_python(self):
        self.assertEqual(plain_task_to_python_func("MyFunction"), "my_function")
        self.assertEqual(plain_task_to_python_func("Main"), "main")
        self.assertEqual(plain_task_to_python_func("CalculateSum"), "calculate_sum")


if __name__ == "__main__":
    unittest.main()

