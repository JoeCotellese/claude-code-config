
# Performance Patterns
C++ gives you the tools for high performance — but also the rope to hang yourself. These patterns catch the most common performance regressions.

## Pass by Const Reference

For any type larger than a pointer (8 bytes), pass by const reference to avoid copies.

**Bad — copying on every call:**
```cpp
void processData(QString data)           // Copies the entire string
void renderItems(QVector<Item> items)    // Copies the entire vector
void setConfig(Configuration config)     // Copies the config object
```

**Good:**
```cpp
void processData(const QString& data)
void renderItems(const QVector<Item>& items)
void setConfig(const Configuration& config)
```

**Exception**: Small types (int, double, pointers, QChar) are cheaper to copy than to reference. Pass those by value.

```cpp
void setIndex(int index)        // Good — small type, copy is free
void setRatio(double ratio)     // Good
void setFlag(bool enabled)      // Good
```

## Move Semantics

When you're done with an object and passing it elsewhere, move instead of copy.

**Bad — unnecessary copy:**
```cpp
QVector<SensorData> readAllSensors()
{
    QVector<SensorData> results;
    // ... fill results ...
    return results;  // Actually fine — compiler applies NRVO (Named Return Value Optimization)
}

// But this IS a problem:
void processThenStore(QVector<SensorData> data)
{
    process(data);
    m_storage = data;  // Copy when we're done with data
}
```

**Good — explicit move:**
```cpp
void processThenStore(QVector<SensorData> data)
{
    process(data);
    m_storage = std::move(data);  // Transfer ownership, no copy
}
```

**When to move:**
- Passing a local variable to its final destination
- Inserting into containers when you don't need the original
- Returning from functions (usually automatic via NRVO, but `std::move` for non-NRVO cases)

**When NOT to move:**
- Don't `std::move` a return value — it prevents NRVO
- Don't move from a const object — it silently copies
- Don't use the object after moving — it's in a valid but unspecified state

## Container Selection

| Need | Best Choice | Avoid |
|------|-------------|-------|
| Sequential access, append | `QVector` / `std::vector` | `QList` in Qt5 (stores pointers for large types) |
| Key-value lookup | `QHash` | `QMap` (unless you need sorted keys) |
| Unique membership test | `QSet` / `std::unordered_set` | Linear search in `QVector` |
| Sorted key-value | `QMap` / `std::map` | Sorting a QHash |
| FIFO queue | `QQueue` / `std::queue` | `QVector` with removeFirst() |
| Stack (LIFO) | `QStack` / `std::stack` | `QVector` with removeLast() |

**Note on Qt6**: `QList` and `QVector` are unified (QList IS QVector). In Qt5, `QList<T>` heap-allocates elements larger than a pointer, which is wasteful.

## Container Pre-allocation

**Bad — repeated reallocation:**
```cpp
QVector<SensorData> results;
for (int i = 0; i < 10000; i++) {
    results.append(readSensor(i));  // May reallocate multiple times
}
```

**Good — reserve upfront:**
```cpp
QVector<SensorData> results;
results.reserve(10000);
for (int i = 0; i < 10000; i++) {
    results.append(readSensor(i));  // No reallocation
}
```

**Rule of thumb**: If you know (or can estimate) the final size, always `reserve()`.

## QString Efficiency

### Concatenation

**Bad — repeated concatenation creates temporaries:**
```cpp
QString result;
for (const auto& item : items) {
    result += item.name() + " (" + QString::number(item.value()) + ")\n";
    // Each + creates a temporary QString
}
```

**Good — use QStringBuilder (automatic with QT_USE_QSTRINGBUILDER) or arg:**
```cpp
// Option 1: QString::arg
QString result;
result.reserve(items.size() * 40);  // Estimate
for (const auto& item : items) {
    result += QString("%1 (%2)\n").arg(item.name()).arg(item.value());
}

// Option 2: QStringList::join for simple cases
QStringList parts;
parts.reserve(items.size());
for (const auto& item : items) {
    parts << QString("%1 (%2)").arg(item.name()).arg(item.value());
}
QString result = parts.join('\n');
```

### String Comparisons

**Bad — creating QString just to compare:**
```cpp
if (name == QString("temperature")) { ... }
```

**Good — use string literals:**
```cpp
if (name == QLatin1String("temperature")) { ... }
// Or in Qt 5.14+ / Qt6:
if (name == u"temperature"_s) { ... }
// Or Qt6 QStringView:
if (name == QStringView(u"temperature")) { ... }
```

### Avoid Repeated Conversions

**Bad:**
```cpp
for (int i = 0; i < 1000; i++) {
    qDebug() << QString::fromUtf8(data[i]);  // Conversion every iteration
}
```

## Unnecessary Copies in Loops

**Bad — copy in range-for:**
```cpp
for (auto item : expensiveVector) {  // Copies each element
    process(item);
}
```

**Good — const reference:**
```cpp
for (const auto& item : expensiveVector) {  // No copy
    process(item);
}
```

**Bad — copying container to iterate:**
```cpp
QStringList keys = map.keys();  // Creates a new QStringList
for (const auto& key : keys) { ... }
```

**Good — iterate directly:**
```cpp
for (auto it = map.cbegin(); it != map.cend(); ++it) {
    // Use it.key() and it.value()
}
// Or in C++17:
for (const auto& [key, value] : map.asKeyValueRange()) { ... }  // Qt6
```

## Avoid Repeated Lookups

**Bad:**
```cpp
if (map.contains(key)) {
    process(map.value(key));  // Double lookup
    update(map.value(key));   // Triple lookup
}
```

**Good:**
```cpp
auto it = map.find(key);
if (it != map.end()) {
    process(it.value());
    update(it.value());
}
```

**Bad — repeated QObject::findChild:**
```cpp
void updateUI()
{
    findChild<QLabel*>("statusLabel")->setText("OK");     // Searches object tree
    findChild<QLabel*>("statusLabel")->setVisible(true);  // Searches again
}
```

**Good — cache the pointer:**
```cpp
// Store as member, looked up once in constructor
QLabel* m_statusLabel = findChild<QLabel*>("statusLabel");

void updateUI()
{
    m_statusLabel->setText("OK");
    m_statusLabel->setVisible(true);
}
```

## Virtual Functions in Hot Paths

Virtual dispatch adds indirection (vtable lookup). In tight loops this matters.

**Consideration — not always a problem:**
```cpp
// Fine for UI code, event handling, infrequent calls:
virtual void onButtonClicked();

// Worth scrutiny in tight loops processing thousands of items:
for (const auto& sensor : sensors) {
    sensor->read();  // Virtual call per iteration
}
```

**Alternatives for hot paths:**
- CRTP (Curiously Recurring Template Pattern) for compile-time polymorphism
- `std::variant` with `std::visit` (type-safe, no heap allocation)
- `final` keyword to allow devirtualization

## Review Checklist

- [ ] Non-trivial types passed by const reference (not by value)
- [ ] `std::move` used when transferring ownership
- [ ] No `std::move` on return values (let NRVO work)
- [ ] Appropriate container type for the use case
- [ ] `reserve()` called when final size is known or estimable
- [ ] No QString concatenation with `+` in loops (use arg or QStringBuilder)
- [ ] QLatin1String or u""_s for string literal comparisons
- [ ] Range-for uses `const auto&` (not `auto` by value) for non-trivial types
- [ ] No double lookups in maps (use find + iterator)
- [ ] No repeated findChild calls (cache the result)
- [ ] Virtual function overhead considered in performance-critical loops
