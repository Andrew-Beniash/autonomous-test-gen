"""Integration tests for the TestGenerator with other system components."""
import pytest
from src.core.generators.test_generator import TestGenerator
from src.core.analyzers.code_analyzer import CodeAnalyzer
from src.parser.python_parser import PythonParser

@pytest.fixture
def analysis_chain():
    """Fixture providing the full analysis chain."""
    parser = PythonParser()
    analyzer = CodeAnalyzer()
    generator = TestGenerator()
    return parser, analyzer, generator

@pytest.fixture
def sample_code():
    """Fixture providing sample Python code for testing."""
    return """
def calculate_price(base_price: float, tax_rate: float = 0.1, 
                   discount: float = 0.0) -> float:
    \"\"\"Calculate final price with tax and discount.
    
    Args:
        base_price: Base price of the item
        tax_rate: Tax rate as decimal (default: 0.1)
        discount: Discount as decimal (default: 0.0)
    
    Returns:
        float: Final price after tax and discount
    \"\"\"
    if not isinstance(base_price, (int, float)) or base_price < 0:
        raise ValueError("Base price must be a non-negative number")
    
    pretax = base_price * (1 - discount)
    final_price = pretax * (1 + tax_rate)
    return round(final_price, 2)
"""

def test_end_to_end_test_generation(analysis_chain, sample_code):
    """Test the entire chain from code parsing to test generation."""
    parser, analyzer, generator = analysis_chain
    
    # Parse the code
    parsed_code = parser.parse(sample_code)
    assert parsed_code is not None
    
    # Analyze the code
    analysis_result = analyzer.analyze(parsed_code)
    assert len(analysis_result.functions) == 1
    
    # Generate tests
    function = analysis_result.functions[0]
    test_cases = generator.generate_test_cases(function)
    
    # Verify test cases
    assert len(test_cases) >= 3
    assert all("test_calculate_price" in tc.test_name for tc in test_cases)
    
    # Verify different scenarios are covered
    test_descriptions = " ".join(tc.description.lower() for tc in test_cases)
    assert "valid" in test_descriptions
    assert "invalid" in test_descriptions
    assert "discount" in test_descriptions

@pytest.mark.integration
def test_generated_tests_execution(analysis_chain, sample_code, tmp_path):
    """Test that generated tests can be executed successfully."""
    parser, analyzer, generator = analysis_chain
    
    # Generate and write tests to temporary file
    parsed_code = parser.parse(sample_code)
    function = analyzer.analyze(parsed_code).functions[0]
    test_cases = generator.generate_test_cases(function)
    
    test_file = tmp_path / "test_calculate_price.py"
    with open(test_file, "w") as f:
        f.write(generator.template_engine.render_test_module(test_cases))
    
    # Execute generated tests
    pytest.main([str(test_file), "-v"])

@pytest.mark.integration
def test_complex_code_analysis(analysis_chain):
    """Test handling of more complex code structures."""
    complex_code = """
class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, item: dict, quantity: int = 1) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be positive")
        self.items.extend([item] * quantity)
    
    def get_total(self, tax_rate: float = 0.1) -> float:
        subtotal = sum(item['price'] for item in self.items)
        return subtotal * (1 + tax_rate)
"""
    
    parser, analyzer, generator = analysis_chain
    parsed_code = parser.parse(complex_code)
    analysis_result = analyzer.analyze(parsed_code)
    
    assert len(analysis_result.classes) == 1
    class_info = analysis_result.classes[0]
    
    test_cases = generator.generate_class_test_cases(class_info)
    assert len(test_cases) >= 3
    
    method_names = {tc.test_name for tc in test_cases}
    assert any("init" in name for name in method_names)
    assert any("add_item" in name for name in method_names)
    assert any("get_total" in name for name in method_names)

@pytest.mark.integration
def test_docstring_analysis_integration(analysis_chain, sample_code):
    """Test integration of docstring analysis in test generation."""
    parser, analyzer, generator = analysis_chain
    
    parsed_code = parser.parse(sample_code)
    function = analyzer.analyze(parsed_code).functions[0]
    test_cases = generator.generate_test_cases(function)
    
    # Verify docstring information is used in test cases
    assert any("tax rate" in tc.docstring.lower() for tc in test_cases)
    assert any("discount" in tc.docstring.lower() for tc in test_cases)

@pytest.mark.integration
def test_error_handling_integration(analysis_chain):
    """Test integrated error handling across components."""
    parser, analyzer, generator = analysis_chain
    
    with pytest.raises(ValueError):
        parser.parse("")
    
    with pytest.raises(ValueError):
        analyzer.analyze(None)
    
    with pytest.raises(ValueError):
        generator.generate_test_cases(None)