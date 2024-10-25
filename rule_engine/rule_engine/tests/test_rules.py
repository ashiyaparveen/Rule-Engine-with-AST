import unittest
from app import app, db
from models import Rule

class RuleEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_rule(self):
        response = self.app.post('/create_rule', json={"rule_string": "age > 30"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('rule_id', data)

    def test_combine_rules(self):
        # Create two rules
        response1 = self.app.post('/create_rule', json={"rule_string": "age > 30"})
        self.assertEqual(response1.status_code, 200)
        rule_id1 = response1.get_json()['rule_id']

        response2 = self.app.post('/create_rule', json={"rule_string": "salary > 50000"})
        self.assertEqual(response2.status_code, 200)
        rule_id2 = response2.get_json()['rule_id']

        # Combine the two rules
        response = self.app.post('/combine_rules', json={"rule_ids": [rule_id1, rule_id2]})
        self.assertEqual(response.status_code, 200)
        combined_ast = response.get_json()['combined_ast']
        self.assertIsNotNone(combined_ast)

    def test_evaluate_rule(self):
        # Create a rule
        response = self.app.post('/create_rule', json={"rule_string": "age > 30"})
        self.assertEqual(response.status_code, 200)
        rule_id = response.get_json()['rule_id']

        # Get the rule from the database
        rule = Rule.query.get(rule_id)
        ast = rule.ast_json

        # Evaluate the rule
        response = self.app.post('/evaluate_rule', json={"ast": ast, "data": {"age": 35}})
        self.assertEqual(response.status_code, 200)
        result = response.get_json()['result']
        self.assertTrue(result)

        # Evaluate the rule with different data
        response = self.app.post('/evaluate_rule', json={"ast": ast, "data": {"age": 25}})
        self.assertEqual(response.status_code, 200)
        result = response.get_json()['result']
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()