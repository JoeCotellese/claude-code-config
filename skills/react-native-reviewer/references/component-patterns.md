
# React Native Component Patterns
## Component Structure

### File Organization

```
src/components/
├── Button/
│   ├── index.tsx        # Main component export
│   ├── index.test.tsx   # Tests
│   ├── styles.ts        # StyleSheet (optional)
│   └── types.ts         # TypeScript interfaces (if complex)
├── PatientCard/
│   ├── index.tsx
│   └── index.test.tsx
```

### Basic Component Template

```typescript
// src/components/PatientCard/index.tsx
import React, { memo } from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface PatientCardProps {
  name: string;
  age: number;
  onPress?: () => void;
}

function PatientCard({ name, age, onPress }: PatientCardProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.name}>{name}</Text>
      <Text style={styles.age}>{age} years old</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
  },
  name: {
    fontSize: 18,
    fontWeight: '600',
  },
  age: {
    fontSize: 14,
    color: '#666',
  },
});

export default memo(PatientCard);
```

## Props Design

### Good Props Patterns

```typescript
// ✅ Explicit, typed props
interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  disabled?: boolean;
  loading?: boolean;
}

// ✅ Render props for flexible composition
interface ListProps<T> {
  data: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

// ✅ Children for composition
interface CardProps {
  children: React.ReactNode;
  title?: string;
}
```

### Anti-Patterns

```typescript
// ❌ Boolean props for variants
<Button primary />
<Button secondary />
<Button ghost />

// ✅ Use union type for variants
<Button variant="primary" />

// ❌ Too many props (component doing too much)
<UserWidget
  name={name}
  email={email}
  avatar={avatar}
  onEdit={handleEdit}
  onDelete={handleDelete}
  showBadge={true}
  badgeCount={3}
  isOnline={true}
  lastSeen={date}
  // ... 15 more props
/>

// ✅ Split into focused components or use composition
<UserWidget user={user}>
  <UserBadge count={3} />
  <OnlineStatus isOnline={true} lastSeen={date} />
  <UserActions onEdit={handleEdit} onDelete={handleDelete} />
</UserWidget>

// ❌ Passing callbacks with inline arrow functions to children
<List
  data={items}
  renderItem={(item) => (
    <Item
      onPress={() => handlePress(item.id)} // New function every render
    />
  )}
/>

// ✅ Extract to component or memoize
function ItemRow({ item, onPress }) {
  const handlePress = useCallback(() => onPress(item.id), [item.id, onPress]);
  return <Item onPress={handlePress} />;
}
```

## Composition Patterns

### Compound Components

```typescript
// Header with composable parts
function Header({ children }) {
  return <View style={styles.header}>{children}</View>;
}

Header.Left = function HeaderLeft({ children }) {
  return <View style={styles.left}>{children}</View>;
};

Header.Title = function HeaderTitle({ children }) {
  return <Text style={styles.title}>{children}</Text>;
};

Header.Right = function HeaderRight({ children }) {
  return <View style={styles.right}>{children}</View>;
};

// Usage
<Header>
  <Header.Left>
    <BackButton />
  </Header.Left>
  <Header.Title>Patient Details</Header.Title>
  <Header.Right>
    <MenuButton />
  </Header.Right>
</Header>
```

### Render Props

```typescript
// Flexible data display
interface DataLoaderProps<T> {
  fetch: () => Promise<T>;
  children: (data: T) => React.ReactNode;
  loading?: React.ReactNode;
  error?: (err: Error) => React.ReactNode;
}

function DataLoader<T>({ fetch, children, loading, error }: DataLoaderProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [err, setErr] = useState<Error | null>(null);

  useEffect(() => {
    fetch()
      .then(setData)
      .catch(setErr)
      .finally(() => setIsLoading(false));
  }, [fetch]);

  if (isLoading) return loading ?? <ActivityIndicator />;
  if (err) return error?.(err) ?? <Text>Error</Text>;
  if (!data) return null;
  return <>{children(data)}</>;
}

// Usage
<DataLoader fetch={fetchPatient}>
  {(patient) => <PatientCard patient={patient} />}
</DataLoader>
```

### HOCs (Higher-Order Components)

```typescript
// Use sparingly - hooks are often better
function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
      return <LoginPrompt />;
    }

    return <WrappedComponent {...props} />;
  };
}

// Prefer hooks when possible
function ProtectedScreen() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginPrompt />;
  }

  return <ActualContent />;
}
```

## Render Optimization

### When to Use memo()

```typescript
// ✅ Components receiving complex props that change infrequently
const PatientRow = memo(function PatientRow({ patient, onSelect }) {
  return (
    <TouchableOpacity onPress={() => onSelect(patient.id)}>
      <Text>{patient.name}</Text>
    </TouchableOpacity>
  );
});

// ✅ List items (especially in FlatList)
const ListItem = memo(function ListItem({ item }) {
  return <View>...</View>;
});

// ❌ Don't memo everything - it has overhead
const SimpleText = memo(({ text }) => <Text>{text}</Text>); // Overkill
```

### Custom Comparison

```typescript
// Custom equality check for memo
const PatientCard = memo(
  function PatientCard({ patient }) {
    return <View>...</View>;
  },
  (prevProps, nextProps) => {
    // Return true if props are equal (skip re-render)
    return prevProps.patient.id === nextProps.patient.id &&
           prevProps.patient.updatedAt === nextProps.patient.updatedAt;
  }
);
```

### Avoiding Re-renders

```typescript
// ❌ Inline objects/arrays cause re-renders
function Parent() {
  return (
    <Child
      style={{ padding: 10 }}  // New object every render
      items={[1, 2, 3]}        // New array every render
    />
  );
}

// ✅ Define outside component or memoize
const childStyle = { padding: 10 };
const defaultItems = [1, 2, 3];

function Parent() {
  return <Child style={childStyle} items={defaultItems} />;
}

// Or with useMemo for dynamic values
function Parent({ padding }) {
  const style = useMemo(() => ({ padding }), [padding]);
  return <Child style={style} />;
}
```

## Conditional Rendering

### Good Patterns

```typescript
// ✅ Early returns for guard clauses
function PatientDetails({ patient }) {
  if (!patient) {
    return <EmptyState />;
  }

  return (
    <View>
      <Text>{patient.name}</Text>
    </View>
  );
}

// ✅ Ternary for simple conditions
function Status({ isActive }) {
  return (
    <Text style={isActive ? styles.active : styles.inactive}>
      {isActive ? 'Active' : 'Inactive'}
    </Text>
  );
}

// ✅ && for conditional rendering (with boolean coercion)
function Badge({ count }) {
  return (
    <View>
      {count > 0 && <Text>{count}</Text>}
    </View>
  );
}
```

### Anti-Patterns

```typescript
// ❌ Rendering 0 instead of nothing
function Badge({ count }) {
  return (
    <View>
      {count && <Text>{count}</Text>}  // Renders "0" when count is 0!
    </View>
  );
}

// ✅ Use explicit boolean
{count > 0 && <Text>{count}</Text>}
// or
{!!count && <Text>{count}</Text>}
// or
{count ? <Text>{count}</Text> : null}

// ❌ Complex nested ternaries
{isLoading
  ? <Loading />
  : error
    ? <Error />
    : data
      ? <Content data={data} />
      : <Empty />}

// ✅ Extract to variables or early returns
if (isLoading) return <Loading />;
if (error) return <Error error={error} />;
if (!data) return <Empty />;
return <Content data={data} />;
```

## React Native Specific

### Platform-Specific Code

```typescript
import { Platform, StyleSheet } from 'react-native';

// ✅ Platform.select for styles
const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 3.84,
    },
    android: {
      elevation: 5,
    },
  }),
});

// ✅ Platform-specific components
import { Platform } from 'react-native';

const DatePicker = Platform.select({
  ios: () => require('./DatePickerIOS').default,
  android: () => require('./DatePickerAndroid').default,
})();
```

### Safe Area Handling

```typescript
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';

// ✅ Use SafeAreaView for screens
function Screen() {
  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <Content />
    </SafeAreaView>
  );
}

// ✅ Use hook for custom inset handling
function CustomHeader() {
  const insets = useSafeAreaInsets();
  return (
    <View style={{ paddingTop: insets.top }}>
      <Text>Header</Text>
    </View>
  );
}
```

### Keyboard Handling

```typescript
import { KeyboardAvoidingView, Platform } from 'react-native';

// ✅ Proper keyboard avoiding
function FormScreen() {
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView>
        <TextInput />
        <TextInput />
        <Button title="Submit" />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
```

## Error Boundaries

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <Text>Something went wrong</Text>;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorScreen />}>
  <RiskyComponent />
</ErrorBoundary>
```
