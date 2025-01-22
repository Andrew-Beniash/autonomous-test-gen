import ast
from typing import List, Optional, Dict, Set, Any
from dataclasses import dataclass, field
from src.core.models.code_elements import (
    AnalysisResult,
    ClassDefinition,
    FunctionDefinition,
    ImportDefinition,
    ComplexityMetrics
)

@dataclass
class NodeContext:
    """Context for tracking AST node relationships."""
    node: ast.AST
    parent: Optional['NodeContext'] = None
    children: List['NodeContext'] = field(default_factory=list)

class CodeStructureAnalyzer:
    """Analyzes Python code structure using AST."""
    
    def analyze(self, code: str) -> AnalysisResult:
        """
        Analyze Python code and return structured information about its contents.
        
        Args:
            code (str): Python source code to analyze
            
        Returns:
            AnalysisResult: Analysis results containing code structure information
            
        Raises:
            SyntaxError: If the provided code has syntax errors
        """
        try:
            tree = ast.parse(code)
            self.node_context = self._build_node_context(tree)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python code: {str(e)}") from e
            
        result = AnalysisResult()
        
        # Analyze the AST
        for node in ast.walk(tree):
            # Handle imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                result.imports.extend(self._process_import(node))
                
            # Handle function definitions
            elif isinstance(node, ast.FunctionDef):
                if not self._is_class_method(node):  # Only add top-level functions
                    result.functions.append(self._process_function(node))
                    
            # Handle class definitions
            elif isinstance(node, ast.ClassDef):
                result.classes.append(self._process_class(node))
                
        return result

    def _build_node_context(self, node: ast.AST, parent: Optional[NodeContext] = None) -> NodeContext:
        """Build node context tree for tracking relationships."""
        context = NodeContext(node=node, parent=parent)
        
        for child in ast.iter_child_nodes(node):
            child_context = self._build_node_context(child, context)
            context.children.append(child_context)
            
        return context
    
    def _get_node_context(self, node: ast.AST) -> Optional[NodeContext]:
        """Find context for a specific node."""
        def find_in_context(context: NodeContext, target: ast.AST) -> Optional[NodeContext]:
            if context.node is target:
                return context
            for child in context.children:
                result = find_in_context(child, target)
                if result:
                    return result
            return None
            
        return find_in_context(self.node_context, node)
    
    def _process_import(self, node: ast.AST) -> List[ImportDefinition]:
        """Process import statements."""
        imports = []
        
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(ImportDefinition(
                    module=name.name,
                    names=[name.asname or name.name]
                ))
        elif isinstance(node, ast.ImportFrom):
            imports.append(ImportDefinition(
                module=node.module or '',
                names=[n.name for n in node.names],
                is_from_import=True
            ))
            
        return imports
    
    def _process_function(self, node: ast.FunctionDef) -> FunctionDefinition:
        """Process function definitions."""
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Check for return type annotation
        return_type = None
        if node.returns:
            return_type = self._get_annotation_name(node.returns)
            
        # Check if it's a property
        is_property = any(
            isinstance(decorator, ast.Name) and decorator.id == 'property'
            for decorator in node.decorator_list
        )
        
        return FunctionDefinition(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            is_property=is_property
        )
    
    def _process_class(self, node: ast.ClassDef) -> ClassDefinition:
        """Process class definitions."""
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get base classes
        base_classes = [self._get_annotation_name(base) for base in node.bases]
        
        # Process methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._process_function(item))
                
        return ClassDefinition(
            name=node.name,
            methods=methods,
            docstring=docstring,
            base_classes=base_classes
        )
    
    def _is_class_method(self, node: ast.FunctionDef) -> bool:
        """Check if a function definition is inside a class."""
        context = self._get_node_context(node)
        if not context:
            return False
            
        current = context.parent
        while current:
            if isinstance(current.node, ast.ClassDef):
                return True
            current = current.parent
        return False
    
    def _get_annotation_name(self, node: ast.AST) -> str:
        """Extract name from type annotation."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return self._get_annotation_name(node.value)
        return ""