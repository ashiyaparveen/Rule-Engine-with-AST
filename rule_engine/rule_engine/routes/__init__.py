from flask import Blueprint

rule_bp = Blueprint('rule_bp', __name__)

from . import rule_routes