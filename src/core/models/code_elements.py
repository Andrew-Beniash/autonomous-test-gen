from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class Function:
    name: str
    params: List[str]
    return_type: str
    body: str
    docstring: Optional[str] = None

@dataclass
class Class:
    name: str
    methods: List[Function]
    attributes: List[str]
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None

@dataclass
class TestCase:
    test_name: str
    function_name: str
    parameters: Dict[str, Any]
    body: str
    description: str
    test_data: Dict[str, Any]
    docstring: Optional[str] = None

@dataclass
class ImportDefinition:
    module: str
    names: List[str]
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
    cognitive_complexity: int
    lines_of_code: int
    

@dataclass
class AnalysisResult:
    classes: List[ClassDefinition] = field(default_factory=list)
    functions: List[FunctionDefinition] = field(default_factory=list)
    imports: List[ImportDefinition] = field(default_factory=list)
    
    def get_dependencies(self) -> List[CodeDependency]:
        """Extract all code dependencies."""
        dependencies = []
        for imp in self.imports:
            dependencies.append(CodeDependency(
                name=imp.module,
                type='import'
            ))
        return dependencies
    
    def get_complexity_metrics(self) -> ComplexityMetrics:
        """Calculate code complexity metrics."""
        return ComplexityMetrics(
            cyclomatic_complexity=1,
            cognitive_complexity=1,
            lines_of_code=len(str(self).split('\n'))
        )