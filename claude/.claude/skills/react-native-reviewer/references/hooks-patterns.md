# ABOUTME: React Hooks patterns and best practices reference for code review
# ABOUTME: Covers rules of hooks, dependency arrays, memoization, and common anti-patterns

# React Hooks Patterns

## Rules of Hooks (Enforced by ESLint)

1. **Only call hooks at the top level** - Never inside loops, conditions, or nested functions
2. **Only call hooks from React functions** - Components or custom hooks, not regular JS functions

## useState Patterns

### Good Patterns

```typescript
// Lazy initialization for expensive computations
const [data, setData] = useState(() => computeExpensiveInitialValue());

// Functional updates when new state depends on previous
setCount(prevCount => prevCount + 1);

// Object state with spread
setUser(prev => ({ ...prev, name: newName }));
```

### Anti-Patterns

```typescript
// ❌ Multiple useState for related data - use object or useReducer
const [firstName, setFirstName] = useState('');
const [lastName, setLastName] = useState('');
const [email, setEmail] = useState('');

// ✅ Better: group related state
const [formData, setFormData] = useState({ firstName: '', lastName: '', email: '' });

// ❌ Derived state stored in useState
const [items, setItems] = useState([]);
const [filteredItems, setFilteredItems] = useState([]); // Derived!

// ✅ Better: compute during render
const filteredItems = useMemo(() => items.filter(predicate), [items, predicate]);

// ❌ Props copied into state (unless intentionally "seeding")
const [value, setValue] = useState(props.initialValue);
// This won't update when props.initialValue changes!
```

## useEffect Patterns

### Dependency Array Rules

```typescript
// Every value from component scope used inside effect must be in deps
useEffect(() => {
  fetchData(userId, filters); // Both must be in deps
}, [userId, filters]);

// Functions should be memoized or defined inside useEffect
useEffect(() => {
  const fetchData = async () => { /* ... */ };
  fetchData();
}, [userId]); // Function defined inside, only external deps needed
```

### Common Anti-Patterns

```typescript
// ❌ Missing dependencies (stale closure)
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1); // count is stale!
  }, 1000);
  return () => clearInterval(interval);
}, []); // count missing from deps

// ✅ Fix with functional update
useEffect(() => {
  const interval = setInterval(() => {
    setCount(c => c + 1); // No external dependency
  }, 1000);
  return () => clearInterval(interval);
}, []);

// ❌ Object/array in deps causing infinite loops
useEffect(() => {
  doSomething(options);
}, [{ sortBy: 'name' }]); // New object every render!

// ✅ Fix: memoize or use primitive deps
const options = useMemo(() => ({ sortBy }), [sortBy]);
useEffect(() => {
  doSomething(options);
}, [options]);

// ❌ Fetching without cleanup/cancellation
useEffect(() => {
  fetchData().then(setData);
}, [id]);

// ✅ With cleanup
useEffect(() => {
  let cancelled = false;
  fetchData().then(data => {
    if (!cancelled) setData(data);
  });
  return () => { cancelled = true; };
}, [id]);
```

### Effect Categories

1. **Synchronization effects** - Sync with external system (subscriptions, event listeners)
2. **Data fetching** - Consider React Query or similar instead
3. **DOM mutations** - Use useLayoutEffect if measuring/mutating DOM synchronously

## useMemo and useCallback

### When to Use useMemo

```typescript
// ✅ Expensive computations
const sortedItems = useMemo(() =>
  items.slice().sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// ✅ Referential equality for objects/arrays passed to memoized children
const style = useMemo(() => ({ color: theme.primary }), [theme.primary]);

// ❌ Don't memoize cheap operations
const fullName = useMemo(() => `${first} ${last}`, [first, last]); // Overkill
const fullName = `${first} ${last}`; // Just compute it
```

### When to Use useCallback

```typescript
// ✅ Callbacks passed to memoized children
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);

// ✅ Callbacks used in useEffect dependencies
const fetchData = useCallback(async () => {
  const result = await api.get(endpoint);
  setData(result);
}, [endpoint]);

useEffect(() => {
  fetchData();
}, [fetchData]);

// ❌ Don't useCallback for inline handlers on native elements
<Button onPress={useCallback(() => setOpen(true), [])} /> // Unnecessary
<Button onPress={() => setOpen(true)} /> // Fine
```

## Custom Hooks

### Naming Convention
- Always prefix with `use`
- Name should describe what the hook does: `useAuth`, `usePatient`, `useFetch`

### Good Custom Hook Patterns

```typescript
// Encapsulate complex state logic
function useToggle(initial = false) {
  const [value, setValue] = useState(initial);
  const toggle = useCallback(() => setValue(v => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);
  return { value, toggle, setTrue, setFalse };
}

// Abstract data fetching
function usePatient(patientId: string) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    PatientApi.get(patientId)
      .then(data => { if (!cancelled) setPatient(data); })
      .catch(err => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [patientId]);

  return { patient, loading, error };
}
```

### Anti-Patterns

```typescript
// ❌ Hooks that do too much - split into focused hooks
function useEverything() {
  // Auth + API + Navigation + State = too much
}

// ❌ Returning unstable references
function useBad() {
  return { handler: () => {} }; // New function every call!
}

// ✅ Memoize returned callbacks
function useGood() {
  const handler = useCallback(() => {}, []);
  return { handler };
}
```

## useRef Patterns

```typescript
// ✅ Mutable values that don't trigger re-render
const renderCount = useRef(0);
useEffect(() => { renderCount.current++; });

// ✅ Storing previous values
function usePrevious<T>(value: T) {
  const ref = useRef<T>();
  useEffect(() => { ref.current = value; });
  return ref.current;
}

// ✅ Accessing imperative DOM/component APIs
const inputRef = useRef<TextInput>(null);
inputRef.current?.focus();

// ❌ Using ref.current in dependency arrays (won't trigger updates)
useEffect(() => {
  console.log(ref.current); // This won't re-run when ref.current changes
}, [ref.current]); // ESLint will warn
```

## React Native Specific

### useEffect Cleanup in Navigation

```typescript
// Screen may stay mounted when navigating away
useEffect(() => {
  const unsubscribe = navigation.addListener('focus', () => {
    fetchData();
  });
  return unsubscribe;
}, [navigation]);
```

### Avoiding Hooks in Conditional Rendering

```typescript
// ❌ Hook called conditionally
function Screen({ showDetails }) {
  if (!showDetails) return null;
  const [data, setData] = useState(); // Called conditionally!
}

// ✅ Move condition after hooks
function Screen({ showDetails }) {
  const [data, setData] = useState();
  if (!showDetails) return null;
  // ...
}
```
