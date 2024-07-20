/****************************************************************************
** Meta object code from reading C++ file 'Dlg_Tensile.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.3)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../VoxCad/Dlg_Tensile.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'Dlg_Tensile.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_Dlg_Tensile_t {
    QByteArrayData data[9];
    char stringdata0[129];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_Dlg_Tensile_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_Dlg_Tensile_t qt_meta_stringdata_Dlg_Tensile = {
    {
QT_MOC_LITERAL(0, 0, 11), // "Dlg_Tensile"
QT_MOC_LITERAL(1, 12, 18), // "DoneTensileTesting"
QT_MOC_LITERAL(2, 31, 0), // ""
QT_MOC_LITERAL(3, 32, 9), // "StartTest"
QT_MOC_LITERAL(4, 42, 8), // "UpdateUI"
QT_MOC_LITERAL(5, 51, 16), // "ClickedFastRadio"
QT_MOC_LITERAL(6, 68, 20), // "ClickedBalancedRadio"
QT_MOC_LITERAL(7, 89, 20), // "ClickedAccurateRadio"
QT_MOC_LITERAL(8, 110, 18) // "ClickedManualRadio"

    },
    "Dlg_Tensile\0DoneTensileTesting\0\0"
    "StartTest\0UpdateUI\0ClickedFastRadio\0"
    "ClickedBalancedRadio\0ClickedAccurateRadio\0"
    "ClickedManualRadio"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_Dlg_Tensile[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       7,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   49,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       3,    0,   50,    2, 0x0a /* Public */,
       4,    0,   51,    2, 0x0a /* Public */,
       5,    0,   52,    2, 0x0a /* Public */,
       6,    0,   53,    2, 0x0a /* Public */,
       7,    0,   54,    2, 0x0a /* Public */,
       8,    0,   55,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void Dlg_Tensile::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Dlg_Tensile *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->DoneTensileTesting(); break;
        case 1: _t->StartTest(); break;
        case 2: _t->UpdateUI(); break;
        case 3: _t->ClickedFastRadio(); break;
        case 4: _t->ClickedBalancedRadio(); break;
        case 5: _t->ClickedAccurateRadio(); break;
        case 6: _t->ClickedManualRadio(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (Dlg_Tensile::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&Dlg_Tensile::DoneTensileTesting)) {
                *result = 0;
                return;
            }
        }
    }
    (void)_a;
}

QT_INIT_METAOBJECT const QMetaObject Dlg_Tensile::staticMetaObject = { {
    QMetaObject::SuperData::link<QWidget::staticMetaObject>(),
    qt_meta_stringdata_Dlg_Tensile.data,
    qt_meta_data_Dlg_Tensile,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *Dlg_Tensile::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *Dlg_Tensile::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_Dlg_Tensile.stringdata0))
        return static_cast<void*>(this);
    return QWidget::qt_metacast(_clname);
}

int Dlg_Tensile::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 7)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 7;
    }
    return _id;
}

// SIGNAL 0
void Dlg_Tensile::DoneTensileTesting()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
