# qmake Patterns Reference

## Project File Basics

### Application (.pro)

```pro
# Project type
TEMPLATE = app

# Qt modules
QT += core gui widgets network serialport

# C++ standard
CONFIG += c++17

# Application name
TARGET = myapp

# Source files
SOURCES += \
    main.cpp \
    mainwindow.cpp \
    devicecontroller.cpp

HEADERS += \
    mainwindow.h \
    devicecontroller.h

# Forms (UI files)
FORMS += \
    mainwindow.ui

# Resources
RESOURCES += \
    resources.qrc

# Install target
target.path = /usr/local/bin
INSTALLS += target
```

### Library (.pro)

```pro
TEMPLATE = lib

# Static or shared
CONFIG += staticlib    # or: CONFIG += shared

QT += core

TARGET = mylib
VERSION = 1.0.0

SOURCES += \
    mylib.cpp

HEADERS += \
    mylib.h \
    mylib_global.h

# For shared library export
DEFINES += MYLIB_LIBRARY

# Install
headers.files = $$HEADERS
headers.path = /usr/local/include/mylib
target.path = /usr/local/lib
INSTALLS += target headers
```

### Subdirs Project

```pro
# myproject.pro (top-level)
TEMPLATE = subdirs
SUBDIRS = \
    core \
    gui \
    server \
    tests

# Build order dependencies
gui.depends = core
server.depends = core
tests.depends = core gui server
```

```pro
# core/core.pro
TEMPLATE = lib
CONFIG += staticlib
QT += core
TARGET = core

SOURCES += core.cpp
HEADERS += core.h
```

```pro
# gui/gui.pro
TEMPLATE = app
QT += core gui widgets
TARGET = myapp

# Link against core library
LIBS += -L$$OUT_PWD/../core -lcore
INCLUDEPATH += $$PWD/../core
DEPENDPATH += $$PWD/../core

SOURCES += main.cpp mainwindow.cpp
HEADERS += mainwindow.h
```

## Platform-Specific Configuration

### Conditional Settings

```pro
# Platform detection
win32 {
    SOURCES += platform_win.cpp
    LIBS += -luser32
}

unix:!macx {
    SOURCES += platform_linux.cpp
    LIBS += -lgpiod
}

macx {
    SOURCES += platform_mac.cpp
    LIBS += -framework CoreFoundation
}

# Architecture detection
contains(QT_ARCH, arm64) {
    DEFINES += ARM_BUILD
    QMAKE_CXXFLAGS += -march=armv8-a
}

contains(QT_ARCH, x86_64) {
    DEFINES += X64_BUILD
}

# Debug vs Release
CONFIG(debug, debug|release) {
    DEFINES += DEBUG_BUILD
    QMAKE_CXXFLAGS += -fsanitize=address
    QMAKE_LFLAGS += -fsanitize=address
}

CONFIG(release, debug|release) {
    DEFINES += QT_NO_DEBUG_OUTPUT
}
```

### Qt Version Detection

```pro
# Qt5 vs Qt6
greaterThan(QT_MAJOR_VERSION, 5) {
    QT += core5compat   # Qt6 compatibility module
}

lessThan(QT_MAJOR_VERSION, 6) {
    # Qt5-specific modules
    QT += multimedia
}

# Specific version check
versionAtLeast(QT_VERSION, 5.15.0) {
    DEFINES += HAS_NEW_FEATURE
}
```

## Cross-Compilation for Raspberry Pi

### Using mkspec

```pro
# Detect cross-compile via mkspec
linux-rasp-pi4-v3d-g++ {
    message("Building for Raspberry Pi 4")
    DEFINES += RASPBERRY_PI RASPBERRY_PI4
    LIBS += -lwiringPi

    # Pi-specific optimizations
    QMAKE_CXXFLAGS += -march=armv8-a+crc -mtune=cortex-a72
}

linux-rasp-pi3-g++ {
    message("Building for Raspberry Pi 3")
    DEFINES += RASPBERRY_PI RASPBERRY_PI3
    QMAKE_CXXFLAGS += -march=armv8-a -mtune=cortex-a53
}
```

### Cross-Compile Invocation

```bash
# Set up environment
export CROSS_COMPILE=aarch64-linux-gnu-
export SYSROOT=/path/to/pi/sysroot

# Configure with cross-compile spec
qmake -spec linux-aarch64-gnu-g++ \
    "QMAKE_CC=${CROSS_COMPILE}gcc" \
    "QMAKE_CXX=${CROSS_COMPILE}g++" \
    "QMAKE_LINK=${CROSS_COMPILE}g++" \
    "QMAKE_SYSROOT=${SYSROOT}"
```

### Custom mkspec

```
# Create custom mkspec in qtbase/mkspecs/devices/linux-rasp-pi-custom/
# qmake.conf:

include(../common/linux_device_pre.conf)

QMAKE_INCDIR           += $$[QT_SYSROOT]/usr/include
QMAKE_LIBDIR           += $$[QT_SYSROOT]/usr/lib

QMAKE_CC               = aarch64-linux-gnu-gcc
QMAKE_CXX              = aarch64-linux-gnu-g++
QMAKE_LINK             = aarch64-linux-gnu-g++
QMAKE_LINK_SHLIB       = aarch64-linux-gnu-g++

QMAKE_CFLAGS           = -march=armv8-a
QMAKE_CXXFLAGS         = $$QMAKE_CFLAGS

include(../common/linux_device_post.conf)
```

## Build Configuration

### Compiler Flags

```pro
# Additional compiler flags
QMAKE_CXXFLAGS += -Wall -Wextra -Wpedantic

# Warnings as errors (strict)
QMAKE_CXXFLAGS += -Werror

# Optimization
QMAKE_CXXFLAGS_RELEASE += -O3 -flto
QMAKE_LFLAGS_RELEASE += -flto

# Debug symbols in release
QMAKE_CXXFLAGS_RELEASE += -g

# Sanitizers for debug
QMAKE_CXXFLAGS_DEBUG += -fsanitize=address,undefined
QMAKE_LFLAGS_DEBUG += -fsanitize=address,undefined
```

### Pre/Post Build Steps

```pro
# Pre-build command
system(python scripts/generate_version.py)

# Post-build (copy resources)
QMAKE_POST_LINK += $$quote(cp -r $$PWD/assets $$OUT_PWD/)

# Custom target
generateDocs.target = docs
generateDocs.commands = doxygen Doxyfile
generateDocs.depends = $(SOURCES)
QMAKE_EXTRA_TARGETS += generateDocs
```

### Generated Files

```pro
# Version header from git
version.target = version.h
version.commands = echo \\\"$${LITERAL_HASH}define APP_VERSION \\\"\\\"$$system(git describe --tags)\\\"\\\"\\\" > $$OUT_PWD/version.h
version.depends = FORCE
QMAKE_EXTRA_TARGETS += version
PRE_TARGETDEPS += version.h
INCLUDEPATH += $$OUT_PWD
```

## Dependencies

### External Libraries

```pro
# pkg-config (Linux)
CONFIG += link_pkgconfig
PKGCONFIG += libgpiod openssl

# Manual library
LIBS += -L/usr/local/lib -lmylibrary
INCLUDEPATH += /usr/local/include/mylibrary

# Conditional library
packagesExist(libavcodec) {
    CONFIG += link_pkgconfig
    PKGCONFIG += libavcodec
    DEFINES += HAS_FFMPEG
}
```

### Protocol Buffers

```pro
# Protobuf integration
PROTOS = proto/sensor.proto proto/commands.proto

protobuf.name = protobuf
protobuf.input = PROTOS
protobuf.output = ${QMAKE_FILE_BASE}.pb.cc
protobuf.commands = protoc --cpp_out=$$OUT_PWD --proto_path=$$PWD/proto ${QMAKE_FILE_NAME}
protobuf.variable_out = SOURCES
QMAKE_EXTRA_COMPILERS += protobuf

LIBS += -lprotobuf
```

## Testing Configuration

```pro
# tests/tests.pro
QT += testlib
QT -= gui

CONFIG += qt console warn_on testcase
CONFIG -= app_bundle

TEMPLATE = app
TARGET = tests

# Test sources
SOURCES += \
    tst_devicecontroller.cpp \
    tst_protocol.cpp

# Include project headers
INCLUDEPATH += $$PWD/../src

# Link against project library
LIBS += -L$$OUT_PWD/../src -lmyapp
```

## Common Patterns

### Avoid Hardcoded Paths

```pro
# Use variables instead of hardcoded paths
SRC_DIR = $$PWD/src
BUILD_DIR = $$OUT_PWD

# Generated files go to build dir
OBJECTS_DIR = $$BUILD_DIR/obj
MOC_DIR = $$BUILD_DIR/moc
RCC_DIR = $$BUILD_DIR/rcc
UI_DIR = $$BUILD_DIR/ui
```

### Include Common Settings

```pro
# common.pri (shared settings)
CONFIG += c++17
DEFINES += QT_DEPRECATED_WARNINGS

# In each .pro file:
include($$PWD/../common.pri)
```

### Feature Files

```pro
# features/myfeature.prf
# Custom feature that can be loaded with CONFIG += myfeature

defineReplace(myMacro) {
    return($$1_processed)
}

DEFINES += MY_FEATURE_ENABLED
```

```pro
# Load feature
CONFIG += myfeature  # requires myfeature.prf in QMAKEFEATURES path
```

## Debugging qmake

```pro
# Print variable value
message("QT_ARCH is: $$QT_ARCH")
message("SOURCES: $$SOURCES")

# Print all variables
# Run: qmake -d project.pro 2>&1 | grep "Reading"

# Check if variable is defined
isEmpty(MY_VAR) {
    error("MY_VAR is not defined!")
}

# Conditional message
contains(CONFIG, debug) {
    message("Debug build enabled")
}
```
