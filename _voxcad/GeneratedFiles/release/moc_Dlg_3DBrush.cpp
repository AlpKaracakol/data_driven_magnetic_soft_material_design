/****************************************************************************
** Meta object code from reading C++ file 'Dlg_3DBrush.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.3)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../VoxCad/Dlg_3DBrush.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'Dlg_3DBrush.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_Dlg_3DBrush_t {
    QByteArrayData data[8];
    char stringdata0[82];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_Dlg_3DBrush_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_Dlg_3DBrush_t qt_meta_stringdata_Dlg_3DBrush = {
    {
QT_MOC_LITERAL(0, 0, 11), // "Dlg_3DBrush"
QT_MOC_LITERAL(1, 12, 15), // "RequestUpdateGL"
QT_MOC_LITERAL(2, 28, 0), // ""
QT_MOC_LITERAL(3, 29, 10), // "DoneAdding"
QT_MOC_LITERAL(4, 40, 10), // "ApplyBrush"
QT_MOC_LITERAL(5, 51, 8), // "UpdateUI"
QT_MOC_LITERAL(6, 60, 9), // "DrawBrush"
QT_MOC_LITERAL(7, 70, 11) // "ClickedDone"

    },
    "Dlg_3DBrush\0RequestUpdateGL\0\0DoneAdding\0"
    "ApplyBrush\0UpdateUI\0DrawBrush\0ClickedDone"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_Dlg_3DBrush[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       6,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       2,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   44,    2, 0x06 /* Public */,
       3,    0,   45,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       4,    0,   46,    2, 0x0a /* Public */,
       5,    0,   47,    2, 0x0a /* Public */,
       6,    0,   48,    2, 0x0a /* Public */,
       7,    0,   49,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void Dlg_3DBrush::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Dlg_3DBrush *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->RequestUpdateGL(); break;
        case 1: _t->DoneAdding(); break;
        case 2: _t->ApplyBrush(); break;
        case 3: _t->UpdateUI(); break;
        case 4: _t->DrawBrush(); break;
        case 5: _t->ClickedDone(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (Dlg_3DBrush::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&Dlg_3DBrush::RequestUpdateGL)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (Dlg_3DBrush::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&Dlg_3DBrush::DoneAdding)) {
                *result = 1;
                return;
            }
        }
    }
    (void)_a;
}

QT_INIT_METAOBJECT const QMetaObject Dlg_3DBrush::staticMetaObject = { {
    QMetaObject::SuperData::link<QWidget::staticMetaObject>(),
    qt_meta_stringdata_Dlg_3DBrush.data,
    qt_meta_data_Dlg_3DBrush,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *Dlg_3DBrush::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *Dlg_3DBrush::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_Dlg_3DBrush.stringdata0))
        return static_cast<void*>(this);
    return QWidget::qt_metacast(_clname);
}

int Dlg_3DBrush::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 6)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 6;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 6)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 6;
    }
    return _id;
}

// SIGNAL 0
void Dlg_3DBrush::RequestUpdateGL()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void Dlg_3DBrush::DoneAdding()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
