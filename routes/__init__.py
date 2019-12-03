from flask import Blueprint

routes = Blueprint('routes', __name__)

from .data import *
from .login import *
