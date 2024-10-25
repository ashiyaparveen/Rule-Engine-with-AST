class Node:
    def __init__(self, type, left=None, right=None, value=None):
        self.type = type
        self.left = left
        self.right = right
        self.value = value

    def to_dict(self):
        return {
            'type': self.type,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None,
            'value': self.value
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            return None
        node = Node(
            type=data['type'],
            left=Node.from_dict(data['left']),
            right=Node.from_dict(data['right']),
            value=data['value']
        )
        return node

def parse_rule(rule_string):
    import ast
    import operator as op

    # Supported operators
    operators = {
        ast.And: 'AND',
        ast.Or: 'OR',
        ast.Eq: '==',
        ast.NotEq: '!=',
        ast.Lt: '<',
        ast.LtE: '<=',
        ast.Gt: '>',
        ast.GtE: '>='
    }

    def _parse(node):
        if isinstance(node, ast.BoolOp):
            left = _parse(node.values[0])
            for value in node.values[1:]:
                right = _parse(value)
                left = Node(type=operators[type(node.op)], left=left, right=right)
            return left
        elif isinstance(node, ast.Compare):
            left = _parse(node.left)
            right = _parse(node.comparators[0])
            return Node(type=operators[type(node.ops[0])], left=left, right=right)
        elif isinstance(node, ast.Name):
            return Node(type='operand', value=node.id)
        elif isinstance(node, ast.Constant):
            return Node(type='operand', value=node.value)
        else:
            raise ValueError(f"Unsupported AST node type: {type(node)}")

    # Replace logical operators with Python equivalents
    rule_string = rule_string.replace('AND', 'and').replace('OR', 'or').replace('=', '==')
    
    tree = ast.parse(rule_string, mode='eval')
    return _parse(tree.body)

def combine_asts(ast_list):
    if not ast_list:
        return None

    combined_ast = ast_list[0]
    for ast in ast_list[1:]:
        combined_ast = Node(type='AND', left=combined_ast, right=ast)
    return combined_ast

def evaluate_ast(ast, data):
    def _evaluate(node):
        if node.type == 'AND':
            return _evaluate(node.left) and _evaluate(node.right)
        elif node.type == 'OR':
            return _evaluate(node.left) or _evaluate(node.right)
        elif node.type == '==':
            return _evaluate(node.left) == _evaluate(node.right)
        elif node.type == '!=':
            return _evaluate(node.left) != _evaluate(node.right)
        elif node.type == '<':
            return _evaluate(node.left) < _evaluate(node.right)
        elif node.type == '<=':
            return _evaluate(node.left) <= _evaluate(node.right)
        elif node.type == '>':
            return _evaluate(node.left) > _evaluate(node.right)
        elif node.type == '>=':
            return _evaluate(node.left) >= _evaluate(node.right)
        elif node.type == 'operand':
            return data.get(node.value, node.value)
        else:
            raise ValueError(f"Unsupported node type: {node.type}")

    return _evaluate(ast)