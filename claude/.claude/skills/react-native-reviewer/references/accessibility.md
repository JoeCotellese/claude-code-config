# ABOUTME: React Native accessibility (a11y) best practices reference
# ABOUTME: Covers screen readers, accessibility props, and testing guidelines

# React Native Accessibility

## Core Accessibility Props

### accessibilityLabel

Provides text for screen readers. Required for interactive elements without visible text.

```typescript
// ✅ Buttons/icons need labels
<TouchableOpacity
  onPress={handleClose}
  accessibilityLabel="Close dialog"
>
  <CloseIcon />
</TouchableOpacity>

// ✅ Images need descriptions
<Image
  source={profilePic}
  accessibilityLabel="Profile picture of John Doe"
/>

// ❌ Don't just repeat visible text
<TouchableOpacity accessibilityLabel="Submit button">
  <Text>Submit</Text>  {/* Screen reader says "Submit button, button" */}
</TouchableOpacity>

// ✅ Add context when helpful
<TouchableOpacity accessibilityLabel="Submit form">
  <Text>Submit</Text>
</TouchableOpacity>
```

### accessibilityRole

Tells screen readers what type of element this is.

```typescript
// Common roles
<TouchableOpacity accessibilityRole="button">
<TextInput accessibilityRole="search">
<Switch accessibilityRole="switch">
<Image accessibilityRole="image">
<Text accessibilityRole="header">  {/* For headings */}
<Text accessibilityRole="link">    {/* For clickable text links */}
<View accessibilityRole="alert">   {/* For important announcements */}
<View accessibilityRole="menu">
<View accessibilityRole="menuitem">
<View accessibilityRole="tab">
<View accessibilityRole="tablist">

// ✅ Headers for screen structure
<Text
  style={styles.sectionHeader}
  accessibilityRole="header"
>
  Patient Information
</Text>
```

### accessibilityState

Communicates dynamic state to screen readers.

```typescript
<TouchableOpacity
  accessibilityRole="button"
  accessibilityState={{
    disabled: isDisabled,
    selected: isSelected,
    checked: isChecked,    // For checkboxes
    expanded: isExpanded,  // For accordions
    busy: isLoading,       // For loading states
  }}
>
  <Text>Toggle</Text>
</TouchableOpacity>

// ✅ Checkbox example
<TouchableOpacity
  accessibilityRole="checkbox"
  accessibilityState={{ checked: isChecked }}
  accessibilityLabel="Accept terms and conditions"
  onPress={toggleChecked}
>
  <CheckboxIcon checked={isChecked} />
  <Text>Accept terms</Text>
</TouchableOpacity>
```

### accessibilityValue

For elements with values (sliders, progress bars).

```typescript
<Slider
  accessibilityLabel="Volume"
  accessibilityValue={{
    min: 0,
    max: 100,
    now: volume,
    text: `${volume}%`,  // Human-readable value
  }}
/>

<View
  accessibilityRole="progressbar"
  accessibilityLabel="Upload progress"
  accessibilityValue={{
    min: 0,
    max: 100,
    now: progress,
    text: `${progress}% complete`,
  }}
>
  <ProgressBar progress={progress} />
</View>
```

### accessibilityHint

Provides additional context about what happens when activating an element.

```typescript
// ✅ Use for non-obvious actions
<TouchableOpacity
  accessibilityLabel="Profile picture"
  accessibilityHint="Double tap to change your profile picture"
>
  <Image source={avatar} />
</TouchableOpacity>

// ❌ Don't state the obvious
<TouchableOpacity
  accessibilityLabel="Submit"
  accessibilityHint="Taps the submit button"  // Redundant
>
```

## Grouping and Focus

### accessible Prop

Groups child elements into a single accessible element.

```typescript
// ❌ Screen reader focuses each element separately
<View>
  <Text>John Doe</Text>
  <Text>Patient ID: 12345</Text>
  <Text>Last visit: Jan 15</Text>
</View>

// ✅ Group for better UX
<View
  accessible={true}
  accessibilityLabel="John Doe, Patient ID 12345, Last visit January 15"
>
  <Text>John Doe</Text>
  <Text>Patient ID: 12345</Text>
  <Text>Last visit: Jan 15</Text>
</View>
```

### importantForAccessibility (Android)

Controls whether element is exposed to accessibility services.

```typescript
// Hide decorative elements
<Image
  source={decorativeBackground}
  importantForAccessibility="no-hide-descendants"
/>

// Values: 'auto' | 'yes' | 'no' | 'no-hide-descendants'
```

### accessibilityElementsHidden (iOS)

Hides element and children from VoiceOver.

```typescript
<View accessibilityElementsHidden={true}>
  <DecorativeElement />
</View>
```

### accessibilityViewIsModal (iOS)

Limits VoiceOver to elements within this view (for modals).

```typescript
<Modal visible={isVisible}>
  <View accessibilityViewIsModal={true}>
    <Text>Modal content</Text>
    <Button title="Close" onPress={close} />
  </View>
</Modal>
```

## Focus Management

### accessibilityLiveRegion (Android)

Announces changes to screen reader.

```typescript
// Announce errors/updates
<Text
  accessibilityLiveRegion="polite"  // Announces after current speech
  // or "assertive" for immediate
>
  {errorMessage}
</Text>
```

### AccessibilityInfo API

```typescript
import { AccessibilityInfo } from 'react-native';

// Check if screen reader is enabled
const [screenReaderEnabled, setScreenReaderEnabled] = useState(false);

useEffect(() => {
  AccessibilityInfo.isScreenReaderEnabled().then(setScreenReaderEnabled);

  const subscription = AccessibilityInfo.addEventListener(
    'screenReaderChanged',
    setScreenReaderEnabled
  );

  return () => subscription.remove();
}, []);

// Announce to screen reader
AccessibilityInfo.announceForAccessibility('Form submitted successfully');

// Set focus (useful after navigation or modal open)
AccessibilityInfo.setAccessibilityFocus(viewRef);
```

## Form Accessibility

### Text Inputs

```typescript
<TextInput
  accessibilityLabel="Email address"
  accessibilityHint="Enter your email to sign in"
  keyboardType="email-address"
  autoComplete="email"
  textContentType="emailAddress"  // iOS autofill
  placeholder="email@example.com"
/>

// With error state
<TextInput
  accessibilityLabel="Password"
  accessibilityState={{
    disabled: false,
  }}
  accessibilityValue={{
    text: hasError ? 'Error: Password must be at least 8 characters' : undefined
  }}
/>
{hasError && (
  <Text
    accessibilityRole="alert"
    accessibilityLiveRegion="polite"
  >
    Password must be at least 8 characters
  </Text>
)}
```

### Form Validation Errors

```typescript
// ✅ Announce errors to screen reader
function FormField({ label, error, ...props }) {
  return (
    <View>
      <Text accessibilityRole="text">{label}</Text>
      <TextInput
        accessibilityLabel={label}
        accessibilityState={{ invalid: !!error }}
        {...props}
      />
      {error && (
        <Text
          accessibilityRole="alert"
          accessibilityLiveRegion="assertive"
          style={styles.error}
        >
          {error}
        </Text>
      )}
    </View>
  );
}
```

## Lists and Tables

### FlatList Accessibility

```typescript
<FlatList
  data={patients}
  renderItem={({ item, index }) => (
    <TouchableOpacity
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={`Patient ${item.name}, ID ${item.id}`}
      accessibilityHint="Double tap to view patient details"
    >
      <Text>{item.name}</Text>
      <Text>{item.id}</Text>
    </TouchableOpacity>
  )}
/>
```

### Section Headers

```typescript
<SectionList
  sections={sections}
  renderSectionHeader={({ section }) => (
    <Text
      accessibilityRole="header"
      style={styles.sectionHeader}
    >
      {section.title}
    </Text>
  )}
/>
```

## Touch Target Sizes

Minimum 44x44 points for touch targets (Apple HIG) / 48x48 dp (Material Design).

```typescript
// ❌ Too small
<TouchableOpacity style={{ padding: 4 }}>
  <Icon size={16} />
</TouchableOpacity>

// ✅ Adequate touch target
<TouchableOpacity
  style={{ padding: 12, minWidth: 44, minHeight: 44 }}
  hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
>
  <Icon size={20} />
</TouchableOpacity>
```

## Color and Contrast

### Minimum Contrast Ratios

- **Normal text**: 4.5:1
- **Large text (18pt+ or 14pt+ bold)**: 3:1
- **UI components**: 3:1

### Don't Rely on Color Alone

```typescript
// ❌ Status indicated only by color
<View style={{ backgroundColor: isError ? 'red' : 'green' }} />

// ✅ Include text/icon indicator
<View style={[styles.status, isError && styles.error]}>
  <Icon name={isError ? 'error' : 'check'} />
  <Text>{isError ? 'Error' : 'Success'}</Text>
</View>
```

## Motion and Animation

### Reduce Motion Support

```typescript
import { AccessibilityInfo } from 'react-native';

const [reduceMotionEnabled, setReduceMotionEnabled] = useState(false);

useEffect(() => {
  AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotionEnabled);

  const subscription = AccessibilityInfo.addEventListener(
    'reduceMotionChanged',
    setReduceMotionEnabled
  );

  return () => subscription.remove();
}, []);

// Use simplified animations when reduce motion is enabled
const animationDuration = reduceMotionEnabled ? 0 : 300;
```

## Testing Checklist

### Manual Testing

1. **Enable VoiceOver (iOS)** or **TalkBack (Android)**
2. Navigate through entire app using only screen reader
3. Verify all interactive elements have labels
4. Check that focus order is logical
5. Ensure state changes are announced

### Automated Testing

```typescript
// Using react-native-accessibility-engine (per your jest-setup.js)
import { axe } from 'react-native-accessibility-engine';

test('PatientCard is accessible', async () => {
  const { container } = render(<PatientCard patient={mockPatient} />);
  const results = await axe(container);
  expect(results.violations).toHaveLength(0);
});
```

### Common Issues to Check

- [ ] All images have `accessibilityLabel`
- [ ] All buttons/touchables have `accessibilityLabel` and `accessibilityRole`
- [ ] Form inputs have labels
- [ ] Errors are announced with `accessibilityLiveRegion`
- [ ] Touch targets are at least 44x44 points
- [ ] Color is not the only indicator of state
- [ ] Modals trap focus appropriately
- [ ] Loading states are announced
- [ ] Header structure is logical (`accessibilityRole="header"`)
