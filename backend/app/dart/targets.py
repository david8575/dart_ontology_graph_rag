from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field, model_validator

TARGETS_FILE = Path(__file__).resolve().parents[2] / "targets.yaml"


class Target(BaseModel):
    corp_code: str = Field(pattern=r"^\d{8}$")
    name: str
    role: str


class TargetList(BaseModel):
    companies: list[Target] = Field(min_length=1)

    @model_validator(mode="after")
    def check_unique_codes(self) -> Self:
        codes = [company.corp_code for company in self.companies]
        if len(set(codes)) != len(codes):
            raise ValueError(f"corp_code가 중복되었습니다: {codes}")
        return self


def load_targets(path: Path = TARGETS_FILE) -> list[Target]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return TargetList.model_validate(data).companies
