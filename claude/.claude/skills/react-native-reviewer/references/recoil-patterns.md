# ABOUTME: Recoil state management patterns and best practices reference
# ABOUTME: Covers atom design, selectors, performance, and common anti-patterns

# Recoil State Management Patterns

## Atom Design

### Naming Conventions

```typescript
// Atoms: describe the data, suffix with State or Atom
export const accountState = atom<Account | null>({...});
export const kidListState = atom<Kid[]>({...});
export const isLoadingAtom = atom<boolean>({...});

// Selectors: describe derived data or action
export const currentKidSelector = selector<Kid | null>({...});
export const sortedKidsSelector = selector<Kid[]>({...});
```

### Good Atom Patterns

```typescript
// ✅ Atoms should be minimal and focused
export const accountState = atom<Account | null>({
  key: 'accountState',
  default: null,
});

// ✅ Use atom families for collections indexed by ID
export const patientState = atomFamily<Patient | null, string>({
  key: 'patientState',
  default: null,
});

// ✅ Separate loading/error state from data
export const patientsLoadingState = atom<boolean>({
  key: 'patientsLoadingState',
  default: false,
});
```

### Anti-Patterns

```typescript
// ❌ Putting too much in one atom
export const appState = atom({
  key: 'appState',
  default: {
    user: null,
    patients: [],
    settings: {},
    ui: { modal: null, loading: false },
    // Everything in one place = unnecessary re-renders
  },
});

// ✅ Split into focused atoms
export const userState = atom({...});
export const patientsState = atom({...});
export const settingsState = atom({...});
export const modalState = atom({...});

// ❌ Duplicate keys (runtime error)
const atom1 = atom({ key: 'myKey', default: 1 });
const atom2 = atom({ key: 'myKey', default: 2 }); // Conflict!

// ✅ Use consistent key naming: 'featureName/atomName'
const atom1 = atom({ key: 'auth/userState', default: null });
const atom2 = atom({ key: 'patients/listState', default: [] });
```

## Selector Patterns

### Derived State

```typescript
// ✅ Compute derived state with selectors (not useState)
export const activeKidsSelector = selector<Kid[]>({
  key: 'activeKidsSelector',
  get: ({ get }) => {
    const kids = get(kidListState);
    return kids.filter(kid => kid.isActive);
  },
});

// ✅ Combine multiple atoms
export const dashboardDataSelector = selector({
  key: 'dashboardDataSelector',
  get: ({ get }) => {
    const account = get(accountState);
    const kids = get(kidListState);
    const sessions = get(recentSessionsState);
    return { account, kids, sessions };
  },
});
```

### Async Selectors

```typescript
// ✅ Async data fetching with selectors
export const patientDetailsSelector = selectorFamily<Patient, string>({
  key: 'patientDetailsSelector',
  get: (patientId) => async ({ get }) => {
    // Can depend on other atoms
    const token = get(authTokenState);
    const response = await PatientApi.get(patientId, token);
    return response;
  },
});

// Usage with Suspense
function PatientCard({ patientId }) {
  const patient = useRecoilValue(patientDetailsSelector(patientId));
  return <Text>{patient.name}</Text>;
}

// Wrap with Suspense
<Suspense fallback={<Loading />}>
  <PatientCard patientId={id} />
</Suspense>
```

### Writable Selectors

```typescript
// ✅ Transform data on read and write
export const temperatureState = atom({ key: 'tempC', default: 20 });

export const temperatureFahrenheit = selector<number>({
  key: 'tempF',
  get: ({ get }) => get(temperatureState) * 9/5 + 32,
  set: ({ set }, newValue) => {
    if (typeof newValue === 'number') {
      set(temperatureState, (newValue - 32) * 5/9);
    }
  },
});
```

## Hooks Usage

### Reading State

```typescript
// useRecoilValue - read only
const account = useRecoilValue(accountState);

// useRecoilState - read and write (like useState)
const [kids, setKids] = useRecoilState(kidListState);

// useSetRecoilState - write only (doesn't subscribe to changes)
const setAccount = useSetRecoilState(accountState);

// useResetRecoilState - reset to default
const resetAccount = useResetRecoilState(accountState);
```

### When to Use Each

```typescript
// ✅ Use useRecoilValue when only reading
function DisplayName() {
  const account = useRecoilValue(accountState); // Only reads
  return <Text>{account?.name}</Text>;
}

// ✅ Use useSetRecoilState when only writing (avoids re-render on state change)
function LogoutButton() {
  const setAccount = useSetRecoilState(accountState); // Only writes
  const handleLogout = () => setAccount(null);
  return <Button onPress={handleLogout} title="Logout" />;
}

// ✅ Use useRecoilState when both reading and writing
function EditName() {
  const [account, setAccount] = useRecoilState(accountState);
  // ...
}
```

## Performance Patterns

### Minimize Re-renders

```typescript
// ❌ Reading entire state when only needing part
function KidCount() {
  const kids = useRecoilValue(kidListState); // Re-renders on any kid change
  return <Text>{kids.length}</Text>;
}

// ✅ Use selector for derived value
const kidCountSelector = selector({
  key: 'kidCountSelector',
  get: ({ get }) => get(kidListState).length,
});

function KidCount() {
  const count = useRecoilValue(kidCountSelector); // Only re-renders when count changes
  return <Text>{count}</Text>;
}
```

### Atom Families for Collections

```typescript
// ❌ One atom with array (all consumers re-render on any change)
const allPatientsState = atom<Patient[]>({...});

// ✅ Atom family + ID list (targeted re-renders)
const patientIdsState = atom<string[]>({
  key: 'patientIdsState',
  default: [],
});

const patientState = atomFamily<Patient | null, string>({
  key: 'patientState',
  default: null,
});

// Component only re-renders when its specific patient changes
function PatientRow({ patientId }) {
  const patient = useRecoilValue(patientState(patientId));
  return <Text>{patient?.name}</Text>;
}
```

### Batching Updates

```typescript
// ✅ Use useRecoilCallback for complex updates
const updateMultiple = useRecoilCallback(({ set }) => (newData) => {
  set(atom1, newData.value1);
  set(atom2, newData.value2);
  set(atom3, newData.value3);
  // All updates batched into single render
}, []);
```

## State File Organization

### Recommended Structure

```
src/state/
├── accountState.ts      # Account-related atoms and selectors
├── kidState.ts          # Kid/patient atoms and selectors
├── sessionState.ts      # Session/scan atoms and selectors
├── uiState.ts           # UI state (modals, loading, etc.)
└── index.ts             # Re-exports all state
```

### File Template

```typescript
// src/state/kidState.ts
import { atom, selector, atomFamily } from 'recoil';
import { Kid } from '../interfaces/Kid';

// Atoms
export const kidListState = atom<Kid[]>({
  key: 'kid/listState',
  default: [],
});

export const selectedKidIdState = atom<string | null>({
  key: 'kid/selectedIdState',
  default: null,
});

// Selectors
export const selectedKidSelector = selector<Kid | null>({
  key: 'kid/selectedSelector',
  get: ({ get }) => {
    const id = get(selectedKidIdState);
    const kids = get(kidListState);
    return kids.find(k => k.id === id) ?? null;
  },
});
```

## Common Mistakes

### Stale Closures

```typescript
// ❌ Stale closure in callback
function BadExample() {
  const kids = useRecoilValue(kidListState);

  const handleSave = () => {
    // kids might be stale when this runs
    saveKids(kids);
  };
}

// ✅ Use useRecoilCallback
function GoodExample() {
  const handleSave = useRecoilCallback(({ snapshot }) => async () => {
    const kids = await snapshot.getPromise(kidListState);
    saveKids(kids);
  }, []);
}
```

### Circular Dependencies

```typescript
// ❌ Selector A depends on B, B depends on A
const selectorA = selector({
  key: 'A',
  get: ({ get }) => get(selectorB) + 1, // Circular!
});

const selectorB = selector({
  key: 'B',
  get: ({ get }) => get(selectorA) + 1, // Circular!
});

// ✅ Break the cycle with atoms or restructure
```

### Effects for Side Effects

```typescript
// ✅ Use atom effects for persistence, logging, sync
export const settingsState = atom({
  key: 'settingsState',
  default: {},
  effects: [
    // Persist to AsyncStorage
    ({ onSet, setSelf }) => {
      // Load initial value
      AsyncStorage.getItem('settings').then(saved => {
        if (saved) setSelf(JSON.parse(saved));
      });

      // Save on change
      onSet(newValue => {
        AsyncStorage.setItem('settings', JSON.stringify(newValue));
      });
    },
  ],
});
```
