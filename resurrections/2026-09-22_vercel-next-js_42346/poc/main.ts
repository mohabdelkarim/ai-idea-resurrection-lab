import React, { Suspense, useEffect } from \"react\";
import { useRouter, useSearchParams } from \"next/navigation\";

// Async server component that fetches data based on a query param
// This component will suspend while the fetch is in flight
export async function Foo() {
  const searchParams = useSearchParams();
  const query = searchParams.get(\"q\") ?? \"default\";
  // Simulate a fetch that respects Next.js cache API
  const data = await fetchData(query);
  return (
    <div>
      <h2>Result for: {query}</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

// Helper that mimics a server‑side fetch with a delay
async function fetchData(query: string): Promise<any> {
  // The fetch cache API is automatically used by Next.js when using the global fetch
  const response = await fetch(`https://jsonplaceholder.typicode.com/todos/${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch data for ${query}: ${response.statusText}`);
  }
  const json = await response.json();
  // Simulate latency for demonstration purposes
  await new Promise(resolve => setTimeout(resolve, 1500));
  return json;
}

// Client component that triggers a router push with new searchParams
export function SearchController() {
  const router = useRouter();
  const handleClick = (newQuery: string) => {
    // Preserve other params if needed
    router.push(`?q=${encodeURIComponent(newQuery)}`);
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <button onClick={() => handleClick('1')}>Load Todo 1</button>
      <button onClick={() => handleClick('2')}>Load Todo 2</button>
      <button onClick={() => handleClick('3')}>Load Todo 3</button>
    </div>
  );
}

// Page component that composes the controller and the async component inside Suspense
export default function Page() {
  // Force a re‑render when searchParams change so Suspense can re‑evaluate Foo
  const searchParams = useSearchParams();
  useEffect(() => {
    // No side‑effects needed; the hook ensures the component updates on param change
  }, [searchParams]);

  return (
    <main>
      <h1>Next.js 13 SearchParams Suspense Demo</h1>
      <SearchController />
      <Suspense fallback={<Skeleton />}>
        {/* @ts-expect-error Async Server Component */}
        <Foo />
      </Suspense>
    </main>
  );
}

// Simple fallback UI displayed while Foo is loading
function Skeleton() {
  return (
    <div style={{ padding: '2rem', background: '#f0f0f0' }}>
      <p>Loading...</p>
    </div>
  );
}