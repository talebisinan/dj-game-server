from dataclasses import dataclass

from django.shortcuts import get_object_or_404

from runs.models import Run
from runs.schemas import WorldConfigSchema
from users.models import User


@dataclass
class RunService:
    def create_run(self, owner: User, config: WorldConfigSchema) -> Run:
        config_dict = config.dict()
        return Run.objects.create(
            owner=owner, template_config=config_dict, current_config=config_dict
        )

    def get_run(self, invite_code: str) -> Run:
        return get_object_or_404(Run, invite_code=invite_code)

    def start_run(self, user: User, invite_code: str) -> Run:
        run = self.get_run(invite_code)
        if run.owner != user:
            raise ValueError("Only the owner can start the run")

        if not run.is_started:
            run.is_started = True
            run.save()
        return run

    def export_run(self, invite_code: str) -> dict:
        return self.get_run(invite_code).current_config
