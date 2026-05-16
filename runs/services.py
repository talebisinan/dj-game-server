from dataclasses import dataclass

from django.shortcuts import get_object_or_404

from runs.models import Run
from runs.schemas import WorldConfigSchema
from users.models import User


@dataclass
class RunService:
    def create(self, owner: User, config: WorldConfigSchema) -> Run:
        config_dict = config.dict()
        return Run.objects.create(
            owner=owner, template_config=config_dict, current_config=config_dict
        )

    def get(self, invite_code: str) -> Run:
        return get_object_or_404(Run, invite_code=invite_code)

    def start(self, user: User, invite_code: str) -> Run:
        run = self.get(invite_code)
        if run.owner != user:
            raise ValueError("Only the owner can start the run")

        if not run.is_started:
            run.is_started = True
            run.save()
        return run

    def export(self, invite_code: str) -> dict:
        return self.get(invite_code).current_config

    def join(self, user: User, invite_code: str) -> Run:
        run = self.get(invite_code)
        user_id = str(user.id)

        if any(p["user_id"] == user_id for p in run.pending_players):
            raise ValueError("Already waiting for host approval")

        if any(p["user_id"] == user_id for p in run.participants):
            raise ValueError("Already in this run")

        run.pending_players.append({"user_id": user_id, "nickname": user.nickname})
        run.save()
        return run

    def accept_player(self, owner: User, invite_code: str, player_id: str) -> Run:
        run = self.get(invite_code)
        if run.owner != owner:
            raise ValueError("Only the owner can accept players")
        pending = next(
            (p for p in run.pending_players if p["user_id"] == player_id), None
        )
        if not pending:
            raise ValueError("Player is not pending")
        run.pending_players = [
            p for p in run.pending_players if p["user_id"] != player_id
        ]
        run.participants.append(pending)
        run.save()
        return run

    def reject_player(self, owner: User, invite_code: str, player_id: str) -> Run:
        run = self.get(invite_code)
        if run.owner != owner:
            raise ValueError("Only the owner can reject players")
        if not any(p["user_id"] == player_id for p in run.pending_players):
            raise ValueError("Player is not pending")
        run.pending_players = [
            p for p in run.pending_players if p["user_id"] != player_id
        ]
        run.save()
        return run

    def claim(self, user: User, invite_code: str, character_id: str) -> Run:
        run = self.get(invite_code)
        user_id = str(user.id)

        # verify player is a participant
        if not any(p["user_id"] == user_id for p in run.participants):
            raise ValueError("You are not a participant in this run")

        # verify character exists in current_config
        config = WorldConfigSchema(**run.current_config)
        if not any(c.id == character_id for c in config.characters):
            raise ValueError("Character does not exist")

        # verify no pending claim for this character already
        if any(c["character_id"] == character_id for c in run.pending_claims):
            raise ValueError("Character already has a pending claim")

        # add to pending claims
        run.pending_claims.append(
            {
                "user_id": user_id,
                "nickname": user.nickname,
                "character_id": character_id,
            }
        )
        run.save()
        return run

    def approve_claim(self, owner: User, invite_code: str, character_id: str) -> Run:
        run = self.get(invite_code)

        # verify requester is owner
        if run.owner != owner:
            raise ValueError("Only the owner can approve claims")

        # find the pending claim
        claim = next(
            (c for c in run.pending_claims if c["character_id"] == character_id), None
        )
        if not claim:
            raise ValueError("No pending claim for this character")

        # remove from pending claims
        run.pending_claims = [
            c for c in run.pending_claims if c["character_id"] != character_id
        ]

        # add or update player_characters in current_config
        config = run.current_config
        config["player_characters"] = [
            p
            for p in config.get("player_characters", [])
            if p["character_id"] != character_id
        ]
        config["player_characters"].append(
            {
                "character_id": character_id,
                "user_id": claim["user_id"],
                "nickname": claim["nickname"],
                "level": 1,
                "xp": 0,
                "unspent_stat_points": 0,
                "stats": {
                    "vitality": 0,
                    "strength": 0,
                    "intelligence": 0,
                    "chance": 0,
                    "agility": 0,
                },
                "active_effects": [],
            }
        )
        run.current_config = config
        run.save()
        return run

    def reject_claim(self, owner: User, invite_code: str, character_id: str) -> Run:
        run = self.get(invite_code)

        if run.owner != owner:
            raise ValueError("Only the owner can reject claims")

        if not any(c["character_id"] == character_id for c in run.pending_claims):
            raise ValueError("No pending claim for this character")

        run.pending_claims = [
            c for c in run.pending_claims if c["character_id"] != character_id
        ]
        run.save()
        return run
