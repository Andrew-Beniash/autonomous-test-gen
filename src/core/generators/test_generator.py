"""Test case generator for autonomous test generation."""
from typing import List, Dict, Any, Optional
import random
from src.core.models.code_elements import Function, TestCase
from src.core.generators.template_engine import TemplateEngine

class TestGenerator:
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.coverage_threshold = 0.9

    def generate_test_case(self, function: Function) -> TestCase:
        """Generate a single test case for a function."""
        if not function:
            raise ValueError("Function cannot be None")

        test_data = self._generate_test_data(function)
        body = self._generate_test_body(function, test_data)
        
        return TestCase(
            test_name=f"test_{function.name}",
            function_name=function.name,
            parameters=test_data,
            body=body,
            description=f"Test {function.name} with valid input",
            test_data=test_data,
            docstring=self._generate_docstring(function)
        )

    def generate_test_cases(self, function: Function, num_cases: int = 3) -> List[TestCase]:
        """Generate multiple test cases for a function."""
        test_cases = [self.generate_test_case(function)]
        test_cases.extend(self.generate_edge_cases(function))
        
        while len(test_cases) < num_cases:
            test_case = self.generate_test_case(function)
            test_case.test_name = f"test_{function.name}_{len(test_cases)}"
            test_cases.append(test_case)
        
        return test_cases

    def generate_edge_cases(self, function: Function) -> List[TestCase]:
        """Generate edge case tests for a function."""
        edge_cases = []

        # Empty input test
        edge_cases.append(self._generate_empty_input_test(function))
        
        # Type error test
        edge_cases.append(self._generate_type_error_test(function))
        
        # Handle numeric inputs
        if self._has_numeric_params(function):
            edge_cases.append(self._generate_negative_input_test(function))
            edge_cases.append(self._generate_zero_input_test(function))

        return edge_cases

    def _generate_test_data(self, function: Function) -> Dict[str, Any]:
        """Generate test data based on parameter types."""
        test_data = {}
        for param in function.params:
            test_data[param] = self._generate_param_value(param)
        return test_data

    def _generate_param_value(self, param_name: str) -> Any:
        """Generate appropriate test value based on parameter name."""
        if "id" in param_name.lower():
            return random.randint(1, 1000)
        elif "rate" in param_name.lower():
            return round(random.uniform(0, 1), 2)
        elif "items" in param_name.lower():
            return [random.randint(1, 100) for _ in range(3)]
        elif "price" in param_name.lower():
            return round(random.uniform(10, 1000), 2)
        else:
            return "test_value"

    def _generate_test_body(self, function: Function, test_data: Dict[str, Any]) -> str:
        """Generate test body with assertions."""
        params_str = ", ".join(f"{k}={repr(v)}" for k, v in test_data.items())
        
        body = [
            f"result = {function.name}({params_str})",
            f"assert isinstance(result, {function.return_type})"
        ]
        
        if function.return_type in ("float", "int"):
            body.append("assert result >= 0")
        
        return "\n    ".join(body)

    def _generate_docstring(self, function: Function) -> str:
        """Generate docstring for test case."""
        return f"""Test {function.name} functionality.
        
        Tests the {function.name} function with valid input data.
        Original function: {function.docstring}
        """

    def _generate_empty_input_test(self, function: Function) -> TestCase:
        """Generate test for empty input."""
        test_data = {param: [] if "items" in param else "" for param in function.params}
        body = (
            "with pytest.raises(ValueError):\n"
            f"    {function.name}({', '.join(f'{k}={repr(v)}' for k, v in test_data.items())})"
        )
        
        return TestCase(
            test_name=f"test_{function.name}_empty_input",
            function_name=function.name,
            parameters=test_data,
            body=body,
            description="Test with empty input",
            test_data=test_data,
            docstring="Test handling of empty input values."
        )

    def _generate_type_error_test(self, function: Function) -> TestCase:
        """Generate test for type errors."""
        test_data = {param: None for param in function.params}
        body = (
            "with pytest.raises((TypeError, ValueError)):\n"
            f"    {function.name}({', '.join(f'{k}={repr(v)}' for k, v in test_data.items())})"
        )
        
        return TestCase(
            test_name=f"test_{function.name}_type_error",
            function_name=function.name,
            parameters=test_data,
            body=body,
            description="Test with invalid types",
            test_data=test_data,
            docstring="Test handling of invalid input types."
        )

    def _has_numeric_params(self, function: Function) -> bool:
        """Check if function has numeric parameters."""
        numeric_indicators = {"price", "rate", "amount", "total", "quantity", "num", "count"}
        return any(any(ind in param.lower() for ind in numeric_indicators) 
                  for param in function.params)

    def _generate_negative_input_test(self, function: Function) -> TestCase:
        """Generate test for negative numeric inputs."""
        test_data = {param: -1 for param in function.params}
        body = (
            "with pytest.raises(ValueError):\n"
            f"    {function.name}({', '.join(f'{k}={repr(v)}' for k, v in test_data.items())})"
        )
        
        return TestCase(
            test_name=f"test_{function.name}_negative_input",
            function_name=function.name,
            parameters=test_data,
            body=body,
            description="Test with negative input",
            test_data=test_data,
            docstring="Test handling of negative input values."
        )

    def _generate_zero_input_test(self, function: Function) -> TestCase:
        """Generate test for zero value inputs."""
        test_data = {param: 0 for param in function.params}
        body = f"{function.name}({', '.join(f'{k}={repr(v)}' for k, v in test_data.items())})"
        
        return TestCase(
            test_name=f"test_{function.name}_zero_input",
            function_name=function.name,
            parameters=test_data,
            body=body,
            description="Test with zero input",
            test_data=test_data,
            docstring="Test handling of zero input values."
        )