"""
Purpose: Test suite for Python-specific AST parser implementation
"""
import ast
import pytest
from typing import List

from src.parser.python_parser import PythonASTParser
from src.parser.ast_parser import Language, CodeStructure, Function, Class, Parameter

class TestPythonASTParser:
    def setup_method(self):
        """Setup parser instance before each test"""
        self.parser = PythonASTParser()

    def test_parse_simple_function(self):
        """Test parsing a simple Python function with type hints"""
        code = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
'''
        structure = self.parser.parse(code)
        
        assert structure.language == Language.PYTHON
        assert len(structure.functions) == 1
        
        func = structure.functions[0]
        assert func.name == "add_numbers"
        assert len(func.parameters) == 2
        assert func.return_type == "int"
        assert func.has_docstring
        assert func.complexity == 1

    def test_parse_class_with_methods(self):
        """Test parsing a Python class with methods"""
        code = '''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self, initial_value: float = 0.0):
        self.value = initial_value
    
    def add(self, x: float) -> float:
        """Add a number to the current value."""
        self.value += x
        return self.value
        
    @property
    def current_value(self) -> float:
        return self.value
'''
        structure = self.parser.parse(code)
        
        assert len(structure.classes) == 1
        cls = structure.classes[0]
        assert cls.name == "Calculator"
        assert len(cls.methods) == 3
        assert cls.methods[2].is_property
        assert cls.methods[0].name == "__init__"

    def test_parse_complex_function(self):
        """Test parsing a function with complex control flow"""
        code = '''
def calculate_grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
'''
        structure = self.parser.parse(code)
        func = structure.functions[0]
        assert func.complexity > 1  # Should have higher complexity due to if/elif branches

    def test_parse_with_dependencies(self):
        """Test parsing code with import statements"""
        code = '''
from typing import List, Optional
import pandas as pd
from datetime import datetime as dt

def process_data(data: List[float]) -> Optional[float]:
    return sum(data) if data else None
'''
        structure = self.parser.parse(code)
        assert "typing" in structure.dependencies
        assert "pandas" in structure.dependencies
        assert "datetime" in structure.dependencies

    def test_parse_decorated_methods(self):
        """Test parsing methods with decorators"""
        code = '''
class APIHandler:
    @staticmethod
    def format_response(data: dict) -> str:
        return json.dumps(data)
        
    @classmethod
    def create(cls, config: dict):
        return cls()
        
    @property
    def base_url(self) -> str:
        return self._base_url
'''
        structure = self.parser.parse(code)
        cls = structure.classes[0]
        
        assert cls.methods[0].is_static
        assert cls.methods[1].is_class_method
        assert cls.methods[2].is_property

    def test_error_handling(self):
        """Test parser error handling for invalid Python code"""
        with pytest.raises(SyntaxError):
            self.parser.parse("def invalid_syntax(:")

        with pytest.raises(ValueError):
            self.parser.parse("")

    def test_parse_nested_functions(self):
        """Test parsing nested function definitions"""
        code = '''
def outer(x: int) -> callable:
    """Outer function"""
    def inner(y: int) -> int:
        """Inner function"""
        return x + y
    return inner
'''
        structure = self.parser.parse(code)
        assert len(structure.functions) == 2
        assert any(f.name == "outer" for f in structure.functions)
        assert any(f.name == "inner" for f in structure.functions)

    def test_detect_test_files(self):
        """Test detection of test files and classes"""
        code = '''
import pytest

class TestCalculator:
    def test_addition(self):
        assert 1 + 1 == 2
        
    def test_subtraction(self):
        assert 2 - 1 == 1
'''
        structure = self.parser.parse(code)
        assert structure.is_test_file
        assert structure.classes[0].is_test_class
        assert len(structure.classes[0].methods) == 2