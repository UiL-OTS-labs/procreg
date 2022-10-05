from cdh.questions.blueprints import BaseConsumer, BaseQuestionConsumer

from .forms import NewRegistrationQuestion, FacultyQuestion, UsesInformationQuestion


class RegistrationConsumer(BaseQuestionConsumer):

    def get_question_data(self):
        question_data = super().get_question_data()
        question_data["registration"] = self.blueprint.object
        return question_data


class TopQuestionsConsumer(BaseConsumer):

    def consume(self):
        "If both top questions are filled out, append the next consumer"
        required = [NewRegistrationQuestion, FacultyQuestion]
        for q in required:
            if q.slug in self.blueprint.errors.keys():
                if self.blueprint.errors[q.slug] != {}:
                    return []
        return [UsesInformationConsumer]


class NewRegistrationConsumer(RegistrationConsumer):

    question_class = NewRegistrationQuestion

    def consume(self):
        self.blueprint.top_questions.append(
            self.question,
        )
        self.get_errors()
        # TopQuestionsConsumer checks for our errors, so we can just return
        return []

    def get_errors(self):
        self.errors = self.get_django_errors()
        for f in self.empty_fields:
            self.errors.append(f"Field {f} is empty")
        self.blueprint.errors[self.question.slug] = self.errors


class FacultyConsumer(RegistrationConsumer):

    question_class = FacultyQuestion

    def consume(self):
        self.blueprint.top_questions.append(
            self.question,
        )
        self.get_errors()
        # TopQuestionsConsumer checks for our errors, so we can just return
        return []

    def get_errors(self):
        self.errors = self.get_django_errors()
        for f in self.empty_fields:
            self.errors.append(f"Field {f} is empty")
        self.blueprint.errors[self.question.slug] = self.errors


class UsesInformationConsumer(RegistrationConsumer):

    question_class = UsesInformationQuestion

    def consume(self):
        return []
