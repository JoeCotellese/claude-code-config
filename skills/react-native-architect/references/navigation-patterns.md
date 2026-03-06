
# Navigation Patterns
## Navigator Structure

### Basic Stack + Tabs

```
RootNavigator (Stack)
├── AuthStack (not logged in)
│   ├── LoginScreen
│   ├── SignUpScreen
│   └── ForgotPasswordScreen
└── MainTabs (logged in)
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

```typescript
// navigation/RootNavigator.tsx
function RootNavigator() {
  const isLoggedIn = useRecoilValue(isLoggedInSelector);

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isLoggedIn ? (
        <Stack.Screen name="Main" component={MainTabs} />
      ) : (
        <Stack.Screen name="Auth" component={AuthStack} />
      )}
    </Stack.Navigator>
  );
}
```

### Role-Based Navigation

```
RootNavigator
├── AuthStack
└── MainNavigator
    ├── ConsumerTabs (role: consumer)
    ├── ClinicalTabs (role: clinical)
    ├── CaregiverTabs (role: caregiver)
    └── CommercialTabs (role: commercial)
```

```typescript
function MainNavigator() {
  const userRole = useRecoilValue(userRoleSelector);

  const TabNavigator = {
    consumer: ConsumerTabs,
    clinical: ClinicalTabs,
    caregiver: CaregiverTabs,
    commercial: CommercialTabs,
  }[userRole];

  return <TabNavigator />;
}
```

## Screen Transitions

### Push (Default Stack)

Navigate forward, add to stack:

```typescript
navigation.navigate('PatientDetail', { patientId: '123' });
// or explicitly push (always adds)
navigation.push('PatientDetail', { patientId: '123' });
```

### Replace

Replace current screen (no back):

```typescript
// After successful login, replace auth stack
navigation.reset({
  index: 0,
  routes: [{ name: 'Main' }],
});

// Or replace single screen
navigation.replace('Dashboard');
```

### Go Back

```typescript
navigation.goBack();

// Go back to specific screen
navigation.navigate('PatientList'); // If already in stack, goes back to it

// Pop multiple screens
navigation.pop(2);

// Pop to top of stack
navigation.popToTop();
```

## Modal Patterns

### Full Screen Modal

```typescript
<Stack.Navigator>
  <Stack.Screen name="Home" component={HomeScreen} />
  <Stack.Group screenOptions={{ presentation: 'modal' }}>
    <Stack.Screen name="CreatePatient" component={CreatePatientModal} />
    <Stack.Screen name="Settings" component={SettingsModal} />
  </Stack.Group>
</Stack.Navigator>
```

### Transparent Modal (Bottom Sheet)

```typescript
<Stack.Screen
  name="ActionSheet"
  component={ActionSheetModal}
  options={{
    presentation: 'transparentModal',
    cardOverlayEnabled: true,
    cardStyle: { backgroundColor: 'transparent' },
  }}
/>
```

### Modal with Form

```typescript
// Parent screen
function PatientListScreen() {
  const navigation = useNavigation();

  const handleCreate = () => {
    navigation.navigate('CreatePatient', {
      onSuccess: (newPatient) => {
        // Callback when modal completes
        addPatientToList(newPatient);
      },
    });
  };
}

// Modal screen
function CreatePatientModal() {
  const route = useRoute();
  const navigation = useNavigation();

  const handleSubmit = async (data) => {
    const newPatient = await PatientApi.create(data);
    route.params?.onSuccess?.(newPatient);
    navigation.goBack();
  };
}
```

## Parameter Passing

### Type-Safe Params

```typescript
// navigation/types.ts
export type RootStackParamList = {
  PatientList: undefined;
  PatientDetail: { patientId: string };
  PatientEdit: { patientId: string; section?: 'info' | 'medical' };
  CreatePatient: { onSuccess?: (patient: Patient) => void };
};

// Type the navigation prop
type PatientDetailScreenProps = NativeStackScreenProps<
  RootStackParamList,
  'PatientDetail'
>;

function PatientDetailScreen({ route, navigation }: PatientDetailScreenProps) {
  const { patientId } = route.params;
  // ...
}

// Or use hooks with types
type PatientDetailRouteProp = RouteProp<RootStackParamList, 'PatientDetail'>;

function PatientDetailScreen() {
  const route = useRoute<PatientDetailRouteProp>();
  const { patientId } = route.params;
}
```

### Initial Params

```typescript
<Stack.Screen
  name="PatientList"
  component={PatientListScreen}
  initialParams={{ filter: 'active' }}
/>
```

### Passing Data Back

**Option 1: Callback in params**

```typescript
// Parent
navigation.navigate('SelectPatient', {
  onSelect: (patient) => setSelectedPatient(patient),
});

// Child
const handleSelect = (patient) => {
  route.params.onSelect?.(patient);
  navigation.goBack();
};
```

**Option 2: Navigation state**

```typescript
// Parent - listen for focus with params
useFocusEffect(
  useCallback(() => {
    if (route.params?.selectedPatient) {
      setPatient(route.params.selectedPatient);
      // Clear the param
      navigation.setParams({ selectedPatient: undefined });
    }
  }, [route.params?.selectedPatient])
);

// Child
navigation.navigate({
  name: 'Parent',
  params: { selectedPatient: patient },
  merge: true,
});
```

**Option 3: Recoil (recommended for complex cases)**

```typescript
// Shared state
const selectedPatientState = atom<Patient | null>({
  key: 'selectedPatient',
  default: null,
});

// Child sets
const setSelected = useSetRecoilState(selectedPatientState);
setSelected(patient);
navigation.goBack();

// Parent reads
const selected = useRecoilValue(selectedPatientState);
```

## Deep Linking

### Configuration

```typescript
const linking = {
  prefixes: ['wavely://', 'https://wavely.com'],
  config: {
    screens: {
      Main: {
        screens: {
          PatientsTab: {
            screens: {
              PatientList: 'patients',
              PatientDetail: 'patients/:patientId',
            },
          },
        },
      },
      Auth: {
        screens: {
          Login: 'login',
          ResetPassword: 'reset-password/:token',
        },
      },
    },
  },
};

<NavigationContainer linking={linking}>
  <RootNavigator />
</NavigationContainer>
```

### URL Patterns

| URL | Screen | Params |
|-----|--------|--------|
| `wavely://patients` | PatientList | none |
| `wavely://patients/123` | PatientDetail | `{ patientId: '123' }` |
| `wavely://reset-password/abc` | ResetPassword | `{ token: 'abc' }` |

### Handling Deep Links

```typescript
// Get initial URL (app opened via link)
const url = await Linking.getInitialURL();

// Listen for links while app is open
Linking.addEventListener('url', ({ url }) => {
  // NavigationContainer handles this automatically with linking config
});
```

## Focus and Blur Events

### Screen Focus

```typescript
import { useFocusEffect } from '@react-navigation/native';

function PatientListScreen() {
  // Runs when screen focuses
  useFocusEffect(
    useCallback(() => {
      fetchPatients();

      return () => {
        // Cleanup when screen blurs
      };
    }, [])
  );
}
```

### Tab Focus

```typescript
function PatientsTab() {
  const navigation = useNavigation();

  useEffect(() => {
    const unsubscribe = navigation.addListener('tabPress', (e) => {
      // Tab was pressed
      // e.preventDefault() to prevent default behavior
    });

    return unsubscribe;
  }, [navigation]);
}
```

## Header Configuration

### Static Options

```typescript
<Stack.Screen
  name="PatientDetail"
  component={PatientDetailScreen}
  options={{
    title: 'Patient Details',
    headerRight: () => <SettingsButton />,
  }}
/>
```

### Dynamic Options

```typescript
<Stack.Screen
  name="PatientDetail"
  component={PatientDetailScreen}
  options={({ route }) => ({
    title: route.params?.patientName ?? 'Patient',
  })}
/>
```

### From Screen

```typescript
function PatientDetailScreen({ navigation }) {
  const patient = usePatient(patientId);

  useLayoutEffect(() => {
    navigation.setOptions({
      title: patient?.name ?? 'Loading...',
      headerRight: () => (
        <TouchableOpacity onPress={handleEdit}>
          <Text>Edit</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation, patient]);
}
```

## Navigation Patterns Summary

| Pattern | Use Case |
|---------|----------|
| **Stack** | Linear flow (list → detail → edit) |
| **Tabs** | Top-level sections |
| **Drawer** | Settings, secondary nav |
| **Modal** | Create/edit forms, confirmations |
| **Bottom Sheet** | Quick actions, filters |
| **Nested Stack in Tab** | Each tab has its own history |

## Anti-Patterns

```typescript
// ❌ Storing navigation state in Recoil
const currentScreenState = atom({ key: 'screen', default: 'Home' });

// ✅ Let React Navigation manage navigation state

// ❌ Passing large objects in params
navigation.navigate('Detail', { patient: entirePatientObject });

// ✅ Pass IDs, fetch in destination
navigation.navigate('Detail', { patientId: patient.id });

// ❌ Deeply nested navigators (3+ levels)
<Stack>
  <Tabs>
    <Stack>
      <Drawer>
        // Very confusing

// ✅ Keep nesting shallow, use modals for overlays
```
