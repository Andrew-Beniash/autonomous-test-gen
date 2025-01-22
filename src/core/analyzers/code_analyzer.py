"""Code analyzer component for parsing and analyzing Python code."""
import ast
from dataclasses import dataclass
from typing import List, Optional
from src.core.models.code_elements import (
    AnalysisResult,
    FunctionDefinition,
    ClassDefinition,
    ImportDefinition,
)

@dataclass
class NodeContext:
    """Context for tracking AST node relationships."""
    node: ast.AST
    parent: Optional['NodeContext'] = None
    children: List['NodeContext'] = list()

class CodeStructureAnalyzer:
    """Analyzes Python code structure and extracts key elements."""
    
    def analyze(self, code: str) -> AnalysisResult:
        """Analyze code string and return structured analysis result."""
        try:
            tree = ast.parse(code)
            return self._analyze_tree(tree)
        except SyntaxError as e:
            raise SyntaxError(f"Failed to parse code: {str(e)}")

    def _analyze_tree(self, tree: ast.AST) -> AnalysisResult:
        """Analyze parsed AST and extract code elements."""
        result = AnalysisResult()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_class_method(node):
                    result.functions.append(self._analyze_function(node))
            elif isinstance(node, ast.ClassDef):
                result.classes.append(self._analyze_class(node))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                result.imports.extend(self._process_import(node))
        
        return result

    def _analyze_function(self, node: ast.FunctionDef) -> FunctionDefinition:
        """Extract function information from AST node."""
        return FunctionDefinition(
            name=node.name,
            parameters=[arg.arg for arg in node.args.args],
            return_type=self._get_return_type(node),
            docstring=ast.get_docstring(node),
            is_property=any(isinstance(d, ast.Name) and d.id == 'property' 
                          for d in node.decorator_list)
        )

    def _analyze_class(self, node: ast.ClassDef) -> ClassDefinition:
        """Extract class information from AST node."""
        return ClassDefinition(
            name=node.name,
            methods=[self._analyze_function(n) for n in node.body 
                    if isinstance(n, ast.FunctionDef)],
            docstring=ast.get_docstring(node),
            base_classes=[self._get_name(base) for base in node.bases]
        )

    def _process_import(self, node: ast.AST) -> List[ImportDefinition]:
        """Process import statements."""
        imports = []
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(ImportDefinition(
                    module=name.name,
                    names=[name.asname or name.name],
                    is_from_import=False
                ))
        elif isinstance(node, ast.ImportFrom):
            imports.append(ImportDefinition(
                module=node.module or '',
                names=[n.name for n in node.names],
                is_from_import=True
            ))
        return imports

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present."""
        if node.returns:
            return ast.unparse(node.returns)
        return None

    def _is_class_method(self, node: ast.FunctionDef) -> bool:
        """Check if a function definition is inside a class."""
        return any(isinstance(parent, ast.ClassDef) 
                  for parent in ast.walk(node))

    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        return ast.unparse(node)