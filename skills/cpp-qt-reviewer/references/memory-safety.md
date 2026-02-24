# ABOUTME: Memory safety reference for C++/Qt code reviews.
# ABOUTME: Covers RAII, smart pointers, ownership models, Qt parent-child, and Rule of Zero/Five.

# Memory Safety

The #1 source of bugs in C++. Every code review should scrutinize ownership and lifetime.

## RAII (Resource Acquisition Is Initialization)

Every resource (memory, files, locks, sockets) must be tied to an object's lifetime.

**Bad — Manual resource management:**
```cpp
void processFile(const QString &path)
{
    FILE *f = fopen(path.toLocal8Bit(), "r");
    // ... 50 lines of processing ...
    if (error) return;  // LEAK: f never closed
    fclose(f);
}
```

**Good — RAII wrapper:**
```cpp
void processFile(const QString &path)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) return;
    // ... processing ...
    // file closed automatically when scope exits
}
```

## Smart Pointer Selection

| Pointer | When to Use | Example |
|---------|-------------|---------|
| `std::unique_ptr<T>` | Single owner, non-Qt objects | `auto config = std::make_unique<Config>();` |
| `std::shared_ptr<T>` | Shared ownership (rare — question if truly needed) | `auto cache = std::make_shared<DataCache>();` |
| `QPointer<T>` | Observing a QObject that may be deleted elsewhere | `QPointer<QWidget> dialog;` |
| `QScopedPointer<T>` | Qt5 equivalent of unique_ptr for class members | `QScopedPointer<Worker> m_worker;` |
| Raw `T*` | Non-owning pointer, or Qt parent-child ownership | `auto* label = new QLabel(this);` |

### Common Mistakes

**Bad — naked new without ownership:**
```cpp
Config* loadConfig()
{
    return new Config();  // Who deletes this? Caller? Callee? Nobody?
}
```

**Good — clear ownership via unique_ptr:**
```cpp
std::unique_ptr<Config> loadConfig()
{
    return std::make_unique<Config>();  // Caller owns it, period.
}
```

**Bad — shared_ptr when unique_ptr suffices:**
```cpp
// shared_ptr has overhead (reference counting, control block allocation)
std::shared_ptr<Logger> m_logger;  // Is this really shared?
```

**Good — default to unique_ptr:**
```cpp
std::unique_ptr<Logger> m_logger;  // Upgrade to shared only if proven necessary
```

## Qt Parent-Child Ownership

Qt has its own ownership model: a QObject parent deletes all its children in its destructor.

**Rules:**
1. When creating a QObject with `new`, pass a parent → Qt owns it
2. Never wrap a parented QObject in `std::unique_ptr` — double-free
3. Use `QPointer<T>` to observe QObjects you don't own

**Bad — double ownership:**
```cpp
auto button = std::make_unique<QPushButton>("Click", parentWidget);
// BUG: Both unique_ptr AND parentWidget will try to delete button
```

**Good — let Qt own it:**
```cpp
auto* button = new QPushButton("Click", parentWidget);
// parentWidget will delete button. Raw pointer is correct here.
```

**Bad — dangling pointer to deleted child:**
```cpp
QWidget* dialog = new QDialog(this);
QLabel* label = new QLabel("Hello", dialog);
delete dialog;
label->setText("World");  // USE-AFTER-FREE: label was deleted with dialog
```

**Good — use QPointer for safety:**
```cpp
QPointer<QLabel> label = new QLabel("Hello", dialog);
delete dialog;
if (label) {  // QPointer becomes null when target is deleted
    label->setText("World");
}
```

## Rule of Zero / Rule of Five

**Rule of Zero** (preferred): If your class only holds smart pointers and value types, don't write any special member functions.

```cpp
// Good — Rule of Zero
class SensorReader
{
    std::unique_ptr<SerialPort> m_port;
    QString m_name;
    int m_baudRate;
    // No destructor, copy/move constructors, or assignment operators needed.
    // The compiler generates correct ones automatically.
};
```

**Rule of Five**: If you must write a destructor (raw resource), you must also write or delete copy constructor, copy assignment, move constructor, and move assignment.

```cpp
// If you MUST manage a raw resource (rare — prefer RAII wrappers)
class RawBuffer
{
public:
    explicit RawBuffer(size_t size) : m_data(new char[size]), m_size(size) {}
    ~RawBuffer() { delete[] m_data; }

    // Must also define these four:
    RawBuffer(const RawBuffer& other);              // copy ctor
    RawBuffer& operator=(const RawBuffer& other);   // copy assign
    RawBuffer(RawBuffer&& other) noexcept;           // move ctor
    RawBuffer& operator=(RawBuffer&& other) noexcept; // move assign

private:
    char* m_data;
    size_t m_size;
};
```

**Red flag**: A class with a destructor but missing copy/move operations.

## Virtual Destructors

**Rule**: If a class has any virtual methods, its destructor must be virtual.

**Bad:**
```cpp
class Sensor
{
public:
    virtual void read() = 0;
    ~Sensor() {}  // NON-VIRTUAL: deleting via base pointer leaks derived resources
};

class TemperatureSensor : public Sensor { /* ... */ };

std::unique_ptr<Sensor> s = std::make_unique<TemperatureSensor>();
// ~Sensor() called, ~TemperatureSensor() skipped → UNDEFINED BEHAVIOR
```

**Good:**
```cpp
class Sensor
{
public:
    virtual void read() = 0;
    virtual ~Sensor() = default;  // Virtual destructor
};
```

## Dangling References

**Bad — returning reference to local:**
```cpp
const QString& getName()
{
    QString name = buildName();
    return name;  // DANGLING: name destroyed at end of scope
}
```

**Bad — reference to temporary in range-for:**
```cpp
for (const auto& item : getItems()) {
    // If getItems() returns by value, the temporary is valid for the loop.
    // But storing the reference beyond the loop is a bug.
}
```

**Bad — lambda capturing by reference outliving scope:**
```cpp
std::function<void()> createCallback()
{
    int counter = 0;
    return [&counter]() { counter++; };  // DANGLING: counter is gone
}
```

**Good:**
```cpp
std::function<void()> createCallback()
{
    int counter = 0;
    return [counter]() mutable { /* copy is safe */ };
}
```

## Review Checklist

- [ ] Every `new` has a corresponding ownership strategy (smart pointer or Qt parent)
- [ ] No `delete` in application code (RAII handles it)
- [ ] No `std::unique_ptr` or `std::shared_ptr` wrapping parented QObjects
- [ ] `QPointer` used for observing QObjects not owned by this class
- [ ] Base classes with virtual methods have virtual destructors
- [ ] Rule of Zero applied (no custom destructor unless unavoidable)
- [ ] If custom destructor exists, Rule of Five is complete
- [ ] No dangling references (to locals, temporaries, or captured variables)
- [ ] No raw owning pointers in return types (use unique_ptr)
- [ ] `std::shared_ptr` justified (not used as default "safe" pointer)
