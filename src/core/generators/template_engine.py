"""Template engine for generating test code."""
from typing import List
from src.core.models.code_elements import TestCase

class TemplateEngine:
    def render(self, test_case: TestCase) -> str:
        """Render a single test case to code."""
        return self._generate_test_function(test_case)

    def render_test_module(self, test_cases: List[TestCase]) -> str:
        """Render multiple test cases as a test module."""
        imports = "import pytest\n\n"
        test_functions = "\n\n".join(self._generate_test_function(tc) for tc in test_cases)
        return f"{imports}{test_functions}"

    def _generate_test_function(self, test_case: TestCase) -> str:
        """Generate a test function from a test case."""
        docstring = f'    """{test_case.docstring}"""' if test_case.docstring else ""
        return (
            f"def {test_case.test_name}():\n"
            f"{docstring}\n"
            f"    {test_case.body}"
        )