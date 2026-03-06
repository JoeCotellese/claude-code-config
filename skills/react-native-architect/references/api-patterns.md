
# API Integration Patterns
## Fetching Strategies

### Strategy Comparison

| Strategy | Use When | Pros | Cons |
|----------|----------|------|------|
| Fetch on mount | Data needed immediately | Simple | Loading flash |
| Fetch on focus | Data may be stale | Fresh data | Refetch overhead |
| Background refresh | Real-time not critical | UX smooth | Complexity |
| Polling | Near real-time needed | Simple | Battery/bandwidth |
| WebSocket | True real-time | Instant updates | Complexity |
| Optimistic | Fast perceived UX | Feels instant | Rollback complexity |

### Fetch on Mount

```typescript
function usePatient(patientId: string) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetch() {
      try {
        setLoading(true);
        const data = await PatientApi.get(patientId);
        if (!cancelled) {
          setPatient(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetch();

    return () => {
      cancelled = true;
    };
  }, [patientId]);

  return { patient, loading, error };
}
```

### Fetch on Focus

```typescript
import { useFocusEffect } from '@react-navigation/native';

function PatientListScreen() {
  const [patients, setPatients] = useState<Patient[]>([]);

  useFocusEffect(
    useCallback(() => {
      let cancelled = false;

      async function fetch() {
        const data = await PatientApi.list();
        if (!cancelled) {
          setPatients(data);
        }
      }

      fetch();

      return () => {
        cancelled = true;
      };
    }, [])
  );
}
```

### Stale-While-Revalidate

Show cached data immediately, refresh in background:

```typescript
function usePatientSWR(patientId: string) {
  const [patient, setPatient] = useRecoilState(patientState(patientId));
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    async function revalidate() {
      setIsValidating(true);
      try {
        const fresh = await PatientApi.get(patientId);
        setPatient(fresh);
      } finally {
        setIsValidating(false);
      }
    }

    revalidate();
  }, [patientId, setPatient]);

  return {
    patient,           // Cached data (may be stale)
    isValidating,      // Background fetch in progress
    isLoading: !patient && isValidating,  // No cache, fetching
  };
}
```

## Caching with Recoil

### Simple Cache

```typescript
// Atom family for individual items
const patientCache = atomFamily<Patient | null, string>({
  key: 'cache/patient',
  default: null,
});

// Hook with cache-first logic
function usePatient(patientId: string) {
  const [patient, setPatient] = useRecoilState(patientCache(patientId));
  const [loading, setLoading] = useState(!patient);

  useEffect(() => {
    if (!patient) {
      PatientApi.get(patientId)
        .then(setPatient)
        .finally(() => setLoading(false));
    }
  }, [patient, patientId, setPatient]);

  const refetch = useCallback(async () => {
    setLoading(true);
    const fresh = await PatientApi.get(patientId);
    setPatient(fresh);
    setLoading(false);
  }, [patientId, setPatient]);

  return { patient, loading, refetch };
}
```

### Cache Invalidation

```typescript
// After mutation, invalidate cache
function useUpdatePatient() {
  const setPatient = useSetRecoilState(patientCache);

  return async (patientId: string, updates: Partial<Patient>) => {
    const updated = await PatientApi.update(patientId, updates);
    setPatient(patientId)(updated);  // Update cache
    return updated;
  };
}

// Or invalidate to force refetch
function useInvalidatePatient() {
  const resetPatient = useResetRecoilState(patientCache);

  return (patientId: string) => {
    resetPatient(patientId);  // Next read will refetch
  };
}
```

### List + Detail Cache Sync

```typescript
// List cache
const patientListState = atom<Patient[]>({
  key: 'cache/patientList',
  default: [],
});

// Individual cache
const patientState = atomFamily<Patient | null, string>({
  key: 'cache/patient',
  default: null,
});

// When list fetched, populate individual caches
function usePatientList() {
  const [list, setList] = useRecoilState(patientListState);
  const setPatient = useSetRecoilState(patientState);

  const fetchList = useCallback(async () => {
    const patients = await PatientApi.list();
    setList(patients);

    // Populate individual caches
    patients.forEach(p => setPatient(p.id)(p));
  }, [setList, setPatient]);

  // ...
}
```

## Error Handling

### Error Types

```typescript
// api/errors.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class NetworkError extends Error {
  constructor(message = 'Network request failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class AuthError extends ApiError {
  constructor(message = 'Authentication required') {
    super(message, 401, 'AUTH_REQUIRED');
    this.name = 'AuthError';
  }
}
```

### Centralized Error Handling

```typescript
// apis/BaseApi.ts
class BaseApi {
  protected async request<T>(
    method: string,
    endpoint: string,
    data?: unknown
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method,
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });

      if (!response.ok) {
        await this.handleErrorResponse(response);
      }

      return response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new NetworkError();
    }
  }

  private async handleErrorResponse(response: Response): Promise<never> {
    const body = await response.json().catch(() => ({}));

    if (response.status === 401) {
      // Trigger logout
      await this.handleUnauthorized();
      throw new AuthError(body.message);
    }

    if (response.status === 403) {
      throw new ApiError('Access denied', 403, 'FORBIDDEN');
    }

    if (response.status === 404) {
      throw new ApiError('Resource not found', 404, 'NOT_FOUND');
    }

    throw new ApiError(
      body.message || 'Request failed',
      response.status,
      body.code
    );
  }
}
```

### Component Error Handling

```typescript
function PatientDetail({ patientId }) {
  const { patient, error, loading, refetch } = usePatient(patientId);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    if (error instanceof NetworkError) {
      return (
        <ErrorState
          title="No Connection"
          message="Check your internet and try again"
          action={<Button title="Retry" onPress={refetch} />}
        />
      );
    }

    if (error instanceof ApiError && error.statusCode === 404) {
      return <NotFoundState message="Patient not found" />;
    }

    return (
      <ErrorState
        title="Something went wrong"
        message={error.message}
        action={<Button title="Retry" onPress={refetch} />}
      />
    );
  }

  return <PatientCard patient={patient} />;
}
```

## Optimistic Updates

### Simple Optimistic Update

```typescript
function useToggleFavorite(patientId: string) {
  const [patient, setPatient] = useRecoilState(patientState(patientId));

  return async () => {
    if (!patient) return;

    const previousValue = patient.isFavorite;

    // Optimistically update
    setPatient({ ...patient, isFavorite: !previousValue });

    try {
      await PatientApi.toggleFavorite(patientId);
    } catch (error) {
      // Rollback on failure
      setPatient({ ...patient, isFavorite: previousValue });
      throw error;
    }
  };
}
```

### Optimistic List Operations

```typescript
function useAddPatient() {
  const [patients, setPatients] = useRecoilState(patientListState);

  return async (newPatient: CreatePatientInput) => {
    // Generate temp ID
    const tempId = `temp-${Date.now()}`;
    const optimisticPatient = {
      ...newPatient,
      id: tempId,
      createdAt: new Date().toISOString(),
    };

    // Add optimistically
    setPatients(prev => [...prev, optimisticPatient]);

    try {
      const created = await PatientApi.create(newPatient);

      // Replace temp with real
      setPatients(prev =>
        prev.map(p => (p.id === tempId ? created : p))
      );

      return created;
    } catch (error) {
      // Remove on failure
      setPatients(prev => prev.filter(p => p.id !== tempId));
      throw error;
    }
  };
}
```

## Request Patterns

### Request Deduplication

```typescript
const pendingRequests = new Map<string, Promise<any>>();

async function dedupedFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }

  const promise = fetcher().finally(() => {
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, promise);
  return promise;
}

// Usage
function usePatient(patientId: string) {
  useEffect(() => {
    dedupedFetch(`patient-${patientId}`, () => PatientApi.get(patientId))
      .then(setPatient);
  }, [patientId]);
}
```

### Request Cancellation

```typescript
function usePatient(patientId: string) {
  useEffect(() => {
    const controller = new AbortController();

    PatientApi.get(patientId, { signal: controller.signal })
      .then(setPatient)
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err);
        }
      });

    return () => controller.abort();
  }, [patientId]);
}
```

### Retry with Backoff

```typescript
async function fetchWithRetry<T>(
  fetcher: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fetcher();
    } catch (error) {
      lastError = error as Error;

      // Don't retry client errors
      if (error instanceof ApiError && error.statusCode < 500) {
        throw error;
      }

      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(r => setTimeout(r, delay));
      }
    }
  }

  throw lastError!;
}
```

## Pagination

### Cursor-Based

```typescript
function usePatientList() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const { data, nextCursor } = await PatientApi.list({ cursor, limit: 20 });
      setPatients(prev => [...prev, ...data]);
      setCursor(nextCursor);
      setHasMore(!!nextCursor);
    } finally {
      setLoading(false);
    }
  }, [cursor, hasMore, loading]);

  return { patients, loadMore, hasMore, loading };
}
```

### With FlatList

```typescript
function PatientListScreen() {
  const { patients, loadMore, hasMore, loading } = usePatientList();

  return (
    <FlatList
      data={patients}
      renderItem={({ item }) => <PatientRow patient={item} />}
      keyExtractor={item => item.id}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      ListFooterComponent={
        loading ? <ActivityIndicator /> :
        !hasMore ? <Text>No more patients</Text> : null
      }
    />
  );
}
```

## Offline Support

### Queue Mutations

```typescript
// Simple offline queue
const mutationQueue = atom<QueuedMutation[]>({
  key: 'offline/mutationQueue',
  default: [],
  effects: [persistEffect('mutationQueue')],
});

function useOfflineMutation() {
  const [queue, setQueue] = useRecoilState(mutationQueue);
  const isOnline = useNetworkStatus();

  const queueMutation = (mutation: QueuedMutation) => {
    setQueue(prev => [...prev, mutation]);
  };

  // Process queue when online
  useEffect(() => {
    if (isOnline && queue.length > 0) {
      processQueue(queue).then(() => setQueue([]));
    }
  }, [isOnline, queue]);

  return { queueMutation, pendingCount: queue.length };
}
```
