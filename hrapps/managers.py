from django.contrib.auth.models import User
from django.db import models
from typing import Optional


class ApplicationFormQuerySet(models.QuerySet):
    def visible_to(self, user: User):
        if user.is_superuser:
            # return all for SU
            return self

        if user.has_perm("hrapps.view_all_applications"):
            # return all for global perm
            return self
        
        return self.none()

        # queries = []
        # if user.has_perm("hrapps.view_corp_applications"):
        #     queries.append(
        #         models.Q(
        #             form__corp__corporation_id=user.profile.main_character.corporation_id
        #             )
        #     )


class ApplicationFormManager(models.Manager):
    def get_queryset(self):
        return ApplicationFormQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)


class ApplicationQuerySet(models.QuerySet):
    def visible_to(self, user: User):
        if user.is_superuser:
            # return all for SU
            return self

        if user.has_perm("hrapps.view_all_applications"):
            # return all for global perm
            return self
        
        return self.filter(
            user=user
        )

        # queries = []
        # if user.has_perm("hrapps.view_corp_applications"):
        #     queries.append(
        #         models.Q(
        #             form__corp__corporation_id=user.profile.main_character.corporation_id
        #             )
        #     )


class ApplicationManager(models.Manager):
    def get_queryset(self):
        return ApplicationQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def pending_requests_count_for_user(self, user: User) -> Optional[int]:
        """Returns the number of pending group requests for the given user"""
        if user.is_superuser:
            return self.filter(approved__isnull=True).count()
        elif user.has_perm("auth.human_resources"):
            if user.profile.main_character:
                return (
                    self
                    .select_related("form__corp")
                    .get_visible(user)
                    .filter(approved__isnull=True)
                    .count()
                )
            else:
                return None
        else:
            return None
