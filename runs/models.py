import shortuuid
from django.db import models

from users.models import User


def gen_invite_code():
    return shortuuid.ShortUUID().random(length=6).upper()


class Run(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    invite_code = models.CharField(max_length=6, unique=True, default=gen_invite_code)
    is_started = models.BooleanField(default=False)
    template_config = models.JSONField()
    current_config = models.JSONField()
    pending_players = models.JSONField(default=list)
    pending_claims = models.JSONField(default=list)
    participants = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "runs"
