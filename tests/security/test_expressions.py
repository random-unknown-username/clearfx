import pytest
from clearfx.formats.expressions import parse_expression, evaluate_expression, validate_expression, VarRef, NumberLit, BinOp, Error

def test_parse_expression():
    assert isinstance(parse_expression("1.0"), NumberLit)
    assert parse_expression("1.0").value == 1.0
    
    assert isinstance(parse_expression("t"), VarRef)
    assert parse_expression("t").name == "t"

def test_evaluate_expression():
    # Evaluate a basic binary operation
    node = BinOp('+', NumberLit(1.0), VarRef('t'))
    assert evaluate_expression(node, {'t': 2.0}) == 3.0

def test_security_validate_expression():
    # Only allowed vars should pass
    node_valid = VarRef("t")
    errors = validate_expression(node_valid)
    assert len(errors) == 0

    # Disallowed variable should be caught
    node_invalid = VarRef("__class__")
    errors = validate_expression(node_invalid)
    assert len(errors) == 1
    assert "Disallowed variable: __class__" in errors[0].msg
