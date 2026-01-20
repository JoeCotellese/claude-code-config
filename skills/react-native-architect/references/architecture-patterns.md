# ABOUTME: React Native architecture patterns for component hierarchy and screen structure
# ABOUTME: Covers composition strategies, smart/dumb components, and feature organization

# Architecture Patterns

## Component Hierarchy

### Screen → Container → Presentational Pattern

```
Screen (navigation entry point)
└── Container (data fetching, state management)
    ├── Presentational (pure UI, receives props)
    ├── Presentational
    └── Container (nested if complex)
        └── Presentational
```

**Screen Components**
- Entry point from navigation
- Handles route params
- Sets up screen-level providers/context
- Minimal logic - delegates to containers

```typescript
// screens/PatientDetailScreen.tsx
function PatientDetailScreen() {
  const route = useRoute<PatientDetailRouteProp>();
  const { patientId } = route.params;

  return (
    <SafeAreaView style={styles.container}>
      <PatientDetailContainer patientId={patientId} />
    </SafeAreaView>
  );
}
```

**Container Components**
- Fetch data (hooks, Recoil, API calls)
- Manage local state
- Handle business logic
- Pass data down to presentational

```typescript
// containers/PatientDetailContainer.tsx
function PatientDetailContainer({ patientId }: Props) {
  const { patient, loading, error } = usePatient(patientId);
  const [isEditing, setIsEditing] = useState(false);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorState error={error} />;

  return (
    <PatientDetail
      patient={patient}
      isEditing={isEditing}
      onEdit={() => setIsEditing(true)}
    />
  );
}
```

**Presentational Components**
- Pure UI rendering
- Receive all data via props
- No direct state management hooks (except UI state like `useState` for accordion)
- Easily testable and reusable

```typescript
// components/PatientDetail/index.tsx
function PatientDetail({ patient, isEditing, onEdit }: Props) {
  return (
    <View>
      <Text>{patient.name}</Text>
      <Button title="Edit" onPress={onEdit} />
    </View>
  );
}
```

## Feature-Based Organization

### Flat Structure (Small Apps)

```
src/
├── components/          # Shared UI components
├── screens/            # All screens flat
├── hooks/              # All hooks flat
├── state/              # All Recoil atoms
└── apis/               # All API classes
```

### Feature-Based Structure (Growing Apps)

```
src/
├── features/
│   ├── auth/
│   │   ├── screens/
│   │   │   ├── LoginScreen.tsx
│   │   │   └── SignUpScreen.tsx
│   │   ├── components/
│   │   │   ├── LoginForm/
│   │   │   └── SocialButtons/
│   │   ├── hooks/
│   │   │   ├── useLogin.ts
│   │   │   └── useAuth.ts
│   │   ├── state/
│   │   │   └── authState.ts
│   │   └── index.ts        # Public exports
│   ├── patients/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── state/
│   └── scanning/
├── shared/
│   ├── components/         # Cross-feature UI
│   ├── hooks/              # Cross-feature hooks
│   ├── utils/              # Utilities
│   └── services/           # Core services
└── navigation/
```

### When to Use Each

| Criteria | Flat | Feature-Based |
|----------|------|---------------|
| Team size | 1-3 devs | 3+ devs |
| Feature count | < 10 screens | 10+ screens |
| Code ownership | Shared | Feature teams |
| Reuse pattern | High cross-feature | Low cross-feature |

## Composition Patterns

### Compound Components

For complex UI with multiple related parts:

```typescript
// Usage
<Card>
  <Card.Header>
    <Card.Title>Patient Info</Card.Title>
    <Card.Actions>
      <IconButton name="edit" />
    </Card.Actions>
  </Card.Header>
  <Card.Body>
    <PatientInfo patient={patient} />
  </Card.Body>
  <Card.Footer>
    <Button title="View Details" />
  </Card.Footer>
</Card>

// Implementation
function Card({ children }) {
  return <View style={styles.card}>{children}</View>;
}

Card.Header = function CardHeader({ children }) {
  return <View style={styles.header}>{children}</View>;
};

Card.Title = function CardTitle({ children }) {
  return <Text style={styles.title}>{children}</Text>;
};
// ... etc
```

### Render Props

For flexible data display:

```typescript
// Reusable data fetcher
function PatientLoader({ patientId, children, loading, error }) {
  const state = usePatient(patientId);

  if (state.loading) return loading ?? <ActivityIndicator />;
  if (state.error) return error?.(state.error) ?? <Text>Error</Text>;

  return children(state.patient);
}

// Usage - caller controls rendering
<PatientLoader patientId={id}>
  {(patient) => <PatientCard patient={patient} />}
</PatientLoader>
```

### Slots Pattern

For layouts with pluggable sections:

```typescript
interface ScreenLayoutProps {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

function ScreenLayout({ header, footer, children }: ScreenLayoutProps) {
  return (
    <View style={styles.container}>
      {header && <View style={styles.header}>{header}</View>}
      <ScrollView style={styles.content}>{children}</ScrollView>
      {footer && <View style={styles.footer}>{footer}</View>}
    </View>
  );
}

// Usage
<ScreenLayout
  header={<Header title="Patients" />}
  footer={<TabBar />}
>
  <PatientList />
</ScreenLayout>
```

## Screen Patterns

### List → Detail Pattern

```
PatientListScreen
    │
    │ onPress(patientId)
    ▼
PatientDetailScreen
    │
    │ onEdit()
    ▼
PatientEditScreen
```

```typescript
// Navigation setup
<Stack.Navigator>
  <Stack.Screen name="PatientList" component={PatientListScreen} />
  <Stack.Screen name="PatientDetail" component={PatientDetailScreen} />
  <Stack.Screen name="PatientEdit" component={PatientEditScreen} />
</Stack.Navigator>

// PatientListScreen
function PatientListScreen() {
  const navigation = useNavigation();

  const handlePatientPress = (patientId: string) => {
    navigation.navigate('PatientDetail', { patientId });
  };

  return <PatientList onPatientPress={handlePatientPress} />;
}
```

### Multi-Step Form / Wizard Pattern

```
Step1Screen ──► Step2Screen ──► Step3Screen ──► ConfirmationScreen
     │              │              │
     └──────────────┴──────────────┘
              Shared form state (Recoil or Context)
```

```typescript
// Shared form state
const wizardFormState = atom({
  key: 'wizardFormState',
  default: {
    step1: {},
    step2: {},
    step3: {},
  },
});

// Each step updates its portion
function Step1Screen() {
  const [form, setForm] = useRecoilState(wizardFormState);
  const navigation = useNavigation();

  const handleNext = (data: Step1Data) => {
    setForm(prev => ({ ...prev, step1: data }));
    navigation.navigate('Step2');
  };

  return <Step1Form initialData={form.step1} onSubmit={handleNext} />;
}
```

### Tab + Stack Pattern

```
TabNavigator
├── HomeTab (Stack)
│   ├── HomeScreen
│   └── NotificationsScreen
├── PatientsTab (Stack)
│   ├── PatientListScreen
│   ├── PatientDetailScreen
│   └── PatientEditScreen
└── SettingsTab (Stack)
    ├── SettingsScreen
    └── ProfileScreen
```

## Error Boundaries

### Placement Strategy

```
App
└── RootErrorBoundary (catches catastrophic errors)
    └── NavigationContainer
        └── TabNavigator
            └── Stack
                └── ScreenErrorBoundary (per-screen recovery)
                    └── Screen
                        └── ComponentErrorBoundary (optional, for risky components)
                            └── RiskyComponent
```

```typescript
// Screen-level boundary
function PatientDetailScreen() {
  return (
    <ScreenErrorBoundary
      fallback={<ScreenError onRetry={() => navigation.goBack()} />}
    >
      <PatientDetailContainer />
    </ScreenErrorBoundary>
  );
}
```

## Module Boundaries

### Public API Pattern

Each feature exposes a clean public API via `index.ts`:

```typescript
// features/patients/index.ts

// Screens (for navigation registration)
export { PatientListScreen } from './screens/PatientListScreen';
export { PatientDetailScreen } from './screens/PatientDetailScreen';

// Hooks (for cross-feature use)
export { usePatient } from './hooks/usePatient';
export { usePatientList } from './hooks/usePatientList';

// Types
export type { Patient, PatientListItem } from './types';

// Do NOT export:
// - Internal components
// - Internal state atoms
// - Internal utilities
```

### Import Rules

```typescript
// ✅ Import from feature's public API
import { usePatient, Patient } from '@features/patients';

// ❌ Don't reach into feature internals
import { usePatient } from '@features/patients/hooks/usePatient';
import { patientState } from '@features/patients/state/patientState';
```

## Decision Framework

### New Feature Checklist

1. **Screens needed?** List all screens and their relationships
2. **Shared state?** What data is shared across screens?
3. **API calls?** What endpoints, caching strategy?
4. **Reusable components?** What UI is feature-specific vs shared?
5. **Navigation flow?** Stack, tabs, modals?
6. **Error states?** How to handle failures at each level?
7. **Loading states?** Skeleton, spinner, optimistic?
