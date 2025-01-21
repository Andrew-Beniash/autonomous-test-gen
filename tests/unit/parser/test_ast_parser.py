import pytest
from typing import Optional
from src.parser.ast_parser import ASTParser, CodeStructure, Language

def test_ast_parser_initialization():
    """Test that AST parser can be initialized with default settings"""
    parser = ASTParser()
    assert parser is not None
    assert parser.supported_languages == {Language.PYTHON, Language.TYPESCRIPT}

def test_detect_language_from_content():
    """Test language detection from code content"""
    parser = ASTParser()
    
    # Python code detection
    python_code = """
    def hello_world():
        print("Hello, World!")
        return True
    """
    assert parser.detect_language(python_code) == Language.PYTHON
    
    # TypeScript code detection
    typescript_code = """
    function helloWorld(): void {
        console.log("Hello, World!");
    }
    """
    assert parser.detect_language(typescript_code) == Language.TYPESCRIPT

def test_parse_invalid_code():
    """Test parser behavior with invalid code"""
    parser = ASTParser()
    with pytest.raises(ValueError, match="Invalid code content"):
        parser.parse("")
    
    # Test with None type - should be caught before reaching parse method
    with pytest.raises(TypeError, match="Code content must be a string"):
        # Using type: ignore to acknowledge we're deliberately testing invalid type
        parser.parse(None)  # type: ignore

def test_parse_python_function():
    """Test parsing a simple Python function"""
    parser = ASTParser()
    code = """
    def calculate_sum(a: int, b: int) -> int:
        return a + b
    """
    
    structure = parser.parse(code)
    assert structure.language == Language.PYTHON
    assert len(structure.functions) == 1
    assert structure.functions[0].name == "calculate_sum"
    assert len(structure.functions[0].parameters) == 2
    assert structure.functions[0].return_type == "int"

def test_parse_python_class():
    """Test parsing a Python class with methods"""
    parser = ASTParser()
    code = """
    class Calculator:
        def __init__(self):
            self.value = 0
            
        def add(self, x: int) -> None:
            self.value += x
            
        def get_value(self) -> int:
            return self.value
    """
    
    structure = parser.parse(code)
    assert structure.language == Language.PYTHON
    assert len(structure.classes) == 1
    assert structure.classes[0].name == "Calculator"
    assert len(structure.classes[0].methods) == 3

def test_get_code_complexity():
    """Test cyclomatic complexity calculation"""
    parser = ASTParser()
    code = """
    def complex_function(x: int) -> str:
        if x > 0:
            if x > 10:
                return "Large"
            else:
                return "Medium"
        else:
            return "Small"
    """
    
    structure = parser.parse(code)
    complexity = structure.functions[0].complexity
    assert complexity > 1  # Should have higher complexity due to nested if statements

def test_identify_dependencies():
    """Test identification of code dependencies"""
    parser = ASTParser()
    code = """
    from typing import List, Optional
    import pandas as pd
    import numpy as np
    
    def process_data(df: pd.DataFrame) -> Optional[np.ndarray]:
        return df.values if not df.empty else None
    """
    
    structure = parser.parse(code)
    assert "pandas" in structure.dependencies
    assert "numpy" in structure.dependencies
    assert "typing" in structure.dependencies

def test_parse_with_custom_rules():
    """Test parsing with custom analysis rules"""
    parser = ASTParser()
    custom_rules = {
        "max_function_length": 10,
        "check_docstrings": True
    }
    
    code = """
    def long_function():
        '''This is a docstring'''
        a = 1
        b = 2
        c = 3
        return a + b + c
    """
    
    structure = parser.parse(code, rules=custom_rules)
    assert structure.functions[0].has_docstring
    assert not structure.functions[0].exceeds_length_limit

def test_error_handling():
    """Test parser error handling for invalid syntax"""
    parser = ASTParser()
    invalid_code = """
    def broken_function(
        print("Missing closing parenthesis"
    """
    
    with pytest.raises(SyntaxError):
        parser.parse(invalid_code)

def test_contextual_analysis():
    """Test parser's ability to understand code context"""
    parser = ASTParser()
    code = """
    class TestCase:
        def setUp(self):
            self.data = []
            
        def test_functionality(self):
            assert True
    """
    
    structure = parser.parse(code)
    assert structure.is_test_file
    assert structure.classes[0].is_test_class
    assert "test_functionality" in [m.name for m in structure.classes[0].methods]