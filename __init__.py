"""TLSQL: A SQL conversion library for custom SQL statements

This package converts three types of custom SQL statements into standard SQL:
1. TRAIN WITH - Training data queries
2. PREDICT VALUE - Prediction target queries
3. VALIDATE WITH - Validation data queries

Usage:
    Basic usage:
        >>> import tlsql
        >>> result = tlsql.convert("PREDICT VALUE(users.Age, CLF) FROM users")
        >>> print(result.statement_type)
        'PREDICT'

    Advanced usage:
        >>> from tlsql import Parser, SQLGenerator
        >>> parser = Parser("PREDICT VALUE(users.Age, CLF) FROM users")
        >>> ast = parser.parse()
"""

__version__ = "0.1.0"
__author__ = "TLSQL Team"


def convert(tlsql: str):
    """Convert TLSQL statement to standard SQL

    This is the main entry point for TLSQL conversion.

    Args:
        tlsql: TLSQL statement string

    Returns:
        ConversionResult: Unified result containing statement type and all metadata

    """
    from tlsql.tlsql.sql_generator import SQLGenerator
    return SQLGenerator.convert(tlsql)


# Core classes (re-exported for convenience)
from tlsql.tlsql.lexer import Lexer
from tlsql.tlsql.parser import Parser
from tlsql.tlsql.sql_generator import (
    SQLGenerator,
    GeneratedSQL,
    FilterCondition,
    ConversionResult,
)

# AST nodes (commonly used)
from tlsql.tlsql.ast_nodes import (
    Statement,
    TrainStatement,
    ValidateStatement,
    PredictStatement,
    ValueClause,
    FromClause,
    WhereClause,
    BinaryExpr,
    UnaryExpr,
    ColumnExpr,
    LiteralExpr,
    BetweenExpr,
    InExpr,
    ColumnReference,
    PredictType,
)

# Exceptions
from tlsql.tlsql.exceptions import (
    TLSQLError,
    LexerError,
    ParseError,
    GenerationError,
)

__all__ = [
    # Top-level API
    "convert",
    # Core classes
    "Lexer",
    "Parser",
    "SQLGenerator",
    "GeneratedSQL",
    "FilterCondition",
    "ConversionResult",
    # AST nodes
    "Statement",
    "TrainStatement",
    "ValidateStatement",
    "PredictStatement",
    "ValueClause",
    "FromClause",
    "WhereClause",
    "BinaryExpr",
    "UnaryExpr",
    "ColumnExpr",
    "LiteralExpr",
    "BetweenExpr",
    "InExpr",
    "ColumnReference",
    "PredictType",
    # Exceptions
    "TLSQLError",
    "LexerError",
    "ParseError",
    "GenerationError",
]
