from uil.questions.blueprints import Blueprint

from .models import Registration
from .forms import NewRegistrationQuestion



class RegistrationBlueprint(Blueprint):

    model = Registration
    primary_questions = [NewRegistrationQuestion,
    ]
