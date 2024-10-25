from flask import Flask, render_template, request, jsonify
from database import init_db, db
from models import Rule
from astr import parse_rule, combine_asts, evaluate_ast, Node

app = Flask(__name__)
app.config.from_object('config.Config')

# Pass the app instance to init_db
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule():
    rule_string = request.json.get('rule_string')
    ast = parse_rule(rule_string)
    rule = Rule(rule_string=rule_string, ast_json=ast.to_dict())
    db.session.add(rule)
    db.session.commit()
    return jsonify({"message": "Rule created", "rule_id": rule.id})

@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    rule_ids = request.json.get('rule_ids')
    rules = Rule.query.filter(Rule.id.in_(rule_ids)).all()
    ast_list = [Node.from_dict(rule.ast_json) for rule in rules]
    combined_ast = combine_asts(ast_list)
    return jsonify({"combined_ast": combined_ast.to_dict()})

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    rule_id = request.json.get('rule_id')
    ast_data = request.json.get('ast')
    data = request.json.get('data')

    if rule_id:
        rule = Rule.query.get(rule_id)
        if not rule:
            return jsonify({"error": "Rule not found"}), 404
        ast = Node.from_dict(rule.ast_json)
    elif ast_data:
        ast = Node.from_dict(ast_data)
    else:
        return jsonify({"error": "Either rule_id or ast must be provided"}), 400

    result = evaluate_ast(ast, data)
    return jsonify({"result": result})

@app.route('/get_rules', methods=['GET'])
def get_rules():
    rules = Rule.query.all()
    rules_list = [{"id": rule.id, "rule_string": rule.rule_string} for rule in rules]
    return jsonify({"rules": rules_list})

@app.route('/delete_rule', methods=['DELETE'])
def delete_rule():
    rule_id = request.json.get('rule_id')
    rule = Rule.query.get(rule_id)
    if not rule:
        return jsonify({"error": "Rule not found"}), 404
    db.session.delete(rule)
    db.session.commit()
    return jsonify({"message": "Rule deleted"})

if __name__ == '__main__':
    app.run(debug=True)