# app.py
from flask import Flask, request, jsonify
from dataclasses import dataclass
from typing import Optional, Dict, List, Union
import re
from enum import Enum
import sqlite3
import json

app = Flask(__name__)

class NodeType(Enum):
    OPERATOR = "operator"
    OPERAND = "operand"

class Operator(Enum):
    AND = "AND"
    OR = "OR"
    GT = ">"
    LT = "<"
    EQ = "="
    GTE = ">="
    LTE = "<="

@dataclass
class Node:
    type: NodeType
    value: Optional[str] = None
    left: Optional['Node'] = None
    right: Optional['Node'] = None
    attribute: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'type': self.type.value,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None,
            'attribute': self.attribute
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        node = cls(
            type=NodeType(data['type']),
            value=data['value'],
            attribute=data['attribute']
        )
        if data['left']:
            node.left = cls.from_dict(data['left'])
        if data['right']:
            node.right = cls.from_dict(data['right'])
        return node

def setup_database():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rules
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT UNIQUE,
         ast_json TEXT,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def tokenize_rule(rule_string: str) -> List[str]:
    # Split by operators while preserving them
    pattern = r'(\(|\)|\bAND\b|\bOR\b|>=|<=|>|<|=)'
    tokens = [token.strip() for token in re.split(pattern, rule_string) if token.strip()]
    return tokens

def parse_condition(tokens: List[str], index: int) -> tuple[Node, int]:
    attribute = tokens[index].strip()
    operator = tokens[index + 1].strip()
    value = tokens[index + 2].strip().strip("'")
    
    node = Node(
        type=NodeType.OPERAND,
        value=operator,
        attribute=attribute
    )
    node.right = Node(type=NodeType.OPERAND, value=value)
    
    return node, index + 3

def parse_expression(tokens: List[str], index: int = 0) -> tuple[Node, int]:
    if tokens[index] == '(':
        left_node, new_index = parse_expression(tokens, index + 1)
        if new_index >= len(tokens):
            raise ValueError("Unexpected end of expression")
            
        if tokens[new_index] in ('AND', 'OR'):
            operator = tokens[new_index]
            right_node, final_index = parse_expression(tokens, new_index + 1)
            
            node = Node(
                type=NodeType.OPERATOR,
                value=operator,
                left=left_node,
                right=right_node
            )
            
            if final_index < len(tokens) and tokens[final_index] == ')':
                return node, final_index + 1
        elif tokens[new_index] == ')':
            return left_node, new_index + 1
            
    else:
        return parse_condition(tokens, index)
        
    raise ValueError("Invalid expression")

@app.route('/api/rules', methods=['POST'])
def create_rule():
    data = request.get_json()
    rule_string = data.get('rule')
    rule_name = data.get('name')
    
    if not rule_string or not rule_name:
        return jsonify({'error': 'Missing rule or name'}), 400
        
    try:
        tokens = tokenize_rule(rule_string)
        ast_root, _ = parse_expression(tokens)
        
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        c.execute('INSERT INTO rules (name, ast_json) VALUES (?, ?)',
                 (rule_name, json.dumps(ast_root.to_dict())))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Rule created successfully', 'ast': ast_root.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/rules/evaluate', methods=['POST'])
def evaluate_rule():
    data = request.get_json()
    rule_name = data.get('rule_name')
    user_data = data.get('data')
    
    if not rule_name or not user_data:
        return jsonify({'error': 'Missing rule_name or data'}), 400
        
    try:
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        c.execute('SELECT ast_json FROM rules WHERE name = ?', (rule_name,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Rule not found'}), 404
            
        ast_dict = json.loads(result[0])
        ast_root = Node.from_dict(ast_dict)
        
        evaluation_result = evaluate_ast(ast_root, user_data)
        return jsonify({'result': evaluation_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def evaluate_ast(node: Node, data: Dict) -> bool:
    if node.type == NodeType.OPERATOR:
        left_result = evaluate_ast(node.left, data)
        right_result = evaluate_ast(node.right, data)
        
        if node.value == 'AND':
            return left_result and right_result
        elif node.value == 'OR':
            return left_result or right_result
    else:
        attribute_value = data.get(node.attribute)
        if attribute_value is None:
            raise ValueError(f"Missing attribute: {node.attribute}")
            
        comparison_value = node.right.value
        try:
            if node.attribute in ('age', 'salary', 'experience'):
                comparison_value = float(comparison_value)
                attribute_value = float(attribute_value)
        except ValueError:
            pass
            
        if node.value == '>':
            return attribute_value > comparison_value
        elif node.value == '<':
            return attribute_value < comparison_value
        elif node.value == '=':
            return attribute_value == comparison_value
        elif node.value == '>=':
            return attribute_value >= comparison_value
        elif node.value == '<=':
            return attribute_value <= comparison_value
            
    return False

@app.route('/api/rules/combine', methods=['POST'])
def combine_rules():
    data = request.get_json()
    rule_names = data.get('rules', [])
    
    if not rule_names:
        return jsonify({'error': 'No rules provided'}), 400
        
    try:
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        
        asts = []
        for name in rule_names:
            c.execute('SELECT ast_json FROM rules WHERE name = ?', (name,))
            result = c.fetchone()
            if result:
                asts.append(Node.from_dict(json.loads(result[0])))
        
        conn.close()
        
        if not asts:
            return jsonify({'error': 'No valid rules found'}), 404
            
        # Combine rules with OR operator
        combined_ast = asts[0]
        for ast in asts[1:]:
            combined_ast = Node(
                type=NodeType.OPERATOR,
                value='OR',
                left=combined_ast,
                right=ast
            )
            
        return jsonify({'combined_ast': combined_ast.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
