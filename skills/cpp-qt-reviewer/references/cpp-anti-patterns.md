
# C++ Anti-Patterns
Common mistakes, especially from developers coming from C or older C++ standards.

## Const Correctness

The most frequently missed issue in junior C++ code. Const communicates intent and catches bugs at compile time.

**Bad — missing const on read-only parameter:**
```cpp
void printSensorData(SensorData& data)  // Can this modify data? Unclear.
{
    qDebug() << data.temperature();
}
```

**Good:**
```cpp
void printSensorData(const SensorData& data)  // Intent is clear: read-only.
{
    qDebug() << data.temperature();
}
```

**Bad — missing const on method that doesn't mutate:**
```cpp
class Sensor {
public:
    QString name() { return m_name; }  // Should be const
    int reading() { return m_reading; }  // Should be const
};
```

**Good:**
```cpp
class Sensor {
public:
    QString name() const { return m_name; }
    int reading() const { return m_reading; }
};
```

**Bad — non-const local that never changes:**
```cpp
int maxRetries = 5;  // Never modified after initialization
QString prefix = "sensor_";
```

**Good:**
```cpp
const int maxRetries = 5;
const QString prefix = "sensor_";
// Or even better for compile-time constants:
constexpr int maxRetries = 5;
```

## C-Style Casts

**Bad — C-style cast hides dangerous conversions:**
```cpp
void* buffer = getData();
SensorData* data = (SensorData*)buffer;  // What kind of cast is this?
// Could be static_cast, reinterpret_cast, or const_cast — all silently
```

**Good — explicit cast type:**
```cpp
auto* data = static_cast<SensorData*>(buffer);
// Or if crossing unrelated types:
auto* data = reinterpret_cast<SensorData*>(buffer);  // Red flag — but at least explicit
```

**Cast selection guide:**
| Cast | Use |
|------|-----|
| `static_cast` | Related types (base↔derived, numeric conversions) |
| `dynamic_cast` | Polymorphic downcasting (checks at runtime) |
| `const_cast` | Remove/add const (almost always a design smell) |
| `reinterpret_cast` | Unrelated types, raw memory (dangerous — document why) |

## Raw Arrays and C Strings

**Bad:**
```cpp
char name[256];
strcpy(name, input.c_str());  // Buffer overflow if input > 255 chars

int readings[100];
for (int i = 0; i <= 100; i++) {  // Off-by-one: reads readings[100]
    readings[i] = 0;
}
```

**Good:**
```cpp
QString name = input;  // Qt handles memory

std::vector<int> readings(100, 0);  // Or QVector<int>
// No off-by-one possible with range-for:
for (auto& r : readings) {
    r = 0;
}
```

## Implicit Conversions

**Bad — implicit bool conversion hides bugs:**
```cpp
class Connection {
public:
    operator bool() const { return m_connected; }
};

Connection a, b;
int result = a + b;  // Compiles! bool + bool = int. Almost certainly a bug.
```

**Good — explicit conversion:**
```cpp
class Connection {
public:
    explicit operator bool() const { return m_connected; }
};
// Now: int result = a + b;  // COMPILE ERROR
// Must be explicit: if (a) { ... }
```

**Bad — implicit single-arg constructor conversion:**
```cpp
class Temperature {
public:
    Temperature(double celsius) : m_celsius(celsius) {}
};

void logTemp(Temperature t);
logTemp(42.0);  // Implicit conversion — was this intentional?
```

**Good:**
```cpp
class Temperature {
public:
    explicit Temperature(double celsius) : m_celsius(celsius) {}
};
logTemp(Temperature(42.0));  // Intent is clear
```

## Modern C++17 Features to Use

### Structured Bindings
**Bad:**
```cpp
auto result = map.find(key);
if (result != map.end()) {
    auto key = result->first;
    auto value = result->second;
}
```

**Good:**
```cpp
if (auto it = map.find(key); it != map.end()) {
    auto [k, v] = *it;
}
```

### std::optional
**Bad — using magic values for "no result":**
```cpp
int findIndex(const QString& name)
{
    // returns -1 if not found — caller must remember to check
    return -1;
}
```

**Good:**
```cpp
std::optional<int> findIndex(const QString& name)
{
    // returns std::nullopt if not found — type system enforces checking
    return std::nullopt;
}

if (auto idx = findIndex("sensor"); idx.has_value()) {
    process(*idx);
}
```

### if-with-initializer
**Bad:**
```cpp
auto* widget = findWidget(name);
if (widget != nullptr) {
    widget->update();
}
// widget still in scope here — potential misuse
```

**Good:**
```cpp
if (auto* widget = findWidget(name); widget != nullptr) {
    widget->update();
}
// widget out of scope — can't accidentally use it
```

### constexpr
**Bad — runtime computation of compile-time constants:**
```cpp
const double PI = 3.14159265358979;
const int BUFFER_SIZE = 1024 * 1024;
```

**Good:**
```cpp
constexpr double PI = 3.14159265358979;
constexpr int BUFFER_SIZE = 1024 * 1024;
```

## Enum Anti-Patterns

**Bad — unscoped enum pollutes namespace:**
```cpp
enum Color { Red, Green, Blue };
enum TrafficLight { Red, Yellow, Green };  // COMPILE ERROR: Red/Green conflict
```

**Good — scoped enum (enum class):**
```cpp
enum class Color { Red, Green, Blue };
enum class TrafficLight { Red, Yellow, Green };
Color c = Color::Red;  // No ambiguity
```

## Magic Numbers

**Bad:**
```cpp
if (temperature > 85.0) {  // What is 85.0?
    setFanSpeed(3);          // What is 3?
    QTimer::singleShot(5000, this, &Device::checkAgain);  // Why 5000?
}
```

**Good:**
```cpp
constexpr double THERMAL_WARNING_CELSIUS = 85.0;
constexpr int FAN_SPEED_HIGH = 3;
constexpr int THERMAL_CHECK_INTERVAL_MS = 5000;

if (temperature > THERMAL_WARNING_CELSIUS) {
    setFanSpeed(FAN_SPEED_HIGH);
    QTimer::singleShot(THERMAL_CHECK_INTERVAL_MS, this, &Device::checkAgain);
}
```

## Using namespace std

**Bad — in headers:**
```cpp
// SensorReader.h
#pragma once
using namespace std;  // Pollutes every file that includes this header
```

**Good — never in headers, sparingly in .cpp:**
```cpp
// SensorReader.h
#pragma once
#include <string>
std::string getName();  // Fully qualified in headers

// SensorReader.cpp
// If desired, use in implementation file only:
using std::string;
using std::vector;
```

## Review Checklist

- [ ] Const on all parameters, methods, and locals that don't mutate
- [ ] No C-style casts (use static_cast, dynamic_cast, etc.)
- [ ] No raw C arrays (use std::array, std::vector, QVector)
- [ ] No C strings for logic (use QString or std::string)
- [ ] `explicit` on single-argument constructors
- [ ] `explicit` on conversion operators
- [ ] Scoped enums (enum class) instead of plain enums
- [ ] No magic numbers (use named constexpr)
- [ ] No `using namespace` in headers
- [ ] Modern C++17 features used where they improve clarity
- [ ] auto used judiciously (not hiding important types)
