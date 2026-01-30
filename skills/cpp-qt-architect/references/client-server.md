# Client-Server Patterns Reference

## TCP Communication

### TCP Server

```cpp
#include <QTcpServer>
#include <QTcpSocket>

class DataServer : public QObject
{
    Q_OBJECT

public:
    explicit DataServer(QObject *parent = nullptr)
        : QObject(parent)
        , m_server(new QTcpServer(this))
    {
        connect(m_server, &QTcpServer::newConnection,
                this, &DataServer::onNewConnection);
    }

    bool start(quint16 port) {
        if (!m_server->listen(QHostAddress::Any, port)) {
            emit error(m_server->errorString());
            return false;
        }
        emit started(port);
        return true;
    }

    void broadcast(const QByteArray &data) {
        for (QTcpSocket *client : m_clients) {
            client->write(data);
        }
    }

signals:
    void started(quint16 port);
    void clientConnected(const QString &address);
    void clientDisconnected(const QString &address);
    void dataReceived(const QString &clientAddress, const QByteArray &data);
    void error(const QString &message);

private slots:
    void onNewConnection() {
        QTcpSocket *socket = m_server->nextPendingConnection();
        m_clients.append(socket);

        connect(socket, &QTcpSocket::readyRead, this, [this, socket]() {
            emit dataReceived(socket->peerAddress().toString(), socket->readAll());
        });

        connect(socket, &QTcpSocket::disconnected, this, [this, socket]() {
            QString addr = socket->peerAddress().toString();
            m_clients.removeOne(socket);
            socket->deleteLater();
            emit clientDisconnected(addr);
        });

        emit clientConnected(socket->peerAddress().toString());
    }

private:
    QTcpServer *m_server;
    QList<QTcpSocket *> m_clients;
};
```

### TCP Client with Reconnection

```cpp
#include <QTcpSocket>
#include <QTimer>

class TcpClient : public QObject
{
    Q_OBJECT

public:
    explicit TcpClient(QObject *parent = nullptr)
        : QObject(parent)
        , m_socket(new QTcpSocket(this))
        , m_reconnectTimer(new QTimer(this))
    {
        m_reconnectTimer->setInterval(5000);

        connect(m_socket, &QTcpSocket::connected, this, [this]() {
            m_reconnectTimer->stop();
            m_reconnectDelay = 1000;
            emit connected();
        });

        connect(m_socket, &QTcpSocket::disconnected, this, [this]() {
            emit disconnected();
            if (m_autoReconnect) {
                scheduleReconnect();
            }
        });

        connect(m_socket, &QTcpSocket::readyRead, this, [this]() {
            emit dataReceived(m_socket->readAll());
        });

        connect(m_socket, &QTcpSocket::errorOccurred, this,
                [this](QAbstractSocket::SocketError err) {
            if (err != QAbstractSocket::RemoteHostClosedError) {
                emit error(m_socket->errorString());
            }
            if (m_autoReconnect && m_socket->state() != QAbstractSocket::ConnectedState) {
                scheduleReconnect();
            }
        });

        connect(m_reconnectTimer, &QTimer::timeout, this, [this]() {
            m_socket->connectToHost(m_host, m_port);
        });
    }

    void connectToHost(const QString &host, quint16 port) {
        m_host = host;
        m_port = port;
        m_autoReconnect = true;
        m_socket->connectToHost(host, port);
    }

    void disconnect() {
        m_autoReconnect = false;
        m_reconnectTimer->stop();
        m_socket->disconnectFromHost();
    }

    void send(const QByteArray &data) {
        if (m_socket->state() == QAbstractSocket::ConnectedState) {
            m_socket->write(data);
        }
    }

    bool isConnected() const {
        return m_socket->state() == QAbstractSocket::ConnectedState;
    }

signals:
    void connected();
    void disconnected();
    void dataReceived(const QByteArray &data);
    void error(const QString &message);

private:
    void scheduleReconnect() {
        m_reconnectTimer->setInterval(m_reconnectDelay);
        m_reconnectTimer->start();
        // Exponential backoff with cap
        m_reconnectDelay = qMin(m_reconnectDelay * 2, 30000);
    }

    QTcpSocket *m_socket;
    QTimer *m_reconnectTimer;
    QString m_host;
    quint16 m_port = 0;
    bool m_autoReconnect = false;
    int m_reconnectDelay = 1000;
};
```

## WebSocket Communication

### WebSocket Server

```cpp
#include <QWebSocketServer>
#include <QWebSocket>

class WebSocketServer : public QObject
{
    Q_OBJECT

public:
    explicit WebSocketServer(const QString &name, QObject *parent = nullptr)
        : QObject(parent)
        , m_server(new QWebSocketServer(name, QWebSocketServer::NonSecureMode, this))
    {
        connect(m_server, &QWebSocketServer::newConnection,
                this, &WebSocketServer::onNewConnection);
    }

    bool start(quint16 port) {
        return m_server->listen(QHostAddress::Any, port);
    }

    void broadcast(const QString &message) {
        for (QWebSocket *client : m_clients) {
            client->sendTextMessage(message);
        }
    }

    void broadcastBinary(const QByteArray &data) {
        for (QWebSocket *client : m_clients) {
            client->sendBinaryMessage(data);
        }
    }

signals:
    void clientConnected();
    void clientDisconnected();
    void textMessageReceived(const QString &message);
    void binaryMessageReceived(const QByteArray &data);

private slots:
    void onNewConnection() {
        QWebSocket *socket = m_server->nextPendingConnection();
        m_clients.append(socket);

        connect(socket, &QWebSocket::textMessageReceived,
                this, &WebSocketServer::textMessageReceived);
        connect(socket, &QWebSocket::binaryMessageReceived,
                this, &WebSocketServer::binaryMessageReceived);
        connect(socket, &QWebSocket::disconnected, this, [this, socket]() {
            m_clients.removeOne(socket);
            socket->deleteLater();
            emit clientDisconnected();
        });

        emit clientConnected();
    }

private:
    QWebSocketServer *m_server;
    QList<QWebSocket *> m_clients;
};
```

### WebSocket Client

```cpp
#include <QWebSocket>

class WebSocketClient : public QObject
{
    Q_OBJECT

public:
    explicit WebSocketClient(QObject *parent = nullptr)
        : QObject(parent)
        , m_socket(new QWebSocket(QString(), QWebSocketProtocol::VersionLatest, this))
    {
        connect(m_socket, &QWebSocket::connected, this, &WebSocketClient::connected);
        connect(m_socket, &QWebSocket::disconnected, this, &WebSocketClient::disconnected);
        connect(m_socket, &QWebSocket::textMessageReceived,
                this, &WebSocketClient::textMessageReceived);
        connect(m_socket, &QWebSocket::binaryMessageReceived,
                this, &WebSocketClient::binaryMessageReceived);
    }

    void connectTo(const QUrl &url) {
        m_socket->open(url);
    }

    void send(const QString &message) {
        m_socket->sendTextMessage(message);
    }

    void sendBinary(const QByteArray &data) {
        m_socket->sendBinaryMessage(data);
    }

signals:
    void connected();
    void disconnected();
    void textMessageReceived(const QString &message);
    void binaryMessageReceived(const QByteArray &data);

private:
    QWebSocket *m_socket;
};
```

## REST API Client

```cpp
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>

class RestClient : public QObject
{
    Q_OBJECT

public:
    explicit RestClient(const QString &baseUrl, QObject *parent = nullptr)
        : QObject(parent)
        , m_baseUrl(baseUrl)
        , m_manager(new QNetworkAccessManager(this))
    {}

    void get(const QString &path) {
        QNetworkRequest request(QUrl(m_baseUrl + path));
        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

        QNetworkReply *reply = m_manager->get(request);
        connectReply(reply);
    }

    void post(const QString &path, const QJsonObject &body) {
        QNetworkRequest request(QUrl(m_baseUrl + path));
        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

        QNetworkReply *reply = m_manager->post(
            request,
            QJsonDocument(body).toJson(QJsonDocument::Compact)
        );
        connectReply(reply);
    }

    void put(const QString &path, const QJsonObject &body) {
        QNetworkRequest request(QUrl(m_baseUrl + path));
        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

        QNetworkReply *reply = m_manager->put(
            request,
            QJsonDocument(body).toJson(QJsonDocument::Compact)
        );
        connectReply(reply);
    }

    void del(const QString &path) {
        QNetworkRequest request(QUrl(m_baseUrl + path));
        QNetworkReply *reply = m_manager->deleteResource(request);
        connectReply(reply);
    }

signals:
    void success(const QJsonDocument &response);
    void error(int statusCode, const QString &message);

private:
    void connectReply(QNetworkReply *reply) {
        connect(reply, &QNetworkReply::finished, this, [this, reply]() {
            reply->deleteLater();

            int status = reply->attribute(
                QNetworkRequest::HttpStatusCodeAttribute).toInt();

            if (reply->error() == QNetworkReply::NoError) {
                QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
                emit success(doc);
            } else {
                emit error(status, reply->errorString());
            }
        });
    }

    QString m_baseUrl;
    QNetworkAccessManager *m_manager;
};
```

## Message Serialization

### JSON Protocol

```cpp
#include <QJsonDocument>
#include <QJsonObject>

namespace Protocol {

struct Message {
    QString type;
    QJsonObject payload;

    QByteArray serialize() const {
        QJsonObject obj;
        obj["type"] = type;
        obj["payload"] = payload;
        return QJsonDocument(obj).toJson(QJsonDocument::Compact) + "\n";
    }

    static std::optional<Message> deserialize(const QByteArray &data) {
        QJsonParseError error;
        QJsonDocument doc = QJsonDocument::fromJson(data, &error);

        if (error.error != QJsonParseError::NoError) {
            return std::nullopt;
        }

        QJsonObject obj = doc.object();
        return Message{
            obj["type"].toString(),
            obj["payload"].toObject()
        };
    }
};

// Message types
namespace MessageType {
    const QString SensorData = "sensor_data";
    const QString Command = "command";
    const QString Ack = "ack";
    const QString Error = "error";
}

} // namespace Protocol
```

### Binary Protocol with QDataStream

```cpp
#include <QDataStream>
#include <QBuffer>

// Frame format: [length:4][type:1][payload:N]
class BinaryProtocol
{
public:
    enum class MessageType : quint8 {
        SensorData = 0x01,
        Command = 0x02,
        Ack = 0x03,
        Error = 0xFF
    };

    static QByteArray encode(MessageType type, const QByteArray &payload) {
        QByteArray frame;
        QDataStream stream(&frame, QIODevice::WriteOnly);
        stream.setByteOrder(QDataStream::BigEndian);

        quint32 length = 1 + payload.size();  // type + payload
        stream << length;
        stream << static_cast<quint8>(type);
        stream.writeRawData(payload.constData(), payload.size());

        return frame;
    }

    struct DecodedMessage {
        MessageType type;
        QByteArray payload;
    };

    static std::optional<DecodedMessage> decode(QByteArray &buffer) {
        if (buffer.size() < 5) return std::nullopt;  // need at least header

        QDataStream stream(buffer);
        stream.setByteOrder(QDataStream::BigEndian);

        quint32 length;
        stream >> length;

        if (buffer.size() < 4 + static_cast<int>(length)) {
            return std::nullopt;  // incomplete message
        }

        quint8 typeVal;
        stream >> typeVal;

        QByteArray payload(length - 1, 0);
        stream.readRawData(payload.data(), length - 1);

        // Remove consumed bytes from buffer
        buffer.remove(0, 4 + length);

        return DecodedMessage{static_cast<MessageType>(typeVal), payload};
    }
};
```

### Protocol Buffers (with Qt)

```cpp
// sensor.proto
// syntax = "proto3";
// message SensorReading {
//     uint32 timestamp = 1;
//     float temperature = 2;
//     float humidity = 3;
// }

#include "sensor.pb.h"
#include <QByteArray>

class ProtobufCodec
{
public:
    static QByteArray encode(const SensorReading &reading) {
        std::string data;
        reading.SerializeToString(&data);
        return QByteArray::fromStdString(data);
    }

    static std::optional<SensorReading> decode(const QByteArray &data) {
        SensorReading reading;
        if (reading.ParseFromArray(data.constData(), data.size())) {
            return reading;
        }
        return std::nullopt;
    }
};
```

## Threading for Network I/O

### Worker Thread Pattern

```cpp
class NetworkWorker : public QObject
{
    Q_OBJECT

public slots:
    void connectToServer(const QString &host, quint16 port) {
        // This runs in worker thread
        m_socket = new QTcpSocket();

        connect(m_socket, &QTcpSocket::connected, this, &NetworkWorker::connected);
        connect(m_socket, &QTcpSocket::readyRead, this, [this]() {
            emit dataReceived(m_socket->readAll());
        });

        m_socket->connectToHost(host, port);
    }

    void sendData(const QByteArray &data) {
        if (m_socket && m_socket->state() == QAbstractSocket::ConnectedState) {
            m_socket->write(data);
        }
    }

signals:
    void connected();
    void dataReceived(const QByteArray &data);
    void error(const QString &message);

private:
    QTcpSocket *m_socket = nullptr;
};

// Controller in main thread
class NetworkController : public QObject
{
    Q_OBJECT

public:
    NetworkController(QObject *parent = nullptr)
        : QObject(parent)
    {
        m_worker = new NetworkWorker();
        m_worker->moveToThread(&m_workerThread);

        connect(&m_workerThread, &QThread::finished, m_worker, &QObject::deleteLater);
        connect(this, &NetworkController::doConnect, m_worker, &NetworkWorker::connectToServer);
        connect(this, &NetworkController::doSend, m_worker, &NetworkWorker::sendData);
        connect(m_worker, &NetworkWorker::dataReceived, this, &NetworkController::dataReceived);

        m_workerThread.start();
    }

    ~NetworkController() {
        m_workerThread.quit();
        m_workerThread.wait();
    }

    void connectToServer(const QString &host, quint16 port) {
        emit doConnect(host, port);
    }

    void send(const QByteArray &data) {
        emit doSend(data);
    }

signals:
    void doConnect(const QString &host, quint16 port);
    void doSend(const QByteArray &data);
    void dataReceived(const QByteArray &data);

private:
    QThread m_workerThread;
    NetworkWorker *m_worker;
};
```

## D-Bus (Linux IPC)

```cpp
#include <QDBusConnection>
#include <QDBusInterface>

class DBusService : public QObject
{
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "com.example.sensor")

public:
    DBusService(QObject *parent = nullptr)
        : QObject(parent)
    {
        QDBusConnection::sessionBus().registerObject(
            "/sensor",
            this,
            QDBusConnection::ExportAllSlots | QDBusConnection::ExportAllSignals
        );
        QDBusConnection::sessionBus().registerService("com.example.sensor");
    }

public slots:
    double getTemperature() { return m_temperature; }
    void setTemperature(double value) {
        m_temperature = value;
        emit temperatureChanged(value);
    }

signals:
    void temperatureChanged(double value);

private:
    double m_temperature = 0.0;
};

// Client
class DBusClient : public QObject
{
    Q_OBJECT

public:
    DBusClient(QObject *parent = nullptr)
        : QObject(parent)
        , m_interface(new QDBusInterface(
              "com.example.sensor",
              "/sensor",
              "com.example.sensor",
              QDBusConnection::sessionBus(),
              this))
    {
        QDBusConnection::sessionBus().connect(
            "com.example.sensor",
            "/sensor",
            "com.example.sensor",
            "temperatureChanged",
            this,
            SLOT(onTemperatureChanged(double))
        );
    }

    double getTemperature() {
        return m_interface->call("getTemperature").arguments().at(0).toDouble();
    }

private slots:
    void onTemperatureChanged(double value) {
        emit temperatureUpdated(value);
    }

signals:
    void temperatureUpdated(double value);

private:
    QDBusInterface *m_interface;
};
```
