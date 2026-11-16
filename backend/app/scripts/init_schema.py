from neo4j import GraphDatabase

from app.config import get_settings
from app.ontology.constraint import build_constraint_queries
from app.ontology.loader import load_ontology

SHOW_CONSTRAINTS = "SHOW CONSTRAINTS YIELD name RETURN name ORDER BY name"


def main() -> None:
    settings = get_settings()
    queries = build_constraint_queries(load_ontology())

    with GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value())
    ) as driver:
        driver.verify_connectivity()

        for query in queries:
            driver.execute_query(query)
            print(f"ENTERED: {query}")

        records, _, _ = driver.execute_query(SHOW_CONSTRAINTS)
        print(f"current constraint: {[record['name'] for record in records]}")


if __name__ == "__main__":
    main()
