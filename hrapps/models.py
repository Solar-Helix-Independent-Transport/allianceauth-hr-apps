from typing import override

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from sortedm2m.fields import SortedManyToManyField

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from .managers import ApplicationManager, ApplicationFormManager


class ApplicationQuestion(models.Model):
    title = models.CharField(max_length=254, verbose_name='Question')
    help_text = models.CharField(max_length=254, blank=True, null=True)
    multi_select = models.BooleanField(default=False)

    @override
    def __str__(self) -> str:
        return f"Question: {self.title}"


class ApplicationChoice(models.Model):
    question = models.ForeignKey(
        ApplicationQuestion, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=200, verbose_name='Choice')

    @override
    def __str__(self) -> str:
        return str(self.choice_text)


class FilterDataSource(models.Model):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        editable=False
    )
    object_id = models.PositiveIntegerField(
        editable=False
    )
    filter_object = GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id"
    )

    def __str__(self):
        try:
            return f"{self.filter_object.name}: {self.filter_object.description}"
        except:
            return f"Error: {self.content_type.app_label}:{self.content_type} {self.object_id}"

    class Meta:
        default_permissions = []


class ApplicationForm(models.Model):
    questions = SortedManyToManyField(ApplicationQuestion)
    corp = models.OneToOneField(EveCorporationInfo, on_delete=models.CASCADE, related_name='hr_app')

    objects = ApplicationFormManager()

    filters = models.ManyToManyField(FilterDataSource)

    @override
    def __str__(self) -> str:
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

    @override
    def __str__(self) -> str:
        return f"{self.user} Application To {self.form}"

    class Meta:
        permissions = (
            ('approve_application', 'Can approve visible applications'),
            ('reject_application', 'Can reject visible applications'),
            ('create_new_application', 'Can view and send applications'),
            ('view_all_applications', 'Can view all applications'),
            ('view_corp_applications', 'Can view apps to main characters corporation'),
            ('view_alt_corp_applications', 'Can view apps to any corporation your a member of'),
        )
        # unique_together = ('form', 'user')

    @property
    def main_character(self) -> str:
        return self.user.profile.main_character

    @property
    def characters(self) -> list[EveCharacter]:
        return [o.character for o in self.user.character_ownerships.all()]

    @property
    def reviewer_str(self) -> str | None:
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

    def __str__(self) -> str:
        return f"{self.application} Answer To {self.question}"

    class Meta:
        unique_together = ('question', 'application')


class ApplicationComment(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hr_comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    @override
    def __str__(self) -> str:
        return f"{self.user} comment on {self.application}"

