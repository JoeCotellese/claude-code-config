
# Data Flow Patterns
## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                             │
│  Screens, Components (presentation only)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Hooks Layer                            │
│  Custom hooks (usePatient, useAuth, useForm)                │
│  Orchestrates state + API + business logic                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌───────────────────┐ ┌─────────────┐ ┌─────────────────────┐
│   State Layer     │ │  API Layer  │ │   Services Layer    │
│   (Recoil)        │ │  (BaseApi)  │ │   (LocalStorage,    │
│                   │ │             │ │    Analytics, etc)  │
└───────────────────┘ └─────────────┘ └─────────────────────┘
```

## Where Logic Lives

### Decision Matrix

| Logic Type | Location | Example |
|------------|----------|---------|
| **UI state** | Component (useState) | Modal open, accordion expanded |
| **Form validation** | Hook or form library | Email format, required fields |
| **Business rules** | Custom hook | Can user edit this patient? |
| **Data fetching** | Custom hook | usePatient, usePatientList |
| **Data transformation** | Recoil selector or hook | Filter/sort patients |
| **Side effects** | Custom hook | Track analytics, sync storage |
| **Navigation logic** | Screen or hook | Where to go after submit |
| **API calls** | API class | PatientApi.get() |
| **Persistence** | Service | LocalStorageService |

### Component Responsibilities

```typescript
// ✅ Component: UI rendering only
function PatientCard({ patient, onEdit, onDelete }: Props) {
  return (
    <View style={styles.card}>
      <Text>{patient.name}</Text>
      <Text>{patient.email}</Text>
      <Button title="Edit" onPress={onEdit} />
      <Button title="Delete" onPress={onDelete} />
    </View>
  );
}

// ❌ Component doing too much
function PatientCard({ patientId }: Props) {
  const [patient, setPatient] = useState(null);
  const navigation = useNavigation();

  useEffect(() => {
    PatientApi.get(patientId).then(setPatient);  // ❌ Data fetching
  }, []);

  const handleDelete = async () => {
    await PatientApi.delete(patientId);  // ❌ API calls
    Analytics.track('patient_deleted');   // ❌ Side effects
    navigation.goBack();                  // ❌ Navigation
  };

  // Component is now hard to test and reuse
}
```

### Hook Responsibilities

```typescript
// hooks/usePatient.ts
// ✅ Hook: orchestrates data + logic
function usePatient(patientId: string) {
  // State management
  const [patient, setPatient] = useRecoilState(patientState(patientId));
  const [loading, setLoading] = useState(!patient);
  const [error, setError] = useState<Error | null>(null);

  // Data fetching
  useEffect(() => {
    if (!patient) {
      PatientApi.get(patientId)
        .then(setPatient)
        .catch(setError)
        .finally(() => setLoading(false));
    }
  }, [patientId]);

  // Business logic
  const canEdit = useMemo(() => {
    return patient?.status !== 'archived';
  }, [patient]);

  // Actions
  const updatePatient = useCallback(async (updates: Partial<Patient>) => {
    const updated = await PatientApi.update(patientId, updates);
    setPatient(updated);
    return updated;
  }, [patientId, setPatient]);

  return { patient, loading, error, canEdit, updatePatient };
}
```

## Custom Hook Patterns

### Data Hook

Fetches and manages entity data:

```typescript
function useEntity<T>(
  id: string,
  fetcher: (id: string) => Promise<T>,
  cacheAtom: (id: string) => RecoilState<T | null>
) {
  const [entity, setEntity] = useRecoilState(cacheAtom(id));
  const [loading, setLoading] = useState(!entity);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!entity) {
      fetcher(id)
        .then(setEntity)
        .catch(setError)
        .finally(() => setLoading(false));
    }
  }, [id, entity, fetcher, setEntity]);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const fresh = await fetcher(id);
      setEntity(fresh);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [id, fetcher, setEntity]);

  return { data: entity, loading, error, refetch };
}

// Usage
const usePatient = (id: string) =>
  useEntity(id, PatientApi.get, patientState);
```

### Action Hook

Encapsulates mutations with side effects:

```typescript
function useDeletePatient() {
  const navigation = useNavigation();
  const resetPatient = useResetRecoilState(patientState);
  const [patients, setPatients] = useRecoilState(patientListState);

  return useCallback(async (patientId: string) => {
    // Confirm
    const confirmed = await showConfirmDialog('Delete patient?');
    if (!confirmed) return false;

    try {
      // API call
      await PatientApi.delete(patientId);

      // Update caches
      resetPatient(patientId);
      setPatients(prev => prev.filter(p => p.id !== patientId));

      // Side effects
      Analytics.track('patient_deleted', { patientId });

      // Navigate
      navigation.goBack();

      return true;
    } catch (error) {
      showError('Failed to delete patient');
      return false;
    }
  }, [navigation, resetPatient, setPatients]);
}
```

### Feature Hook

Combines multiple hooks for a feature:

```typescript
function usePatientDetail(patientId: string) {
  // Data
  const { patient, loading, error, refetch } = usePatient(patientId);
  const { sessions } = usePatientSessions(patientId);

  // Actions
  const updatePatient = useUpdatePatient(patientId);
  const deletePatient = useDeletePatient();

  // Derived state
  const recentSessions = useMemo(
    () => sessions.slice(0, 5),
    [sessions]
  );

  // Permissions
  const canEdit = useCanEditPatient(patientId);
  const canDelete = useCanDeletePatient(patientId);

  return {
    // Data
    patient,
    sessions,
    recentSessions,
    loading,
    error,
    // Actions
    updatePatient,
    deletePatient: () => deletePatient(patientId),
    refetch,
    // Permissions
    canEdit,
    canDelete,
  };
}
```

## Data Flow Examples

### Read Flow

```
User taps "View Patient"
         │
         ▼
┌─────────────────────┐
│ PatientDetailScreen │  navigation.navigate('PatientDetail', { patientId })
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│    usePatient()     │  Custom hook
└─────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌───────────┐
│Recoil │  │PatientApi │  Check cache, fetch if needed
│ cache │  │  .get()   │
└───────┘  └───────────┘
    │         │
    └────┬────┘
         ▼
┌─────────────────────┐
│   PatientDetail     │  Presentational component
│    (UI render)      │
└─────────────────────┘
```

### Write Flow

```
User taps "Save"
         │
         ▼
┌─────────────────────┐
│  PatientEditScreen  │  handleSubmit(formData)
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  useUpdatePatient() │  Validation, API call
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  PatientApi.update  │  HTTP request
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Update Recoil      │  setPatient(updated)
│  cache              │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Side effects       │  Analytics, notifications
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Navigate back      │  navigation.goBack()
└─────────────────────┘
```

### Multi-Screen Data Sharing

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ PatientList    │     │ PatientDetail  │     │ PatientEdit    │
│    Screen      │     │    Screen      │     │    Screen      │
└───────┬────────┘     └───────┬────────┘     └───────┬────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Recoil State      │
                    │  patientState(id)   │
                    │  patientListState   │
                    └─────────────────────┘

1. PatientList fetches list → populates patientListState
2. PatientDetail reads from patientState(id) (already cached from list)
3. PatientEdit updates via hook → updates patientState(id)
4. PatientList and PatientDetail auto-update via Recoil subscription
```

## Service Layer

### When to Use Services

Services are for cross-cutting concerns that don't fit in hooks:

```typescript
// services/LocalStorageService.ts
class LocalStorageService {
  async get<T>(key: string): Promise<T | null> {
    const value = await AsyncStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  }

  async set<T>(key: string, value: T): Promise<void> {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  }

  async remove(key: string): Promise<void> {
    await AsyncStorage.removeItem(key);
  }
}

export const localStorageService = new LocalStorageService();
```

```typescript
// services/AnalyticsService.ts
class AnalyticsService {
  track(event: string, properties?: Record<string, any>) {
    // Send to analytics provider
  }

  identify(userId: string, traits?: Record<string, any>) {
    // Identify user
  }

  screen(name: string) {
    // Track screen view
  }
}

export const analytics = new AnalyticsService();
```

### Using Services in Hooks

```typescript
function useAuth() {
  const [user, setUser] = useRecoilState(userState);

  const login = useCallback(async (credentials: Credentials) => {
    const response = await AuthApi.login(credentials);

    // Update state
    setUser(response.user);

    // Persist token
    await localStorageService.set('authToken', response.token);

    // Track
    analytics.identify(response.user.id);
    analytics.track('user_logged_in');

    return response.user;
  }, [setUser]);

  const logout = useCallback(async () => {
    // Clear state
    setUser(null);

    // Clear storage
    await localStorageService.remove('authToken');

    // Track
    analytics.track('user_logged_out');
  }, [setUser]);

  return { user, login, logout };
}
```

## Anti-Patterns

### Prop Drilling Data

```typescript
// ❌ Passing data through many levels
<App>
  <Dashboard patient={patient}>
    <PatientSection patient={patient}>
      <PatientHeader patient={patient}>
        <PatientName name={patient.name} />

// ✅ Use Recoil or Context
function PatientName() {
  const patient = useRecoilValue(currentPatientSelector);
  return <Text>{patient?.name}</Text>;
}
```

### Business Logic in Components

```typescript
// ❌ Complex logic in component
function PatientCard({ patient }) {
  const canEdit = patient.status !== 'archived' &&
                  patient.ownerId === currentUserId &&
                  !patient.isLocked;

  const displayName = patient.preferredName ||
                      `${patient.firstName} ${patient.lastName}`;
  // ...
}

// ✅ Extract to hooks/selectors
function PatientCard({ patient }) {
  const canEdit = useCanEditPatient(patient.id);
  const displayName = usePatientDisplayName(patient.id);
  // ...
}
```

### API Calls in Components

```typescript
// ❌ Direct API calls
function PatientList() {
  useEffect(() => {
    PatientApi.list().then(setPatients);
  }, []);
}

// ✅ Through hooks
function PatientList() {
  const { patients, loading, error } = usePatientList();
}
```

### Circular Dependencies

```typescript
// ❌ Hook A uses Hook B, Hook B uses Hook A
function usePatient() {
  const { canEdit } = usePermissions(); // uses usePatient internally!
}

// ✅ Break cycle with lower-level primitives
function usePatient() {
  const patient = useRecoilValue(patientState);
  const canEdit = useCanEdit(patient, 'patient');
}
```
