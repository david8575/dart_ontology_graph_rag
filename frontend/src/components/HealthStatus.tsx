"use client";

import { useEffect, useState } from "react";

import {
  fetchHealth,
  type DependencyStatus,
  type HealthResponse,
} from "@/lib/api";

type DependencyRowProps = {
  name: string;
  dependency: DependencyStatus;
};

function DependencyRow({ name, dependency }: DependencyRowProps) {
  return (
    <li className="break-words">
      <span className={dependency.ok ? "text-green-600" : "text-red-600"}>
        {dependency.ok ? "정상" : "실패"}
      </span>{" "}
      {name}: {dependency.detail}
    </li>
  );
}

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : String(e));
      });
  }, []);

  if (error) {
    return (
      <p className="mt-4 text-red-600">백엔드에 연결할 수 없습니다: {error}</p>
    );
  }

  if (!health) {
    return <p className="mt-4">상태를 확인하는 중입니다...</p>;
  }

  return (
    <section className="mt-4">
      <p className="font-semibold">전체 상태: {health.status}</p>
      <ul className="mt-2 space-y-1">
        <DependencyRow name="Neo4j" dependency={health.neo4j} />
        <DependencyRow name="Ollama" dependency={health.ollama} />
      </ul>
    </section>
  );
}
