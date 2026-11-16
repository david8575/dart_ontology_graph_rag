from app.ontology.loader import Ontology


def build_constraint_queries(ontology: Ontology) -> list[str]:
    queries: list[str] = []

    for label, node in ontology.nodes.items():
        props = [f"n.{key}" for key in node.key]

        if len(props) == 1:
            target = props[0]
        else:
            target = "(" + ", ".join(props) + ")"

        queries.append(
            f"CREATE CONSTRAINT {label.lower()}_key IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE {target} IS UNIQUE"
        )

    return queries
