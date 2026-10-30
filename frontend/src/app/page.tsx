import HealthStatus from "@/components/HealthStatus";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-2xl p-8">
      <h1 className="text-2xl font-bold">DART 그래프 RAG</h1>
      <HealthStatus />
    </main>
  );
}
