
# State Management Decisions
## Decision Tree

```
                    ┌─────────────────────────────────┐
                    │  Where is this state used?      │
                    └─────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Single           Parent +         Multiple
             Component         Children         Unrelated
                │                 │             Components
                ▼                 ▼                 │
           useState            Props               │
                                 │                 │
                          ┌──────┴──────┐          │
                          ▼             ▼          │
                      2-3 levels    4+ levels      │
                          │             │          │
                          ▼             ▼          │
                        Props      Consider        │
                                   Context         │
                                      │            │
                                      └─────┬──────┘
                                            ▼
                              ┌─────────────────────────────┐
                              │  Is it server/async data?   │
                              └─────────────────────────────┘
                                            │
                                    ┌───────┴───────┐
                                    ▼               ▼
                                   Yes              No
                                    │               │
                                    ▼               ▼
                              React Query       Recoil
                              or Recoil
                              async selector
```

## State Types

### 1. UI State (useState)

State that only affects a single component's rendering.

**Examples:**
- Form input values before submission
- Accordion open/closed
- Modal visibility
- Hover/focus states
- Animation values

```typescript
function AccordionItem({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);  // UI state

  return (
    <View>
      <TouchableOpacity onPress={() => setIsOpen(!isOpen)}>
        <Text>{title}</Text>
      </TouchableOpacity>
      {isOpen && children}
    </View>
  );
}
```

### 2. Shared UI State (Recoil atom)

UI state needed by multiple unrelated components.

**Examples:**
- Theme (dark/light mode)
- Current tab selection
- Global modal state
- Toast/snackbar queue

```typescript
// state/uiState.ts
export const themeState = atom<'light' | 'dark'>({
  key: 'ui/theme',
  default: 'light',
});

export const activeModalState = atom<string | null>({
  key: 'ui/activeModal',
  default: null,
});
```

### 3. Server State (Recoil + async or React Query)

Data that originates from an API and may need caching, refetching, or synchronization.

**Examples:**
- User profile
- Patient list
- Session data
- Any API response

```typescript
// Option A: Recoil async selector (simple cases)
export const patientSelector = selectorFamily<Patient, string>({
  key: 'patient/detail',
  get: (patientId) => async () => {
    const response = await PatientApi.get(patientId);
    return response;
  },
});

// Option B: Custom hook with Recoil (more control)
export function usePatient(patientId: string) {
  const [patient, setPatient] = useRecoilState(patientState(patientId));
  const [loading, setLoading] = useState(!patient);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!patient) {
      PatientApi.get(patientId)
        .then(setPatient)
        .catch(setError)
        .finally(() => setLoading(false));
    }
  }, [patientId, patient, setPatient]);

  return { patient, loading, error, refetch: () => { /* ... */ } };
}
```

### 4. Form State (useState or form library)

Temporary state for user input before submission.

**Simple forms:** `useState` with object

```typescript
function SimpleForm() {
  const [form, setForm] = useState({ name: '', email: '' });

  const updateField = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <>
      <TextInput
        value={form.name}
        onChangeText={(v) => updateField('name', v)}
      />
      <TextInput
        value={form.email}
        onChangeText={(v) => updateField('email', v)}
      />
    </>
  );
}
```

**Complex forms:** Consider react-hook-form or formik

```typescript
import { useForm, Controller } from 'react-hook-form';

function ComplexForm() {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: { name: '', email: '' },
  });

  return (
    <Controller
      control={control}
      name="email"
      rules={{ required: true, pattern: /^\S+@\S+$/i }}
      render={({ field: { onChange, value } }) => (
        <TextInput value={value} onChangeText={onChange} />
      )}
    />
  );
}
```

### 5. Navigation State (React Navigation)

State related to which screen is active, route params, etc.

**Let React Navigation manage it:**

```typescript
// Pass data via route params
navigation.navigate('PatientDetail', { patientId: '123' });

// Read params
const route = useRoute<PatientDetailRouteProp>();
const { patientId } = route.params;
```

**Don't duplicate in Recoil:**

```typescript
// ❌ Don't do this
const currentScreenState = atom({ key: 'currentScreen', default: 'Home' });

// ✅ Use navigation state
const navigation = useNavigation();
const state = navigation.getState();
```

## Recoil Patterns

### Atom Granularity

**Too coarse (❌):**
```typescript
const appState = atom({
  key: 'appState',
  default: {
    user: null,
    patients: [],
    settings: {},
    ui: {},
  },
});
// Any change re-renders ALL subscribers
```

**Right granularity (✅):**
```typescript
const userState = atom({ key: 'user', default: null });
const patientsState = atom({ key: 'patients', default: [] });
const settingsState = atom({ key: 'settings', default: {} });
// Changes only affect relevant subscribers
```

### Atom Families for Collections

```typescript
// Store list of IDs
const patientIdsState = atom<string[]>({
  key: 'patient/ids',
  default: [],
});

// Store individual items
const patientState = atomFamily<Patient | null, string>({
  key: 'patient/item',
  default: null,
});

// List component only re-renders when IDs change
function PatientList() {
  const patientIds = useRecoilValue(patientIdsState);
  return patientIds.map(id => <PatientRow key={id} patientId={id} />);
}

// Row only re-renders when its patient changes
function PatientRow({ patientId }) {
  const patient = useRecoilValue(patientState(patientId));
  return <Text>{patient?.name}</Text>;
}
```

### Derived State with Selectors

```typescript
// Base atoms
const patientsState = atom<Patient[]>({ key: 'patients', default: [] });
const filterState = atom<string>({ key: 'patientFilter', default: '' });

// Derived (computed) state
const filteredPatientsSelector = selector({
  key: 'patients/filtered',
  get: ({ get }) => {
    const patients = get(patientsState);
    const filter = get(filterState).toLowerCase();
    if (!filter) return patients;
    return patients.filter(p =>
      p.name.toLowerCase().includes(filter)
    );
  },
});

// Component uses derived state
function PatientList() {
  const patients = useRecoilValue(filteredPatientsSelector);
  // ...
}
```

## Props vs Context vs Recoil

| Scenario | Use |
|----------|-----|
| Parent to child (1-2 levels) | Props |
| Parent to deep child (3+ levels) | Context or Recoil |
| Sibling components | Lift state up + props, or Recoil |
| Across navigation stacks | Recoil |
| Theme/locale | Context |
| Authenticated user | Recoil (persisted) |
| API data with caching | Recoil async selector or React Query |

## When to Deviate from Recoil

### Use Context When:

1. **Provider-scoped state** - Different subtrees need different values
   ```typescript
   <ThemeContext.Provider value="dark">
     <DarkSection />
   </ThemeContext.Provider>
   <ThemeContext.Provider value="light">
     <LightSection />
   </ThemeContext.Provider>
   ```

2. **Dependency injection** - Passing services/utilities
   ```typescript
   <AnalyticsContext.Provider value={analyticsService}>
     <App />
   </AnalyticsContext.Provider>
   ```

### Use Local State When:

1. **Truly isolated UI** - Accordion, modal open/close
2. **Form drafts** - Before submission
3. **Ephemeral state** - Doesn't survive unmount and shouldn't

### Consider React Query When:

1. **Heavy server state needs** - Background refetching, cache invalidation
2. **Optimistic updates** - Complex rollback on failure
3. **Pagination/infinite scroll** - Built-in support
4. **Already using it** - Consistency > mixing libraries

## Migration Patterns

### Local to Recoil

When local state needs to be shared:

```typescript
// Before: Local state
function PatientList() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // ...
}

// After: Recoil (when another component needs selectedId)
// state/patientState.ts
export const selectedPatientIdState = atom<string | null>({
  key: 'patient/selectedId',
  default: null,
});

// PatientList.tsx
function PatientList() {
  const [selectedId, setSelectedId] = useRecoilState(selectedPatientIdState);
  // ...
}

// PatientActions.tsx (now can access)
function PatientActions() {
  const selectedId = useRecoilValue(selectedPatientIdState);
  // ...
}
```

### Props to Recoil

When prop drilling becomes painful:

```typescript
// Before: Props through 4 levels
<App user={user}>
  <Layout user={user}>
    <Sidebar user={user}>
      <UserAvatar user={user} />

// After: Recoil
// App.tsx
const [, setUser] = useSetRecoilState(userState);
useEffect(() => { setUser(fetchedUser); }, [fetchedUser]);

// UserAvatar.tsx (any level)
function UserAvatar() {
  const user = useRecoilValue(userState);
  return <Avatar uri={user.avatarUrl} />;
}
```
