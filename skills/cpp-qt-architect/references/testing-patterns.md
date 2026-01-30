# Testing Patterns Reference

## QtTest Framework

### Basic Test Structure

```cpp
// tst_devicecontroller.cpp
#include <QtTest>
#include "devicecontroller.h"

class TestDeviceController : public QObject
{
    Q_OBJECT

private slots:
    // Special slots
    void initTestCase();    // Before all tests
    void cleanupTestCase(); // After all tests
    void init();            // Before each test
    void cleanup();         // After each test

    // Test methods (must be private slots)
    void testConnect();
    void testSendCommand();
    void testDisconnect();
    void testReconnection();

private:
    DeviceController *m_controller;
};

void TestDeviceController::initTestCase()
{
    // One-time setup
}

void TestDeviceController::cleanupTestCase()
{
    // One-time cleanup
}

void TestDeviceController::init()
{
    // Per-test setup
    m_controller = new DeviceController();
}

void TestDeviceController::cleanup()
{
    // Per-test cleanup
    delete m_controller;
    m_controller = nullptr;
}

void TestDeviceController::testConnect()
{
    // Arrange
    QSignalSpy spy(m_controller, &DeviceController::connected);

    // Act
    m_controller->connectToDevice("test-device");

    // Assert
    QVERIFY(spy.wait(1000));  // Wait up to 1 second
    QCOMPARE(m_controller->isConnected(), true);
}

void TestDeviceController::testSendCommand()
{
    // ...
}

QTEST_MAIN(TestDeviceController)
#include "tst_devicecontroller.moc"
```

### QtTest Macros

```cpp
// Verification macros
QVERIFY(condition);                     // Assert condition is true
QVERIFY2(condition, message);           // With custom message
QCOMPARE(actual, expected);             // Compare with nice output
QCOMPARE_EQ(actual, expected);          // Qt6: ==
QCOMPARE_NE(actual, expected);          // Qt6: !=
QCOMPARE_LT(actual, expected);          // Qt6: <
QCOMPARE_LE(actual, expected);          // Qt6: <=
QCOMPARE_GT(actual, expected);          // Qt6: >
QCOMPARE_GE(actual, expected);          // Qt6: >=

// Floating point comparison
QCOMPARE(actual, expected);             // Uses fuzzy comparison
QVERIFY(qFuzzyCompare(a, b));          // Explicit fuzzy

// Expected failures
QEXPECT_FAIL("", "Known bug #123", Continue);  // Continue after fail
QEXPECT_FAIL("", "Known bug #123", Abort);     // Stop test

// Skip test
QSKIP("Feature not implemented yet");

// Fail immediately
QFAIL("This should never happen");
```

### Data-Driven Tests

```cpp
void TestParser::testParse_data()
{
    QTest::addColumn<QString>("input");
    QTest::addColumn<int>("expected");
    QTest::addColumn<bool>("valid");

    QTest::newRow("positive") << "42" << 42 << true;
    QTest::newRow("negative") << "-17" << -17 << true;
    QTest::newRow("zero") << "0" << 0 << true;
    QTest::newRow("empty") << "" << 0 << false;
    QTest::newRow("invalid") << "abc" << 0 << false;
    QTest::newRow("overflow") << "99999999999" << 0 << false;
}

void TestParser::testParse()
{
    QFETCH(QString, input);
    QFETCH(int, expected);
    QFETCH(bool, valid);

    bool ok;
    int result = input.toInt(&ok);

    QCOMPARE(ok, valid);
    if (valid) {
        QCOMPARE(result, expected);
    }
}
```

### Signal Spy

```cpp
void TestSensor::testDataEmission()
{
    Sensor sensor;
    QSignalSpy dataSpy(&sensor, &Sensor::dataReceived);
    QSignalSpy errorSpy(&sensor, &Sensor::errorOccurred);

    // Trigger data emission
    sensor.start();

    // Wait for signal
    QVERIFY(dataSpy.wait(5000));

    // Check signal was emitted
    QCOMPARE(dataSpy.count(), 1);

    // Get signal arguments
    QList<QVariant> arguments = dataSpy.takeFirst();
    QByteArray data = arguments.at(0).toByteArray();
    QVERIFY(data.size() > 0);

    // Verify no errors
    QCOMPARE(errorSpy.count(), 0);
}

// Wait for multiple signals
void TestAsync::testMultipleResponses()
{
    Client client;
    QSignalSpy spy(&client, &Client::responseReceived);

    client.sendBatchRequest(5);

    // Wait until we have 5 responses or timeout
    QTRY_COMPARE_WITH_TIMEOUT(spy.count(), 5, 10000);
}
```

### Testing Async Code

```cpp
void TestNetwork::testAsyncFetch()
{
    NetworkClient client;
    QSignalSpy spy(&client, &NetworkClient::dataReceived);

    client.fetch("http://example.com/api");

    // QTRY macros poll with event processing
    QTRY_VERIFY(spy.count() > 0);
    QTRY_COMPARE(spy.count(), 1);
    QTRY_VERIFY_WITH_TIMEOUT(client.isComplete(), 5000);
}

// Manual event loop control
void TestNetwork::testWithEventLoop()
{
    NetworkClient client;
    QEventLoop loop;

    connect(&client, &NetworkClient::finished, &loop, &QEventLoop::quit);

    client.fetch("http://example.com/api");

    // Set timeout
    QTimer timer;
    timer.setSingleShot(true);
    connect(&timer, &QTimer::timeout, &loop, &QEventLoop::quit);
    timer.start(5000);

    loop.exec();

    QVERIFY(timer.isActive());  // Didn't timeout
    QVERIFY(client.isComplete());
}
```

## Mocking Strategies

### Interface-Based Mocking

```cpp
// Abstract interface
class IDeviceConnection {
public:
    virtual ~IDeviceConnection() = default;
    virtual bool connect(const QString &address) = 0;
    virtual void disconnect() = 0;
    virtual void send(const QByteArray &data) = 0;
    virtual bool isConnected() const = 0;
};

// Production implementation
class TcpConnection : public IDeviceConnection {
    // Real implementation...
};

// Mock implementation
class MockConnection : public IDeviceConnection {
public:
    bool connect(const QString &address) override {
        m_connectCalls.append(address);
        return m_connectResult;
    }

    void disconnect() override {
        m_disconnected = true;
    }

    void send(const QByteArray &data) override {
        m_sentData.append(data);
    }

    bool isConnected() const override {
        return m_connected;
    }

    // Test control
    bool m_connectResult = true;
    bool m_connected = false;
    bool m_disconnected = false;
    QList<QString> m_connectCalls;
    QList<QByteArray> m_sentData;
};

// Test using mock
void TestController::testSendWhenConnected()
{
    auto mock = std::make_unique<MockConnection>();
    mock->m_connected = true;

    DeviceController controller(std::move(mock));
    controller.send("TEST");

    QCOMPARE(mock->m_sentData.count(), 1);
    QCOMPARE(mock->m_sentData.first(), QByteArray("TEST"));
}
```

### Google Mock Integration

```cpp
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <QtTest>

class MockConnection : public IDeviceConnection {
public:
    MOCK_METHOD(bool, connect, (const QString &), (override));
    MOCK_METHOD(void, disconnect, (), (override));
    MOCK_METHOD(void, send, (const QByteArray &), (override));
    MOCK_METHOD(bool, isConnected, (), (const, override));
};

class ControllerTest : public ::testing::Test {
protected:
    void SetUp() override {
        mock = std::make_shared<MockConnection>();
        controller = std::make_unique<DeviceController>(mock);
    }

    std::shared_ptr<MockConnection> mock;
    std::unique_ptr<DeviceController> controller;
};

TEST_F(ControllerTest, SendWhenConnected) {
    using ::testing::Return;
    using ::testing::_;

    EXPECT_CALL(*mock, isConnected())
        .WillRepeatedly(Return(true));
    EXPECT_CALL(*mock, send(_))
        .Times(1);

    controller->send("TEST");
}
```

### Fake Servers for Integration Tests

```cpp
class FakeServer : public QObject {
    Q_OBJECT

public:
    FakeServer(QObject *parent = nullptr)
        : QObject(parent)
        , m_server(new QTcpServer(this))
    {
        connect(m_server, &QTcpServer::newConnection, this, [this]() {
            m_client = m_server->nextPendingConnection();
            connect(m_client, &QTcpSocket::readyRead, this, [this]() {
                m_receivedData.append(m_client->readAll());
                emit dataReceived();
            });
        });
    }

    bool start() {
        return m_server->listen(QHostAddress::LocalHost, 0);
    }

    quint16 port() const {
        return m_server->serverPort();
    }

    void sendToClient(const QByteArray &data) {
        if (m_client) {
            m_client->write(data);
        }
    }

    QByteArray receivedData() const { return m_receivedData; }

signals:
    void dataReceived();

private:
    QTcpServer *m_server;
    QTcpSocket *m_client = nullptr;
    QByteArray m_receivedData;
};

// Usage in test
void TestClient::testCommunication()
{
    FakeServer server;
    QVERIFY(server.start());

    Client client;
    QSignalSpy spy(&client, &Client::connected);

    client.connectTo("localhost", server.port());
    QVERIFY(spy.wait());

    client.send("Hello");
    QVERIFY(QTest::qWaitFor([&]() {
        return server.receivedData().contains("Hello");
    }));

    server.sendToClient("World");
    QTRY_COMPARE(client.lastReceived(), QByteArray("World"));
}
```

## Test Organization

### qmake Test Project

```pro
# tests/tests.pro
QT += testlib network
QT -= gui

CONFIG += qt console warn_on testcase
CONFIG -= app_bundle

TEMPLATE = app
TARGET = tests

# Test sources
SOURCES += \
    main.cpp \
    tst_devicecontroller.cpp \
    tst_protocol.cpp \
    mock_connection.cpp

HEADERS += \
    mock_connection.h

# Include production code
INCLUDEPATH += $$PWD/../src
DEPENDPATH += $$PWD/../src

# Link production library
LIBS += -L$$OUT_PWD/../src -lmyappcore
```

### Test Main for Multiple Test Classes

```cpp
// main.cpp
#include <QtTest>
#include "tst_devicecontroller.h"
#include "tst_protocol.h"
#include "tst_parser.h"

int main(int argc, char *argv[])
{
    int status = 0;
    QCoreApplication app(argc, argv);

    {
        TestDeviceController test;
        status |= QTest::qExec(&test, argc, argv);
    }
    {
        TestProtocol test;
        status |= QTest::qExec(&test, argc, argv);
    }
    {
        TestParser test;
        status |= QTest::qExec(&test, argc, argv);
    }

    return status;
}
```

## Continuous Integration

### Running Tests in CI

```bash
#!/bin/bash
# ci/run_tests.sh

# Build
qmake && make -j$(nproc)

# Run with XML output for CI parsing
./tests -o results.xml,xml

# Or JUnit format
./tests -o results.xml,junitxml

# Verbose output for debugging
./tests -v2 -maxwarnings 0
```

### Coverage with gcov/lcov

```pro
# Enable coverage in debug build
CONFIG(debug, debug|release) {
    QMAKE_CXXFLAGS += --coverage
    QMAKE_LFLAGS += --coverage
}
```

```bash
# Generate coverage report
./tests
lcov --capture --directory . --output-file coverage.info
lcov --remove coverage.info '/usr/*' --output-file coverage.info
genhtml coverage.info --output-directory coverage_html
```

## Best Practices

### Test Naming Convention

```cpp
// Method: test<MethodName>_<scenario>_<expectedBehavior>
void testConnect_validAddress_emitsConnected();
void testConnect_invalidAddress_emitsError();
void testSend_whenDisconnected_queuesMessage();
void testSend_whenConnected_sendsImmediately();
```

### Arrange-Act-Assert Pattern

```cpp
void TestController::testStartMeasurement()
{
    // Arrange
    Controller controller;
    QSignalSpy spy(&controller, &Controller::measurementStarted);

    // Act
    controller.startMeasurement(100);  // 100ms interval

    // Assert
    QVERIFY(spy.wait());
    QVERIFY(controller.isRunning());
    QCOMPARE(controller.interval(), 100);
}
```

### Test Isolation

```cpp
void TestDatabase::init()
{
    // Each test gets fresh database
    m_db = QSqlDatabase::addDatabase("QSQLITE", "test_connection");
    m_db.setDatabaseName(":memory:");
    m_db.open();

    // Initialize schema
    QSqlQuery query(m_db);
    query.exec("CREATE TABLE data (id INTEGER PRIMARY KEY, value TEXT)");
}

void TestDatabase::cleanup()
{
    m_db.close();
    QSqlDatabase::removeDatabase("test_connection");
}
```
