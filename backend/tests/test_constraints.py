from app.ontology.constraint import build_constraint_queries
from app.ontology.loader import Ontology, load_ontology


def prop() -> dict:
    return {"type": "string", "description": "테스트"}


def make_ontology(nodes: dict) -> Ontology:
    return Ontology.model_validate({"version": 1, "nodes": nodes, "relationships": {}})


def test_single_key():
    ontology = make_ontology(
        {
            "Company": {
                "description": "회사",
                "key": ["corp_code"],
                "properties": {"corp_code": prop()},
            },
        }
    )

    assert build_constraint_queries(ontology) == [
        "CREATE CONSTRAINT company_key IF NOT EXISTS FOR (n:Company) REQUIRE n.corp_code IS UNIQUE"
    ]


def test_composite_key():
    ontology = make_ontology(
        {
            "Person": {
                "description": "인물",
                "key": ["name", "birth_ym"],
                "properties": {"name": prop(), "birth_ym": prop()},
            },
        }
    )

    queries = build_constraint_queries(ontology)

    assert len(queries) == 1
    assert "FOR (n:Person) REQUIRE (n.name, n.birth_ym) IS UNIQUE" in queries[0]


def test_one_query_per_node_in_real_ontology():
    ontology = load_ontology()

    queries = build_constraint_queries(ontology)

    assert len(queries) == len(ontology.nodes)


def test_constraint_names_are_unique():
    queries = build_constraint_queries(load_ontology())

    names = [query.split()[2] for query in queries]

    assert len(set(names)) == len(names)


def test_all_queries_are_idempotent():
    queries = build_constraint_queries(load_ontology())

    assert all("IF NOT EXISTS" in query for query in queries)
