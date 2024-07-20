/****************************************************************************
** Meta object code from reading C++ file 'Dlg_Physics.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.3)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../VoxCad/Dlg_Physics.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'Dlg_Physics.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_Dlg_Physics_t {
    QByteArrayData data[74];
    char stringdata0[1225];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_Dlg_Physics_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_Dlg_Physics_t qt_meta_stringdata_Dlg_Physics = {
    {
QT_MOC_LITERAL(0, 0, 11), // "Dlg_Physics"
QT_MOC_LITERAL(1, 12, 13), // "SetStatusText"
QT_MOC_LITERAL(2, 26, 0), // ""
QT_MOC_LITERAL(3, 27, 4), // "Text"
QT_MOC_LITERAL(4, 32, 17), // "ApplyVoxSelection"
QT_MOC_LITERAL(5, 50, 6), // "NewSel"
QT_MOC_LITERAL(6, 57, 12), // "AddPlotPoint"
QT_MOC_LITERAL(7, 70, 4), // "Time"
QT_MOC_LITERAL(8, 75, 16), // "DeletePlotPoints"
QT_MOC_LITERAL(9, 92, 8), // "UpdateUI"
QT_MOC_LITERAL(10, 101, 10), // "UpdatePlot"
QT_MOC_LITERAL(11, 112, 26), // "UseEquilibriumCheckChanged"
QT_MOC_LITERAL(12, 139, 5), // "State"
QT_MOC_LITERAL(13, 145, 17), // "StopSelectChanged"
QT_MOC_LITERAL(14, 163, 8), // "NewIndex"
QT_MOC_LITERAL(15, 172, 20), // "StopValueEditChanged"
QT_MOC_LITERAL(16, 193, 15), // "dtSliderChanged"
QT_MOC_LITERAL(17, 209, 6), // "NewVal"
QT_MOC_LITERAL(18, 216, 13), // "dtEditChanged"
QT_MOC_LITERAL(19, 230, 21), // "BondDampSliderChanged"
QT_MOC_LITERAL(20, 252, 19), // "BondDampEditChanged"
QT_MOC_LITERAL(21, 272, 25), // "MotionFloorThrEditChanged"
QT_MOC_LITERAL(22, 298, 13), // "KpEditChanged"
QT_MOC_LITERAL(23, 312, 13), // "KiEditChanged"
QT_MOC_LITERAL(24, 326, 21), // "AntiWindupEditChanged"
QT_MOC_LITERAL(25, 348, 20), // "GNDDampSliderChanged"
QT_MOC_LITERAL(26, 369, 18), // "GNDDampEditChanged"
QT_MOC_LITERAL(27, 388, 20), // "ColDampSliderChanged"
QT_MOC_LITERAL(28, 409, 18), // "ColDampEditChanged"
QT_MOC_LITERAL(29, 428, 24), // "MaxVelLimitSliderChanged"
QT_MOC_LITERAL(30, 453, 22), // "UseSelfColCheckChanged"
QT_MOC_LITERAL(31, 476, 26), // "UseMaxVelLimitCheckChanged"
QT_MOC_LITERAL(32, 503, 25), // "UseVolEffectsCheckChanged"
QT_MOC_LITERAL(33, 529, 19), // "UseTempCheckChanged"
QT_MOC_LITERAL(34, 549, 17), // "TempSliderChanged"
QT_MOC_LITERAL(35, 567, 15), // "TempEditChanged"
QT_MOC_LITERAL(36, 583, 20), // "VaryTempCheckChanged"
QT_MOC_LITERAL(37, 604, 20), // "TempPerSliderChanged"
QT_MOC_LITERAL(38, 625, 18), // "TempPerEditChanged"
QT_MOC_LITERAL(39, 644, 19), // "UseGravCheckChanged"
QT_MOC_LITERAL(40, 664, 17), // "GravSliderChanged"
QT_MOC_LITERAL(41, 682, 15), // "GravEditChanged"
QT_MOC_LITERAL(42, 698, 20), // "UseFloorCheckChanged"
QT_MOC_LITERAL(43, 719, 21), // "DisplayDisableChanged"
QT_MOC_LITERAL(44, 741, 17), // "DisplayVoxChanged"
QT_MOC_LITERAL(45, 759, 17), // "DisplayConChanged"
QT_MOC_LITERAL(46, 777, 18), // "VoxDiscreteChanged"
QT_MOC_LITERAL(47, 796, 18), // "VoxDeformedChanged"
QT_MOC_LITERAL(48, 815, 16), // "VoxSmoothChanged"
QT_MOC_LITERAL(49, 832, 18), // "ForcesCheckChanged"
QT_MOC_LITERAL(50, 851, 15), // "LCsCheckChanged"
QT_MOC_LITERAL(51, 867, 12), // "CTypeChanged"
QT_MOC_LITERAL(52, 880, 12), // "CKinEChanged"
QT_MOC_LITERAL(53, 893, 12), // "CDispChanged"
QT_MOC_LITERAL(54, 906, 18), // "CGrowthRateChanged"
QT_MOC_LITERAL(55, 925, 16), // "CStimulusChanged"
QT_MOC_LITERAL(56, 942, 27), // "CStiffnessPlasticityChanged"
QT_MOC_LITERAL(57, 970, 15), // "CStrainEChanged"
QT_MOC_LITERAL(58, 986, 14), // "CStrainChanged"
QT_MOC_LITERAL(59, 1001, 14), // "CStressChanged"
QT_MOC_LITERAL(60, 1016, 16), // "CPressureChanged"
QT_MOC_LITERAL(61, 1033, 15), // "CoMCheckChanged"
QT_MOC_LITERAL(62, 1049, 22), // "PlotSourcesRaysChanged"
QT_MOC_LITERAL(63, 1072, 15), // "VarComboChanged"
QT_MOC_LITERAL(64, 1088, 15), // "DirComboChanged"
QT_MOC_LITERAL(65, 1104, 19), // "LogEachCheckChanged"
QT_MOC_LITERAL(66, 1124, 12), // "ClickedPause"
QT_MOC_LITERAL(67, 1137, 12), // "ClickedReset"
QT_MOC_LITERAL(68, 1150, 13), // "ClickedRecord"
QT_MOC_LITERAL(69, 1164, 15), // "ClickedSaveData"
QT_MOC_LITERAL(70, 1180, 15), // "IsOutputVisible"
QT_MOC_LITERAL(71, 1196, 5), // "bool*"
QT_MOC_LITERAL(72, 1202, 8), // "pVisible"
QT_MOC_LITERAL(73, 1211, 13) // "IsPlotVisible"

    },
    "Dlg_Physics\0SetStatusText\0\0Text\0"
    "ApplyVoxSelection\0NewSel\0AddPlotPoint\0"
    "Time\0DeletePlotPoints\0UpdateUI\0"
    "UpdatePlot\0UseEquilibriumCheckChanged\0"
    "State\0StopSelectChanged\0NewIndex\0"
    "StopValueEditChanged\0dtSliderChanged\0"
    "NewVal\0dtEditChanged\0BondDampSliderChanged\0"
    "BondDampEditChanged\0MotionFloorThrEditChanged\0"
    "KpEditChanged\0KiEditChanged\0"
    "AntiWindupEditChanged\0GNDDampSliderChanged\0"
    "GNDDampEditChanged\0ColDampSliderChanged\0"
    "ColDampEditChanged\0MaxVelLimitSliderChanged\0"
    "UseSelfColCheckChanged\0"
    "UseMaxVelLimitCheckChanged\0"
    "UseVolEffectsCheckChanged\0UseTempCheckChanged\0"
    "TempSliderChanged\0TempEditChanged\0"
    "VaryTempCheckChanged\0TempPerSliderChanged\0"
    "TempPerEditChanged\0UseGravCheckChanged\0"
    "GravSliderChanged\0GravEditChanged\0"
    "UseFloorCheckChanged\0DisplayDisableChanged\0"
    "DisplayVoxChanged\0DisplayConChanged\0"
    "VoxDiscreteChanged\0VoxDeformedChanged\0"
    "VoxSmoothChanged\0ForcesCheckChanged\0"
    "LCsCheckChanged\0CTypeChanged\0CKinEChanged\0"
    "CDispChanged\0CGrowthRateChanged\0"
    "CStimulusChanged\0CStiffnessPlasticityChanged\0"
    "CStrainEChanged\0CStrainChanged\0"
    "CStressChanged\0CPressureChanged\0"
    "CoMCheckChanged\0PlotSourcesRaysChanged\0"
    "VarComboChanged\0DirComboChanged\0"
    "LogEachCheckChanged\0ClickedPause\0"
    "ClickedReset\0ClickedRecord\0ClickedSaveData\0"
    "IsOutputVisible\0bool*\0pVisible\0"
    "IsPlotVisible"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_Dlg_Physics[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
      64,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    1,  334,    2, 0x0a /* Public */,
       4,    1,  337,    2, 0x0a /* Public */,
       6,    1,  340,    2, 0x0a /* Public */,
       8,    0,  343,    2, 0x0a /* Public */,
       9,    0,  344,    2, 0x0a /* Public */,
      10,    0,  345,    2, 0x0a /* Public */,
      11,    1,  346,    2, 0x0a /* Public */,
      13,    1,  349,    2, 0x0a /* Public */,
      15,    0,  352,    2, 0x0a /* Public */,
      16,    1,  353,    2, 0x0a /* Public */,
      18,    0,  356,    2, 0x0a /* Public */,
      19,    1,  357,    2, 0x0a /* Public */,
      20,    0,  360,    2, 0x0a /* Public */,
      21,    0,  361,    2, 0x0a /* Public */,
      22,    0,  362,    2, 0x0a /* Public */,
      23,    0,  363,    2, 0x0a /* Public */,
      24,    0,  364,    2, 0x0a /* Public */,
      25,    1,  365,    2, 0x0a /* Public */,
      26,    0,  368,    2, 0x0a /* Public */,
      27,    1,  369,    2, 0x0a /* Public */,
      28,    0,  372,    2, 0x0a /* Public */,
      29,    1,  373,    2, 0x0a /* Public */,
      30,    1,  376,    2, 0x0a /* Public */,
      31,    1,  379,    2, 0x0a /* Public */,
      32,    1,  382,    2, 0x0a /* Public */,
      33,    1,  385,    2, 0x0a /* Public */,
      34,    1,  388,    2, 0x0a /* Public */,
      35,    0,  391,    2, 0x0a /* Public */,
      36,    1,  392,    2, 0x0a /* Public */,
      37,    1,  395,    2, 0x0a /* Public */,
      38,    0,  398,    2, 0x0a /* Public */,
      39,    1,  399,    2, 0x0a /* Public */,
      40,    1,  402,    2, 0x0a /* Public */,
      41,    0,  405,    2, 0x0a /* Public */,
      42,    1,  406,    2, 0x0a /* Public */,
      43,    1,  409,    2, 0x0a /* Public */,
      44,    1,  412,    2, 0x0a /* Public */,
      45,    1,  415,    2, 0x0a /* Public */,
      46,    1,  418,    2, 0x0a /* Public */,
      47,    1,  421,    2, 0x0a /* Public */,
      48,    1,  424,    2, 0x0a /* Public */,
      49,    1,  427,    2, 0x0a /* Public */,
      50,    1,  430,    2, 0x0a /* Public */,
      51,    1,  433,    2, 0x0a /* Public */,
      52,    1,  436,    2, 0x0a /* Public */,
      53,    1,  439,    2, 0x0a /* Public */,
      54,    1,  442,    2, 0x0a /* Public */,
      55,    1,  445,    2, 0x0a /* Public */,
      56,    1,  448,    2, 0x0a /* Public */,
      57,    1,  451,    2, 0x0a /* Public */,
      58,    1,  454,    2, 0x0a /* Public */,
      59,    1,  457,    2, 0x0a /* Public */,
      60,    1,  460,    2, 0x0a /* Public */,
      61,    1,  463,    2, 0x0a /* Public */,
      62,    1,  466,    2, 0x0a /* Public */,
      63,    1,  469,    2, 0x0a /* Public */,
      64,    1,  472,    2, 0x0a /* Public */,
      65,    1,  475,    2, 0x0a /* Public */,
      66,    0,  478,    2, 0x0a /* Public */,
      67,    0,  479,    2, 0x0a /* Public */,
      68,    1,  480,    2, 0x0a /* Public */,
      69,    0,  483,    2, 0x0a /* Public */,
      70,    1,  484,    2, 0x0a /* Public */,
      73,    1,  487,    2, 0x0a /* Public */,

 // slots: parameters
    QMetaType::Void, QMetaType::QString,    3,
    QMetaType::Void, QMetaType::Int,    5,
    QMetaType::Void, QMetaType::Double,    7,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Int,   14,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Int,   17,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void, QMetaType::Int,   14,
    QMetaType::Void, QMetaType::Int,   14,
    QMetaType::Void, QMetaType::Bool,   17,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 71,   72,
    QMetaType::Void, 0x80000000 | 71,   72,

       0        // eod
};

void Dlg_Physics::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Dlg_Physics *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->SetStatusText((*reinterpret_cast< QString(*)>(_a[1]))); break;
        case 1: _t->ApplyVoxSelection((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 2: _t->AddPlotPoint((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 3: _t->DeletePlotPoints(); break;
        case 4: _t->UpdateUI(); break;
        case 5: _t->UpdatePlot(); break;
        case 6: _t->UseEquilibriumCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 7: _t->StopSelectChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 8: _t->StopValueEditChanged(); break;
        case 9: _t->dtSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 10: _t->dtEditChanged(); break;
        case 11: _t->BondDampSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 12: _t->BondDampEditChanged(); break;
        case 13: _t->MotionFloorThrEditChanged(); break;
        case 14: _t->KpEditChanged(); break;
        case 15: _t->KiEditChanged(); break;
        case 16: _t->AntiWindupEditChanged(); break;
        case 17: _t->GNDDampSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 18: _t->GNDDampEditChanged(); break;
        case 19: _t->ColDampSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 20: _t->ColDampEditChanged(); break;
        case 21: _t->MaxVelLimitSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 22: _t->UseSelfColCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 23: _t->UseMaxVelLimitCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 24: _t->UseVolEffectsCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 25: _t->UseTempCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 26: _t->TempSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 27: _t->TempEditChanged(); break;
        case 28: _t->VaryTempCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 29: _t->TempPerSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 30: _t->TempPerEditChanged(); break;
        case 31: _t->UseGravCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 32: _t->GravSliderChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 33: _t->GravEditChanged(); break;
        case 34: _t->UseFloorCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 35: _t->DisplayDisableChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 36: _t->DisplayVoxChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 37: _t->DisplayConChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 38: _t->VoxDiscreteChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 39: _t->VoxDeformedChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 40: _t->VoxSmoothChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 41: _t->ForcesCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 42: _t->LCsCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 43: _t->CTypeChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 44: _t->CKinEChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 45: _t->CDispChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 46: _t->CGrowthRateChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 47: _t->CStimulusChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 48: _t->CStiffnessPlasticityChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 49: _t->CStrainEChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 50: _t->CStrainChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 51: _t->CStressChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 52: _t->CPressureChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 53: _t->CoMCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 54: _t->PlotSourcesRaysChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 55: _t->VarComboChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 56: _t->DirComboChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 57: _t->LogEachCheckChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 58: _t->ClickedPause(); break;
        case 59: _t->ClickedReset(); break;
        case 60: _t->ClickedRecord((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 61: _t->ClickedSaveData(); break;
        case 62: _t->IsOutputVisible((*reinterpret_cast< bool*(*)>(_a[1]))); break;
        case 63: _t->IsPlotVisible((*reinterpret_cast< bool*(*)>(_a[1]))); break;
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject Dlg_Physics::staticMetaObject = { {
    QMetaObject::SuperData::link<QWidget::staticMetaObject>(),
    qt_meta_stringdata_Dlg_Physics.data,
    qt_meta_data_Dlg_Physics,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *Dlg_Physics::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *Dlg_Physics::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_Dlg_Physics.stringdata0))
        return static_cast<void*>(this);
    return QWidget::qt_metacast(_clname);
}

int Dlg_Physics::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 64)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 64;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 64)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 64;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
