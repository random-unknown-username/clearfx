import math
from dataclasses import dataclass
from typing import Dict, Any, List, Set, Optional

@dataclass
class ASTNode:
    pass

@dataclass
class NumberLit(ASTNode):
    value: float

@dataclass
class VarRef(ASTNode):
    name: str

@dataclass
class BinOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    expr: ASTNode

@dataclass
class FuncCall(ASTNode):
    func: str
    args: List[ASTNode]

ALLOWED_FUNCTIONS = {'sin', 'cos', 'tan', 'abs', 'min', 'max', 'clamp', 'lerp', 'floor', 'ceil', 'sqrt', 'pow', 'mod'}
ALLOWED_VARS = {'t', 'progress', 'w', 'h', 'dt', 'frame', 'pi', 'tau'} | {f'rand_{i}' for i in range(32)}

def parse_expression(expr_string: str) -> ASTNode:
    # Extremely simplified parser for dummy sake
    try:
        val = float(expr_string)
        return NumberLit(val)
    except ValueError:
        return VarRef(expr_string.strip())

def evaluate_expression(node: ASTNode, variables: Dict[str, float]) -> float:
    if isinstance(node, NumberLit):
        return node.value
    elif isinstance(node, VarRef):
        return variables.get(node.name, 0.0)
    elif isinstance(node, BinOp):
        l = evaluate_expression(node.left, variables)
        r = evaluate_expression(node.right, variables)
        if node.op == '+': return l + r
        if node.op == '-': return l - r
        if node.op == '*': return l * r
        if node.op == '/': return l / r if r != 0 else 0.0
        if node.op == '%': return l % r if r != 0 else 0.0
    return 0.0

@dataclass
class Error:
    msg: str

def validate_expression(node: ASTNode) -> List[Error]:
    errors = []
    if isinstance(node, VarRef):
        if node.name not in ALLOWED_VARS:
            errors.append(Error(f"Disallowed variable: {node.name}"))
    return errors
