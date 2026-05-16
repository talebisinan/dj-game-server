from datetime import datetime
from typing import Literal

from ninja import Schema
from pydantic import Field

type SkillType = Literal["damage", "heal", "buff", "debuff", "resurrection"]
type Element = Literal["fire", "earth", "water", "air"]
type TargetType = Literal["character", "monster", "npc"]
type EffectType = Literal[
    "damage", "heal", "xp", "skill_up", "item", "death", "dialogue"
]
type Stat = Literal[
    "hp", "ap", "mp", "vitality", "strength", "intelligence", "chance", "agility"
]


class SkillEffectSchema(Schema):
    stat: Stat
    modifier: float
    duration_turns: int = Field(ge=0)  # 0 = instant


class SkillSchema(Schema):
    id: str
    name: str
    type: SkillType
    element: Element
    base_damage: int = Field(ge=0, le=500)
    ap_cost: int = Field(ge=1, le=10)
    range: int = Field(ge=1, le=20)
    effects: list[SkillEffectSchema] = []


class CharacterStatsSchema(Schema):
    vitality: int = Field(ge=0)
    strength: int = Field(ge=0)
    intelligence: int = Field(ge=0)
    chance: int = Field(ge=0)
    agility: int = Field(ge=0)


class CharacterSkillSchema(Schema):
    skill_id: str
    unlock_level: int = Field(ge=1, default=1)


class CharacterClassSchema(Schema):
    id: str
    name: str
    stat_points: int = Field(ge=0)
    initiative_bonus: int = Field(default=0)
    skills: list[CharacterSkillSchema]


class ExplorationTileSchema(Schema):
    x: int
    y: int
    walkable: bool
    resource: str | None = None
    npc_id: str | None = None  # references NPCSchema id
    zone_transition: str | None = None  # references ZoneSchema id


class TacticalTileSchema(Schema):
    x: int
    y: int
    elevation: int = 0  # -1 = pit, 0 = ground, 1 = elevated
    line_of_sight: bool = True
    spawn_order: int | None = None  # None = not a spawn tile


class ZoneSchema(Schema):
    id: str
    name: str
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    monster_limit: int | None = None  # None = infinite
    spawn_interval_seconds: int = Field(ge=1, default=30)
    max_simultaneous_spawns: int = Field(ge=1, default=2)
    monster_pool: list[dict] = []  # [{"monster_id": str, "weight": int}]
    tiles: list[ExplorationTileSchema]
    tactical_tiles: list[TacticalTileSchema]


type MonsterBehavior = Literal["aggressive", "defensive", "passive"]


class MonsterSchema(Schema):
    id: str
    name: str
    hp: int = Field(ge=1, le=1000)
    ap: int = Field(ge=1, le=20)
    mp: int = Field(ge=1, le=20)
    behavior: MonsterBehavior = "aggressive"
    skill_ids: list[str]  # references SkillSchema ids


class NPCSchema(Schema):
    id: str
    name: str
    zone_id: str  # references ZoneSchema id


class EventEffectSchema(Schema):
    target_id: str
    target_type: TargetType
    effect_type: EffectType
    value: int | str | None = None
    source_id: str | None = None


class EventReportSchema(Schema):
    event_type: str
    description: str
    effects: list[EventEffectSchema]


class GlobalConfigSchema(Schema):
    respawn_enabled: bool = False
    stat_points_on_creation: int = Field(ge=0, default=10)


class PlayerStatsSchema(Schema):
    vitality: int = Field(ge=0, default=0)
    strength: int = Field(ge=0, default=0)
    intelligence: int = Field(ge=0, default=0)
    chance: int = Field(ge=0, default=0)
    agility: int = Field(ge=0, default=0)


class PlayerCharacterSchema(Schema):
    character_id: str
    user_id: str | None = None  # None = unclaimed
    nickname: str | None = None
    level: int = Field(ge=1, default=1)
    xp: int = Field(ge=0, default=0)
    unspent_stat_points: int = Field(ge=0, default=0)
    stats: PlayerStatsSchema = PlayerStatsSchema()
    active_effects: list = []


class WorldConfigSchema(Schema):
    name: str
    version: str = "1.0.0"
    global_config: GlobalConfigSchema = GlobalConfigSchema()
    skills: list[SkillSchema]
    characters: list[CharacterClassSchema]
    zones: list[ZoneSchema]
    monsters: list[MonsterSchema]
    npcs: list[NPCSchema]
    player_characters: list[PlayerCharacterSchema] = []


class CreateRunSchema(Schema):
    template_config: WorldConfigSchema


class RunSchema(Schema):
    id: int
    invite_code: str
    is_started: bool
    template_config: WorldConfigSchema
    current_config: WorldConfigSchema
    pending_players: list
    pending_claims: list
    participants: list
    created_at: datetime
    updated_at: datetime


class RunStartedSchema(Schema):
    id: int
    invite_code: str
    is_started: bool
