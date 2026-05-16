from ninja.errors import HttpError
from ninja.router import Router

from runs.schemas import CreateRunSchema, RunSchema, RunStartedSchema, WorldConfigSchema
from runs.services import RunService
from users.auth import BearerAuth

router = Router(tags=["runs"])


@router.post("/", response=RunSchema, auth=BearerAuth())
def create_run(request, payload: CreateRunSchema):
    return RunService().create_run(request.auth, payload.template_config)


@router.get("/{invite_code}", response=RunSchema, auth=BearerAuth())
def get_run(request, invite_code: str):
    return RunService().get_run(invite_code)


@router.post("/{invite_code}/start/", response=RunStartedSchema, auth=BearerAuth())
def start_run(request, invite_code: str):
    try:
        return RunService().start_run(request.auth, invite_code)
    except ValueError as e:
        raise HttpError(403, str(e))


@router.get("/{invite_code}/export/", response=WorldConfigSchema, auth=BearerAuth())
def export_run(request, invite_code: str):
    return RunService().export_run(invite_code)
