# Qt Patterns Reference

## Signal/Slot Patterns

### Basic Connection Syntax

**Qt5 Style (SIGNAL/SLOT macros):**
```cpp
// Works but no compile-time checking
connect(sender, SIGNAL(valueChanged(int)), receiver, SLOT(updateValue(int)));
```

**Modern Style (Qt5+, recommended):**
```cpp
// Compile-time type checking, refactor-safe
connect(sender, &Sender::valueChanged, receiver, &Receiver::updateValue);

// With lambda
connect(button, &QPushButton::clicked, this, [this]() {
    handleClick();
});

// With context object for automatic disconnect
connect(timer, &QTimer::timeout, widget, [widget]() {
    widget->update();
});
```

### Connection Types

```cpp
// Direct: slot called immediately in sender's thread (default for same-thread)
connect(sender, &Sender::signal, receiver, &Receiver::slot, Qt::DirectConnection);

// Queued: slot called in receiver's event loop (default for cross-thread)
connect(sender, &Sender::signal, receiver, &Receiver::slot, Qt::QueuedConnection);

// BlockingQueued: sender blocks until slot completes (cross-thread only)
connect(sender, &Sender::signal, receiver, &Receiver::slot, Qt::BlockingQueuedConnection);

// UniqueConnection: prevents duplicate connections
connect(sender, &Sender::signal, receiver, &Receiver::slot, Qt::UniqueConnection);
```

### Disconnection Patterns

```cpp
// Disconnect all signals from sender to receiver
disconnect(sender, nullptr, receiver, nullptr);

// Disconnect specific signal
disconnect(sender, &Sender::signal, receiver, &Receiver::slot);

// Store connection for later disconnect
QMetaObject::Connection conn = connect(sender, &Sender::signal, receiver, &Receiver::slot);
// ...later...
disconnect(conn);

// Auto-disconnect when lambda captures context object that is destroyed
connect(sender, &Sender::signal, contextObj, [=]() { /* ... */ });
```

## QObject Ownership

### Parent-Child Relationship

```cpp
// Child is automatically deleted when parent is deleted
QWidget *parent = new QWidget();
QPushButton *button = new QPushButton("Click", parent);  // parent owns button

// Reparenting
button->setParent(newParent);  // ownership transferred

// Deleting removes from parent's children
delete button;  // safe, parent's child list updated
```

### Safe Pointer Patterns

```cpp
// QPointer - weak pointer for QObjects, becomes null when object deleted
QPointer<QWidget> widget = new QWidget();
if (widget) {  // check before use
    widget->show();
}

// QScopedPointer - RAII for non-parented objects (Qt5)
QScopedPointer<MyClass> obj(new MyClass());
// automatically deleted at scope end

// std::unique_ptr works fine for non-QObject classes
std::unique_ptr<DataProcessor> processor = std::make_unique<DataProcessor>();
```

## Property System (Q_PROPERTY)

### Declaring Properties

```cpp
class Device : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)
    Q_PROPERTY(int sensorValue READ sensorValue NOTIFY sensorValueChanged)

public:
    QString name() const { return m_name; }
    void setName(const QString &name) {
        if (m_name != name) {
            m_name = name;
            emit nameChanged();
        }
    }

    bool isConnected() const { return m_connected; }
    int sensorValue() const { return m_sensorValue; }

signals:
    void nameChanged();
    void connectedChanged();
    void sensorValueChanged();

private:
    QString m_name;
    bool m_connected = false;
    int m_sensorValue = 0;
};
```

### Using Properties

```cpp
// Type-safe access
QString name = device->name();
device->setName("Sensor A");

// Dynamic access (useful for QML, serialization)
QVariant value = device->property("name");
device->setProperty("name", "Sensor B");
```

## Qt Widgets Patterns

### Widget Composition

```cpp
class ControlPanel : public QWidget
{
    Q_OBJECT

public:
    explicit ControlPanel(QWidget *parent = nullptr)
        : QWidget(parent)
    {
        auto *layout = new QVBoxLayout(this);

        m_statusLabel = new QLabel("Ready", this);
        m_startButton = new QPushButton("Start", this);
        m_stopButton = new QPushButton("Stop", this);

        layout->addWidget(m_statusLabel);
        layout->addWidget(m_startButton);
        layout->addWidget(m_stopButton);

        connect(m_startButton, &QPushButton::clicked, this, &ControlPanel::onStart);
        connect(m_stopButton, &QPushButton::clicked, this, &ControlPanel::onStop);
    }

signals:
    void startRequested();
    void stopRequested();

private slots:
    void onStart() {
        m_statusLabel->setText("Running...");
        emit startRequested();
    }

    void onStop() {
        m_statusLabel->setText("Stopped");
        emit stopRequested();
    }

private:
    QLabel *m_statusLabel;
    QPushButton *m_startButton;
    QPushButton *m_stopButton;
};
```

### Model/View Pattern

```cpp
// Custom model for sensor data
class SensorDataModel : public QAbstractTableModel
{
    Q_OBJECT

public:
    explicit SensorDataModel(QObject *parent = nullptr);

    int rowCount(const QModelIndex &parent = QModelIndex()) const override;
    int columnCount(const QModelIndex &parent = QModelIndex()) const override;
    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role) const override;

public slots:
    void addReading(const SensorReading &reading);
    void clear();

private:
    QVector<SensorReading> m_readings;
};

// Usage
auto *model = new SensorDataModel(this);
auto *view = new QTableView(this);
view->setModel(model);
```

## QML/C++ Integration

### Exposing C++ to QML

```cpp
// Register type for QML
qmlRegisterType<DeviceController>("MyApp", 1, 0, "DeviceController");

// Register singleton
qmlRegisterSingletonType<AppSettings>("MyApp", 1, 0, "Settings",
    [](QQmlEngine *, QJSEngine *) -> QObject * {
        return new AppSettings();
    });

// Context property (instance)
engine.rootContext()->setContextProperty("deviceController", controller);
```

### QML Usage

```qml
import MyApp 1.0

Item {
    DeviceController {
        id: controller
        onConnected: statusText.text = "Connected"
        onDataReceived: chart.addPoint(data)
    }

    Text {
        id: statusText
        text: controller.connected ? "Online" : "Offline"
    }

    Button {
        text: "Connect"
        onClicked: controller.connectToDevice(addressField.text)
    }
}
```

## Qt5 ↔ Qt6 Compatibility Macros

```cpp
// Version-dependent code
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    // Qt6 code
    #include <QStringView>
#else
    // Qt5 code
    #include <QStringRef>
#endif

// Common compatibility header pattern
// compat.h
#pragma once

#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    #define QT_SKIP_EMPTY_PARTS Qt::SkipEmptyParts
#else
    #define QT_SKIP_EMPTY_PARTS QString::SkipEmptyParts
#endif

// Usage
QStringList parts = str.split(',', QT_SKIP_EMPTY_PARTS);
```

## Event Handling

### Custom Events

```cpp
// Define custom event type
class DataEvent : public QEvent
{
public:
    static const QEvent::Type Type;

    explicit DataEvent(const QByteArray &data)
        : QEvent(Type), m_data(data) {}

    QByteArray data() const { return m_data; }

private:
    QByteArray m_data;
};

const QEvent::Type DataEvent::Type =
    static_cast<QEvent::Type>(QEvent::registerEventType());

// Post event to object
QCoreApplication::postEvent(receiver, new DataEvent(data));

// Handle in receiver
bool MyWidget::event(QEvent *event)
{
    if (event->type() == DataEvent::Type) {
        auto *dataEvent = static_cast<DataEvent *>(event);
        processData(dataEvent->data());
        return true;
    }
    return QWidget::event(event);
}
```

### Event Filters

```cpp
// Install filter
button->installEventFilter(this);

// Filter implementation
bool MyWidget::eventFilter(QObject *watched, QEvent *event)
{
    if (watched == button && event->type() == QEvent::MouseButtonPress) {
        // Handle before button gets the event
        return true;  // consume event
    }
    return QWidget::eventFilter(watched, event);  // pass through
}
```
