# Rule Engine Application

## Overview

This is a simple 3-tier rule engine application that determines user eligibility based on attributes like age, department, income, spend, etc. The system uses an Abstract Syntax Tree (AST) to represent conditional rules and allows for dynamic creation, combination, and modification of these rules.

## Features

- Create rules using a string representation.
- Combine multiple rules into a single AST.
- Evaluate rules against provided data.
- Display created rules.
- Evaluate rules using either rule ID or AST and data.

## Data Structure

The AST is represented using a `Node` data structure with the following fields:
- `type`: String indicating the node type ("operator" for AND/OR, "operand" for conditions).
- `left`: Reference to another Node (left child).
- `right`: Reference to another Node (right child for operators).
- `value`: Optional value for operand nodes (e.g., number for comparisons).

## Data Storage

The rules and application metadata are stored in a SQLite database. The schema includes a `Rule` table with the following fields:
- `id`: Integer, primary key.
- `rule_string`: String, the original rule string.
- `ast_json`: JSON, the AST representation of the rule.

## Sample Rules

- `rule1 = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"`
- `rule2 = "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)"`

## API Endpoints

### Create Rule

- **Endpoint**: `/create_rule`
- **Method**: `POST`
- **Request Body**: `{ "rule_string": "<rule_string>" }`
- **Response**: `{ "message": "Rule created", "rule_id": <rule_id> }`

### Combine Rules

- **Endpoint**: `/combine_rules`
- **Method**: `POST`
- **Request Body**: `{ "rule_ids": [<rule_id1>, <rule_id2>, ...] }`
- **Response**: `{ "combined_ast": <combined_ast> }`

### Evaluate Rule

- **Endpoint**: `/evaluate_rule`
- **Method**: `POST`
- **Request Body**: `{ "rule_id": <rule_id>, "ast": <ast>, "data": <data> }`
- **Response**: `{ "result": <result> }`

### Get Rules

- **Endpoint**: `/get_rules`
- **Method**: `GET`
- **Response**: `{ "rules": [ { "id": <rule_id>, "rule_string": "<rule_string>" }, ... ] }`

## Setup

### Prerequisites

- Python 3.x
- Flask
- Flask-SQLAlchemy

### Installation

1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd rule_engine

2. Install the required packages:

    ```
    pip install -r requirements.txt

3. Run the application
    ```
     python app.py
4. Open your browser and navigate to 
    ```
    http://127.0.0.1:5000

## Useage
### Creating a Rule
1. Enter a rule string in the "Create Rule" form.
2. Click "Create Rule".
3. The rule will be created and displayed in the "Created Rules" section.
### Combing the Rules
1. Enter rule IDs (comma-separated) in the "Combine Rules" form.
2. Click "Combine Rules".
3. The combined AST will be displayed in the result section.
### Evaluating a Rule
1. Enter a rule ID or AST and data in the "Evaluate Rule" form.
2. Click "Evaluate Rule".
3. The evaluation result will be displayed in the result section.
