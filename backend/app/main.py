from fastapi import FastAPI

app = FastAPI(title="DART ONTOLOGY GRAPH RAG")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
