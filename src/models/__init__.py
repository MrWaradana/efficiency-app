from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .case_inputs import Case_inputs
from .case_ouputs import Case_outputs
from .cases import Cases
from .excels import Excels
from .units import Units
from .variables import Variables

