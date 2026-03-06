
# Security Checks
C++ security issues are particularly dangerous because they often lead to undefined behavior — crashes, data corruption, or exploitable vulnerabilities that silently compile.

## Buffer Overflows

The classic C/C++ vulnerability. Occurs when writing beyond allocated memory.

**Bad — unbounded copy:**
```cpp
char buffer[256];
strcpy(buffer, userInput.toLocal8Bit().data());  // No bounds check
```

**Bad — off-by-one in loop:**
```cpp
char buffer[SIZE];
for (int i = 0; i <= SIZE; i++) {  // <= writes one past end
    buffer[i] = data[i];
}
```

**Good — use safe alternatives:**
```cpp
// Best: use QString/QByteArray — no manual buffer management
QString buffer = userInput;

// If raw buffer needed:
QByteArray buffer = userInput.toUtf8();

// If C API required:
std::vector<char> buffer(userInput.size() + 1);
std::strncpy(buffer.data(), userInput.toLocal8Bit().data(), buffer.size() - 1);
buffer.back() = '\0';
```

**Red flags to grep for:**
- `strcpy`, `strcat`, `sprintf`, `gets` — always unbounded
- `strncpy`, `snprintf` — safer but check the size argument
- Fixed-size `char[]` buffers receiving external data

## Integer Overflow

Signed integer overflow is undefined behavior in C++. Unsigned wraps silently.

**Bad — size calculation overflow:**
```cpp
int width = getUserWidth();    // Could be INT_MAX
int height = getUserHeight();  // Could be INT_MAX
int size = width * height;     // OVERFLOW: undefined behavior
char* buffer = new char[size]; // Allocates wrong amount
```

**Good — check before arithmetic:**
```cpp
int width = getUserWidth();
int height = getUserHeight();
if (width > 0 && height > 0 && width <= INT_MAX / height) {
    size_t size = static_cast<size_t>(width) * static_cast<size_t>(height);
    auto buffer = std::make_unique<char[]>(size);
}
```

**Bad — signed/unsigned comparison:**
```cpp
int index = getUserIndex();       // Could be negative
if (index < vector.size()) {      // WARNING: signed/unsigned comparison
    return vector[index];          // Negative index → huge positive → out of bounds
}
```

**Good:**
```cpp
int index = getUserIndex();
if (index >= 0 && static_cast<size_t>(index) < vector.size()) {
    return vector[static_cast<size_t>(index)];
}
```

## Format String Vulnerabilities

**Bad — user input as format string:**
```cpp
QString userMessage = getUserInput();
qDebug(userMessage.toLocal8Bit().data());  // User controls format string
printf(userInput.c_str());                 // Same problem
```

**Good — format string is literal:**
```cpp
qDebug() << userMessage;                    // No format interpretation
qDebug("%s", userMessage.toLocal8Bit().data());  // %s is safe
printf("%s", userInput.c_str());            // Explicit format
```

## Command Injection

**Bad — user input in shell command:**
```cpp
QString filename = getUserFilename();
QProcess::execute("convert " + filename + " output.png");
// If filename is "; rm -rf /" → disaster
```

**Bad — system() with user input:**
```cpp
std::string cmd = "ls " + userPath;
system(cmd.c_str());  // Full shell interpretation
```

**Good — use argument lists (no shell interpretation):**
```cpp
QString filename = getUserFilename();
QProcess process;
process.start("convert", QStringList() << filename << "output.png");
// Arguments are passed directly, no shell involved
```

**Good — validate input:**
```cpp
QString filename = getUserFilename();
// Whitelist approach: only allow safe characters
static const QRegularExpression safePattern("^[a-zA-Z0-9._-]+$");
if (!safePattern.match(filename).hasMatch()) {
    qWarning() << "Invalid filename rejected";
    return;
}
```

## Path Traversal

**Bad — user controls file path:**
```cpp
QString filename = request.param("file");
QFile file("/data/uploads/" + filename);  // filename could be "../../etc/passwd"
file.open(QIODevice::ReadOnly);
```

**Good — validate and canonicalize:**
```cpp
QString filename = request.param("file");
QFileInfo info("/data/uploads/" + filename);
QString canonical = info.canonicalFilePath();

// Verify the resolved path is still within the allowed directory
if (!canonical.startsWith("/data/uploads/")) {
    qWarning() << "Path traversal attempt rejected";
    return;
}
QFile file(canonical);
```

## Use-After-Free

**Bad — using object after deletion:**
```cpp
Widget* widget = new Widget();
connect(button, &QPushButton::clicked, [widget]() {
    widget->update();  // widget may be deleted by the time this fires
});
delete widget;
```

**Good — use QPointer for safety:**
```cpp
QPointer<Widget> widget = new Widget(parent);
connect(button, &QPushButton::clicked, [widget]() {
    if (widget) {
        widget->update();
    }
});
```

## Hardcoded Credentials

**Bad:**
```cpp
const QString API_KEY = "sk-1234567890abcdef";
const QString DB_PASSWORD = "hunter2";
```

**Good:**
```cpp
const QString apiKey = qEnvironmentVariable("API_KEY");
const QString dbPassword = qEnvironmentVariable("DB_PASSWORD");

if (apiKey.isEmpty() || dbPassword.isEmpty()) {
    qFatal("Required environment variables not set");
}
```

## Uninitialized Variables

**Bad — uninitialized variable used in conditional:**
```cpp
int status;  // Uninitialized
if (someCondition) {
    status = 0;
}
// If someCondition is false, status is garbage
processStatus(status);  // UNDEFINED BEHAVIOR
```

**Good:**
```cpp
int status = -1;  // Always initialize
if (someCondition) {
    status = 0;
}
processStatus(status);
```

## Unsafe Deserialization

**Bad — trusting external data format:**
```cpp
QDataStream stream(&networkData, QIODevice::ReadOnly);
int size;
stream >> size;
QVector<int> data(size);  // If size is 2 billion, this allocates 8GB
for (int i = 0; i < size; i++) {
    stream >> data[i];
}
```

**Good — validate before allocating:**
```cpp
QDataStream stream(&networkData, QIODevice::ReadOnly);
int size;
stream >> size;

constexpr int MAX_REASONABLE_SIZE = 10000;
if (size < 0 || size > MAX_REASONABLE_SIZE) {
    qWarning() << "Suspicious data size rejected:" << size;
    return;
}

QVector<int> data(size);
```

## Cryptographic Weaknesses

**Bad:**
```cpp
// Weak hash
QByteArray hash = QCryptographicHash::hash(password, QCryptographicHash::Md5);

// Predictable random
qsrand(QTime::currentTime().msec());
int token = qrand();
```

**Good:**
```cpp
// Strong hash (SHA-256 minimum; for passwords use bcrypt/argon2 via external lib)
QByteArray hash = QCryptographicHash::hash(password, QCryptographicHash::Sha256);

// Cryptographic random (Qt 5.10+)
quint32 token = QRandomGenerator::securelySeeded()->generate();
```

## Review Checklist

- [ ] No `strcpy`, `strcat`, `sprintf`, `gets` — use bounded or Qt alternatives
- [ ] Integer arithmetic checked for overflow before use in allocations
- [ ] No signed/unsigned comparison bugs
- [ ] No user input as format string
- [ ] No user input in `system()` or `QProcess::execute()` shell commands
- [ ] File paths validated against traversal (`../`)
- [ ] No use-after-free (QPointer for observed QObjects)
- [ ] No hardcoded credentials (use environment variables)
- [ ] All variables initialized before use
- [ ] External data validated before allocation/processing
- [ ] Strong cryptographic algorithms (no MD5/SHA1 for security)
- [ ] Cryptographic random for tokens (not qrand/srand)
