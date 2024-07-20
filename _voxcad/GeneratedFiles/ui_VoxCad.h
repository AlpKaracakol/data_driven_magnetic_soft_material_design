/********************************************************************************
** Form generated from reading UI file 'VoxCad.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VOXCAD_H
#define UI_VOXCAD_H

#include <QtCore/QVariant>
#include <QtGui/QIcon>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_VoxCadClass
{
public:
    QAction *actionOpen;
    QAction *actionSave;
    QAction *actionCenter_View;
    QAction *actionSave_As;
    QAction *actionASCII_VXC;
    QAction *actionBASE64_VXC;
    QAction *actionSolve;
    QAction *actionPerspective;
    QAction *actionTop;
    QAction *actionBottom;
    QAction *actionLeft;
    QAction *actionRight;
    QAction *actionFront;
    QAction *actionBack;
    QAction *actionEdit_Voxels;
    QAction *actionLayer_Back;
    QAction *actionLayer_Forward;
    QAction *actionPencil;
    QAction *actionRectangle;
    QAction *actionCircle;
    QAction *actionReference_View;
    QAction *actionPalette;
    QAction *actionWorkspace;
    QAction *actionInfo;
    QAction *actionBCs;
    QAction *actionSection_View;
    QAction *actionNew;
    QAction *actionVXA_OUT;
    QAction *actionSTL;
    QAction *actionDMU_Out;
    QAction *actionCopy;
    QAction *actionCut;
    QAction *actionPaste;
    QAction *actionVXA_IN;
    QAction *actionLarge_Mode;
    QAction *actionPhysics;
    QAction *action3D_Brush;
    QAction *actionTensile;
    QAction *actionVoxelCoordinates;
    QAction *actionPaint_Bucket;
    QAction *actionView_Tiled;
    QAction *actionGraphics_Enabled;
    QAction *actionKV6;
    QAction *actionBenchmark;
    QAction *actionShow_Triad;
    QWidget *centralWidget;
    QHBoxLayout *horizontalLayout;
    QMenuBar *menuBar;
    QMenu *menuFile;
    QMenu *menuExport;
    QMenu *menuAlternate_VXC;
    QMenu *menuMesh;
    QMenu *menuImport;
    QMenu *menuView;
    QMenu *menuStandard_Views;
    QMenu *menuSection;
    QMenu *menuAnalyze;
    QMenu *menuTools;
    QMenu *menuDrawing;
    QMenu *menuEdit;
    QStatusBar *statusBar;
    QToolBar *FileToolBar;
    QToolBar *ViewtoolBar;
    QToolBar *DrawingtoolBar;
    QToolBar *DialogToolbar;
    QToolBar *SectionToolBar;

    void setupUi(QMainWindow *VoxCadClass)
    {
        if (VoxCadClass->objectName().isEmpty())
            VoxCadClass->setObjectName(QString::fromUtf8("VoxCadClass"));
        VoxCadClass->setEnabled(true);
        VoxCadClass->resize(751, 478);
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/VoxCad/VoxCad.ico"), QSize(), QIcon::Normal, QIcon::Off);
        VoxCadClass->setWindowIcon(icon);
        actionOpen = new QAction(VoxCadClass);
        actionOpen->setObjectName(QString::fromUtf8("actionOpen"));
        QIcon icon1;
        icon1.addFile(QString::fromUtf8(":/Icons/Icons/Open.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionOpen->setIcon(icon1);
        actionSave = new QAction(VoxCadClass);
        actionSave->setObjectName(QString::fromUtf8("actionSave"));
        QIcon icon2;
        icon2.addFile(QString::fromUtf8(":/Icons/Icons/Save.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionSave->setIcon(icon2);
        actionCenter_View = new QAction(VoxCadClass);
        actionCenter_View->setObjectName(QString::fromUtf8("actionCenter_View"));
        QIcon icon3;
        icon3.addFile(QString::fromUtf8(":/Icons/Icons/ZoomExtents2.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionCenter_View->setIcon(icon3);
        actionSave_As = new QAction(VoxCadClass);
        actionSave_As->setObjectName(QString::fromUtf8("actionSave_As"));
        actionASCII_VXC = new QAction(VoxCadClass);
        actionASCII_VXC->setObjectName(QString::fromUtf8("actionASCII_VXC"));
        actionBASE64_VXC = new QAction(VoxCadClass);
        actionBASE64_VXC->setObjectName(QString::fromUtf8("actionBASE64_VXC"));
        actionSolve = new QAction(VoxCadClass);
        actionSolve->setObjectName(QString::fromUtf8("actionSolve"));
        actionSolve->setCheckable(true);
        QIcon icon4;
        icon4.addFile(QString::fromUtf8(":/Icons/Icons/Analyze.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionSolve->setIcon(icon4);
        actionSolve->setVisible(false);
        actionPerspective = new QAction(VoxCadClass);
        actionPerspective->setObjectName(QString::fromUtf8("actionPerspective"));
        QIcon icon5;
        icon5.addFile(QString::fromUtf8(":/Icons/Icons/ViewPerspective.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionPerspective->setIcon(icon5);
        actionTop = new QAction(VoxCadClass);
        actionTop->setObjectName(QString::fromUtf8("actionTop"));
        QIcon icon6;
        icon6.addFile(QString::fromUtf8(":/Icons/Icons/ViewTop.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionTop->setIcon(icon6);
        actionBottom = new QAction(VoxCadClass);
        actionBottom->setObjectName(QString::fromUtf8("actionBottom"));
        QIcon icon7;
        icon7.addFile(QString::fromUtf8(":/Icons/Icons/ViewBottom.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionBottom->setIcon(icon7);
        actionLeft = new QAction(VoxCadClass);
        actionLeft->setObjectName(QString::fromUtf8("actionLeft"));
        QIcon icon8;
        icon8.addFile(QString::fromUtf8(":/Icons/Icons/ViewLeft.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionLeft->setIcon(icon8);
        actionRight = new QAction(VoxCadClass);
        actionRight->setObjectName(QString::fromUtf8("actionRight"));
        QIcon icon9;
        icon9.addFile(QString::fromUtf8(":/Icons/Icons/ViewRight.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionRight->setIcon(icon9);
        actionFront = new QAction(VoxCadClass);
        actionFront->setObjectName(QString::fromUtf8("actionFront"));
        QIcon icon10;
        icon10.addFile(QString::fromUtf8(":/Icons/Icons/ViewFront.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionFront->setIcon(icon10);
        actionBack = new QAction(VoxCadClass);
        actionBack->setObjectName(QString::fromUtf8("actionBack"));
        QIcon icon11;
        icon11.addFile(QString::fromUtf8(":/Icons/Icons/ViewBack.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionBack->setIcon(icon11);
        actionEdit_Voxels = new QAction(VoxCadClass);
        actionEdit_Voxels->setObjectName(QString::fromUtf8("actionEdit_Voxels"));
        actionEdit_Voxels->setCheckable(true);
        QIcon icon12;
        icon12.addFile(QString::fromUtf8(":/Icons/Icons/EditLayer.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionEdit_Voxels->setIcon(icon12);
        actionLayer_Back = new QAction(VoxCadClass);
        actionLayer_Back->setObjectName(QString::fromUtf8("actionLayer_Back"));
        QIcon icon13;
        icon13.addFile(QString::fromUtf8(":/Icons/Icons/LayerBack.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionLayer_Back->setIcon(icon13);
        actionLayer_Forward = new QAction(VoxCadClass);
        actionLayer_Forward->setObjectName(QString::fromUtf8("actionLayer_Forward"));
        QIcon icon14;
        icon14.addFile(QString::fromUtf8(":/Icons/Icons/LayerForward.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionLayer_Forward->setIcon(icon14);
        actionPencil = new QAction(VoxCadClass);
        actionPencil->setObjectName(QString::fromUtf8("actionPencil"));
        actionPencil->setCheckable(true);
        actionPencil->setChecked(true);
        QIcon icon15;
        icon15.addFile(QString::fromUtf8(":/Icons/Icons/Pencil.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionPencil->setIcon(icon15);
        actionRectangle = new QAction(VoxCadClass);
        actionRectangle->setObjectName(QString::fromUtf8("actionRectangle"));
        actionRectangle->setCheckable(true);
        QIcon icon16;
        icon16.addFile(QString::fromUtf8(":/Icons/Icons/Rectangle.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionRectangle->setIcon(icon16);
        actionCircle = new QAction(VoxCadClass);
        actionCircle->setObjectName(QString::fromUtf8("actionCircle"));
        actionCircle->setCheckable(true);
        QIcon icon17;
        icon17.addFile(QString::fromUtf8(":/Icons/Icons/Ellipse.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionCircle->setIcon(icon17);
        actionReference_View = new QAction(VoxCadClass);
        actionReference_View->setObjectName(QString::fromUtf8("actionReference_View"));
        actionReference_View->setCheckable(true);
        QIcon icon18;
        icon18.addFile(QString::fromUtf8(":/Icons/Icons/Aux_View.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionReference_View->setIcon(icon18);
        actionPalette = new QAction(VoxCadClass);
        actionPalette->setObjectName(QString::fromUtf8("actionPalette"));
        actionPalette->setCheckable(true);
        QIcon icon19;
        icon19.addFile(QString::fromUtf8(":/Icons/Icons/Material.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionPalette->setIcon(icon19);
        actionWorkspace = new QAction(VoxCadClass);
        actionWorkspace->setObjectName(QString::fromUtf8("actionWorkspace"));
        actionWorkspace->setCheckable(true);
        QIcon icon20;
        icon20.addFile(QString::fromUtf8(":/Icons/Icons/Workspace.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionWorkspace->setIcon(icon20);
        actionInfo = new QAction(VoxCadClass);
        actionInfo->setObjectName(QString::fromUtf8("actionInfo"));
        actionInfo->setCheckable(true);
        QIcon icon21;
        icon21.addFile(QString::fromUtf8(":/Icons/Icons/Info.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionInfo->setIcon(icon21);
        actionBCs = new QAction(VoxCadClass);
        actionBCs->setObjectName(QString::fromUtf8("actionBCs"));
        actionBCs->setCheckable(true);
        QIcon icon22;
        icon22.addFile(QString::fromUtf8(":/Icons/Icons/BCs.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionBCs->setIcon(icon22);
        actionSection_View = new QAction(VoxCadClass);
        actionSection_View->setObjectName(QString::fromUtf8("actionSection_View"));
        actionSection_View->setCheckable(true);
        QIcon icon23;
        icon23.addFile(QString::fromUtf8(":/Icons/Icons/Section.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionSection_View->setIcon(icon23);
        actionNew = new QAction(VoxCadClass);
        actionNew->setObjectName(QString::fromUtf8("actionNew"));
        QIcon icon24;
        icon24.addFile(QString::fromUtf8(":/Icons/Icons/New.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionNew->setIcon(icon24);
        actionVXA_OUT = new QAction(VoxCadClass);
        actionVXA_OUT->setObjectName(QString::fromUtf8("actionVXA_OUT"));
        actionSTL = new QAction(VoxCadClass);
        actionSTL->setObjectName(QString::fromUtf8("actionSTL"));
        actionDMU_Out = new QAction(VoxCadClass);
        actionDMU_Out->setObjectName(QString::fromUtf8("actionDMU_Out"));
        actionCopy = new QAction(VoxCadClass);
        actionCopy->setObjectName(QString::fromUtf8("actionCopy"));
        QIcon icon25;
        icon25.addFile(QString::fromUtf8(":/Icons/Icons/Copy.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionCopy->setIcon(icon25);
        actionCut = new QAction(VoxCadClass);
        actionCut->setObjectName(QString::fromUtf8("actionCut"));
        QIcon icon26;
        icon26.addFile(QString::fromUtf8(":/Icons/Icons/Cut.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionCut->setIcon(icon26);
        actionPaste = new QAction(VoxCadClass);
        actionPaste->setObjectName(QString::fromUtf8("actionPaste"));
        QIcon icon27;
        icon27.addFile(QString::fromUtf8(":/Icons/Icons/Paste.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionPaste->setIcon(icon27);
        actionVXA_IN = new QAction(VoxCadClass);
        actionVXA_IN->setObjectName(QString::fromUtf8("actionVXA_IN"));
        actionLarge_Mode = new QAction(VoxCadClass);
        actionLarge_Mode->setObjectName(QString::fromUtf8("actionLarge_Mode"));
        actionLarge_Mode->setCheckable(true);
        actionPhysics = new QAction(VoxCadClass);
        actionPhysics->setObjectName(QString::fromUtf8("actionPhysics"));
        actionPhysics->setCheckable(true);
        QIcon icon28;
        icon28.addFile(QString::fromUtf8(":/Icons/Icons/Sandbox.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionPhysics->setIcon(icon28);
        action3D_Brush = new QAction(VoxCadClass);
        action3D_Brush->setObjectName(QString::fromUtf8("action3D_Brush"));
        action3D_Brush->setCheckable(true);
        QIcon icon29;
        icon29.addFile(QString::fromUtf8(":/Icons/Icons/3DBrush.png"), QSize(), QIcon::Normal, QIcon::Off);
        action3D_Brush->setIcon(icon29);
        actionTensile = new QAction(VoxCadClass);
        actionTensile->setObjectName(QString::fromUtf8("actionTensile"));
        actionTensile->setCheckable(true);
        QIcon icon30;
        icon30.addFile(QString::fromUtf8(":/Icons/Icons/Tensile.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionTensile->setIcon(icon30);
        actionVoxelCoordinates = new QAction(VoxCadClass);
        actionVoxelCoordinates->setObjectName(QString::fromUtf8("actionVoxelCoordinates"));
        actionPaint_Bucket = new QAction(VoxCadClass);
        actionPaint_Bucket->setObjectName(QString::fromUtf8("actionPaint_Bucket"));
        actionPaint_Bucket->setCheckable(true);
        QIcon icon31;
        icon31.addFile(QString::fromUtf8(":/Icons/Icons/Bucket.png"), QSize(), QIcon::Normal, QIcon::Off);
        actionPaint_Bucket->setIcon(icon31);
        actionView_Tiled = new QAction(VoxCadClass);
        actionView_Tiled->setObjectName(QString::fromUtf8("actionView_Tiled"));
        actionView_Tiled->setCheckable(true);
        actionGraphics_Enabled = new QAction(VoxCadClass);
        actionGraphics_Enabled->setObjectName(QString::fromUtf8("actionGraphics_Enabled"));
        actionGraphics_Enabled->setCheckable(true);
        actionKV6 = new QAction(VoxCadClass);
        actionKV6->setObjectName(QString::fromUtf8("actionKV6"));
        actionBenchmark = new QAction(VoxCadClass);
        actionBenchmark->setObjectName(QString::fromUtf8("actionBenchmark"));
        actionBenchmark->setVisible(false);
        actionShow_Triad = new QAction(VoxCadClass);
        actionShow_Triad->setObjectName(QString::fromUtf8("actionShow_Triad"));
        actionShow_Triad->setCheckable(true);
        actionShow_Triad->setChecked(true);
        centralWidget = new QWidget(VoxCadClass);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        horizontalLayout = new QHBoxLayout(centralWidget);
        horizontalLayout->setSpacing(6);
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        VoxCadClass->setCentralWidget(centralWidget);
        menuBar = new QMenuBar(VoxCadClass);
        menuBar->setObjectName(QString::fromUtf8("menuBar"));
        menuBar->setGeometry(QRect(0, 0, 751, 21));
        menuFile = new QMenu(menuBar);
        menuFile->setObjectName(QString::fromUtf8("menuFile"));
        menuExport = new QMenu(menuFile);
        menuExport->setObjectName(QString::fromUtf8("menuExport"));
        menuAlternate_VXC = new QMenu(menuExport);
        menuAlternate_VXC->setObjectName(QString::fromUtf8("menuAlternate_VXC"));
        menuMesh = new QMenu(menuExport);
        menuMesh->setObjectName(QString::fromUtf8("menuMesh"));
        menuImport = new QMenu(menuFile);
        menuImport->setObjectName(QString::fromUtf8("menuImport"));
        menuView = new QMenu(menuBar);
        menuView->setObjectName(QString::fromUtf8("menuView"));
        menuStandard_Views = new QMenu(menuView);
        menuStandard_Views->setObjectName(QString::fromUtf8("menuStandard_Views"));
        menuSection = new QMenu(menuView);
        menuSection->setObjectName(QString::fromUtf8("menuSection"));
        menuAnalyze = new QMenu(menuBar);
        menuAnalyze->setObjectName(QString::fromUtf8("menuAnalyze"));
        menuTools = new QMenu(menuBar);
        menuTools->setObjectName(QString::fromUtf8("menuTools"));
        menuDrawing = new QMenu(menuTools);
        menuDrawing->setObjectName(QString::fromUtf8("menuDrawing"));
        menuEdit = new QMenu(menuBar);
        menuEdit->setObjectName(QString::fromUtf8("menuEdit"));
        VoxCadClass->setMenuBar(menuBar);
        statusBar = new QStatusBar(VoxCadClass);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        VoxCadClass->setStatusBar(statusBar);
        FileToolBar = new QToolBar(VoxCadClass);
        FileToolBar->setObjectName(QString::fromUtf8("FileToolBar"));
        FileToolBar->setIconSize(QSize(16, 16));
        VoxCadClass->addToolBar(Qt::TopToolBarArea, FileToolBar);
        ViewtoolBar = new QToolBar(VoxCadClass);
        ViewtoolBar->setObjectName(QString::fromUtf8("ViewtoolBar"));
        ViewtoolBar->setIconSize(QSize(16, 16));
        VoxCadClass->addToolBar(Qt::TopToolBarArea, ViewtoolBar);
        DrawingtoolBar = new QToolBar(VoxCadClass);
        DrawingtoolBar->setObjectName(QString::fromUtf8("DrawingtoolBar"));
        DrawingtoolBar->setIconSize(QSize(16, 16));
        VoxCadClass->addToolBar(Qt::LeftToolBarArea, DrawingtoolBar);
        DialogToolbar = new QToolBar(VoxCadClass);
        DialogToolbar->setObjectName(QString::fromUtf8("DialogToolbar"));
        DialogToolbar->setIconSize(QSize(16, 16));
        VoxCadClass->addToolBar(Qt::TopToolBarArea, DialogToolbar);
        SectionToolBar = new QToolBar(VoxCadClass);
        SectionToolBar->setObjectName(QString::fromUtf8("SectionToolBar"));
        SectionToolBar->setIconSize(QSize(16, 16));
        VoxCadClass->addToolBar(Qt::TopToolBarArea, SectionToolBar);

        menuBar->addAction(menuFile->menuAction());
        menuBar->addAction(menuEdit->menuAction());
        menuBar->addAction(menuView->menuAction());
        menuBar->addAction(menuTools->menuAction());
        menuBar->addAction(menuAnalyze->menuAction());
        menuFile->addAction(actionNew);
        menuFile->addAction(actionOpen);
        menuFile->addSeparator();
        menuFile->addAction(actionSave);
        menuFile->addAction(actionSave_As);
        menuFile->addSeparator();
        menuFile->addAction(menuImport->menuAction());
        menuFile->addAction(menuExport->menuAction());
        menuExport->addAction(actionVXA_OUT);
        menuExport->addAction(actionKV6);
        menuExport->addAction(actionDMU_Out);
        menuExport->addAction(actionVoxelCoordinates);
        menuExport->addAction(menuMesh->menuAction());
        menuExport->addAction(menuAlternate_VXC->menuAction());
        menuAlternate_VXC->addAction(actionBASE64_VXC);
        menuAlternate_VXC->addAction(actionASCII_VXC);
        menuMesh->addAction(actionSTL);
        menuImport->addAction(actionVXA_IN);
        menuView->addAction(actionCenter_View);
        menuView->addAction(menuStandard_Views->menuAction());
        menuView->addAction(menuSection->menuAction());
        menuView->addSeparator();
        menuView->addAction(actionShow_Triad);
        menuView->addAction(actionLarge_Mode);
        menuView->addAction(actionView_Tiled);
        menuView->addAction(actionGraphics_Enabled);
        menuView->addSeparator();
        menuView->addAction(actionReference_View);
        menuView->addAction(actionInfo);
        menuView->addSeparator();
        menuStandard_Views->addAction(actionPerspective);
        menuStandard_Views->addSeparator();
        menuStandard_Views->addAction(actionTop);
        menuStandard_Views->addAction(actionBottom);
        menuStandard_Views->addAction(actionLeft);
        menuStandard_Views->addAction(actionRight);
        menuStandard_Views->addAction(actionFront);
        menuStandard_Views->addAction(actionBack);
        menuSection->addAction(actionSection_View);
        menuSection->addAction(actionLayer_Forward);
        menuSection->addAction(actionLayer_Back);
        menuAnalyze->addAction(actionBCs);
        menuAnalyze->addAction(actionSolve);
        menuAnalyze->addSeparator();
        menuAnalyze->addAction(actionTensile);
        menuAnalyze->addAction(actionPhysics);
        menuAnalyze->addAction(actionBenchmark);
        menuTools->addAction(actionEdit_Voxels);
        menuTools->addAction(action3D_Brush);
        menuTools->addSeparator();
        menuTools->addAction(menuDrawing->menuAction());
        menuDrawing->addAction(actionPencil);
        menuDrawing->addAction(actionRectangle);
        menuDrawing->addAction(actionCircle);
        menuDrawing->addAction(actionPaint_Bucket);
        menuEdit->addAction(actionCopy);
        menuEdit->addAction(actionCut);
        menuEdit->addAction(actionPaste);
        menuEdit->addSeparator();
        menuEdit->addAction(actionWorkspace);
        menuEdit->addAction(actionPalette);
        FileToolBar->addAction(actionNew);
        FileToolBar->addAction(actionOpen);
        FileToolBar->addAction(actionSave);
        ViewtoolBar->addAction(actionCenter_View);
        ViewtoolBar->addAction(actionPerspective);
        ViewtoolBar->addAction(actionTop);
        ViewtoolBar->addAction(actionBottom);
        ViewtoolBar->addAction(actionLeft);
        ViewtoolBar->addAction(actionRight);
        ViewtoolBar->addAction(actionFront);
        ViewtoolBar->addAction(actionBack);
        DrawingtoolBar->addAction(actionPencil);
        DrawingtoolBar->addAction(actionRectangle);
        DrawingtoolBar->addAction(actionCircle);
        DrawingtoolBar->addAction(actionPaint_Bucket);
        DialogToolbar->addAction(actionPalette);
        DialogToolbar->addAction(actionWorkspace);
        DialogToolbar->addAction(actionEdit_Voxels);
        DialogToolbar->addAction(action3D_Brush);
        DialogToolbar->addAction(actionInfo);
        DialogToolbar->addAction(actionReference_View);
        DialogToolbar->addAction(actionBCs);
        DialogToolbar->addAction(actionPhysics);
        DialogToolbar->addAction(actionTensile);
        SectionToolBar->addAction(actionSection_View);
        SectionToolBar->addAction(actionLayer_Back);
        SectionToolBar->addAction(actionLayer_Forward);

        retranslateUi(VoxCadClass);

        QMetaObject::connectSlotsByName(VoxCadClass);
    } // setupUi

    void retranslateUi(QMainWindow *VoxCadClass)
    {
        VoxCadClass->setWindowTitle(QCoreApplication::translate("VoxCadClass", "GrowthVoxCad", nullptr));
        actionOpen->setText(QCoreApplication::translate("VoxCadClass", "Open", nullptr));
#if QT_CONFIG(shortcut)
        actionOpen->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+O", nullptr));
#endif // QT_CONFIG(shortcut)
        actionSave->setText(QCoreApplication::translate("VoxCadClass", "Save", nullptr));
#if QT_CONFIG(shortcut)
        actionSave->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+S", nullptr));
#endif // QT_CONFIG(shortcut)
        actionCenter_View->setText(QCoreApplication::translate("VoxCadClass", "Zoom Extents", nullptr));
        actionSave_As->setText(QCoreApplication::translate("VoxCadClass", "Save As", nullptr));
#if QT_CONFIG(shortcut)
        actionSave_As->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+Shift+S", nullptr));
#endif // QT_CONFIG(shortcut)
        actionASCII_VXC->setText(QCoreApplication::translate("VoxCadClass", "Ascii", nullptr));
        actionBASE64_VXC->setText(QCoreApplication::translate("VoxCadClass", "Base64", nullptr));
        actionSolve->setText(QCoreApplication::translate("VoxCadClass", "Solve", nullptr));
        actionPerspective->setText(QCoreApplication::translate("VoxCadClass", "Perspective", nullptr));
#if QT_CONFIG(shortcut)
        actionPerspective->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+1", nullptr));
#endif // QT_CONFIG(shortcut)
        actionTop->setText(QCoreApplication::translate("VoxCadClass", "Top", nullptr));
#if QT_CONFIG(shortcut)
        actionTop->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+2", nullptr));
#endif // QT_CONFIG(shortcut)
        actionBottom->setText(QCoreApplication::translate("VoxCadClass", "Bottom", nullptr));
#if QT_CONFIG(shortcut)
        actionBottom->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+3", nullptr));
#endif // QT_CONFIG(shortcut)
        actionLeft->setText(QCoreApplication::translate("VoxCadClass", "Left", nullptr));
#if QT_CONFIG(shortcut)
        actionLeft->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+4", nullptr));
#endif // QT_CONFIG(shortcut)
        actionRight->setText(QCoreApplication::translate("VoxCadClass", "Right", nullptr));
#if QT_CONFIG(shortcut)
        actionRight->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+5", nullptr));
#endif // QT_CONFIG(shortcut)
        actionFront->setText(QCoreApplication::translate("VoxCadClass", "Front", nullptr));
#if QT_CONFIG(shortcut)
        actionFront->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+6", nullptr));
#endif // QT_CONFIG(shortcut)
        actionBack->setText(QCoreApplication::translate("VoxCadClass", "Back", nullptr));
#if QT_CONFIG(shortcut)
        actionBack->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+7", nullptr));
#endif // QT_CONFIG(shortcut)
        actionEdit_Voxels->setText(QCoreApplication::translate("VoxCadClass", "Edit Voxels", nullptr));
#if QT_CONFIG(shortcut)
        actionEdit_Voxels->setShortcut(QCoreApplication::translate("VoxCadClass", "E", nullptr));
#endif // QT_CONFIG(shortcut)
        actionLayer_Back->setText(QCoreApplication::translate("VoxCadClass", "Layer Back", nullptr));
#if QT_CONFIG(shortcut)
        actionLayer_Back->setShortcut(QCoreApplication::translate("VoxCadClass", "-", nullptr));
#endif // QT_CONFIG(shortcut)
        actionLayer_Forward->setText(QCoreApplication::translate("VoxCadClass", "Layer Forward", nullptr));
#if QT_CONFIG(shortcut)
        actionLayer_Forward->setShortcut(QCoreApplication::translate("VoxCadClass", "+", nullptr));
#endif // QT_CONFIG(shortcut)
        actionPencil->setText(QCoreApplication::translate("VoxCadClass", "Pencil", nullptr));
#if QT_CONFIG(shortcut)
        actionPencil->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+Q", nullptr));
#endif // QT_CONFIG(shortcut)
        actionRectangle->setText(QCoreApplication::translate("VoxCadClass", "Rectangle", nullptr));
#if QT_CONFIG(shortcut)
        actionRectangle->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+W", nullptr));
#endif // QT_CONFIG(shortcut)
        actionCircle->setText(QCoreApplication::translate("VoxCadClass", "Circle", nullptr));
#if QT_CONFIG(shortcut)
        actionCircle->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+E", nullptr));
#endif // QT_CONFIG(shortcut)
        actionReference_View->setText(QCoreApplication::translate("VoxCadClass", "Reference View", nullptr));
#if QT_CONFIG(shortcut)
        actionReference_View->setShortcut(QCoreApplication::translate("VoxCadClass", "R", nullptr));
#endif // QT_CONFIG(shortcut)
        actionPalette->setText(QCoreApplication::translate("VoxCadClass", "Palette", nullptr));
#if QT_CONFIG(shortcut)
        actionPalette->setShortcut(QCoreApplication::translate("VoxCadClass", "P", nullptr));
#endif // QT_CONFIG(shortcut)
        actionWorkspace->setText(QCoreApplication::translate("VoxCadClass", "Workspace", nullptr));
#if QT_CONFIG(shortcut)
        actionWorkspace->setShortcut(QCoreApplication::translate("VoxCadClass", "W", nullptr));
#endif // QT_CONFIG(shortcut)
        actionInfo->setText(QCoreApplication::translate("VoxCadClass", "Info", nullptr));
#if QT_CONFIG(shortcut)
        actionInfo->setShortcut(QCoreApplication::translate("VoxCadClass", "I", nullptr));
#endif // QT_CONFIG(shortcut)
        actionBCs->setText(QCoreApplication::translate("VoxCadClass", "Boundary Conditions", nullptr));
#if QT_CONFIG(shortcut)
        actionBCs->setShortcut(QCoreApplication::translate("VoxCadClass", "B", nullptr));
#endif // QT_CONFIG(shortcut)
        actionSection_View->setText(QCoreApplication::translate("VoxCadClass", "Section View", nullptr));
#if QT_CONFIG(shortcut)
        actionSection_View->setShortcut(QCoreApplication::translate("VoxCadClass", "Alt+S", nullptr));
#endif // QT_CONFIG(shortcut)
        actionNew->setText(QCoreApplication::translate("VoxCadClass", "New", nullptr));
#if QT_CONFIG(shortcut)
        actionNew->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+N", nullptr));
#endif // QT_CONFIG(shortcut)
        actionVXA_OUT->setText(QCoreApplication::translate("VoxCadClass", "Simulation", nullptr));
        actionSTL->setText(QCoreApplication::translate("VoxCadClass", "STL", nullptr));
        actionDMU_Out->setText(QCoreApplication::translate("VoxCadClass", "DMU", nullptr));
        actionCopy->setText(QCoreApplication::translate("VoxCadClass", "Copy", nullptr));
#if QT_CONFIG(shortcut)
        actionCopy->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+C", nullptr));
#endif // QT_CONFIG(shortcut)
        actionCut->setText(QCoreApplication::translate("VoxCadClass", "Cut", nullptr));
#if QT_CONFIG(shortcut)
        actionCut->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+X", nullptr));
#endif // QT_CONFIG(shortcut)
        actionPaste->setText(QCoreApplication::translate("VoxCadClass", "Paste", nullptr));
#if QT_CONFIG(shortcut)
        actionPaste->setShortcut(QCoreApplication::translate("VoxCadClass", "Ctrl+V", nullptr));
#endif // QT_CONFIG(shortcut)
        actionVXA_IN->setText(QCoreApplication::translate("VoxCadClass", "Simulation", nullptr));
        actionLarge_Mode->setText(QCoreApplication::translate("VoxCadClass", "Large Mode", nullptr));
        actionPhysics->setText(QCoreApplication::translate("VoxCadClass", "Physics Sandbox", nullptr));
        action3D_Brush->setText(QCoreApplication::translate("VoxCadClass", "3D Brush", nullptr));
        actionTensile->setText(QCoreApplication::translate("VoxCadClass", "Tensile Test", nullptr));
        actionVoxelCoordinates->setText(QCoreApplication::translate("VoxCadClass", "Voxel Coordinates", nullptr));
        actionPaint_Bucket->setText(QCoreApplication::translate("VoxCadClass", "Paint Bucket", nullptr));
        actionView_Tiled->setText(QCoreApplication::translate("VoxCadClass", "View Tiled", nullptr));
        actionGraphics_Enabled->setText(QCoreApplication::translate("VoxCadClass", "Graphics Enabled", nullptr));
        actionKV6->setText(QCoreApplication::translate("VoxCadClass", "KV6", nullptr));
        actionBenchmark->setText(QCoreApplication::translate("VoxCadClass", "Benchmark", nullptr));
        actionShow_Triad->setText(QCoreApplication::translate("VoxCadClass", "Show Triad", nullptr));
        menuFile->setTitle(QCoreApplication::translate("VoxCadClass", "File", nullptr));
        menuExport->setTitle(QCoreApplication::translate("VoxCadClass", "Export", nullptr));
        menuAlternate_VXC->setTitle(QCoreApplication::translate("VoxCadClass", "Alternate VXC", nullptr));
        menuMesh->setTitle(QCoreApplication::translate("VoxCadClass", "Mesh", nullptr));
        menuImport->setTitle(QCoreApplication::translate("VoxCadClass", "Import", nullptr));
        menuView->setTitle(QCoreApplication::translate("VoxCadClass", "View", nullptr));
        menuStandard_Views->setTitle(QCoreApplication::translate("VoxCadClass", "Standard Views", nullptr));
        menuSection->setTitle(QCoreApplication::translate("VoxCadClass", "Section", nullptr));
        menuAnalyze->setTitle(QCoreApplication::translate("VoxCadClass", "Analyze", nullptr));
        menuTools->setTitle(QCoreApplication::translate("VoxCadClass", "Tools", nullptr));
        menuDrawing->setTitle(QCoreApplication::translate("VoxCadClass", "Drawing", nullptr));
        menuEdit->setTitle(QCoreApplication::translate("VoxCadClass", "Edit", nullptr));
        FileToolBar->setWindowTitle(QCoreApplication::translate("VoxCadClass", "File", nullptr));
        ViewtoolBar->setWindowTitle(QCoreApplication::translate("VoxCadClass", "View", nullptr));
        DrawingtoolBar->setWindowTitle(QCoreApplication::translate("VoxCadClass", "Draw", nullptr));
        DialogToolbar->setWindowTitle(QCoreApplication::translate("VoxCadClass", "Dialogs", nullptr));
        SectionToolBar->setWindowTitle(QCoreApplication::translate("VoxCadClass", "Section", nullptr));
    } // retranslateUi

};

namespace Ui {
    class VoxCadClass: public Ui_VoxCadClass {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VOXCAD_H
