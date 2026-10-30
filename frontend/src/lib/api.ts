export type DependencyStatus = {
  ok: boolean;
  detail: string | null;
};

export type HealthResponse = {
  status: "ok" | "degraded";
  neo4j: DependencyStatus;
  ollama: DependencyStatus;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (response.status !== 200 && response.status !== 503) {
    throw new Error(`Wrong Answer: ${response.status}`);
  }

  return response.json();
}
