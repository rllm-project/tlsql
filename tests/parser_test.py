import sys

sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")

from tlsql import Parser
from tlsql import (
    PredictStatement, ValueClause, FromClause, WhereClause,
    BinaryExpr, UnaryExpr, ColumnExpr, LiteralExpr, BetweenExpr, InExpr,
    ColumnReference, PredictType
)


def test_train_syntax():
    """Test TRAIN USING statement"""
    print("Test 1: TRAIN USING statement")

    query = """
    TRAIN with  (user.*, movie.title, rating.*)
    FROM Tables(user, movie, rating)
    WHERE user.loc = 'BJ' AND movie.year > 1990 AND rating.score > 3
    """

    try:
        parser = Parser(query)
        ast = parser.parse()

        print("[SUCCESS] Parsed successfully")
        print(f"Statement type: {ast.statement_type}")

        # Access TRAIN statement / 访问TRAIN语句
        train = ast.train

        print("USING clause:")
        print(f"  Selector count: {len(train.with_clause.selectors)}")
        for i, selector in enumerate(train.with_clause.selectors, 1):
            print(f"  {i}. {selector.table}.{selector.column} (is wildcard: {selector.is_wildcard})")

        print("FROM Tables:")
        print(f"  Tables: {', '.join(train.tables.tables)}")
        print(f"  Count: {len(train.tables.tables)}")

        if train.where:
            print("\nWHERE clause:")
            print(f"  Type: {type(train.where.condition).__name__}")
            print("  Condition: <expression tree>")

        print("Full AST:")
        print(train)

    except Exception as e:
        print(f"\n[FAILED] Parse failed: {e}")
        import traceback
        traceback.print_exc()


def test_validate_syntax():
    """Test VALIDATE WITH statement"""
    print("Test 1: VALIDATE WITH statement")

    query = """
    VALIDATE WITH  (user.*, movie.title, rating.*)
    FROM Tables(user, movie, rating)
    WHERE user.loc = 'BJ' AND movie.year > 1990 AND rating.score > 3
    """

    try:
        parser = Parser(query)
        ast = parser.parse()

        print("[SUCCESS] Parsed successfully")
        print(f"Statement type / 语句类型: {ast.statement_type}")

        # Access VALIDATE statement
        validate = ast.validate

        print("USING clause:")
        print(f"  Selector count: {len(validate.with_clause.selectors)}")
        for i, selector in enumerate(validate.with_clause.selectors, 1):
            print(f"  {i}. {selector.table}.{selector.column} (is wildcard: {selector.is_wildcard})")

        print("FROM Tables:")
        print(f"  Tables: {', '.join(validate.tables.tables)}")
        print(f"  Count: {len(validate.tables.tables)}")

        if validate.where:
            print("\nWHERE clause:")
            print(f"  Type: {type(validate.where.condition).__name__}")
            print("  Condition: <expression tree / 表达式树>")

        print("Full AST:")
        print(validate)

    except Exception as e:
        print(f"\n[FAILED] Parse failed: {e}")
        import traceback
        traceback.print_exc()


def print_ast_tree(node, indent=0, prefix=""):
    """Recursively print AST tree structure"""
    indent_str = "  " * indent
    node_type = type(node).__name__

    if isinstance(node, PredictStatement):
        print(f"{indent_str}{prefix}PredictStatement")
        print(f"{indent_str}  ├─ value: ValueClause")
        print_ast_tree(node.value, indent + 2, "    ├─ ")
        print(f"{indent_str}  ├─ from_table: FromClause")
        print_ast_tree(node.from_table, indent + 2, "    ├─ ")
        if node.where:
            print(f"{indent_str}  └─ where: WhereClause")
            print_ast_tree(node.where, indent + 2, "      └─ ")
        else:
            print(f"{indent_str}  └─ where: None")

    elif isinstance(node, ValueClause):
        print(f"{indent_str}{prefix}ValueClause")
        print(f"{indent_str}    ├─ target: ColumnReference")
        print_ast_tree(node.target, indent + 3, "      ├─ ")
        print(f"{indent_str}    └─ predict_type: PredictType")
        print_ast_tree(node.predict_type, indent + 3, "        └─ ")

    elif isinstance(node, FromClause):
        print(f"{indent_str}{prefix}FromClause")
        print(f"{indent_str}      └─ table: '{node.table}'")

    elif isinstance(node, WhereClause):
        print(f"{indent_str}{prefix}WhereClause")
        print(f"{indent_str}        └─ condition:")
        print_ast_tree(node.condition, indent + 4, "          └─ ")

    elif isinstance(node, ColumnReference):
        if node.table:
            print(f"{indent_str}{prefix}ColumnReference(table='{node.table}', column='{node.column}')")
        else:
            print(f"{indent_str}{prefix}ColumnReference(column='{node.column}')")

    elif isinstance(node, PredictType):
        print(f"{indent_str}{prefix}PredictType(type_name='{node.type_name}')")

    elif isinstance(node, BinaryExpr):
        print(f"{indent_str}{prefix}BinaryExpr(operator='{node.operator}')")
        print_ast_tree(node.left, indent + 1, "  ├─ left: ")
        print_ast_tree(node.right, indent + 1, "  └─ right: ")

    elif isinstance(node, UnaryExpr):
        print(f"{indent_str}{prefix}UnaryExpr(operator='{node.operator}')")
        print_ast_tree(node.operand, indent + 1, "  └─ operand: ")

    elif isinstance(node, ColumnExpr):
        print(f"{indent_str}{prefix}ColumnExpr")
        print_ast_tree(node.column, indent + 1, "  └─ column: ")

    elif isinstance(node, LiteralExpr):
        value_str = f"'{node.value}'" if node.value_type == 'string' else str(node.value)
        print(f"{indent_str}{prefix}LiteralExpr(value={value_str}, value_type='{node.value_type}')")

    elif isinstance(node, BetweenExpr):
        print(f"{indent_str}{prefix}BetweenExpr")
        print_ast_tree(node.column, indent + 1, "  ├─ column: ")
        print_ast_tree(node.lower, indent + 1, "  ├─ lower: ")
        print_ast_tree(node.upper, indent + 1, "  └─ upper: ")

    elif isinstance(node, InExpr):
        print(f"{indent_str}{prefix}InExpr")
        print_ast_tree(node.column, indent + 1, "  ├─ column: ")
        print(f"{indent_str}    └─ values: [{len(node.values)} items]")
        for i, val in enumerate(node.values):
            is_last = (i == len(node.values) - 1)
            prefix_char = "  └─ " if is_last else "  ├─ "
            print_ast_tree(val, indent + 2, f"      {prefix_char}[{i}]: ")

    else:
        print(f"{indent_str}{prefix}{node_type}({node})")


def test_predict_syntax():
    """Test PREDICT VALUE statement with full AST tree"""
    print("\n\nTest 2: PREDICT VALUE statement")

    query = """
    PREDICT VALUE(user.age, CLF)
    FROM user
    WHERE user.loc = 'Florida'
    """

    try:
        parser = Parser(query)
        ast = parser.parse()

        print("[SUCCESS] Parsed successfully")
        print(f"Statement type / 语句类型: {ast.statement_type}")

        # Access PREDICT statement
        predict = ast.predict

        print("\n" + "=" * 60)
        print("Basic Information / 基本信息:")
        print("=" * 60)
        print("VALUE clause:")
        print(f"  Target: {predict.value.target}")
        print(f"  Type: {predict.value.predict_type.type_name}")
        print(f"  Is classifier: {predict.value.predict_type.is_classifier}")
        print(f"  Is regressor: {predict.value.predict_type.is_regressor}")

        print("\nFROM clause:")
        print(f"  Table: {predict.from_table.table}")

        if predict.where:
            print("\nWHERE clause:")
            print(f"  Type: {type(predict.where.condition).__name__}")

        print("\n" + "=" * 60)
        print("Complete AST Tree Structure / 完整语法树结构:")
        print("=" * 60)
        print_ast_tree(predict)

        print("\n" + "=" * 60)
        print("AST String Representation / AST字符串表示:")
        print("=" * 60)
        print(predict)

    except Exception as e:
        print(f"\n[FAILED] Parse failed: {e}")
        import traceback
        traceback.print_exc()


def test_predict_complex_nested():
    """Test PREDICT with complex nested WHERE conditions"""
    print("\n\nTest 3: PREDICT with Complex Nested WHERE")

    query = """
    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender = 'M'

    """

    try:
        parser = Parser(query)
        ast = parser.parse()

        print("[SUCCESS] Parsed successfully")
        print(f"Statement type: {ast.statement_type}")

        predict = ast.predict

        print("\n" + "=" * 60)
        print("Complete AST Tree Structure:")
        print("=" * 60)
        print_ast_tree(predict)

    except Exception as e:
        print(f"\n[FAILED] Parse failed: {e}")
        import traceback
        traceback.print_exc()


def test_predict_regression():
    """Test PREDICT VALUE regression statement"""
    print("\n\nTest 4: PREDICT VALUE regression")

    query = """
    PREDICT VALUE(users.Age, REG)
    FROM users
    WHERE users.Gender = 'M'
    """

    try:
        parser = Parser(query)
        ast = parser.parse()

        print("\n[SUCCESS] Parsed successfully")
        print(f"Statement type: {ast.statement_type}")

        predict = ast.predict
        print(f"Target: {predict.value.target}")
        print(f"Type: {predict.value.predict_type.type_name}")
        print(f"Table: {predict.from_table.table}")

        print("\n" + "=" * 60)
        print("Complete AST Tree Structure:")
        print("=" * 60)
        print_ast_tree(predict)

    except Exception as e:
        print(f"\n[FAILED] Parse failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Uncomment to run additional tests:
    # test_train_syntax()
    # test_validate_syntax()
    # test_predict_regression()
    test_predict_syntax()
    test_predict_complex_nested()
