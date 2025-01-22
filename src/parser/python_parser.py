"""
Purpose: Implementation of Python-specific AST parser
"""
import ast
import logging
from typing import Dict, List, Optional, Set, Union, cast

from src.parser.ast_parser import (
    ASTParser, CodeStructure, Language, Function,
    Method, Class, Parameter
)

logger = logging.getLogger(__name__)

class PythonASTParser(ASTParser):
    """Python-specific implementation of the AST parser"""

    def __init__(self):
        """Initialize the Python AST parser"""
        super().__init__()
        self.current_class: Optional[str] = None

    def detect_language(self, code: str) -> Language:
        """Detect if the code is Python"""
        try:
            ast.parse(code)
            return Language.PYTHON
        except SyntaxError:
            raise ValueError("Invalid Python code")

    def parse(self, code: str, rules: Optional[Dict] = None) -> CodeStructure:
        """Parse Python code and return its structure"""
        if not isinstance(code, str):
            raise TypeError("Code content must be a string")
        if not code.strip():
            raise ValueError("Invalid code content")

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error in Python code: {e}")
            raise

        structure = CodeStructure(
            language=Language.PYTHON,
            functions=[],
            classes=[],
            dependencies=self._extract_dependencies(tree),
            is_test_file=self._is_test_file(tree)
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                structure.classes.append(self._parse_class(node))
            elif isinstance(node, ast.FunctionDef) and not self.current_class:
                structure.functions.append(self._parse_function(node))

        return structure

    def _extract_dependencies(self, tree: ast.AST) -> Set[str]:
        """Extract import dependencies from the code"""
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    dependencies.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split('.')[0])
                
        return dependencies

    def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Function:
        """Parse a function definition"""
        parameters = []
        for arg in node.args.args:
            param_type = self._get_annotation(arg.annotation) if hasattr(arg, 'annotation') else None
            parameters.append(Parameter(
                name=arg.arg,
                type_hint=param_type,
                default_value=None  # TODO: Add default value parsing
            ))

        return_type = self._get_annotation(node.returns) if hasattr(node, 'returns') else None
        
        # Check if function is async
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Check if function is a generator (contains yield or yield from)
        is_generator = False
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                is_generator = True
                break
        
        # A coroutine is either an async function or an async generator
        is_coroutine = is_async
        
        return Function(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            complexity=self._calculate_complexity(node),
            has_docstring=ast.get_docstring(node) is not None,
            exceeds_length_limit=self._check_length_limit(node),
            body=self._get_function_body(node),
            is_async=is_async,
            is_generator=is_generator,
            is_coroutine=is_coroutine
        )

    def _parse_class(self, node: ast.ClassDef) -> Class:
        """Parse a class definition"""
        self.current_class = node.name
        methods = []
        
        for body_item in node.body:
            if isinstance(body_item, ast.FunctionDef):
                method = self._parse_method(body_item)
                methods.append(method)
                
        self.current_class = None
        
        parent_classes: List[str] = []
        for base in node.bases:
            annotation = self._get_annotation(base)
            if annotation is not None:
                parent_classes.append(annotation)
                
        return Class(
            name=node.name,
            methods=methods,
            parent_classes=parent_classes,
            is_test_class=self._is_test_class_node(node)
        )

    def _parse_method(self, node: ast.FunctionDef) -> Method:
        """Parse a class method"""
        is_static = any(isinstance(dec, ast.Name) and dec.id == 'staticmethod' 
                       for dec in node.decorator_list)
        is_class_method = any(isinstance(dec, ast.Name) and dec.id == 'classmethod' 
                            for dec in node.decorator_list)
        is_property = any(isinstance(dec, ast.Name) and dec.id == 'property'
                         for dec in node.decorator_list)

        function = self._parse_function(node)
        return Method(
            name=function.name,
            parameters=function.parameters,
            return_type=function.return_type,
            complexity=function.complexity,
            has_docstring=function.has_docstring,
            exceeds_length_limit=function.exceeds_length_limit,
            body=function.body,
            is_static=is_static,
            is_class_method=is_class_method,
            is_property=is_property
        )

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.Await, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1  # Add complexity for async operations

        return complexity

    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get type annotation as string"""
        if node is None:
            return None
            
        if isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation(node.value)}.{node.attr}"
        
        return None

    def _check_length_limit(self, node: ast.AST) -> bool:
        """Check if function exceeds length limit"""
        return len(ast.unparse(node).split('\n')) > 50  # arbitrary limit

    def _get_function_body(self, node: ast.AST) -> str:
        """Get function body as string"""
        return ast.unparse(node)

    def _is_test_file(self, tree: ast.AST) -> bool:
        """Determine if this is a test file"""
        has_pytest_import = False
        has_test_case = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name == 'pytest':
                        has_pytest_import = True
            elif isinstance(node, ast.ClassDef) and self._is_test_class_node(node):
                has_test_case = True
            elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                has_test_case = True
                
        return has_pytest_import or has_test_case

    def _is_test_class_node(self, node: ast.ClassDef) -> bool:
        """Determine if a class is a test class"""
        return (node.name.startswith('Test') or 
                any(base.id == 'TestCase' for base in node.bases 
                    if isinstance(base, ast.Name)))
    
class PythonParser:
    def parse(self, code: str) -> Optional[ast.AST]:
        """Parse Python code string into AST."""
        if not code or not code.strip():
            raise ValueError("Cannot parse empty code")
        
        try:
            return ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {str(e)}")