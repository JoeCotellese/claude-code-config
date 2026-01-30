# Modern C++ Standards Reference

## C++17 Baseline (Recommended for Qt5/Qt6 Compatibility)

### Structured Bindings

```cpp
// Decompose pairs and tuples
auto [key, value] = map.first();

// Decompose structs
struct Point { int x, y; };
Point p{10, 20};
auto [x, y] = p;

// Range-based for with structured bindings
QMap<QString, int> scores;
for (const auto &[name, score] : scores.asKeyValueRange()) {
    qDebug() << name << score;
}
```

### If-Init Statements

```cpp
// Variable scoped to if-else block
if (auto it = map.find(key); it != map.end()) {
    return it.value();
} else {
    return defaultValue;
}

// With lock
if (std::lock_guard lock(mutex); !data.isEmpty()) {
    process(data);
}
```

### if constexpr

```cpp
template<typename T>
QString toString(const T &value)
{
    if constexpr (std::is_same_v<T, QString>) {
        return value;
    } else if constexpr (std::is_integral_v<T>) {
        return QString::number(value);
    } else if constexpr (std::is_floating_point_v<T>) {
        return QString::number(value, 'f', 2);
    } else {
        static_assert(always_false<T>::value, "Unsupported type");
    }
}
```

### std::optional

```cpp
#include <optional>

std::optional<int> parseInt(const QString &str)
{
    bool ok;
    int value = str.toInt(&ok);
    if (ok) {
        return value;
    }
    return std::nullopt;
}

// Usage
if (auto value = parseInt(input); value.has_value()) {
    process(*value);
} else {
    handleError();
}

// With value_or
int value = parseInt(input).value_or(0);
```

### std::variant

```cpp
#include <variant>

using ConfigValue = std::variant<int, double, QString, bool>;

struct ConfigVisitor {
    QString operator()(int v) { return QString::number(v); }
    QString operator()(double v) { return QString::number(v); }
    QString operator()(const QString &v) { return v; }
    QString operator()(bool v) { return v ? "true" : "false"; }
};

QString toString(const ConfigValue &value)
{
    return std::visit(ConfigVisitor{}, value);
}
```

### std::string_view (use with QString carefully)

```cpp
#include <string_view>

// For pure C++ interfaces
void processData(std::string_view data);

// Qt integration - convert at boundaries
QString qstr = "Hello";
std::string_view sv = qstr.toStdString();  // careful: lifetime!

// Better: use QStringView in Qt6
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
void processText(QStringView text);
#endif
```

### Inline Variables

```cpp
// Header-only constants
class Constants
{
public:
    static inline const QString DefaultHost = "localhost";
    static inline constexpr int DefaultPort = 8080;
    static inline constexpr int MaxRetries = 3;
};
```

### Fold Expressions

```cpp
template<typename... Args>
void logAll(Args&&... args)
{
    (qDebug() << ... << args);
}

template<typename... Ts>
bool allPositive(Ts... values)
{
    return (... && (values > 0));
}
```

## C++20 Features (Optional, Qt6 recommended)

### Concepts

```cpp
#include <concepts>

template<typename T>
concept Serializable = requires(T t, QDataStream &stream) {
    { stream << t } -> std::same_as<QDataStream &>;
    { stream >> t } -> std::same_as<QDataStream &>;
};

template<Serializable T>
void save(const T &value, const QString &path)
{
    QFile file(path);
    if (file.open(QIODevice::WriteOnly)) {
        QDataStream stream(&file);
        stream << value;
    }
}
```

### Ranges

```cpp
#include <ranges>
#include <algorithm>

std::vector<int> values = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Filter and transform
auto result = values
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::transform([](int n) { return n * n; });

for (int v : result) {
    qDebug() << v;  // 4, 16, 36, 64, 100
}
```

### Coroutines (for async patterns)

```cpp
#include <coroutine>
#include <QFuture>

// Qt6 has QCoro library for coroutine support
// Example with hypothetical syntax:
QCoro::Task<QByteArray> fetchData(const QString &url)
{
    QNetworkAccessManager manager;
    QNetworkReply *reply = manager.get(QNetworkRequest(url));

    co_await reply;  // suspend until reply finished

    co_return reply->readAll();
}
```

### Three-way Comparison (Spaceship Operator)

```cpp
#include <compare>

struct Version {
    int major, minor, patch;

    auto operator<=>(const Version &) const = default;
};

Version v1{1, 2, 3};
Version v2{1, 3, 0};

if (v1 < v2) {
    qDebug() << "v1 is older";
}
```

## RAII Patterns

### Scope Guards

```cpp
// Using std::unique_ptr with custom deleter
auto fileGuard = std::unique_ptr<QFile, void(*)(QFile*)>(
    file,
    [](QFile *f) { f->close(); delete f; }
);

// Simple scope guard
class ScopeGuard {
public:
    explicit ScopeGuard(std::function<void()> cleanup)
        : m_cleanup(std::move(cleanup)) {}
    ~ScopeGuard() { if (m_cleanup) m_cleanup(); }

    void dismiss() { m_cleanup = nullptr; }

private:
    std::function<void()> m_cleanup;
};

// Usage
void process() {
    resource->acquire();
    ScopeGuard guard([&]() { resource->release(); });

    // ... work ...
    // resource automatically released at scope end
}
```

### Smart Pointers with Qt

```cpp
// For non-QObject classes, use std smart pointers
std::unique_ptr<DataBuffer> buffer = std::make_unique<DataBuffer>();
std::shared_ptr<Config> config = std::make_shared<Config>();

// For QObject-derived, parent-child is often sufficient
auto *widget = new QWidget(parent);  // parent manages lifetime

// For QObject without parent, use QPointer for observation
QPointer<QTimer> timer = new QTimer();  // must delete manually or set parent

// Qt5 RAII for QObjects
QScopedPointer<QTimer> timer(new QTimer());
```

## Error Handling Patterns

### Expected/Result Type (C++23, or use library)

```cpp
// Using std::expected (C++23) or tl::expected
#include <expected>

std::expected<Data, QString> loadConfig(const QString &path)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        return std::unexpected(file.errorString());
    }

    QJsonParseError error;
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &error);
    if (error.error != QJsonParseError::NoError) {
        return std::unexpected(error.errorString());
    }

    return Data::fromJson(doc.object());
}

// Usage
auto result = loadConfig("config.json");
if (result) {
    useConfig(*result);
} else {
    qWarning() << "Failed:" << result.error();
}
```

### Exception-Safe Code

```cpp
// Qt prefers error codes over exceptions, but when using exceptions:
void processFile(const QString &path)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        throw std::runtime_error(file.errorString().toStdString());
    }

    // RAII ensures file is closed even if exception thrown
    auto data = file.readAll();
    // ... process data (may throw) ...
}  // file automatically closed here
```

## Template Patterns

### CRTP (Curiously Recurring Template Pattern)

```cpp
template<typename Derived>
class Singleton {
public:
    static Derived &instance() {
        static Derived instance;
        return instance;
    }

protected:
    Singleton() = default;
    ~Singleton() = default;

    Singleton(const Singleton &) = delete;
    Singleton &operator=(const Singleton &) = delete;
};

class AppSettings : public Singleton<AppSettings> {
    friend class Singleton<AppSettings>;
    // ...
};
```

### Type Traits for Qt Types

```cpp
// Check if type is a QObject
template<typename T>
constexpr bool is_qobject_v = std::is_base_of_v<QObject, T>;

// Check if type has Qt metatype
template<typename T>
constexpr bool is_metatype_v = !std::is_same_v<
    decltype(qMetaTypeId<T>()),
    void
>;
```
