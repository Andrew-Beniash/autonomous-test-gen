from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ImportDefinition:
    module: str
    names: List[str] = field(default_factory=list)
    is_from_import: bool = False

@dataclass
class FunctionDefinition:
    name: str
    parameters: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    is_property: bool = False
    
@dataclass
class ClassDefinition:
    name: str
    methods: List[FunctionDefinition] = field(default_factory=list)
    docstring: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)

@dataclass
class CodeDependency:
    name: str
    type: str  # 'import', 'class', 'function'
    path: Optional[str] = None

@dataclass
class ComplexityMetrics:
    cyclomatic_complexity: int
    loc: int  # Lines of code
    comment_ratio: float
    
@dataclass
class AnalysisResult:
    classes: List[ClassDefinition] = field(default_factory=list)
    functions: List[FunctionDefinition] = field(default_factory=list)
    imports: List[ImportDefinition] = field(default_factory=list)
    
    def get_dependencies(self) -> List[CodeDependency]:
        """Extract all code dependencies."""
        dependencies = []
        
        # Add import dependencies
        for imp in self.imports:
            dependencies.append(CodeDependency(
                name=imp.module,
                type='import'
            ))
            
        return dependencies
    
    def get_complexity_metrics(self) -> ComplexityMetrics:
        """Calculate code complexity metrics."""
        # This is a placeholder implementation
        return ComplexityMetrics(
            cyclomatic_complexity=1,
            loc=len(str(self).split('\n')),
            comment_ratio=0.1
        )