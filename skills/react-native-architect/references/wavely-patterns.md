
# Wavely Existing Patterns
This reference documents the established patterns in the Wavely codebase. When architecting new features, these serve as the baseline. Deviate consciously when there's a clear benefit.

## Directory Structure

```
react-native-wavelydx-v2/
├── src/
│   ├── apis/               # API classes extending BaseApi
│   │   ├── BaseApi.ts
│   │   ├── AccountApi.ts
│   │   ├── PatientApi.ts
│   │   └── SessionApi.ts
│   ├── components/         # Reusable UI components
│   │   └── [Name]/
│   │       ├── index.tsx
│   │       └── index.test.tsx
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── usePatient.ts
│   │   └── useSession.ts
│   ├── interfaces/         # TypeScript type definitions
│   │   ├── Account.ts
│   │   ├── Patient.ts
│   │   └── Session.ts
│   ├── navigation/         # React Navigation setup
│   │   └── index.tsx
│   ├── screens/            # Screen components
│   ├── services/           # Core services
│   │   └── LocalStorageService.ts
│   └── state/              # Recoil atoms and selectors
│       ├── accountState.ts
│       ├── kidState.ts
│       └── sessionState.ts
```

## API Layer

### BaseApi Pattern

All API classes extend `BaseApi` which handles:
- Authentication headers (Authorization, x-api-key, device_id)
- Request timeout (15 seconds)
- Error handling
- Token refresh

```typescript
// Existing pattern in apis/BaseApi.ts
class BaseApi {
  protected baseUrl: string;

  protected async get<T>(endpoint: string): Promise<T> {
    // Handles auth headers, timeout, errors
  }

  protected async post<T>(endpoint: string, data: unknown): Promise<T> {
    // ...
  }

  protected getHeaders(): Headers {
    // Returns Authorization, x-api-key, device_id
  }
}

// API classes follow this pattern:
class PatientApi extends BaseApi {
  async get(patientId: string): Promise<Patient> {
    return this.get(`/commercial/patient/${patientId}`);
  }

  async list(accountId: string): Promise<Patient[]> {
    return this.get(`/commercial/patient/patients/${accountId}`);
  }

  async create(data: CreatePatientInput): Promise<Patient> {
    return this.post('/commercial/patient', data);
  }
}
```

### When to Deviate

- **Consider React Query**: If a feature needs complex caching, background refetch, or optimistic updates beyond what the current pattern provides
- **Consider GraphQL**: If the feature requires complex data relationships with over/under-fetching concerns

## State Management

### Recoil Pattern

State files in `src/state/` follow naming convention `*State.ts`:

```typescript
// state/kidState.ts
import { atom, selector } from 'recoil';
import { Kid } from '../interfaces/Kid';

// Atoms for raw data
export const kidListState = atom<Kid[]>({
  key: 'kidListState',
  default: [],
});

export const selectedKidIdState = atom<string | null>({
  key: 'selectedKidIdState',
  default: null,
});

// Selectors for derived data
export const selectedKidSelector = selector<Kid | null>({
  key: 'selectedKidSelector',
  get: ({ get }) => {
    const id = get(selectedKidIdState);
    const kids = get(kidListState);
    return kids.find(k => k.id === id) ?? null;
  },
});
```

### Key Naming Convention

- Simple: `kidListState`, `accountState`
- With prefix for related atoms: `kid/listState`, `kid/selectedId`

### When to Deviate

- **Use atom families**: When storing collections where individual item updates shouldn't re-render the whole list
- **Use Context**: For provider-scoped state (e.g., different themes in different sections)

## Hooks

### Hook Patterns

Hooks in `src/hooks/` encapsulate business logic:

```typescript
// hooks/useAuth.ts
function useAuth() {
  const [account, setAccount] = useRecoilState(accountState);

  const login = useCallback(async (credentials) => {
    const response = await AccountApi.login(credentials);
    setAccount(response.account);
    await LocalStorageService.setToken(response.token);
  }, [setAccount]);

  const logout = useCallback(async () => {
    setAccount(null);
    await LocalStorageService.clearToken();
  }, [setAccount]);

  return {
    account,
    isLoggedIn: !!account,
    login,
    logout,
  };
}
```

### Hook Naming

- Data hooks: `usePatient`, `useKid`, `useSession`
- Auth hooks: `useAuth`, `useCognito`, `useLogin`, `useSignOut`
- Feature hooks: `useClinical`, `useScanning`

## Navigation

### Structure

Multi-role support with separate tab navigators per role:

```typescript
// navigation/index.tsx
function RootNavigator() {
  const role = useUserRole();

  return (
    <Stack.Navigator>
      {!isLoggedIn ? (
        <Stack.Screen name="Auth" component={AuthStack} />
      ) : (
        <Stack.Screen
          name="Main"
          component={getTabNavigatorForRole(role)}
        />
      )}
    </Stack.Navigator>
  );
}

// Roles: Consumer, Clinical, Caregiver, Commercial
```

### Tab Navigator Pattern

Each role has its own TabNavigator with role-specific screens:

```typescript
function ConsumerTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeStack} />
      <Tab.Screen name="Kids" component={KidsStack} />
      <Tab.Screen name="Settings" component={SettingsStack} />
    </Tab.Navigator>
  );
}
```

## Components

### Directory Structure

Each component in its own directory:

```
components/
├── Button/
│   ├── index.tsx      # Main component
│   └── index.test.tsx # Tests
├── PatientCard/
│   ├── index.tsx
│   └── index.test.tsx
```

### Component Pattern

```typescript
// components/PatientCard/index.tsx
import React, { memo } from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface PatientCardProps {
  patient: Patient;
  onPress?: () => void;
}

function PatientCard({ patient, onPress }: PatientCardProps) {
  return (
    <TouchableOpacity onPress={onPress} style={styles.container}>
      <Text style={styles.name}>{patient.name}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { /* ... */ },
  name: { /* ... */ },
});

export default memo(PatientCard);
```

## Testing

### Setup

- Jest with react-native preset
- `react-native-accessibility-engine` for a11y testing
- Config in `jest.config.js`, setup in `jest-setup.js`

### Pattern

```typescript
// components/PatientCard/index.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import PatientCard from './index';

describe('PatientCard', () => {
  const mockPatient = { id: '1', name: 'John Doe' };

  it('renders patient name', () => {
    render(<PatientCard patient={mockPatient} />);
    expect(screen.getByText('John Doe')).toBeTruthy();
  });

  it('calls onPress when tapped', () => {
    const onPress = jest.fn();
    render(<PatientCard patient={mockPatient} onPress={onPress} />);
    fireEvent.press(screen.getByText('John Doe'));
    expect(onPress).toHaveBeenCalled();
  });
});
```

## Services

### LocalStorageService

Wrapper around AsyncStorage:

```typescript
// services/LocalStorageService.ts
class LocalStorageService {
  async getToken(): Promise<string | null> {
    return AsyncStorage.getItem('authToken');
  }

  async setToken(token: string): Promise<void> {
    return AsyncStorage.setItem('authToken', token);
  }

  async clearToken(): Promise<void> {
    return AsyncStorage.removeItem('authToken');
  }
}
```

## Authentication

### AWS Amplify/Cognito

Authentication handled via AWS Amplify:

```typescript
import { Auth } from 'aws-amplify';

// Sign in
await Auth.signIn(email, password);

// Get current user
const user = await Auth.currentAuthenticatedUser();

// Sign out
await Auth.signOut();
```

## wavelydxcmd Package

### Shared Component Pattern

The `@wavely_dev/wavelydxcmd` package exports embeddable components:

```typescript
// In wavelydxcmd package
export function WavelyCMD({
  account_id,
  patient_id,
  goToDashboard,
  onSignOut,
}: WavelyCMDProps) {
  // Self-contained scanning flow
}

// In consumer app
import { WavelyCMD } from '@wavely_dev/wavelydxcmd';

function ScanScreen() {
  return (
    <WavelyCMD
      account_id={accountId}
      patient_id={patientId}
      goToDashboard={() => navigation.navigate('Dashboard')}
      onSignOut={handleSignOut}
    />
  );
}
```

### Local Development with Yalc

```bash
# In wavelydx-cmd
npx yalc publish

# In consumer app
npx yalc link @wavely_dev/wavelydxcmd
```

## Summary: When to Follow vs Deviate

| Pattern | Follow When | Deviate When |
|---------|-------------|--------------|
| BaseApi | Standard CRUD | Complex caching needs (use React Query) |
| Recoil atoms | Simple state | Collections with item-level updates (use atomFamily) |
| Hooks for logic | Always | - |
| Component directories | Always | - |
| Role-based navigation | Multi-role features | Single-role features (simpler structure) |
| LocalStorageService | Simple persistence | Complex offline (use dedicated offline library) |
