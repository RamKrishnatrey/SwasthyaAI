export type HealthStatus = {
  status: 'ok';
  mode: 'demo';
};

export async function getHealth(): Promise<HealthStatus> {
  const response = await fetch('/api/v1/health');
  if (!response.ok) throw new Error(`Health check failed (${response.status})`);
  return response.json() as Promise<HealthStatus>;
}
