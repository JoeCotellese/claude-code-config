# Raspberry Pi Qt Development Reference

## Cross-Compilation Setup

### Toolchain for Pi (ARM)

```bash
# Install cross-compiler on Ubuntu/Debian host
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu  # 64-bit Pi
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf  # 32-bit Pi
```

### qmake Cross-Compilation

```pro
# In .pro file for cross-compilation
linux-rasp-pi4-v3d-g++ {
    # Pi-specific settings
    DEFINES += RASPBERRY_PI
    LIBS += -lwiringPi
}

# Or detect at qmake time
contains(QT_ARCH, arm64) {
    DEFINES += ARM_BUILD
}
```

### Sysroot Setup

```bash
# Sync Pi sysroot to host (run on host)
rsync -avz pi@raspberrypi:/lib sysroot/
rsync -avz pi@raspberrypi:/usr/include sysroot/usr/
rsync -avz pi@raspberrypi:/usr/lib sysroot/usr/
rsync -avz pi@raspberrypi:/opt/vc sysroot/opt/  # VideoCore

# Fix symlinks
./fixQualifiedLibraryPaths sysroot/
```

### Qt Configure for Cross-Compilation

```bash
# Qt6 cross-compile configure
../qt6/configure \
    -prefix /opt/qt6pi \
    -device linux-rasp-pi4-v3d-g++ \
    -device-option CROSS_COMPILE=aarch64-linux-gnu- \
    -sysroot /path/to/sysroot \
    -nomake examples \
    -nomake tests
```

## GPIO Access

### Using wiringPi (Legacy, still works)

```cpp
#include <wiringPi.h>

class GpioController : public QObject
{
    Q_OBJECT

public:
    GpioController(QObject *parent = nullptr)
        : QObject(parent)
    {
        wiringPiSetupGpio();  // BCM pin numbering
    }

    void setPinMode(int pin, bool output) {
        pinMode(pin, output ? OUTPUT : INPUT);
    }

    void writePin(int pin, bool high) {
        digitalWrite(pin, high ? HIGH : LOW);
        emit pinChanged(pin, high);
    }

    bool readPin(int pin) {
        return digitalRead(pin) == HIGH;
    }

signals:
    void pinChanged(int pin, bool value);
};
```

### Using libgpiod (Modern, recommended)

```cpp
#include <gpiod.h>
#include <QObject>

class GpioLine : public QObject
{
    Q_OBJECT

public:
    GpioLine(const QString &chipPath, int offset, QObject *parent = nullptr)
        : QObject(parent)
    {
        m_chip = gpiod_chip_open(chipPath.toLocal8Bit().constData());
        if (m_chip) {
            m_line = gpiod_chip_get_line(m_chip, offset);
        }
    }

    ~GpioLine() {
        if (m_line) gpiod_line_release(m_line);
        if (m_chip) gpiod_chip_close(m_chip);
    }

    bool requestOutput(const QString &consumer, bool initialValue) {
        return gpiod_line_request_output(
            m_line,
            consumer.toLocal8Bit().constData(),
            initialValue ? 1 : 0
        ) == 0;
    }

    bool requestInput(const QString &consumer) {
        return gpiod_line_request_input(
            m_line,
            consumer.toLocal8Bit().constData()
        ) == 0;
    }

    void setValue(bool high) {
        gpiod_line_set_value(m_line, high ? 1 : 0);
    }

    bool getValue() {
        return gpiod_line_get_value(m_line) == 1;
    }

private:
    gpiod_chip *m_chip = nullptr;
    gpiod_line *m_line = nullptr;
};
```

### qmake for GPIO

```pro
# wiringPi
LIBS += -lwiringPi

# libgpiod
LIBS += -lgpiod
```

## Serial Port (QSerialPort)

```cpp
#include <QSerialPort>
#include <QSerialPortInfo>

class SerialDevice : public QObject
{
    Q_OBJECT

public:
    SerialDevice(QObject *parent = nullptr)
        : QObject(parent)
        , m_port(new QSerialPort(this))
    {
        connect(m_port, &QSerialPort::readyRead, this, &SerialDevice::onReadyRead);
        connect(m_port, &QSerialPort::errorOccurred, this, &SerialDevice::onError);
    }

    bool open(const QString &portName, int baudRate = 115200) {
        m_port->setPortName(portName);  // e.g., "/dev/ttyUSB0" or "/dev/serial0"
        m_port->setBaudRate(baudRate);
        m_port->setDataBits(QSerialPort::Data8);
        m_port->setParity(QSerialPort::NoParity);
        m_port->setStopBits(QSerialPort::OneStop);

        if (!m_port->open(QIODevice::ReadWrite)) {
            emit error(m_port->errorString());
            return false;
        }

        emit connected();
        return true;
    }

    void send(const QByteArray &data) {
        m_port->write(data);
    }

    static QStringList availablePorts() {
        QStringList ports;
        for (const QSerialPortInfo &info : QSerialPortInfo::availablePorts()) {
            ports << info.portName();
        }
        return ports;
    }

signals:
    void connected();
    void disconnected();
    void dataReceived(const QByteArray &data);
    void error(const QString &message);

private slots:
    void onReadyRead() {
        emit dataReceived(m_port->readAll());
    }

    void onError(QSerialPort::SerialPortError err) {
        if (err != QSerialPort::NoError) {
            emit error(m_port->errorString());
        }
    }

private:
    QSerialPort *m_port;
};
```

## I2C Access

```cpp
#include <QFile>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

class I2CDevice : public QObject
{
    Q_OBJECT

public:
    I2CDevice(int bus, int address, QObject *parent = nullptr)
        : QObject(parent)
        , m_address(address)
    {
        QString path = QString("/dev/i2c-%1").arg(bus);
        m_fd = open(path.toLocal8Bit().constData(), O_RDWR);

        if (m_fd >= 0) {
            if (ioctl(m_fd, I2C_SLAVE, address) < 0) {
                close(m_fd);
                m_fd = -1;
            }
        }
    }

    ~I2CDevice() {
        if (m_fd >= 0) close(m_fd);
    }

    bool isOpen() const { return m_fd >= 0; }

    bool writeRegister(uint8_t reg, uint8_t value) {
        uint8_t buf[2] = {reg, value};
        return write(m_fd, buf, 2) == 2;
    }

    int readRegister(uint8_t reg) {
        if (write(m_fd, &reg, 1) != 1) return -1;

        uint8_t value;
        if (read(m_fd, &value, 1) != 1) return -1;

        return value;
    }

    QByteArray readRegisters(uint8_t startReg, int count) {
        if (write(m_fd, &startReg, 1) != 1) return {};

        QByteArray data(count, 0);
        if (read(m_fd, data.data(), count) != count) return {};

        return data;
    }

private:
    int m_fd = -1;
    int m_address;
};
```

## SPI Access

```cpp
#include <linux/spi/spidev.h>
#include <sys/ioctl.h>

class SPIDevice : public QObject
{
    Q_OBJECT

public:
    SPIDevice(int bus, int device, QObject *parent = nullptr)
        : QObject(parent)
    {
        QString path = QString("/dev/spidev%1.%2").arg(bus).arg(device);
        m_fd = open(path.toLocal8Bit().constData(), O_RDWR);

        if (m_fd >= 0) {
            // Default settings
            setMode(SPI_MODE_0);
            setSpeed(1000000);  // 1 MHz
            setBitsPerWord(8);
        }
    }

    ~SPIDevice() {
        if (m_fd >= 0) close(m_fd);
    }

    bool setMode(uint8_t mode) {
        return ioctl(m_fd, SPI_IOC_WR_MODE, &mode) >= 0;
    }

    bool setSpeed(uint32_t hz) {
        m_speed = hz;
        return ioctl(m_fd, SPI_IOC_WR_MAX_SPEED_HZ, &hz) >= 0;
    }

    bool setBitsPerWord(uint8_t bits) {
        m_bits = bits;
        return ioctl(m_fd, SPI_IOC_WR_BITS_PER_WORD, &bits) >= 0;
    }

    QByteArray transfer(const QByteArray &txData) {
        QByteArray rxData(txData.size(), 0);

        struct spi_ioc_transfer tr = {};
        tr.tx_buf = reinterpret_cast<unsigned long>(txData.constData());
        tr.rx_buf = reinterpret_cast<unsigned long>(rxData.data());
        tr.len = txData.size();
        tr.speed_hz = m_speed;
        tr.bits_per_word = m_bits;

        if (ioctl(m_fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
            return {};
        }

        return rxData;
    }

private:
    int m_fd = -1;
    uint32_t m_speed = 1000000;
    uint8_t m_bits = 8;
};
```

## Deployment

### Remote Deployment Script

```bash
#!/bin/bash
# deploy.sh - Deploy Qt app to Raspberry Pi

PI_HOST="pi@raspberrypi.local"
PI_PATH="/home/pi/app"
APP_NAME="myapp"

# Build
qmake && make -j$(nproc)

# Deploy binary and Qt libs
rsync -avz $APP_NAME $PI_HOST:$PI_PATH/
rsync -avz /opt/qt6pi/lib/*.so* $PI_HOST:$PI_PATH/lib/
rsync -avz /opt/qt6pi/plugins $PI_HOST:$PI_PATH/

# Create run script on Pi
ssh $PI_HOST "cat > $PI_PATH/run.sh << 'EOF'
#!/bin/bash
export LD_LIBRARY_PATH=$PI_PATH/lib:\$LD_LIBRARY_PATH
export QT_QPA_PLATFORM=eglfs
export QT_QPA_EGLFS_PHYSICAL_WIDTH=800
export QT_QPA_EGLFS_PHYSICAL_HEIGHT=480
$PI_PATH/$APP_NAME
EOF
chmod +x $PI_PATH/run.sh"
```

### Systemd Service

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Qt Application
After=network.target

[Service]
Type=simple
User=pi
Environment=QT_QPA_PLATFORM=eglfs
Environment=QT_QPA_EGLFS_PHYSICAL_WIDTH=800
Environment=QT_QPA_EGLFS_PHYSICAL_HEIGHT=480
ExecStart=/home/pi/app/myapp
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Performance Optimization

### Reduce Memory Usage

```cpp
// Use smaller data types when possible
struct CompactSensorData {
    uint32_t timestamp;  // ms since start, not full datetime
    int16_t temperature;  // hundredths of degree
    uint16_t humidity;    // hundredths of percent
};

// Pre-allocate containers
QVector<SensorData> readings;
readings.reserve(1000);  // avoid reallocations

// Use QByteArray for binary data, not QString
QByteArray buffer(1024, 0);  // pre-sized buffer
```

### Avoid GUI Overhead on Headless Pi

```pro
# For server/daemon, don't link GUI
QT -= gui
QT += core network serialport
```

### Profile on Target

```bash
# Install perf on Pi
sudo apt install linux-perf

# Profile application
perf record -g ./myapp
perf report
```
