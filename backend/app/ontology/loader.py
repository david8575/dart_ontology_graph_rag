import re
from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, Field, model_validator

ONTOLOGY_FILE = Path(__file__).resolve().parents[2] / "ontology" / "dart.yaml"

NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

PropertyType = Literal["string", "integer", "float", "boolean"]


def _check_name(name: str) -> None:
    if not NAME_PATTERN.fullmatch(name):
        raise ValueError(f"이름에는 영문자, 숫자, 밑줄만 쓸 수 있습니다: {name!r}")


class PropertyDef(BaseModel):
    type: PropertyType
    description: str


class NodeDef(BaseModel):
    description: str
    key: list[str] = Field(min_length=1)
    properties: dict[str, PropertyDef]

    @model_validator(mode="after")
    def check_key_in_properties(self) -> Self:
        missing = [k for k in self.key if k not in self.properties]
        if missing:
            raise ValueError(f"key에 있는 속성이 properties에 없습니다: {missing}")
        return self


class RelationshipDef(BaseModel):
    description: str
    from_: list[str] = Field(alias="from", min_length=1)
    to: list[str] = Field(min_length=1)
    source: Literal["structured", "extracted"]
    properties: dict[str, PropertyDef] = Field(default_factory=dict)


class Ontology(BaseModel):
    version: int
    nodes: dict[str, NodeDef]
    relationships: dict[str, RelationshipDef]

    @model_validator(mode="after")
    def check_names_and_references(self) -> Self:
        for node_name, node in self.nodes.items():
            _check_name(node_name)
            for prop_name in node.properties:
                _check_name(prop_name)

        for rel_name, rel in self.relationships.items():
            _check_name(rel_name)
            for prop_name in rel.properties:
                _check_name(prop_name)
            unknown = [n for n in rel.from_ + rel.to if n not in self.nodes]
            if unknown:
                raise ValueError(f"관계 {rel_name}가 정의되지 않은 노드를 가리킵니다: {unknown}")
        return self


def load_ontology(path: Path = ONTOLOGY_FILE) -> Ontology:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    return Ontology.model_validate(data)
