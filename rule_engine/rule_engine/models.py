from database import db

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_string = db.Column(db.String, nullable=False)
    ast_json = db.Column(db.JSON, nullable=False)