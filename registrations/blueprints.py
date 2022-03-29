from django.urls import reverse

from uil.questions.blueprints import Blueprint

from .models import Registration
from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS



class RegistrationBlueprint():

    model = Registration
    primary_questions = [NewRegistrationQuestion,
    ]

    def __init__(self, registration):

        self.required = []

        self.consumers = [BasicDetailsConsumer]
        self.registration = registration
        self.desired_next = None

        self.evaluate()

    def evaluate(self, consumers=None):
        """Go through the list of consumers and try to satisfy their needs"""

        # First run, get all consumers
        if consumers == None:
            consumers = self.consumers

        # We've run out of consumers
        if consumers == []:
            return True

        current = consumers[0]()

        next_consumers = current.consume(self) + consumers[1:]

        return self.evaluate(consumers=next_consumers)

    def get_desired_next_url(self):
        if self.desired_next in QUESTIONS.values():
            if self.desired_next.model == Registration:
                question = self.desired_next(instance=self.registration)
                print(question.instance)
                return question.get_edit_url()
        return reverse(
            "registrations:overview",
            kwargs={
                "reg_pk": self.registration.pk,
            })



class BasicDetailsConsumer:

    def consume(self, blueprint):

        if self.check_details(blueprint.registration):
            blueprint.desired_next = TraversalQuestion

        return []

    def check_details(self, registration):

        for field in [registration.title,
                      registration.faculty,
                      ]:
            if field in ['', None]:
                print(field, 'was not filled in')
                return False

        return True
