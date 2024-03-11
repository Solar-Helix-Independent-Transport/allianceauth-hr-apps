from django.contrib.auth.models import User
from django.db import models
from sortedm2m.fields import SortedManyToManyField

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

from .managers import ApplicationManager, ApplicationFormManager


class ApplicationQuestion(models.Model):
    title = models.CharField(max_length=254, verbose_name='Question')
    help_text = models.CharField(max_length=254, blank=True, null=True)
    multi_select = models.BooleanField(default=False)

    def __str__(self):
        return "Question: " + self.title


class ApplicationChoice(models.Model):
    question = models.ForeignKey(
        ApplicationQuestion, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=200, verbose_name='Choice')

    def __str__(self):
        return self.choice_text


class ApplicationForm(models.Model):
    questions = SortedManyToManyField(ApplicationQuestion)
    corp = models.OneToOneField(EveCorporationInfo, on_delete=models.CASCADE, related_name='hr_app')

    objects = ApplicationFormManager()

    def __str__(self):
        return str(self.corp)


class Application(models.Model):
    form = models.ForeignKey(
        ApplicationForm, on_delete=models.CASCADE, related_name='application')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='hrapp')
    approved = models.BooleanField(blank=True, null=True, default=None)
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name='hr_reviews')
    reviewer_character = models.ForeignKey(
        EveCharacter, on_delete=models.SET_NULL, blank=True, null=True, related_name='hr_reviews')
    created = models.DateTimeField(auto_now_add=True)

    objects = ApplicationManager()

    def __str__(self):
        return str(self.user) + " Application To " + str(self.form)

    class Meta:
        permissions = (
            ('approve_application', 'Can approve visible applications'),
            ('reject_application', 'Can reject visible applications'),
            ('create_new_application', 'Can view and send applications'),
            ('view_all_applications', 'Can view all applications'),
            ('view_corp_applications',
             'Can view apps to any corporation your a member of'),
            ('view_alt_corp_applications',
             'Can view apps to main characters corporation'),
        )
        # unique_together = ('form', 'user')

    @property
    def main_character(self):
        return self.user.profile.main_character

    @property
    def characters(self):
        return [o.character for o in self.user.character_ownerships.all()]

    @property
    def reviewer_str(self):
        if self.reviewer_character:
            return str(self.reviewer_character)
        elif self.reviewer:
            return "User " + str(self.reviewer)
        else:
            return None


class ApplicationResponse(models.Model):
    question = models.ForeignKey(ApplicationQuestion, on_delete=models.CASCADE)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()

    def __str__(self):
        return str(self.application) + " Answer To " + str(self.question)

    class Meta:
        unique_together = ('question', 'application')


class ApplicationComment(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hr_comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + " comment on " + str(self.application)
