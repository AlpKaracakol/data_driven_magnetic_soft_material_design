/****************************************************************************
** Meta object code from reading C++ file 'VoxCad.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.3)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../VoxCad/VoxCad.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'VoxCad.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_VoxCad_t {
    QByteArrayData data[84];
    char stringdata0[907];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_VoxCad_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_VoxCad_t qt_meta_stringdata_VoxCad = {
    {
QT_MOC_LITERAL(0, 0, 6), // "VoxCad"
QT_MOC_LITERAL(1, 7, 3), // "New"
QT_MOC_LITERAL(2, 11, 0), // ""
QT_MOC_LITERAL(3, 12, 7), // "OpenVXC"
QT_MOC_LITERAL(4, 20, 8), // "SaveZLib"
QT_MOC_LITERAL(5, 29, 10), // "SaveAsZLib"
QT_MOC_LITERAL(6, 40, 9), // "ImportVXA"
QT_MOC_LITERAL(7, 50, 7), // "SaveVXA"
QT_MOC_LITERAL(8, 58, 4), // "Copy"
QT_MOC_LITERAL(9, 63, 3), // "Cut"
QT_MOC_LITERAL(10, 67, 5), // "Paste"
QT_MOC_LITERAL(11, 73, 15), // "ViewPerspective"
QT_MOC_LITERAL(12, 89, 9), // "RedrawNow"
QT_MOC_LITERAL(13, 99, 7), // "ViewTop"
QT_MOC_LITERAL(14, 107, 10), // "ViewBottom"
QT_MOC_LITERAL(15, 118, 8), // "ViewLeft"
QT_MOC_LITERAL(16, 127, 9), // "ViewRight"
QT_MOC_LITERAL(17, 137, 9), // "ViewFront"
QT_MOC_LITERAL(18, 147, 8), // "ViewBack"
QT_MOC_LITERAL(19, 156, 9), // "ViewTriad"
QT_MOC_LITERAL(20, 166, 7), // "Visible"
QT_MOC_LITERAL(21, 174, 15), // "FastModeChanged"
QT_MOC_LITERAL(22, 190, 8), // "Entering"
QT_MOC_LITERAL(23, 199, 9), // "ViewTiled"
QT_MOC_LITERAL(24, 209, 5), // "Tiled"
QT_MOC_LITERAL(25, 215, 14), // "EnableGraphics"
QT_MOC_LITERAL(26, 230, 7), // "Enabled"
QT_MOC_LITERAL(27, 238, 11), // "CheckNumVox"
QT_MOC_LITERAL(28, 250, 13), // "UpdateAllWins"
QT_MOC_LITERAL(29, 264, 14), // "ReqGLUpdateAll"
QT_MOC_LITERAL(30, 279, 10), // "ZoomExtAll"
QT_MOC_LITERAL(31, 290, 18), // "ResizeGlWindowArea"
QT_MOC_LITERAL(32, 309, 5), // "Width"
QT_MOC_LITERAL(33, 315, 6), // "Height"
QT_MOC_LITERAL(34, 322, 17), // "ResetGlWindowArea"
QT_MOC_LITERAL(35, 340, 9), // "ExportSTL"
QT_MOC_LITERAL(36, 350, 13), // "SetGLSelected"
QT_MOC_LITERAL(37, 364, 6), // "NewSel"
QT_MOC_LITERAL(38, 371, 16), // "GetCurGLSelected"
QT_MOC_LITERAL(39, 388, 4), // "int*"
QT_MOC_LITERAL(40, 393, 6), // "CurSel"
QT_MOC_LITERAL(41, 400, 12), // "WSDimChanged"
QT_MOC_LITERAL(42, 413, 14), // "SetSectionView"
QT_MOC_LITERAL(43, 428, 7), // "ViewSec"
QT_MOC_LITERAL(44, 436, 12), // "DrawCurScene"
QT_MOC_LITERAL(45, 449, 8), // "FastMode"
QT_MOC_LITERAL(46, 458, 19), // "DrawCurSceneOverlay"
QT_MOC_LITERAL(47, 478, 8), // "ViewMode"
QT_MOC_LITERAL(48, 487, 13), // "ForceViewMode"
QT_MOC_LITERAL(49, 501, 8), // "EditMode"
QT_MOC_LITERAL(50, 510, 8), // "entering"
QT_MOC_LITERAL(51, 519, 7), // "BCsMode"
QT_MOC_LITERAL(52, 527, 7), // "FEAMode"
QT_MOC_LITERAL(53, 535, 14), // "RequestFEAMode"
QT_MOC_LITERAL(54, 550, 11), // "PhysicsMode"
QT_MOC_LITERAL(55, 562, 11), // "TensileMode"
QT_MOC_LITERAL(56, 574, 11), // "Brush3DMode"
QT_MOC_LITERAL(57, 586, 11), // "WantGLIndex"
QT_MOC_LITERAL(58, 598, 5), // "bool*"
QT_MOC_LITERAL(59, 604, 2), // "YN"
QT_MOC_LITERAL(60, 607, 11), // "WantCoord3D"
QT_MOC_LITERAL(61, 619, 9), // "HoverMove"
QT_MOC_LITERAL(62, 629, 1), // "X"
QT_MOC_LITERAL(63, 631, 1), // "Y"
QT_MOC_LITERAL(64, 633, 1), // "Z"
QT_MOC_LITERAL(65, 635, 10), // "LMouseDown"
QT_MOC_LITERAL(66, 646, 6), // "IsCtrl"
QT_MOC_LITERAL(67, 653, 8), // "LMouseUp"
QT_MOC_LITERAL(68, 662, 14), // "LMouseDownMove"
QT_MOC_LITERAL(69, 677, 13), // "PressedEscape"
QT_MOC_LITERAL(70, 691, 13), // "CtrlMouseRoll"
QT_MOC_LITERAL(71, 705, 8), // "Positive"
QT_MOC_LITERAL(72, 714, 17), // "ViewPaletteWindow"
QT_MOC_LITERAL(73, 732, 19), // "ViewWorkspaceWindow"
QT_MOC_LITERAL(74, 752, 15), // "ViewRef3DWindow"
QT_MOC_LITERAL(75, 768, 17), // "ViewVoxInfoWindow"
QT_MOC_LITERAL(76, 786, 13), // "ViewBCsWindow"
QT_MOC_LITERAL(77, 800, 17), // "ViewFEAInfoWindow"
QT_MOC_LITERAL(78, 818, 17), // "ViewPhysicsWindow"
QT_MOC_LITERAL(79, 836, 17), // "ViewTensileWindow"
QT_MOC_LITERAL(80, 854, 15), // "ViewBrushWindow"
QT_MOC_LITERAL(81, 870, 18), // "GetPlotRqdDataType"
QT_MOC_LITERAL(82, 889, 5), // "char*"
QT_MOC_LITERAL(83, 895, 11) // "pRqdDataOut"

    },
    "VoxCad\0New\0\0OpenVXC\0SaveZLib\0SaveAsZLib\0"
    "ImportVXA\0SaveVXA\0Copy\0Cut\0Paste\0"
    "ViewPerspective\0RedrawNow\0ViewTop\0"
    "ViewBottom\0ViewLeft\0ViewRight\0ViewFront\0"
    "ViewBack\0ViewTriad\0Visible\0FastModeChanged\0"
    "Entering\0ViewTiled\0Tiled\0EnableGraphics\0"
    "Enabled\0CheckNumVox\0UpdateAllWins\0"
    "ReqGLUpdateAll\0ZoomExtAll\0ResizeGlWindowArea\0"
    "Width\0Height\0ResetGlWindowArea\0ExportSTL\0"
    "SetGLSelected\0NewSel\0GetCurGLSelected\0"
    "int*\0CurSel\0WSDimChanged\0SetSectionView\0"
    "ViewSec\0DrawCurScene\0FastMode\0"
    "DrawCurSceneOverlay\0ViewMode\0ForceViewMode\0"
    "EditMode\0entering\0BCsMode\0FEAMode\0"
    "RequestFEAMode\0PhysicsMode\0TensileMode\0"
    "Brush3DMode\0WantGLIndex\0bool*\0YN\0"
    "WantCoord3D\0HoverMove\0X\0Y\0Z\0LMouseDown\0"
    "IsCtrl\0LMouseUp\0LMouseDownMove\0"
    "PressedEscape\0CtrlMouseRoll\0Positive\0"
    "ViewPaletteWindow\0ViewWorkspaceWindow\0"
    "ViewRef3DWindow\0ViewVoxInfoWindow\0"
    "ViewBCsWindow\0ViewFEAInfoWindow\0"
    "ViewPhysicsWindow\0ViewTensileWindow\0"
    "ViewBrushWindow\0GetPlotRqdDataType\0"
    "char*\0pRqdDataOut"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_VoxCad[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
      71,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,  369,    2, 0x0a /* Public */,
       3,    0,  370,    2, 0x0a /* Public */,
       4,    0,  371,    2, 0x0a /* Public */,
       5,    0,  372,    2, 0x0a /* Public */,
       6,    0,  373,    2, 0x0a /* Public */,
       7,    0,  374,    2, 0x0a /* Public */,
       8,    0,  375,    2, 0x0a /* Public */,
       9,    0,  376,    2, 0x0a /* Public */,
      10,    0,  377,    2, 0x0a /* Public */,
      11,    1,  378,    2, 0x0a /* Public */,
      11,    0,  381,    2, 0x2a /* Public | MethodCloned */,
      13,    1,  382,    2, 0x0a /* Public */,
      13,    0,  385,    2, 0x2a /* Public | MethodCloned */,
      14,    0,  386,    2, 0x0a /* Public */,
      15,    0,  387,    2, 0x0a /* Public */,
      16,    0,  388,    2, 0x0a /* Public */,
      17,    0,  389,    2, 0x0a /* Public */,
      18,    0,  390,    2, 0x0a /* Public */,
      19,    1,  391,    2, 0x0a /* Public */,
      21,    1,  394,    2, 0x0a /* Public */,
      23,    1,  397,    2, 0x0a /* Public */,
      25,    1,  400,    2, 0x0a /* Public */,
      27,    0,  403,    2, 0x0a /* Public */,
      28,    0,  404,    2, 0x0a /* Public */,
      29,    0,  405,    2, 0x0a /* Public */,
      30,    0,  406,    2, 0x0a /* Public */,
      31,    2,  407,    2, 0x0a /* Public */,
      34,    0,  412,    2, 0x0a /* Public */,
      35,    0,  413,    2, 0x0a /* Public */,
      36,    1,  414,    2, 0x0a /* Public */,
      36,    0,  417,    2, 0x2a /* Public | MethodCloned */,
      38,    1,  418,    2, 0x0a /* Public */,
      41,    0,  421,    2, 0x0a /* Public */,
      42,    1,  422,    2, 0x0a /* Public */,
      44,    1,  425,    2, 0x0a /* Public */,
      44,    0,  428,    2, 0x2a /* Public | MethodCloned */,
      46,    0,  429,    2, 0x0a /* Public */,
      47,    0,  430,    2, 0x0a /* Public */,
      48,    0,  431,    2, 0x0a /* Public */,
      49,    1,  432,    2, 0x0a /* Public */,
      49,    0,  435,    2, 0x2a /* Public | MethodCloned */,
      51,    1,  436,    2, 0x0a /* Public */,
      51,    0,  439,    2, 0x2a /* Public | MethodCloned */,
      52,    1,  440,    2, 0x0a /* Public */,
      52,    0,  443,    2, 0x2a /* Public | MethodCloned */,
      53,    1,  444,    2, 0x0a /* Public */,
      53,    0,  447,    2, 0x2a /* Public | MethodCloned */,
      54,    1,  448,    2, 0x0a /* Public */,
      54,    0,  451,    2, 0x2a /* Public | MethodCloned */,
      55,    1,  452,    2, 0x0a /* Public */,
      55,    0,  455,    2, 0x2a /* Public | MethodCloned */,
      56,    1,  456,    2, 0x0a /* Public */,
      56,    0,  459,    2, 0x2a /* Public | MethodCloned */,
      57,    1,  460,    2, 0x0a /* Public */,
      60,    1,  463,    2, 0x0a /* Public */,
      61,    3,  466,    2, 0x0a /* Public */,
      65,    4,  473,    2, 0x0a /* Public */,
      67,    3,  482,    2, 0x0a /* Public */,
      68,    3,  489,    2, 0x0a /* Public */,
      69,    0,  496,    2, 0x0a /* Public */,
      70,    1,  497,    2, 0x0a /* Public */,
      72,    1,  500,    2, 0x0a /* Public */,
      73,    1,  503,    2, 0x0a /* Public */,
      74,    1,  506,    2, 0x0a /* Public */,
      75,    1,  509,    2, 0x0a /* Public */,
      76,    1,  512,    2, 0x0a /* Public */,
      77,    1,  515,    2, 0x0a /* Public */,
      78,    1,  518,    2, 0x0a /* Public */,
      79,    1,  521,    2, 0x0a /* Public */,
      80,    1,  524,    2, 0x0a /* Public */,
      81,    1,  527,    2, 0x0a /* Public */,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   12,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   22,
    QMetaType::Void, QMetaType::Bool,   24,
    QMetaType::Void, QMetaType::Bool,   26,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int, QMetaType::Int,   32,   33,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int,   37,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 39,   40,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   43,
    QMetaType::Void, QMetaType::Bool,   45,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   50,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 58,   59,
    QMetaType::Void, 0x80000000 | 58,   59,
    QMetaType::Void, QMetaType::Float, QMetaType::Float, QMetaType::Float,   62,   63,   64,
    QMetaType::Void, QMetaType::Float, QMetaType::Float, QMetaType::Float, QMetaType::Bool,   62,   63,   64,   66,
    QMetaType::Void, QMetaType::Float, QMetaType::Float, QMetaType::Float,   62,   63,   64,
    QMetaType::Void, QMetaType::Float, QMetaType::Float, QMetaType::Float,   62,   63,   64,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   71,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, QMetaType::Bool,   20,
    QMetaType::Void, 0x80000000 | 82,   83,

       0        // eod
};

void VoxCad::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<VoxCad *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->New(); break;
        case 1: _t->OpenVXC(); break;
        case 2: _t->SaveZLib(); break;
        case 3: _t->SaveAsZLib(); break;
        case 4: _t->ImportVXA(); break;
        case 5: _t->SaveVXA(); break;
        case 6: _t->Copy(); break;
        case 7: _t->Cut(); break;
        case 8: _t->Paste(); break;
        case 9: _t->ViewPerspective((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 10: _t->ViewPerspective(); break;
        case 11: _t->ViewTop((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 12: _t->ViewTop(); break;
        case 13: _t->ViewBottom(); break;
        case 14: _t->ViewLeft(); break;
        case 15: _t->ViewRight(); break;
        case 16: _t->ViewFront(); break;
        case 17: _t->ViewBack(); break;
        case 18: _t->ViewTriad((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 19: _t->FastModeChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 20: _t->ViewTiled((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 21: _t->EnableGraphics((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 22: _t->CheckNumVox(); break;
        case 23: _t->UpdateAllWins(); break;
        case 24: _t->ReqGLUpdateAll(); break;
        case 25: _t->ZoomExtAll(); break;
        case 26: _t->ResizeGlWindowArea((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        case 27: _t->ResetGlWindowArea(); break;
        case 28: _t->ExportSTL(); break;
        case 29: _t->SetGLSelected((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 30: _t->SetGLSelected(); break;
        case 31: _t->GetCurGLSelected((*reinterpret_cast< int*(*)>(_a[1]))); break;
        case 32: _t->WSDimChanged(); break;
        case 33: _t->SetSectionView((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 34: _t->DrawCurScene((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 35: _t->DrawCurScene(); break;
        case 36: _t->DrawCurSceneOverlay(); break;
        case 37: _t->ViewMode(); break;
        case 38: _t->ForceViewMode(); break;
        case 39: _t->EditMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 40: _t->EditMode(); break;
        case 41: _t->BCsMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 42: _t->BCsMode(); break;
        case 43: _t->FEAMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 44: _t->FEAMode(); break;
        case 45: _t->RequestFEAMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 46: _t->RequestFEAMode(); break;
        case 47: _t->PhysicsMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 48: _t->PhysicsMode(); break;
        case 49: _t->TensileMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 50: _t->TensileMode(); break;
        case 51: _t->Brush3DMode((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 52: _t->Brush3DMode(); break;
        case 53: _t->WantGLIndex((*reinterpret_cast< bool*(*)>(_a[1]))); break;
        case 54: _t->WantCoord3D((*reinterpret_cast< bool*(*)>(_a[1]))); break;
        case 55: _t->HoverMove((*reinterpret_cast< float(*)>(_a[1])),(*reinterpret_cast< float(*)>(_a[2])),(*reinterpret_cast< float(*)>(_a[3]))); break;
        case 56: _t->LMouseDown((*reinterpret_cast< float(*)>(_a[1])),(*reinterpret_cast< float(*)>(_a[2])),(*reinterpret_cast< float(*)>(_a[3])),(*reinterpret_cast< bool(*)>(_a[4]))); break;
        case 57: _t->LMouseUp((*reinterpret_cast< float(*)>(_a[1])),(*reinterpret_cast< float(*)>(_a[2])),(*reinterpret_cast< float(*)>(_a[3]))); break;
        case 58: _t->LMouseDownMove((*reinterpret_cast< float(*)>(_a[1])),(*reinterpret_cast< float(*)>(_a[2])),(*reinterpret_cast< float(*)>(_a[3]))); break;
        case 59: _t->PressedEscape(); break;
        case 60: _t->CtrlMouseRoll((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 61: _t->ViewPaletteWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 62: _t->ViewWorkspaceWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 63: _t->ViewRef3DWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 64: _t->ViewVoxInfoWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 65: _t->ViewBCsWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 66: _t->ViewFEAInfoWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 67: _t->ViewPhysicsWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 68: _t->ViewTensileWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 69: _t->ViewBrushWindow((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 70: _t->GetPlotRqdDataType((*reinterpret_cast< char*(*)>(_a[1]))); break;
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject VoxCad::staticMetaObject = { {
    QMetaObject::SuperData::link<QMainWindow::staticMetaObject>(),
    qt_meta_stringdata_VoxCad.data,
    qt_meta_data_VoxCad,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *VoxCad::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *VoxCad::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_VoxCad.stringdata0))
        return static_cast<void*>(this);
    return QMainWindow::qt_metacast(_clname);
}

int VoxCad::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QMainWindow::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 71)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 71;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 71)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 71;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
