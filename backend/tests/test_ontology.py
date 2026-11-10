from pathlib import Path

import pytest

from app.ontology.loader import Ontology, load_ontology


def minimal_ontology() -> dict:
    return {
        "version": 1,
        "nodes": {
            "Company": {
                "description": "회사",
                "key": ["corp_code"],
                "properties": {
                    "corp_code": {"type": "string", "description": "고유번호"},
                },
            },
        },
        "relationships": {
            "INVESTS_IN": {
                "description": "출자",
                "from": ["Company"],
                "to": ["Company"],
                "source": "structured",
            },
        },
    }


def test_load_real_file():
    ontology = load_ontology()

    assert "Company" in ontology.nodes
    assert "Person" in ontology.nodes
    assert "EXECUTIVE_OF" in ontology.relationships
    assert ontology.relationships["SHAREHOLDER_OF"].from_ == ["Person", "Company"]


def test_minimal_ontology_is_valid():
    ontology = Ontology.model_validate(minimal_ontology())

    assert ontology.relationships["INVESTS_IN"].properties == {}


def test_key_must_be_in_properties():
    data = minimal_ontology()
    data["nodes"]["Company"]["key"] = ["missing"]

    with pytest.raises(ValueError, match="properties에 없습니다"):
        Ontology.model_validate(data)


def test_relationship_must_point_to_known_node():
    data = minimal_ontology()
    data["relationships"]["INVESTS_IN"]["to"] = ["Ghost"]

    with pytest.raises(ValueError, match="Ghost"):
        Ontology.model_validate(data)


@pytest.mark.parametrize("bad_name", ["Comp any", "회사", "1Company", "A-B"])
def test_invalid_node_name(bad_name):
    data = minimal_ontology()
    data["nodes"][bad_name] = data["nodes"].pop("Company")
    data["relationships"] = {}

    with pytest.raises(ValueError, match="영문자"):
        Ontology.model_validate(data)


def test_unknown_property_type():
    data = minimal_ontology()
    data["nodes"]["Company"]["properties"]["corp_code"]["type"] = "date"

    with pytest.raises(ValueError):
        Ontology.model_validate(data)


def test_load_from_custom_path(tmp_path: Path):
    yaml_file = tmp_path / "broken.yaml"
    yaml_file.write_text(
        """
version: 1
nodes:
  Company:
    description: 회사
    key: [corp_code]
    properties:
      corp_code: { tpye: string, description: 고유번호 }
relationships: {}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="type"):
        load_ontology(yaml_file)
