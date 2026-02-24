# ABOUTME: Concurrency patterns reference for C++/Qt code reviews.
# ABOUTME: Covers data races, mutexes, deadlocks, Qt threading, and atomic operations.

# Concurrency

Threading bugs are the hardest to find because they're non-deterministic — the code works 99% of the time, then fails in production. Every piece of shared mutable state must be scrutinized.

## Data Races

A data race occurs when two threads access the same memory, at least one writes, and there's no synchronization. This is **undefined behavior** in C++ — not just "wrong results" but anything can happen.

**Bad — unprotected shared state:**
```cpp
class SensorHub : public QObject
{
    QVector<SensorData> m_readings;  // Accessed from multiple threads

public slots:
    void onNewReading(const SensorData& data)
    {
        m_readings.append(data);  // Called from worker thread
    }

    void getLatest() const
    {
        if (!m_readings.isEmpty()) {
            return m_readings.last();  // Called from main thread
            // DATA RACE: concurrent read + write on m_readings
        }
    }
};
```

**Good — mutex protection:**
```cpp
class SensorHub : public QObject
{
    mutable QMutex m_mutex;
    QVector<SensorData> m_readings;

public slots:
    void onNewReading(const SensorData& data)
    {
        QMutexLocker locker(&m_mutex);
        m_readings.append(data);
    }

    SensorData getLatest() const
    {
        QMutexLocker locker(&m_mutex);
        if (!m_readings.isEmpty()) {
            return m_readings.last();
        }
        return {};
    }
};
```

## Mutex Patterns

### Always Use RAII Lock Guards

**Bad — manual lock/unlock:**
```cpp
m_mutex.lock();
processData();       // If this throws, mutex is never unlocked → deadlock
m_mutex.unlock();
```

**Good — RAII lock guard:**
```cpp
{
    QMutexLocker locker(&m_mutex);  // Locked
    processData();
}  // Unlocked automatically, even if processData() throws

// Or with std::mutex:
{
    std::lock_guard<std::mutex> lock(m_mutex);
    processData();
}
```

### Minimize Lock Scope

**Bad — holding lock too long:**
```cpp
QMutexLocker locker(&m_mutex);
auto data = m_sharedData;          // Need lock for this
expensiveComputation(data);        // Don't need lock for this — but holding it
networkRequest(data);              // Definitely don't need lock — blocks other threads
```

**Good — copy under lock, process outside:**
```cpp
SensorData localCopy;
{
    QMutexLocker locker(&m_mutex);
    localCopy = m_sharedData;      // Quick copy under lock
}
expensiveComputation(localCopy);   // No lock needed
networkRequest(localCopy);         // No lock needed
```

### Read-Write Lock for Read-Heavy Workloads

**When many threads read but few write:**
```cpp
class ConfigStore
{
    mutable QReadWriteLock m_lock;
    QHash<QString, QVariant> m_config;

public:
    QVariant get(const QString& key) const
    {
        QReadLocker locker(&m_lock);  // Multiple readers OK
        return m_config.value(key);
    }

    void set(const QString& key, const QVariant& value)
    {
        QWriteLocker locker(&m_lock);  // Exclusive write access
        m_config[key] = value;
    }
};
```

## Deadlocks

### Lock Ordering

**Bad — inconsistent lock ordering:**
```cpp
// Thread 1:
m_mutexA.lock();
m_mutexB.lock();    // Waits for Thread 2 to release B

// Thread 2:
m_mutexB.lock();
m_mutexA.lock();    // Waits for Thread 1 to release A
// DEADLOCK: both threads waiting for each other
```

**Good — consistent ordering:**
```cpp
// Both threads lock in the same order:
// Thread 1:
m_mutexA.lock();
m_mutexB.lock();

// Thread 2:
m_mutexA.lock();    // Same order
m_mutexB.lock();
```

**Better — use std::scoped_lock (C++17):**
```cpp
// Locks both mutexes atomically, avoiding deadlock regardless of order:
std::scoped_lock lock(m_mutexA, m_mutexB);
```

### Self-Deadlock

**Bad — recursive locking on non-recursive mutex:**
```cpp
void outerFunction()
{
    QMutexLocker locker(&m_mutex);
    innerFunction();  // Also tries to lock m_mutex → DEADLOCK
}

void innerFunction()
{
    QMutexLocker locker(&m_mutex);
    // ...
}
```

**Good — use QRecursiveMutex or restructure:**
```cpp
// Option 1: QRecursiveMutex (Qt 5.14+)
QRecursiveMutex m_mutex;

// Option 2 (preferred): Factor out unprotected implementation
void outerFunction()
{
    QMutexLocker locker(&m_mutex);
    innerFunctionLocked();  // Assumes lock is held
}

void innerFunction()
{
    QMutexLocker locker(&m_mutex);
    innerFunctionLocked();
}

void innerFunctionLocked()  // Private, assumes caller holds lock
{
    // ... actual work ...
}
```

## Qt Threading Patterns

### Worker Object Pattern (Preferred)

**Bad — subclassing QThread:**
```cpp
class Worker : public QThread
{
    void run() override
    {
        // Everything runs in the new thread
        // But slots connected to this object run in the CREATING thread
        // This is confusing and error-prone
    }
};
```

**Good — worker object moved to thread:**
```cpp
class Worker : public QObject
{
    Q_OBJECT
public slots:
    void doWork()
    {
        // Runs in the thread this object lives in
        emit resultReady(result);
    }
signals:
    void resultReady(const QByteArray& data);
};

// Setup:
auto* thread = new QThread(this);
auto* worker = new Worker();  // No parent — will be moved
worker->moveToThread(thread);

connect(thread, &QThread::started, worker, &Worker::doWork);
connect(worker, &Worker::resultReady, this, &MainWindow::handleResult);
connect(thread, &QThread::finished, worker, &QObject::deleteLater);
connect(thread, &QThread::finished, thread, &QObject::deleteLater);

thread->start();
```

### QtConcurrent for Simple Parallelism

```cpp
// Fire and forget:
QtConcurrent::run([]() {
    heavyComputation();
});

// With result:
QFuture<int> future = QtConcurrent::run([]() {
    return expensiveCalculation();
});

// Check later:
QFutureWatcher<int>* watcher = new QFutureWatcher<int>(this);
connect(watcher, &QFutureWatcher<int>::finished, this, [watcher, this]() {
    int result = watcher->result();
    updateUI(result);
    watcher->deleteLater();
});
watcher->setFuture(future);
```

### Thread-Safe Signal Emission

**Bad — emitting signal that triggers UI from worker thread:**
```cpp
// In worker thread:
emit updateProgress(50);  // If connected with DirectConnection, modifies UI from worker thread
```

**Good — ensure queued connection:**
```cpp
// Either use default AutoConnection (safe):
connect(worker, &Worker::updateProgress, this, &MainWindow::setProgress);

// Or be explicit:
connect(worker, &Worker::updateProgress, this, &MainWindow::setProgress, Qt::QueuedConnection);

// Or use invokeMethod for one-off cross-thread calls:
QMetaObject::invokeMethod(mainWindow, "setProgress", Qt::QueuedConnection, Q_ARG(int, 50));
```

## Atomic Operations

For simple shared flags or counters, atomics are lighter than mutexes.

**Bad — boolean flag without synchronization:**
```cpp
class Worker : public QObject
{
    bool m_running = false;  // Read and written from different threads

public:
    void stop() { m_running = false; }  // Main thread
    void doWork()
    {
        while (m_running) {  // Worker thread — DATA RACE
            process();
        }
    }
};
```

**Good — atomic flag:**
```cpp
class Worker : public QObject
{
    std::atomic<bool> m_running{false};

public:
    void stop() { m_running.store(false); }
    void doWork()
    {
        while (m_running.load()) {
            process();
        }
    }
};
```

**When to use atomics vs mutexes:**
| Scenario | Use |
|----------|-----|
| Single flag/counter | `std::atomic` |
| Multiple related variables | `QMutex` (need to update atomically together) |
| Complex data structure | `QMutex` or `QReadWriteLock` |
| Counter with relaxed ordering | `std::atomic` with `memory_order_relaxed` |

## Common Threading Anti-Patterns

### Accessing UI from Worker Thread
```cpp
// NEVER DO THIS:
void Worker::run()
{
    m_label->setText("Processing...");  // CRASH or corruption
    m_progressBar->setValue(50);        // Only main thread can touch UI
}
```

### Creating QObjects with Wrong Thread Affinity
```cpp
// BAD: Timer created before moveToThread
auto* worker = new Worker();
worker->m_timer = new QTimer(worker);  // Timer has affinity to creating thread
worker->moveToThread(thread);
// Timer still fires in the original thread!

// GOOD: Create timer after move, or in a slot that runs in the target thread
```

### Forgetting QThread Needs an Event Loop
```cpp
// If your worker uses signals/slots or timers, the thread needs an event loop
// QThread::run() calls exec() by default — don't override run() if you need this
```

## Review Checklist

- [ ] All shared mutable state protected by mutex or atomic
- [ ] Mutexes use RAII lock guards (QMutexLocker, std::lock_guard)
- [ ] Lock scope is minimal (copy under lock, process outside)
- [ ] Consistent lock ordering (or use std::scoped_lock)
- [ ] No UI access from worker threads
- [ ] Worker object pattern used (not QThread subclassing)
- [ ] Signal/slot connections across threads use QueuedConnection
- [ ] QObjects created in correct thread (or moved before use)
- [ ] Simple flags use std::atomic instead of unprotected bool
- [ ] No blocking calls in event loop (use async or worker threads)
- [ ] QThread has event loop if worker uses signals/slots/timers
- [ ] Thread cleanup handled (deleteLater on finished signal)
