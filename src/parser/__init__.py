"""
Purpose: Initializes the parser package and provides convenient imports
"""
from src.parser.ast_parser import (
    ASTParser,
    CodeStructure,
    Language,
    Function,
    Method,
    Class,
    Parameter
)

__all__ = [
    'ASTParser',
    'CodeStructure',
    'Language',
    'Function',
    'Method',
    'Class',
    'Parameter'
]