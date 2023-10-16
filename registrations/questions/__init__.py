from .helpers import RegistrationQuestionMixin, PlaceholderQuestion
from .involved_questions import NewInvolvedQuestion, PurposeQuestion, \
    SensitiveDetailsQuestion, SpecialDetailsQuestion, RegularDetailsQuestion, \
    InvolvedPeopleQuestion
from .misc_questions import NewRegistrationQuestion, FacultyQuestion, \
    TraversalQuestion, GoalQuestion, CategoryQuestion, SoftwareQuestion, \
    NewSoftwareQuestion, RetentionQuestion, ReceiverQuestion, \
    NewReceiverQuestion, SecurityQuestion
from .attachment_questions import AttachmentsQuestion, NewAttachmentQuestion

Q_LIST = [
    NewRegistrationQuestion,
    FacultyQuestion,
    CategoryQuestion,
    TraversalQuestion,
    InvolvedPeopleQuestion,
    RetentionQuestion,
    NewInvolvedQuestion,
    GoalQuestion,
    PurposeQuestion,
    NewSoftwareQuestion,
    SoftwareQuestion,
    ReceiverQuestion,
    NewReceiverQuestion,
    AttachmentsQuestion,
    SecurityQuestion,
]

QUESTIONS = {q.slug: q for q in Q_LIST}

