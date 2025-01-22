import pytest
from typing import Dict, List
from src.core.analyzers import CodeStructureAnalyzer
from src.core.models.code_elements import (
    ClassDefinition,
    FunctionDefinition,
    CodeDependency
)

# Sample code snippets for testing
SIMPLE_FUNCTION = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
'''

CLASS_WITH_METHODS = '''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.value = 0
        
    def add(self, x: int) -> int:
        """Add a number to the current value."""
        self.value += x
        return self.value
'''

COMPLEX_CODE = '''
from typing import List, Optional
import math

class DataProcessor:
    def __init__(self, data: List[float]):
        self.data = data
        self._processed = False
        
    def process(self) -> Optional[float]:
        if not self.data:
            return None
        result = sum(self.data) / len(self.data)
        self._processed = True
        return result
        
    @property
    def is_processed(self) -> bool:
        return self._processed
'''

@pytest.fixture
def analyzer():
    """Fixture to provide a CodeStructureAnalyzer instance."""
    return CodeStructureAnalyzer()

class TestCodeStructureAnalyzer:
    def test_analyze_simple_function(self, analyzer):
        """Test analysis of a simple function definition."""
        result = analyzer.analyze(SIMPLE_FUNCTION)
        
        assert len(result.functions) == 1
        func = result.functions[0]
        assert func.name == "add_numbers"
        assert func.parameters == ["a", "b"]
        assert func.return_type == "int"
        assert func.docstring is not None
        assert "Add two numbers together" in func.docstring
        
    def test_analyze_class_structure(self, analyzer):
        """Test analysis of a class with methods."""
        result = analyzer.analyze(CLASS_WITH_METHODS)
        
        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "Calculator"
        assert len(cls.methods) == 2
        assert "add" in [m.name for m in cls.methods]
        assert "__init__" in [m.name for m in cls.methods]
        
    def test_analyze_complex_code(self, analyzer):
        """Test analysis of complex code with imports and decorators."""
        result = analyzer.analyze(COMPLEX_CODE)
        
        # Check imports
        assert len(result.imports) == 2
        assert "typing" in [imp.module for imp in result.imports]
        assert "math" in [imp.module for imp in result.imports]
        
        # Check class structure
        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "DataProcessor"
        assert len(cls.methods) == 3  # __init__, process, is_processed
        
        # Check property decorator
        property_method = next(m for m in cls.methods if m.name == "is_processed")
        assert property_method.is_property == True
        
    def test_analyze_dependencies(self, analyzer):
        """Test analysis of code dependencies."""
        result = analyzer.analyze(COMPLEX_CODE)
        
        # Check direct dependencies
        deps = result.get_dependencies()
        assert any(d.name == "typing" for d in deps)
        assert any(d.name == "math" for d in deps)
        
    def test_empty_code(self, analyzer):
        """Test analysis of empty code."""
        result = analyzer.analyze("")
        
        assert len(result.classes) == 0
        assert len(result.functions) == 0
        assert len(result.imports) == 0
        
    def test_invalid_code(self, analyzer):
        """Test analysis of invalid Python code."""
        with pytest.raises(SyntaxError):
            analyzer.analyze("def invalid_func(:")
            
    def test_code_complexity(self, analyzer):
        """Test analysis of code complexity metrics."""
        result = analyzer.analyze(COMPLEX_CODE)
        
        complexity = result.get_complexity_metrics()
        assert complexity.cyclomatic_complexity > 0
        assert isinstance(complexity.loc, int)
        assert complexity.loc > 0
        
    def test_docstring_extraction(self, analyzer):
        """Test extraction of docstrings."""
        result = analyzer.analyze(CLASS_WITH_METHODS)
        
        cls = result.classes[0]
        assert cls.docstring is not None
        assert "simple calculator class" in cls.docstring.lower()
        
        add_method = next(m for m in cls.methods if m.name == "add")
        assert add_method.docstring is not None
        assert "add a number" in add_method.docstring.lower()