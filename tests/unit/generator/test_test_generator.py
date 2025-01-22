"""Unit tests for the TestGenerator class which creates test cases autonomously."""
import pytest
from unittest.mock import Mock, patch
from src.core.generators.test_generator import TestGenerator
from src.core.models.code_elements import Function, Class, TestCase

def test_generator_initialization():
    """Test TestGenerator initializes with correct default settings."""
    generator = TestGenerator()
    assert generator.template_engine is not None
    assert generator.coverage_threshold == 0.9

@pytest.fixture
def sample_function():
    """Fixture providing a sample function for testing."""
    return Function(
        name="calculate_total",
        params=["items", "tax_rate"],
        return_type="float",
        body="return sum(items) * (1 + tax_rate)",
        docstring="Calculate total cost including tax."
    )

@pytest.fixture
def generator():
    """Fixture providing a TestGenerator instance."""
    return TestGenerator()

def test_generate_function_test_case(generator, sample_function):
    """Test generation of test case for a simple function."""
    test_case = generator.generate_test_case(sample_function)
    
    assert isinstance(test_case, TestCase)
    assert test_case.function_name == "test_calculate_total"
    assert "items" in test_case.parameters
    assert "tax_rate" in test_case.parameters
    assert "assert" in test_case.body

def test_generate_multiple_test_cases(generator, sample_function):
    """Test generation of multiple test cases for edge cases."""
    test_cases = generator.generate_test_cases(sample_function, num_cases=3)
    
    assert len(test_cases) == 3
    assert all(isinstance(tc, TestCase) for tc in test_cases)
    assert len({tc.test_name for tc in test_cases}) == 3  # Unique names

def test_handle_invalid_input(generator):
    """Test generator handles invalid input gracefully."""
    with pytest.raises(ValueError):
        generator.generate_test_case(None)

def test_generate_edge_cases(generator, sample_function):
    """Test generation of edge cases."""
    edge_cases = generator.generate_edge_cases(sample_function)
    
    assert len(edge_cases) >= 2  # At least empty list and negative numbers
    assert any("empty" in tc.description.lower() for tc in edge_cases)
    assert any("negative" in tc.description.lower() for tc in edge_cases)

@pytest.mark.integration
def test_integration_with_template_engine(generator, sample_function):
    """Test integration between generator and template engine."""
    test_case = generator.generate_test_case(sample_function)
    rendered_test = generator.template_engine.render(test_case)
    
    assert "def test_calculate_total" in rendered_test
    assert "pytest" in rendered_test

def test_custom_assertion_generation(generator, sample_function):
    """Test generation of custom assertions based on return type."""
    test_case = generator.generate_test_case(sample_function)
    
    assert "assert isinstance(" in test_case.body
    assert "float" in test_case.body

def test_docstring_generation(generator, sample_function):
    """Test generation of meaningful test docstrings."""
    test_case = generator.generate_test_case(sample_function)
    
    assert test_case.docstring is not None
    assert "Calculate total cost" in test_case.docstring

def test_parameter_type_inference(generator):
    """Test inference of parameter types for test data generation."""
    complex_function = Function(
        name="process_order",
        params=["order_id", "items", "customer"],
        return_type="dict",
        body="...",
        docstring="Process an order with validation."
    )
    
    test_case = generator.generate_test_case(complex_function)
    test_data = test_case.test_data
    
    assert isinstance(test_data["order_id"], (str, int))
    assert isinstance(test_data["items"], list)
    assert isinstance(test_data["customer"], dict)

def test_exception_test_generation(generator):
    """Test generation of tests for exception cases."""
    function = Function(
        name="divide",
        params=["a", "b"],
        return_type="float",
        body="return a / b",
        docstring="Divide a by b."
    )
    
    test_cases = generator.generate_edge_cases(function)
    zero_division_test = next(tc for tc in test_cases 
                            if "zero" in tc.description.lower())
    
    assert "pytest.raises(ZeroDivisionError)" in zero_division_test.body