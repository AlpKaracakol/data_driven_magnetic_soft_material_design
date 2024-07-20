/****************************************************************************
** Meta object code from reading C++ file 'QVX_TensileTest.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.3)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../VoxCad/QVX_TensileTest.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'QVX_TensileTest.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_QVX_TensileTest_t {
    QByteArrayData data[17];
    char stringdata0[202];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_QVX_TensileTest_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_QVX_TensileTest_t qt_meta_stringdata_QVX_TensileTest = {
    {
QT_MOC_LITERAL(0, 0, 15), // "QVX_TensileTest"
QT_MOC_LITERAL(1, 16, 21), // "StartExternalGLUpdate"
QT_MOC_LITERAL(2, 38, 0), // ""
QT_MOC_LITERAL(3, 39, 20), // "StopExternalGLUpdate"
QT_MOC_LITERAL(4, 60, 16), // "BeginTensileTest"
QT_MOC_LITERAL(5, 77, 8), // "QVX_Sim*"
QT_MOC_LITERAL(6, 86, 4), // "pSim"
QT_MOC_LITERAL(7, 91, 9), // "NumStepIn"
QT_MOC_LITERAL(8, 101, 12), // "ConvThreshIn"
QT_MOC_LITERAL(9, 114, 13), // "Vec3D<double>"
QT_MOC_LITERAL(10, 128, 8), // "MixRadIn"
QT_MOC_LITERAL(11, 137, 13), // "MatBlendModel"
QT_MOC_LITERAL(12, 151, 7), // "ModelIn"
QT_MOC_LITERAL(13, 159, 9), // "PolyExpIn"
QT_MOC_LITERAL(14, 169, 14), // "RunTensileTest"
QT_MOC_LITERAL(15, 184, 8), // "QString*"
QT_MOC_LITERAL(16, 193, 8) // "pMessage"

    },
    "QVX_TensileTest\0StartExternalGLUpdate\0"
    "\0StopExternalGLUpdate\0BeginTensileTest\0"
    "QVX_Sim*\0pSim\0NumStepIn\0ConvThreshIn\0"
    "Vec3D<double>\0MixRadIn\0MatBlendModel\0"
    "ModelIn\0PolyExpIn\0RunTensileTest\0"
    "QString*\0pMessage"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_QVX_TensileTest[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       8,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       2,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    1,   54,    2, 0x06 /* Public */,
       3,    0,   57,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       4,    6,   58,    2, 0x0a /* Public */,
       4,    5,   71,    2, 0x2a /* Public | MethodCloned */,
       4,    4,   82,    2, 0x2a /* Public | MethodCloned */,
       4,    3,   91,    2, 0x2a /* Public | MethodCloned */,
      14,    1,   98,    2, 0x0a /* Public */,
      14,    0,  101,    2, 0x2a /* Public | MethodCloned */,

 // signals: parameters
    QMetaType::Void, QMetaType::Int,    2,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void, 0x80000000 | 5, QMetaType::Int, QMetaType::Double, 0x80000000 | 9, 0x80000000 | 11, QMetaType::Double,    6,    7,    8,   10,   12,   13,
    QMetaType::Void, 0x80000000 | 5, QMetaType::Int, QMetaType::Double, 0x80000000 | 9, 0x80000000 | 11,    6,    7,    8,   10,   12,
    QMetaType::Void, 0x80000000 | 5, QMetaType::Int, QMetaType::Double, 0x80000000 | 9,    6,    7,    8,   10,
    QMetaType::Void, 0x80000000 | 5, QMetaType::Int, QMetaType::Double,    6,    7,    8,
    QMetaType::Void, 0x80000000 | 15,   16,
    QMetaType::Void,

       0        // eod
};

void QVX_TensileTest::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<QVX_TensileTest *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->StartExternalGLUpdate((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 1: _t->StopExternalGLUpdate(); break;
        case 2: _t->BeginTensileTest((*reinterpret_cast< QVX_Sim*(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< double(*)>(_a[3])),(*reinterpret_cast< Vec3D<double>(*)>(_a[4])),(*reinterpret_cast< MatBlendModel(*)>(_a[5])),(*reinterpret_cast< double(*)>(_a[6]))); break;
        case 3: _t->BeginTensileTest((*reinterpret_cast< QVX_Sim*(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< double(*)>(_a[3])),(*reinterpret_cast< Vec3D<double>(*)>(_a[4])),(*reinterpret_cast< MatBlendModel(*)>(_a[5]))); break;
        case 4: _t->BeginTensileTest((*reinterpret_cast< QVX_Sim*(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< double(*)>(_a[3])),(*reinterpret_cast< Vec3D<double>(*)>(_a[4]))); break;
        case 5: _t->BeginTensileTest((*reinterpret_cast< QVX_Sim*(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< double(*)>(_a[3]))); break;
        case 6: _t->RunTensileTest((*reinterpret_cast< QString*(*)>(_a[1]))); break;
        case 7: _t->RunTensileTest(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (QVX_TensileTest::*)(int );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&QVX_TensileTest::StartExternalGLUpdate)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (QVX_TensileTest::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&QVX_TensileTest::StopExternalGLUpdate)) {
                *result = 1;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject QVX_TensileTest::staticMetaObject = { {
    QMetaObject::SuperData::link<QWidget::staticMetaObject>(),
    qt_meta_stringdata_QVX_TensileTest.data,
    qt_meta_data_QVX_TensileTest,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *QVX_TensileTest::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *QVX_TensileTest::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_QVX_TensileTest.stringdata0))
        return static_cast<void*>(this);
    if (!strcmp(_clname, "CVX_Sim"))
        return static_cast< CVX_Sim*>(this);
    return QWidget::qt_metacast(_clname);
}

int QVX_TensileTest::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 8)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 8;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 8)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 8;
    }
    return _id;
}

// SIGNAL 0
void QVX_TensileTest::StartExternalGLUpdate(int _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void QVX_TensileTest::StopExternalGLUpdate()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
