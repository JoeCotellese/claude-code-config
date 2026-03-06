
# React Native Testing Patterns
## Test Structure

### File Organization

```
src/components/
├── Button/
│   ├── index.tsx
│   └── index.test.tsx    # Co-located tests
├── PatientCard/
│   ├── index.tsx
│   └── index.test.tsx
```

### Basic Test Template

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import PatientCard from './index';

describe('PatientCard', () => {
  const defaultProps = {
    name: 'John Doe',
    age: 35,
    onPress: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders patient name', () => {
    render(<PatientCard {...defaultProps} />);
    expect(screen.getByText('John Doe')).toBeTruthy();
  });

  it('calls onPress when tapped', () => {
    render(<PatientCard {...defaultProps} />);
    fireEvent.press(screen.getByText('John Doe'));
    expect(defaultProps.onPress).toHaveBeenCalledTimes(1);
  });
});
```

## React Testing Library Queries

### Query Priority (Most to Least Preferred)

```typescript
// 1. Accessible queries (best)
screen.getByRole('button', { name: 'Submit' })
screen.getByLabelText('Email address')
screen.getByPlaceholderText('Enter email')
screen.getByDisplayValue('current value')

// 2. Text queries (good)
screen.getByText('Submit')
screen.getByText(/submit/i)  // Case insensitive regex

// 3. TestID (last resort)
screen.getByTestId('submit-button')
```

### Query Variants

```typescript
// getBy - throws if not found (use for elements that should exist)
const button = screen.getByText('Submit');

// queryBy - returns null if not found (use for asserting absence)
expect(screen.queryByText('Error')).toBeNull();

// findBy - async, waits for element (use for async rendering)
const data = await screen.findByText('Loaded data');

// getAllBy/queryAllBy/findAllBy - for multiple elements
const items = screen.getAllByRole('button');
```

## Testing Components

### Testing User Interactions

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';

describe('LoginForm', () => {
  it('submits form with entered values', async () => {
    const onSubmit = jest.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    // Fill in fields
    fireEvent.changeText(
      screen.getByLabelText('Email'),
      'test@example.com'
    );
    fireEvent.changeText(
      screen.getByLabelText('Password'),
      'password123'
    );

    // Submit
    fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows validation error for invalid email', async () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    fireEvent.changeText(screen.getByLabelText('Email'), 'invalid');
    fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByText('Invalid email address')).toBeTruthy();
  });
});
```

### Testing Conditional Rendering

```typescript
describe('LoadingState', () => {
  it('shows loading indicator when loading', () => {
    render(<DataView loading={true} data={null} />);
    expect(screen.getByTestId('loading-spinner')).toBeTruthy();
    expect(screen.queryByText('Data loaded')).toBeNull();
  });

  it('shows data when loaded', () => {
    render(<DataView loading={false} data={{ name: 'Test' }} />);
    expect(screen.queryByTestId('loading-spinner')).toBeNull();
    expect(screen.getByText('Test')).toBeTruthy();
  });

  it('shows error state', () => {
    render(<DataView loading={false} data={null} error="Failed to load" />);
    expect(screen.getByText('Failed to load')).toBeTruthy();
  });
});
```

### Testing Lists

```typescript
describe('PatientList', () => {
  const patients = [
    { id: '1', name: 'John Doe' },
    { id: '2', name: 'Jane Smith' },
  ];

  it('renders all patients', () => {
    render(<PatientList patients={patients} />);
    expect(screen.getAllByRole('button')).toHaveLength(2);
    expect(screen.getByText('John Doe')).toBeTruthy();
    expect(screen.getByText('Jane Smith')).toBeTruthy();
  });

  it('calls onSelect with patient id when tapped', () => {
    const onSelect = jest.fn();
    render(<PatientList patients={patients} onSelect={onSelect} />);

    fireEvent.press(screen.getByText('Jane Smith'));
    expect(onSelect).toHaveBeenCalledWith('2');
  });
});
```

## Testing Hooks

### Custom Hook Testing

```typescript
import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useToggle } from './useToggle';

describe('useToggle', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useToggle(false));
    expect(result.current.value).toBe(false);
  });

  it('toggles value', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current.toggle();
    });

    expect(result.current.value).toBe(true);
  });
});
```

### Testing Async Hooks

```typescript
import { renderHook, waitFor } from '@testing-library/react-native';
import { usePatient } from './usePatient';
import { PatientApi } from '../apis/PatientApi';

jest.mock('../apis/PatientApi');

describe('usePatient', () => {
  it('fetches patient data', async () => {
    const mockPatient = { id: '1', name: 'John Doe' };
    (PatientApi.get as jest.Mock).mockResolvedValue(mockPatient);

    const { result } = renderHook(() => usePatient('1'));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.patient).toEqual(mockPatient);
    expect(result.current.error).toBeNull();
  });

  it('handles error', async () => {
    const error = new Error('Failed to fetch');
    (PatientApi.get as jest.Mock).mockRejectedValue(error);

    const { result } = renderHook(() => usePatient('1'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.patient).toBeNull();
    expect(result.current.error).toEqual(error);
  });
});
```

## Mocking

### Mocking Modules

```typescript
// Mock entire module
jest.mock('../apis/PatientApi');

// Mock with implementation
jest.mock('../apis/PatientApi', () => ({
  PatientApi: {
    get: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
  },
}));

// Mock default export
jest.mock('../services/Analytics', () => ({
  __esModule: true,
  default: {
    track: jest.fn(),
  },
}));
```

### Mocking React Native Modules

```typescript
// jest-setup.js or at top of test file
jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');

jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

jest.mock('react-native-config', () => ({
  API_URL: 'https://test-api.example.com',
}));
```

### Mocking Navigation

```typescript
const mockNavigate = jest.fn();
const mockGoBack = jest.fn();

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
    goBack: mockGoBack,
  }),
  useRoute: () => ({
    params: { patientId: '123' },
  }),
}));

describe('PatientScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('navigates to edit screen', () => {
    render(<PatientScreen />);
    fireEvent.press(screen.getByText('Edit'));
    expect(mockNavigate).toHaveBeenCalledWith('EditPatient', { patientId: '123' });
  });
});
```

### Mocking Recoil State

```typescript
import { RecoilRoot } from 'recoil';
import { accountState, kidListState } from '../state';

const mockAccount = { id: '1', email: 'test@example.com' };
const mockKids = [{ id: 'k1', name: 'Child 1' }];

function renderWithRecoil(ui: React.ReactElement) {
  return render(
    <RecoilRoot
      initializeState={({ set }) => {
        set(accountState, mockAccount);
        set(kidListState, mockKids);
      }}
    >
      {ui}
    </RecoilRoot>
  );
}

describe('Dashboard', () => {
  it('shows account info', () => {
    renderWithRecoil(<Dashboard />);
    expect(screen.getByText('test@example.com')).toBeTruthy();
  });
});
```

## Testing Async Operations

### Waiting for Updates

```typescript
import { render, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react-native';

it('loads and displays data', async () => {
  render(<DataScreen />);

  // Wait for loading to disappear
  await waitForElementToBeRemoved(() => screen.queryByTestId('loading'));

  // Or wait for data to appear
  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeTruthy();
  });
});

it('handles async form submission', async () => {
  const onSubmit = jest.fn().mockResolvedValue({ success: true });
  render(<Form onSubmit={onSubmit} />);

  fireEvent.press(screen.getByText('Submit'));

  // Wait for success message
  expect(await screen.findByText('Submitted successfully')).toBeTruthy();
});
```

### Testing Timers

```typescript
describe('AutoSave', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('auto-saves after 5 seconds of inactivity', () => {
    const onSave = jest.fn();
    render(<AutoSaveForm onSave={onSave} />);

    fireEvent.changeText(screen.getByLabelText('Notes'), 'Some text');

    // Fast-forward 5 seconds
    jest.advanceTimersByTime(5000);

    expect(onSave).toHaveBeenCalled();
  });
});
```

## Snapshot Testing

Use sparingly - for stable UI components.

```typescript
describe('StaticComponent', () => {
  it('matches snapshot', () => {
    const tree = render(<Badge label="New" variant="primary" />);
    expect(tree.toJSON()).toMatchSnapshot();
  });
});
```

## Accessibility Testing

```typescript
// Using react-native-accessibility-engine (from your project)
import { axe } from 'react-native-accessibility-engine';

describe('Button accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(
      <Button title="Submit" onPress={() => {}} />
    );
    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it('has correct accessibility props', () => {
    render(<Button title="Submit" onPress={() => {}} />);
    const button = screen.getByRole('button', { name: 'Submit' });
    expect(button).toBeTruthy();
  });
});
```

## Testing Best Practices

### Do's

```typescript
// ✅ Test behavior, not implementation
it('disables submit when form is invalid', () => {
  render(<Form />);
  const submitButton = screen.getByRole('button', { name: 'Submit' });
  expect(submitButton.props.accessibilityState.disabled).toBe(true);
});

// ✅ Use accessible queries
screen.getByRole('button', { name: 'Submit' });
screen.getByLabelText('Email');

// ✅ Test error states
it('shows error message on API failure', async () => {
  mockApi.mockRejectedValue(new Error('Network error'));
  render(<DataScreen />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Network error');
});

// ✅ Group related tests
describe('when user is logged in', () => {
  beforeEach(() => {
    mockAuth.isLoggedIn = true;
  });

  it('shows dashboard', () => { /* ... */ });
  it('shows logout button', () => { /* ... */ });
});
```

### Don'ts

```typescript
// ❌ Don't test implementation details
expect(component.state.isLoading).toBe(true);  // Testing internal state

// ❌ Don't use testID as primary query
screen.getByTestId('submit-btn');  // Use getByRole instead

// ❌ Don't test third-party libraries
it('calls Recoil setter', () => {
  expect(setRecoilState).toHaveBeenCalled();  // Too coupled
});

// ❌ Don't write tests that pass regardless of component behavior
it('renders', () => {
  render(<MyComponent />);
  // No assertions!
});
```

## Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  // ...
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',  // Re-exports
    '!src/**/*.stories.{ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```
