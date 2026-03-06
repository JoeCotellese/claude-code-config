
# Qt-Specific Pitfalls
These are issues that compile and run — until they don't. Qt's meta-object system and event loop have specific rules that, when violated, cause subtle and hard-to-debug failures.

## Missing Q_OBJECT Macro

The Q_OBJECT macro is required for any QObject subclass that declares signals, slots, or uses Q_PROPERTY. Without it, signals won't emit and slots won't connect.

**Bad — missing Q_OBJECT:**
```cpp
class SensorController : public QObject
{
    // No Q_OBJECT macro!
public:
    explicit SensorController(QObject* parent = nullptr);

signals:
    void dataReady(const QByteArray& data);  // Will never emit

public slots:
    void startReading();  // Old-style connect() won't find this
};
```

**Good:**
```cpp
class SensorController : public QObject
{
    Q_OBJECT  // Required for MOC to process this class

public:
    explicit SensorController(QObject* parent = nullptr);

signals:
    void dataReady(const QByteArray& data);

public slots:
    void startReading();
};
```

**Symptoms of missing Q_OBJECT:**
- `connect()` returns false or warns "No such slot"
- `qobject_cast<T*>()` returns nullptr
- Signals appear to emit but no slots fire
- Properties don't work in QML

**After adding Q_OBJECT to an existing class**, you must re-run CMake/qmake so MOC processes the header.

## Blocking the Event Loop

Qt's event loop processes UI events, timers, network I/O, and signal/slot delivery. Blocking it freezes the entire application.

**Bad — blocking call on main thread:**
```cpp
void MainWindow::onFetchClicked()
{
    QNetworkAccessManager manager;
    QNetworkReply* reply = manager.get(QNetworkRequest(url));

    // BAD: Busy-wait blocks the event loop
    while (!reply->isFinished()) {
        QThread::msleep(100);
    }

    processReply(reply);
}
```

**Bad — long computation on main thread:**
```cpp
void MainWindow::onProcessClicked()
{
    // This takes 10 seconds — UI is frozen the entire time
    for (int i = 0; i < 10000000; i++) {
        heavyComputation(i);
    }
}
```

**Good — async with signals:**
```cpp
void MainWindow::onFetchClicked()
{
    auto* reply = m_networkManager->get(QNetworkRequest(url));
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        processReply(reply);
        reply->deleteLater();
    });
}
```

**Good — offload to worker thread:**
```cpp
void MainWindow::onProcessClicked()
{
    QtConcurrent::run([this]() {
        for (int i = 0; i < 10000000; i++) {
            heavyComputation(i);
        }
        // Signal back to main thread when done
        QMetaObject::invokeMethod(this, "onProcessingComplete", Qt::QueuedConnection);
    });
}
```

## Signal/Slot Connection Issues

### Wrong Connection Type for Threading

**Bad — direct connection across threads:**
```cpp
// worker runs in a different thread
connect(worker, &Worker::resultReady, this, &MainWindow::updateUI);
// Default connection type is Auto, which is usually fine.
// But explicitly specifying Direct across threads is a bug:
connect(worker, &Worker::resultReady, this, &MainWindow::updateUI, Qt::DirectConnection);
// updateUI() runs in the worker thread — accessing UI from non-main thread is UB
```

**Good — let Qt choose or specify queued:**
```cpp
// Qt::AutoConnection (default) — automatically uses QueuedConnection across threads
connect(worker, &Worker::resultReady, this, &MainWindow::updateUI);

// Or be explicit:
connect(worker, &Worker::resultReady, this, &MainWindow::updateUI, Qt::QueuedConnection);
```

### Connecting to Deleted Objects

**Bad:**
```cpp
auto* dialog = new QDialog(this);
auto* worker = new Worker();
connect(worker, &Worker::done, dialog, &QDialog::accept);

delete dialog;
worker->start();  // When done emits, dialog is gone → crash
```

**Good — Qt auto-disconnects when receiver is destroyed (for QObject-based connections):**
```cpp
// This is actually safe IF using the 4-arg connect with a QObject receiver:
connect(worker, &Worker::done, dialog, &QDialog::accept);
// Qt automatically disconnects when dialog is destroyed.

// But lambda connections without context object are NOT auto-disconnected:
connect(worker, &Worker::done, [dialog]() {
    dialog->accept();  // DANGEROUS if dialog is deleted
});

// Good — pass context object:
connect(worker, &Worker::done, dialog, [dialog]() {
    dialog->accept();  // Safe: disconnected when dialog is destroyed
});
```

### Old-Style vs New-Style Connections

**Bad — string-based connections (no compile-time checking):**
```cpp
connect(button, SIGNAL(clicked()), this, SLOT(onButtonClicked()));
// Typos compile fine but fail silently at runtime
```

**Good — pointer-to-member (compile-time checked):**
```cpp
connect(button, &QPushButton::clicked, this, &MainWindow::onButtonClicked);
// Typos cause compile errors — catch bugs early
```

## deleteLater() Misuse

**Bad — delete in a slot called by the object being deleted:**
```cpp
void Worker::onError()
{
    cleanup();
    delete this;  // If called from a signal, other slots haven't fired yet → crash
}
```

**Good — use deleteLater:**
```cpp
void Worker::onError()
{
    cleanup();
    deleteLater();  // Scheduled for next event loop iteration — safe
}
```

**When to use deleteLater:**
- Deleting `this` from within a member function
- Deleting the sender from within a slot
- Deleting QNetworkReply in its finished handler

## QTimer Patterns

**Bad — QTimer in wrong thread:**
```cpp
void Worker::startInThread()
{
    m_timer = new QTimer();  // Created in calling thread
    m_timer->start(1000);    // Timer fires in calling thread, not worker thread
}
```

**Good — create timer after moving to thread, or in thread's start:**
```cpp
void Worker::startInThread()
{
    // Timer must be created in the thread where it will run
    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &Worker::doWork);
    m_timer->start(1000);
}
```

**One-shot pattern:**
```cpp
// Deferred execution (next event loop iteration)
QTimer::singleShot(0, this, &Widget::deferredInit);

// Delayed execution
QTimer::singleShot(5000, this, [this]() {
    if (isVisible()) {
        hideTooltip();
    }
});
```

## QString Misuse

**Bad — empty string check:**
```cpp
if (name == "")        // Creates a temporary QString
if (name.size() == 0)  // Works but less idiomatic
```

**Good:**
```cpp
if (name.isEmpty())  // Most efficient and readable
```

**Bad — null vs empty confusion:**
```cpp
QString a;            // Null (and empty)
QString b = "";       // Empty (but not null)
// a == b is TRUE — Qt treats null and empty as equal
// But a.isNull() != b.isNull()
```

**Best practice**: Don't distinguish null from empty. Use `isEmpty()` for all checks.

**Bad — QString::number in loops:**
```cpp
for (int i = 0; i < 1000; i++) {
    labels[i]->setText("Sensor " + QString::number(i));
}
```

**Good — use arg:**
```cpp
for (int i = 0; i < 1000; i++) {
    labels[i]->setText(QString("Sensor %1").arg(i));
}
```

## Event Filter Pitfalls

**Bad — forgetting to call base class:**
```cpp
bool MyWidget::eventFilter(QObject* obj, QEvent* event)
{
    if (event->type() == QEvent::KeyPress) {
        handleKey(static_cast<QKeyEvent*>(event));
        return true;  // Swallows ALL key events — even ones you don't handle
    }
    // Missing: return QWidget::eventFilter(obj, event);
    return false;  // Should call base instead
}
```

**Good:**
```cpp
bool MyWidget::eventFilter(QObject* obj, QEvent* event)
{
    if (event->type() == QEvent::KeyPress) {
        auto* keyEvent = static_cast<QKeyEvent*>(event);
        if (keyEvent->key() == Qt::Key_Escape) {
            handleEscape();
            return true;  // Only swallow the specific event you handle
        }
    }
    return QWidget::eventFilter(obj, event);  // Let base handle everything else
}
```

## Property System

**Bad — Q_PROPERTY without NOTIFY:**
```cpp
class Sensor : public QObject
{
    Q_OBJECT
    Q_PROPERTY(int value READ value WRITE setValue)  // Missing NOTIFY
    // QML bindings won't update when value changes
};
```

**Good:**
```cpp
class Sensor : public QObject
{
    Q_OBJECT
    Q_PROPERTY(int value READ value WRITE setValue NOTIFY valueChanged)

signals:
    void valueChanged();
};
```

## Review Checklist

- [ ] Q_OBJECT macro present on all QObject subclasses with signals/slots/properties
- [ ] No blocking calls on the main/GUI thread
- [ ] Signal/slot connections use new-style (pointer-to-member) syntax
- [ ] Cross-thread connections use QueuedConnection (or AutoConnection default)
- [ ] Lambda connections have a context QObject for auto-disconnect
- [ ] `deleteLater()` used instead of `delete this` in slots
- [ ] QTimer created in the correct thread
- [ ] `isEmpty()` used for string emptiness checks
- [ ] Event filters call base class for unhandled events
- [ ] Q_PROPERTY has NOTIFY signal for QML-exposed properties
- [ ] No direct UI access from worker threads
