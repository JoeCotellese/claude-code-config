# ABOUTME: React Native performance optimization checklist and patterns
# ABOUTME: Covers re-render prevention, list optimization, images, and profiling

# React Native Performance Checklist

## Re-render Prevention

### Identify Unnecessary Re-renders

Use React DevTools Profiler or add debug logging:

```typescript
// Debug: log when component renders
function MyComponent(props) {
  console.log('MyComponent rendered');
  // or use useEffect
  useEffect(() => {
    console.log('MyComponent mounted/updated');
  });
}
```

### Common Causes and Fixes

| Cause | Fix |
|-------|-----|
| Inline functions in props | `useCallback` or extract to constant |
| Inline objects/arrays in props | `useMemo` or extract to constant |
| Parent re-renders | `memo()` the child component |
| Context value changes | Split contexts, memoize value |
| State stored too high | Move state down to where it's used |

### State Optimization

```typescript
// ❌ State too high - entire tree re-renders
function App() {
  const [searchQuery, setSearchQuery] = useState('');
  return (
    <View>
      <SearchBar value={searchQuery} onChange={setSearchQuery} />
      <ExpensiveList /> {/* Re-renders on every keystroke */}
      <Footer />
    </View>
  );
}

// ✅ State colocated - only SearchBar re-renders
function App() {
  return (
    <View>
      <SearchBar /> {/* Owns its own state */}
      <ExpensiveList />
      <Footer />
    </View>
  );
}

function SearchBar() {
  const [searchQuery, setSearchQuery] = useState('');
  // ...
}
```

## FlatList Optimization

### Essential Props

```typescript
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={keyExtractor}
  // Performance props:
  removeClippedSubviews={true}      // Unmount off-screen items (Android)
  maxToRenderPerBatch={10}          // Items per batch render
  updateCellsBatchingPeriod={50}    // Ms between batch renders
  initialNumToRender={10}           // Initial items to render
  windowSize={5}                    // Viewport multiplier for render window
  getItemLayout={getItemLayout}     // Skip measurement if fixed height
/>
```

### getItemLayout for Fixed Height

```typescript
// ✅ Skip measurement for fixed-height items
const ITEM_HEIGHT = 80;

const getItemLayout = useCallback(
  (data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  }),
  []
);

<FlatList
  data={items}
  getItemLayout={getItemLayout}
  // ...
/>
```

### Memoized renderItem

```typescript
// ❌ Inline renderItem creates new function every render
<FlatList
  renderItem={({ item }) => <ItemRow item={item} />}
/>

// ✅ Memoize with useCallback
const renderItem = useCallback(
  ({ item }) => <ItemRow item={item} onPress={handlePress} />,
  [handlePress]
);

<FlatList
  data={items}
  renderItem={renderItem}
/>

// ✅ Memoize the item component too
const ItemRow = memo(function ItemRow({ item, onPress }) {
  return (
    <TouchableOpacity onPress={() => onPress(item.id)}>
      <Text>{item.name}</Text>
    </TouchableOpacity>
  );
});
```

### Stable keyExtractor

```typescript
// ❌ Index as key (causes issues on reorder/delete)
keyExtractor={(item, index) => index.toString()}

// ✅ Stable unique ID
keyExtractor={(item) => item.id}

// Memoize if needed
const keyExtractor = useCallback((item: Item) => item.id, []);
```

### List Separators and Headers

```typescript
// ✅ Memoize separators and headers
const ItemSeparator = memo(() => (
  <View style={styles.separator} />
));

const ListHeader = memo(() => (
  <Text style={styles.header}>My List</Text>
));

<FlatList
  ItemSeparatorComponent={ItemSeparator}
  ListHeaderComponent={ListHeader}
  // ...
/>
```

## Image Optimization

### Use FastImage

```typescript
// ❌ Default Image component
import { Image } from 'react-native';
<Image source={{ uri: url }} />

// ✅ FastImage for better caching and performance
import FastImage from 'react-native-fast-image';

<FastImage
  source={{ uri: url, priority: FastImage.priority.normal }}
  style={styles.image}
  resizeMode={FastImage.resizeMode.cover}
/>
```

### Image Sizing

```typescript
// ❌ Large images scaled down in React Native
<Image
  source={{ uri: 'https://example.com/huge-4k-image.jpg' }}
  style={{ width: 100, height: 100 }}
/>

// ✅ Request appropriately sized images from server
<Image
  source={{ uri: 'https://example.com/image.jpg?w=200&h=200' }}
  style={{ width: 100, height: 100 }}
/>
```

### Preloading

```typescript
// Preload images before showing screen
import FastImage from 'react-native-fast-image';

useEffect(() => {
  FastImage.preload([
    { uri: 'https://example.com/image1.jpg' },
    { uri: 'https://example.com/image2.jpg' },
  ]);
}, []);
```

## Animation Performance

### Use Native Driver

```typescript
import { Animated } from 'react-native';

// ✅ Enable native driver for transform/opacity animations
Animated.timing(animatedValue, {
  toValue: 1,
  duration: 300,
  useNativeDriver: true,  // Runs on UI thread
}).start();

// Note: useNativeDriver only works with:
// - transform properties (translateX, scale, rotate, etc.)
// - opacity
// Does NOT work with: layout properties (width, height, margin, etc.)
```

### Use Reanimated for Complex Animations

```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

function AnimatedBox() {
  const offset = useSharedValue(0);

  const animatedStyles = useAnimatedStyle(() => ({
    transform: [{ translateX: offset.value }],
  }));

  return (
    <Animated.View style={[styles.box, animatedStyles]} />
  );
}
```

### Avoid Layout Thrashing

```typescript
// ❌ Animating layout properties
Animated.timing(width, {
  toValue: 200,
  useNativeDriver: false,  // Can't use native driver
}).start();

// ✅ Use transform for size animations
Animated.timing(scale, {
  toValue: 2,
  useNativeDriver: true,
}).start();
```

## Memory Management

### Cleanup Subscriptions

```typescript
useEffect(() => {
  const subscription = eventEmitter.addListener('event', handler);

  return () => {
    subscription.remove();  // Clean up!
  };
}, []);
```

### Cancel Async Operations

```typescript
useEffect(() => {
  let isMounted = true;

  async function fetchData() {
    const data = await api.get('/data');
    if (isMounted) {
      setData(data);
    }
  }

  fetchData();

  return () => {
    isMounted = false;
  };
}, []);
```

### Clear Intervals/Timeouts

```typescript
useEffect(() => {
  const intervalId = setInterval(() => {
    // ...
  }, 1000);

  return () => {
    clearInterval(intervalId);
  };
}, []);
```

## Bundle Size

### Import Only What You Need

```typescript
// ❌ Import entire library
import _ from 'lodash';
_.map(array, fn);

// ✅ Import specific functions
import map from 'lodash/map';
map(array, fn);

// ❌ Import entire icon library
import * as Icons from '@expo/vector-icons';

// ✅ Import specific icon set
import { Ionicons } from '@expo/vector-icons';
```

### Lazy Loading Screens

```typescript
// ✅ Lazy load heavy screens
const HeavyScreen = React.lazy(() => import('./HeavyScreen'));

// In navigator
<Stack.Screen
  name="Heavy"
  component={HeavyScreen}
  options={{ lazy: true }}
/>
```

## JavaScript Thread

### Avoid Blocking Operations

```typescript
// ❌ Heavy computation on JS thread
function processLargeData(data) {
  return data.map(item => expensiveTransform(item));
}

// ✅ Move to native module or use InteractionManager
import { InteractionManager } from 'react-native';

InteractionManager.runAfterInteractions(() => {
  // Run after animations complete
  processLargeData(data);
});
```

### Debounce Expensive Operations

```typescript
import { useMemo } from 'react';
import debounce from 'lodash/debounce';

function SearchInput() {
  const debouncedSearch = useMemo(
    () => debounce((query) => fetchResults(query), 300),
    []
  );

  return (
    <TextInput
      onChangeText={debouncedSearch}
      placeholder="Search..."
    />
  );
}
```

## Profiling Checklist

1. **Use Flipper** for debugging and profiling
2. **React DevTools Profiler** to identify slow renders
3. **Systrace** (Android) for detailed performance analysis
4. **Instruments** (iOS) for Time Profiler and Allocations
5. **`console.time`/`console.timeEnd`** for quick measurements:

```typescript
console.time('expensiveOperation');
expensiveOperation();
console.timeEnd('expensiveOperation');
```

## Quick Performance Wins

1. ✅ Add `memo()` to FlatList item components
2. ✅ Add `getItemLayout` for fixed-height lists
3. ✅ Use `useNativeDriver: true` for animations
4. ✅ Replace Image with FastImage
5. ✅ Memoize callbacks passed to child components
6. ✅ Move state down to where it's actually used
7. ✅ Use Recoil selectors for derived state
8. ✅ Clean up subscriptions and timers in useEffect
9. ✅ Lazy load screens that aren't immediately needed
10. ✅ Use specific lodash imports instead of full library
