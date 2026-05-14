---
name: cpp-qt-architect
effort: xhigh
description: This skill should be used when consulting on C++/Qt app architecture and design decisions. Use this before starting a new feature, when facing design decisions mid-implementation, or when planning refactors for Qt-based firmware, client, or server applications. Provides component hierarchies, signal/slot patterns, Qt5↔Qt6 migration guidance, and cross-compilation strategies with ASCII diagrams, decision matrices, and code scaffolding.
---

# C++/Qt Architect
## Overview

Expert architectural consultation for C++ applications using the Qt framework. This skill helps developers think through app architecture before writing code, covering desktop clients, embedded systems (Raspberry Pi), and server components. Provides structured analysis, pattern recommendations, and concrete implementation guidance for both Qt5 and Qt6 projects.

## When to Use This Skill

Invoke this skill when:
- Starting a new Qt-based feature and need to plan the architecture
- Facing a design decision mid-implementation (signal/slot design, state management, threading)
- Planning a refactor or Qt5 → Qt6 migration
- Unsure which Qt patterns to apply (Widgets vs QML, networking approach)
- Need to understand cross-compilation for Raspberry Pi targets
- Designing client-server communication in Qt

## Core Capabilities

### 0. Architecture Document Discovery

**Before starting any consultation**, search for existing architecture documentation in the project:

1. **Search locations** (in order of priority):
   - `./ARCHITECTURE.md` or `./Architecture.md`
   - `./docs/ARCHITECTURE.md` or `./docs/architecture.md`
   - `./README.md` (may contain architecture section)

2. **Use Glob to find architecture docs:**
   ```
   Glob pattern: "**/[Aa]rchitecture*.md"
   Glob pattern: "**/ARCHITECTURE.md"
   ```

3. **If found**, read and incorporate:
   - Existing patterns and conventions
   - Qt version in use (Qt5 or Qt6)
   - Build system configuration
   - Target platforms
   - Reference the document in recommendations

4. **If not found**, note this and offer to help create one after the consultation.

### 1. Architectural Analysis

When presented with a feature or problem:

1. **Discover existing architecture** - Search for ARCHITECTURE.md (see above)
2. **Clarify requirements** - Use AskUserQuestion prompt forms (see below)
3. **Identify components** - Break down into UI, Controllers, Models, Services
4. **Map signal/slot connections** - How components communicate
5. **Recommend patterns** - MVC, MVVM, Service Layer, etc.
6. **Provide scaffolding** - Starter code structure

### 2. Pattern Recommendations

**Qt Object Model**
- `QObject` - Base for all Qt objects with signals/slots
- `Q_OBJECT` macro - Required for MOC to process signals/slots
- `Q_PROPERTY` - Property system for QML bindings
- `QPointer` - Weak pointer for QObject-derived classes
- Parent-child ownership - Automatic memory management

**Signal/Slot Patterns**
- Direct connections (same thread) vs queued connections (cross-thread)
- Signal chaining for complex workflows
- Lambda connections for inline handlers
- Disconnect patterns for cleanup

**Architecture Patterns**
- **MVC** - Model-View-Controller with Qt Model/View framework
- **MVVM** - For QML applications with C++ backend
- **Service Layer** - Business logic behind interfaces
- **Plugin Architecture** - Extensibility via QPluginLoader

**Threading Patterns**
- `QThread` with worker objects (moveToThread)
- `QtConcurrent` for parallel operations
- `QThreadPool` for task-based parallelism
- Thread-safe signal/slot across threads

### 3. Qt5 ↔ Qt6 Compatibility

**Key Differences:**
| Feature | Qt5 | Qt6 |
|---------|-----|-----|
| CMake | Optional, qmake primary | Primary build system |
| String handling | QString implicit Latin1 | Explicit encoding |
| Container behavior | COW everywhere | More move semantics |
| QML imports | versioned | unversioned |
| QRegExp | Available | Removed (use QRegularExpression) |
| Qt3D, Charts | Separate modules | Integrated |

**Migration Strategy:**
1. Enable Qt5 deprecation warnings: `QT_DISABLE_DEPRECATED_BEFORE`
2. Run `clazy` static analyzer for Qt-specific issues
3. Address one module at a time
4. Maintain compat macros where needed: `#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)`

### 4. Reference Documentation

Load reference files for detailed guidance:

- **Qt Patterns**: `Read: references/qt-patterns.md`
- **C++ Standards**: `Read: references/cpp-standards.md`
- **Raspberry Pi**: `Read: references/raspberry-pi.md`
- **Client-Server**: `Read: references/client-server.md`
- **qmake Patterns**: `Read: references/qmake-patterns.md`
- **Testing**: `Read: references/testing-patterns.md`

### 5. Deliverables

When consulting on architecture, provide:

**ASCII Component Diagrams**
```
┌─────────────────────────────────────────────────────┐
│                     Application                      │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐         ┌─────────────────────────┐│
│  │  MainWindow │────────▶│    DeviceController     ││
│  │  (QWidget)  │  signal │      (QObject)          ││
│  └─────────────┘         └─────────────────────────┘│
│         │                          │                │
│         │                          │ signal         │
│         ▼                          ▼                │
│  ┌─────────────┐         ┌─────────────────────────┐│
│  │ StatusPanel │         │    DeviceService        ││
│  │  (QWidget)  │         │   (runs in QThread)     ││
│  └─────────────┘         └─────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**Decision Matrices**
| Approach | Complexity | Testability | Qt5/Qt6 Compat |
|----------|------------|-------------|----------------|
| Widgets only | Low | Medium | High |
| QML + C++ | Medium | High | Medium |
| Pure C++ (no UI) | Low | Very High | High |

**Code Scaffolding**
```cpp

#pragma once

#include <QObject>
#include <QThread>

class DeviceController : public QObject
{
    Q_OBJECT

public:
    explicit DeviceController(QObject *parent = nullptr);
    ~DeviceController() override;

signals:
    void connected();
    void disconnected();
    void dataReceived(const QByteArray &data);
    void errorOccurred(const QString &message);

public slots:
    void connectToDevice(const QString &address);
    void sendCommand(const QByteArray &command);
    void disconnect();

private:
    QThread m_workerThread;
    // Worker object lives in m_workerThread
};
```

## Consultation Workflow

### Step 1: Discover Existing Architecture

Before asking questions, search for architecture documentation:
```
Glob: "**/[Aa]rchitecture*.md"
Glob: "**/ARCHITECTURE.md"
```

Also check for `.pro` or `CMakeLists.txt` to understand the build system and Qt version.

### Step 2: Gather Requirements via Prompt Forms

**Use the AskUserQuestion tool** to collect clarifying information.

**Initial Context Form:**
```
AskUserQuestion with 2-4 questions:

1. Component Type (header: "Component")
   - Desktop GUI (Qt Widgets)
   - Desktop GUI (QML/Qt Quick)
   - Embedded/headless service
   - Server/daemon
   - Library/plugin

2. Qt Version (header: "Qt Version")
   - Qt5 only
   - Qt6 only
   - Both Qt5 and Qt6 (need compat)

3. Target Platform (header: "Platform")
   - Desktop (Windows/macOS/Linux)
   - Raspberry Pi
   - Cross-platform (multiple targets)
   - Embedded Linux (other)

4. Communication (header: "IPC/Network")
   - Serial port (QSerialPort)
   - TCP/UDP sockets
   - WebSocket
   - HTTP REST API
   - D-Bus
   - No networking needed
```

### Step 3: Analyze and Recommend

1. **Break down components** - Identify all UI, Controllers, Models, Services needed
2. **Map signal/slot connections** - Draw component diagram showing communication
3. **Choose patterns** - Recommend architecture with rationale
4. **Identify thread boundaries** - Note which components need their own thread
5. **Address Qt5/Qt6 compatibility** - If both versions needed

### Step 4: Provide Implementation Guidance

- **File structure** - Where each component lives
- **Interface definitions** - Abstract base classes for testability
- **Starter code** - Scaffolding for key pieces
- **qmake configuration** - .pro file setup
- **Testing strategy** - How to unit test with QtTest

## C++17 Best Practices

### Modern C++ in Qt Context
- Use `auto` for iterator types and complex template types
- Prefer `std::unique_ptr` and `std::shared_ptr` for non-QObject classes
- Use `QPointer<T>` for QObject-derived classes (safer than raw pointers)
- Structured bindings: `auto [key, value] = map.first();`
- `if constexpr` for compile-time branching
- `std::optional` for nullable values

### Qt-Specific Idioms
- Raw pointers are OK when Qt parent-child ownership is used
- Use `QScopedPointer` for RAII in Qt5
- Prefer `QString::arg()` over string concatenation
- Use `qDebug()` with categories for logging

## Example Consultation

**User**: "I need to build a client that connects to a Raspberry Pi server over TCP and displays sensor data."

**Architect Response**:

Let me help you design the sensor client architecture.

**Step 1: Check for architecture docs**
```
Glob: "**/[Aa]rchitecture*.md"
→ Not found
```

**Step 2: Gather requirements via prompt form**
```
AskUserQuestion:

1. UI Framework (header: "UI")
   - Qt Widgets
   - QML/Qt Quick
   - Hybrid (Widgets embedding QML)

2. Data Rate (header: "Data Rate")
   - Low (< 1 Hz)
   - Medium (1-60 Hz)
   - High (> 60 Hz, need buffering)

3. History (header: "Data History")
   - Live values only
   - Store locally for charts
   - Persist to database

4. Connection (header: "Connection")
   - Always connected
   - Reconnect on failure
   - Manual connect/disconnect
```

*User selects: Qt Widgets, Medium rate, Store locally for charts, Reconnect on failure*

**Proposed Architecture**:

```
┌──────────────────────────────────────────────────────┐
│                  SensorClientApp                      │
├──────────────────────────────────────────────────────┤
│  ┌──────────────┐        ┌─────────────────────────┐ │
│  │  MainWindow  │───────▶│  SensorDisplayWidget    │ │
│  │              │        │  - Real-time chart      │ │
│  └──────────────┘        └─────────────────────────┘ │
│         │                           ▲                │
│         │                           │ signal         │
│         ▼                           │                │
│  ┌──────────────┐        ┌─────────────────────────┐ │
│  │ConnectionMgr │◀──────▶│   SensorDataModel       │ │
│  │ (reconnect)  │ signal │   (QAbstractTableModel) │ │
│  └──────────────┘        └─────────────────────────┘ │
│         │                           │                │
│         ▼                           ▼                │
│  ┌──────────────┐        ┌─────────────────────────┐ │
│  │ TcpClient    │        │   DataStore             │ │
│  │ (in QThread) │        │   (SQLite via QtSql)    │ │
│  └──────────────┘        └─────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

**Key Decisions**:
- `TcpClient` runs in dedicated thread for non-blocking I/O
- `ConnectionMgr` handles reconnection logic with exponential backoff
- `SensorDataModel` adapts data for both table and chart views
- Queued signal/slot connections cross thread boundaries safely

**File Structure**:
```
src/
├── main.cpp
├── app/
│   ├── MainWindow.h/.cpp
│   └── ConnectionManager.h/.cpp
├── network/
│   ├── TcpClient.h/.cpp
│   └── Protocol.h/.cpp
├── data/
│   ├── SensorDataModel.h/.cpp
│   └── DataStore.h/.cpp
└── widgets/
    └── SensorDisplayWidget.h/.cpp
```

Would you like me to scaffold the TcpClient with thread-safe signal/slot communication?

## Next Phase

After architecture consultation:
- Use `/implement` to begin coding with the agreed architecture
- Create ARCHITECTURE.md to document decisions for future reference
