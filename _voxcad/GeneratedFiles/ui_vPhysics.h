/********************************************************************************
** Form generated from reading UI file 'vPhysics.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VPHYSICS_H
#define UI_VPHYSICS_H

#include <QtCore/QVariant>
#include <QtGui/QIcon>
#include <QtWidgets/QApplication>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSlider>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_PhysicsDialog
{
public:
    QVBoxLayout *verticalLayout_6;
    QHBoxLayout *horizontalLayout_6;
    QPushButton *PauseButton;
    QPushButton *ResetButton;
    QPushButton *RecordButton;
    QHBoxLayout *horizontalLayout_16;
    QCheckBox *UseEquilibriumCheck;
    QHBoxLayout *horizontalLayout_15;
    QLabel *label_11;
    QComboBox *StopSelectCombo;
    QLineEdit *StopValueEdit;
    QLabel *StopValueLabel;
    QHBoxLayout *horizontalLayout_3;
    QSlider *dtSlider;
    QLabel *label;
    QLineEdit *dtEdit;
    QHBoxLayout *horizontalLayout_9;
    QSlider *GNDDampSlider;
    QLabel *label_9;
    QLineEdit *GNDDampEdit;
    QCheckBox *UseSelfColCheck;
    QHBoxLayout *horizontalLayout_7;
    QSlider *ColDampSlider;
    QLabel *label_7;
    QLineEdit *ColDampEdit;
    QTabWidget *PhysTabWidget;
    QWidget *View;
    QVBoxLayout *verticalLayout_11;
    QGroupBox *DisplayBox;
    QHBoxLayout *horizontalLayout_12;
    QRadioButton *DispDisableRadio;
    QRadioButton *DispVoxelsRadio;
    QRadioButton *DispConnRadio;
    QGroupBox *ViewOptionsGroup;
    QHBoxLayout *horizontalLayout_14;
    QVBoxLayout *verticalLayout_9;
    QRadioButton *ViewDiscreteRadio;
    QRadioButton *ViewDeformedRadio;
    QRadioButton *ViewSmoothRadio;
    QVBoxLayout *verticalLayout_7;
    QCheckBox *ForcesCheck;
    QCheckBox *LocalCoordCheck;
    QGroupBox *ColorGroup;
    QHBoxLayout *horizontalLayout_11;
    QVBoxLayout *verticalLayout_10;
    QRadioButton *TypeRadio;
    QRadioButton *KineticERadio;
    QRadioButton *DisplacementRadio;
    QRadioButton *GrowthRateRadio;
    QRadioButton *StimulusRadio;
    QRadioButton *StiffnessPlasticityRadio;
    QVBoxLayout *verticalLayout_8;
    QRadioButton *StrainERadio;
    QRadioButton *StressRadio;
    QRadioButton *StrainRadio;
    QRadioButton *PressureRadio;
    QCheckBox *CoMCheck;
    QCheckBox *PlotSourcesRays;
    QSpacerItem *verticalSpacer_2;
    QWidget *Environment;
    QVBoxLayout *verticalLayout_5;
    QCheckBox *UseTempCheck;
    QHBoxLayout *horizontalLayout_4;
    QSlider *TempSlider;
    QLabel *label_5;
    QLineEdit *TempEdit;
    QCheckBox *VaryTempCheck;
    QHBoxLayout *horizontalLayout_8;
    QSlider *TempPerSlider;
    QLabel *label_8;
    QLineEdit *TempPerEdit;
    QCheckBox *UseGravCheck;
    QHBoxLayout *horizontalLayout_5;
    QSlider *GravSlider;
    QLabel *label_6;
    QLineEdit *GravEdit;
    QCheckBox *UseFloorCheck;
    QSpacerItem *verticalSpacer;
    QWidget *Trace;
    QVBoxLayout *verticalLayout_3;
    QHBoxLayout *horizontalLayout_2;
    QVBoxLayout *verticalLayout_2;
    QComboBox *VariableCombo;
    QLabel *label_2;
    QVBoxLayout *verticalLayout;
    QComboBox *DirectionCombo;
    QLabel *label_3;
    QHBoxLayout *horizontalLayout_10;
    QSpacerItem *horizontalSpacer;
    QCheckBox *LogEachCheck;
    QPushButton *SaveDataButton;
    QWidget *Output;
    QVBoxLayout *verticalLayout_4;
    QTextEdit *OutText;
    QVBoxLayout *verticalLayout1;
    QLabel *label_40;
    QLineEdit *MotionFloorThrEdit;
    QLabel *label_41;
    QLineEdit *KpEdit;
    QLabel *label_42;
    QLineEdit *KiEdit;
    QLabel *label_43;
    QLineEdit *AntiWindupEdit;
    QWidget *Other;
    QVBoxLayout *verticalLayout_12;
    QHBoxLayout *horizontalLayout;
    QSlider *BondDampSlider;
    QLabel *label_4;
    QLineEdit *BondDampEdit;
    QCheckBox *UseMaxVelLimitCheck;
    QHBoxLayout *horizontalLayout_13;
    QSlider *MaxVelLimitSlider;
    QLabel *label_10;
    QCheckBox *UseVolumeEffectsCheck;
    QSpacerItem *verticalSpacer_3;

    void setupUi(QWidget *PhysicsDialog)
    {
        if (PhysicsDialog->objectName().isEmpty())
            PhysicsDialog->setObjectName(QString::fromUtf8("PhysicsDialog"));
        PhysicsDialog->resize(263, 708);
        verticalLayout_6 = new QVBoxLayout(PhysicsDialog);
        verticalLayout_6->setObjectName(QString::fromUtf8("verticalLayout_6"));
        horizontalLayout_6 = new QHBoxLayout();
        horizontalLayout_6->setObjectName(QString::fromUtf8("horizontalLayout_6"));
        PauseButton = new QPushButton(PhysicsDialog);
        PauseButton->setObjectName(QString::fromUtf8("PauseButton"));
        PauseButton->setMinimumSize(QSize(0, 24));

        horizontalLayout_6->addWidget(PauseButton);

        ResetButton = new QPushButton(PhysicsDialog);
        ResetButton->setObjectName(QString::fromUtf8("ResetButton"));
        ResetButton->setMinimumSize(QSize(0, 24));

        horizontalLayout_6->addWidget(ResetButton);

        RecordButton = new QPushButton(PhysicsDialog);
        RecordButton->setObjectName(QString::fromUtf8("RecordButton"));
        QSizePolicy sizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(RecordButton->sizePolicy().hasHeightForWidth());
        RecordButton->setSizePolicy(sizePolicy);
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/Icons/Icons/Record.png"), QSize(), QIcon::Normal, QIcon::Off);
        RecordButton->setIcon(icon);
        RecordButton->setCheckable(true);

        horizontalLayout_6->addWidget(RecordButton);


        verticalLayout_6->addLayout(horizontalLayout_6);

        horizontalLayout_16 = new QHBoxLayout();
        horizontalLayout_16->setObjectName(QString::fromUtf8("horizontalLayout_16"));
        UseEquilibriumCheck = new QCheckBox(PhysicsDialog);
        UseEquilibriumCheck->setObjectName(QString::fromUtf8("UseEquilibriumCheck"));

        horizontalLayout_16->addWidget(UseEquilibriumCheck);


        verticalLayout_6->addLayout(horizontalLayout_16);

        horizontalLayout_15 = new QHBoxLayout();
        horizontalLayout_15->setObjectName(QString::fromUtf8("horizontalLayout_15"));
        label_11 = new QLabel(PhysicsDialog);
        label_11->setObjectName(QString::fromUtf8("label_11"));
        QSizePolicy sizePolicy1(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(label_11->sizePolicy().hasHeightForWidth());
        label_11->setSizePolicy(sizePolicy1);
        label_11->setMinimumSize(QSize(0, 0));
        label_11->setMaximumSize(QSize(80, 16777215));
        label_11->setWordWrap(true);

        horizontalLayout_15->addWidget(label_11);

        StopSelectCombo = new QComboBox(PhysicsDialog);
        StopSelectCombo->setObjectName(QString::fromUtf8("StopSelectCombo"));

        horizontalLayout_15->addWidget(StopSelectCombo);

        StopValueEdit = new QLineEdit(PhysicsDialog);
        StopValueEdit->setObjectName(QString::fromUtf8("StopValueEdit"));
        StopValueEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(StopValueEdit->sizePolicy().hasHeightForWidth());
        StopValueEdit->setSizePolicy(sizePolicy);
        StopValueEdit->setMinimumSize(QSize(41, 0));
        StopValueEdit->setMaximumSize(QSize(41, 16777215));
        StopValueEdit->setAcceptDrops(false);

        horizontalLayout_15->addWidget(StopValueEdit);

        StopValueLabel = new QLabel(PhysicsDialog);
        StopValueLabel->setObjectName(QString::fromUtf8("StopValueLabel"));
        sizePolicy1.setHeightForWidth(StopValueLabel->sizePolicy().hasHeightForWidth());
        StopValueLabel->setSizePolicy(sizePolicy1);
        StopValueLabel->setMinimumSize(QSize(0, 0));
        StopValueLabel->setMaximumSize(QSize(80, 16777215));
        StopValueLabel->setWordWrap(true);

        horizontalLayout_15->addWidget(StopValueLabel);


        verticalLayout_6->addLayout(horizontalLayout_15);

        horizontalLayout_3 = new QHBoxLayout();
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        dtSlider = new QSlider(PhysicsDialog);
        dtSlider->setObjectName(QString::fromUtf8("dtSlider"));
        QSizePolicy sizePolicy2(QSizePolicy::Expanding, QSizePolicy::Fixed);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(dtSlider->sizePolicy().hasHeightForWidth());
        dtSlider->setSizePolicy(sizePolicy2);
        dtSlider->setMinimumSize(QSize(120, 0));
        dtSlider->setMaximum(100);
        dtSlider->setSingleStep(1);
        dtSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_3->addWidget(dtSlider);

        label = new QLabel(PhysicsDialog);
        label->setObjectName(QString::fromUtf8("label"));
        sizePolicy1.setHeightForWidth(label->sizePolicy().hasHeightForWidth());
        label->setSizePolicy(sizePolicy1);
        label->setMinimumSize(QSize(70, 0));
        label->setMaximumSize(QSize(80, 16777215));
        label->setWordWrap(true);

        horizontalLayout_3->addWidget(label);

        dtEdit = new QLineEdit(PhysicsDialog);
        dtEdit->setObjectName(QString::fromUtf8("dtEdit"));
        dtEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(dtEdit->sizePolicy().hasHeightForWidth());
        dtEdit->setSizePolicy(sizePolicy);
        dtEdit->setMinimumSize(QSize(41, 0));
        dtEdit->setMaximumSize(QSize(41, 16777215));
        dtEdit->setAcceptDrops(false);

        horizontalLayout_3->addWidget(dtEdit);


        verticalLayout_6->addLayout(horizontalLayout_3);

        horizontalLayout_9 = new QHBoxLayout();
        horizontalLayout_9->setObjectName(QString::fromUtf8("horizontalLayout_9"));
        GNDDampSlider = new QSlider(PhysicsDialog);
        GNDDampSlider->setObjectName(QString::fromUtf8("GNDDampSlider"));
        sizePolicy2.setHeightForWidth(GNDDampSlider->sizePolicy().hasHeightForWidth());
        GNDDampSlider->setSizePolicy(sizePolicy2);
        GNDDampSlider->setMinimumSize(QSize(120, 0));
        GNDDampSlider->setMaximum(100);
        GNDDampSlider->setSingleStep(1);
        GNDDampSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_9->addWidget(GNDDampSlider);

        label_9 = new QLabel(PhysicsDialog);
        label_9->setObjectName(QString::fromUtf8("label_9"));
        label_9->setMinimumSize(QSize(70, 0));
        label_9->setMaximumSize(QSize(80, 16777215));
        label_9->setWordWrap(true);
        label_9->setIndent(-2);

        horizontalLayout_9->addWidget(label_9);

        GNDDampEdit = new QLineEdit(PhysicsDialog);
        GNDDampEdit->setObjectName(QString::fromUtf8("GNDDampEdit"));
        GNDDampEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(GNDDampEdit->sizePolicy().hasHeightForWidth());
        GNDDampEdit->setSizePolicy(sizePolicy);
        GNDDampEdit->setMinimumSize(QSize(41, 0));
        GNDDampEdit->setMaximumSize(QSize(41, 16777215));

        horizontalLayout_9->addWidget(GNDDampEdit);


        verticalLayout_6->addLayout(horizontalLayout_9);

        UseSelfColCheck = new QCheckBox(PhysicsDialog);
        UseSelfColCheck->setObjectName(QString::fromUtf8("UseSelfColCheck"));

        verticalLayout_6->addWidget(UseSelfColCheck);

        horizontalLayout_7 = new QHBoxLayout();
        horizontalLayout_7->setObjectName(QString::fromUtf8("horizontalLayout_7"));
        ColDampSlider = new QSlider(PhysicsDialog);
        ColDampSlider->setObjectName(QString::fromUtf8("ColDampSlider"));
        sizePolicy2.setHeightForWidth(ColDampSlider->sizePolicy().hasHeightForWidth());
        ColDampSlider->setSizePolicy(sizePolicy2);
        ColDampSlider->setMinimumSize(QSize(120, 0));
        ColDampSlider->setMaximum(100);
        ColDampSlider->setSingleStep(1);
        ColDampSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_7->addWidget(ColDampSlider);

        label_7 = new QLabel(PhysicsDialog);
        label_7->setObjectName(QString::fromUtf8("label_7"));
        label_7->setMinimumSize(QSize(70, 0));
        label_7->setMaximumSize(QSize(70, 16777215));
        label_7->setWordWrap(true);
        label_7->setIndent(-2);

        horizontalLayout_7->addWidget(label_7);

        ColDampEdit = new QLineEdit(PhysicsDialog);
        ColDampEdit->setObjectName(QString::fromUtf8("ColDampEdit"));
        ColDampEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(ColDampEdit->sizePolicy().hasHeightForWidth());
        ColDampEdit->setSizePolicy(sizePolicy);
        ColDampEdit->setMinimumSize(QSize(41, 0));
        ColDampEdit->setMaximumSize(QSize(41, 16777215));

        horizontalLayout_7->addWidget(ColDampEdit);


        verticalLayout_6->addLayout(horizontalLayout_7);

        PhysTabWidget = new QTabWidget(PhysicsDialog);
        PhysTabWidget->setObjectName(QString::fromUtf8("PhysTabWidget"));
        PhysTabWidget->setTabPosition(QTabWidget::North);
        View = new QWidget();
        View->setObjectName(QString::fromUtf8("View"));
        verticalLayout_11 = new QVBoxLayout(View);
        verticalLayout_11->setSpacing(2);
        verticalLayout_11->setObjectName(QString::fromUtf8("verticalLayout_11"));
        verticalLayout_11->setContentsMargins(-1, 3, -1, 3);
        DisplayBox = new QGroupBox(View);
        DisplayBox->setObjectName(QString::fromUtf8("DisplayBox"));
        horizontalLayout_12 = new QHBoxLayout(DisplayBox);
        horizontalLayout_12->setSpacing(2);
        horizontalLayout_12->setObjectName(QString::fromUtf8("horizontalLayout_12"));
        horizontalLayout_12->setContentsMargins(-1, 3, -1, 3);
        DispDisableRadio = new QRadioButton(DisplayBox);
        DispDisableRadio->setObjectName(QString::fromUtf8("DispDisableRadio"));

        horizontalLayout_12->addWidget(DispDisableRadio);

        DispVoxelsRadio = new QRadioButton(DisplayBox);
        DispVoxelsRadio->setObjectName(QString::fromUtf8("DispVoxelsRadio"));

        horizontalLayout_12->addWidget(DispVoxelsRadio);

        DispConnRadio = new QRadioButton(DisplayBox);
        DispConnRadio->setObjectName(QString::fromUtf8("DispConnRadio"));

        horizontalLayout_12->addWidget(DispConnRadio);


        verticalLayout_11->addWidget(DisplayBox);

        ViewOptionsGroup = new QGroupBox(View);
        ViewOptionsGroup->setObjectName(QString::fromUtf8("ViewOptionsGroup"));
        horizontalLayout_14 = new QHBoxLayout(ViewOptionsGroup);
        horizontalLayout_14->setSpacing(2);
        horizontalLayout_14->setObjectName(QString::fromUtf8("horizontalLayout_14"));
        horizontalLayout_14->setContentsMargins(-1, 3, -1, 3);
        verticalLayout_9 = new QVBoxLayout();
        verticalLayout_9->setObjectName(QString::fromUtf8("verticalLayout_9"));
        ViewDiscreteRadio = new QRadioButton(ViewOptionsGroup);
        ViewDiscreteRadio->setObjectName(QString::fromUtf8("ViewDiscreteRadio"));

        verticalLayout_9->addWidget(ViewDiscreteRadio);

        ViewDeformedRadio = new QRadioButton(ViewOptionsGroup);
        ViewDeformedRadio->setObjectName(QString::fromUtf8("ViewDeformedRadio"));

        verticalLayout_9->addWidget(ViewDeformedRadio);

        ViewSmoothRadio = new QRadioButton(ViewOptionsGroup);
        ViewSmoothRadio->setObjectName(QString::fromUtf8("ViewSmoothRadio"));

        verticalLayout_9->addWidget(ViewSmoothRadio);


        horizontalLayout_14->addLayout(verticalLayout_9);

        verticalLayout_7 = new QVBoxLayout();
        verticalLayout_7->setObjectName(QString::fromUtf8("verticalLayout_7"));
        ForcesCheck = new QCheckBox(ViewOptionsGroup);
        ForcesCheck->setObjectName(QString::fromUtf8("ForcesCheck"));

        verticalLayout_7->addWidget(ForcesCheck);

        LocalCoordCheck = new QCheckBox(ViewOptionsGroup);
        LocalCoordCheck->setObjectName(QString::fromUtf8("LocalCoordCheck"));

        verticalLayout_7->addWidget(LocalCoordCheck);


        horizontalLayout_14->addLayout(verticalLayout_7);


        verticalLayout_11->addWidget(ViewOptionsGroup);

        ColorGroup = new QGroupBox(View);
        ColorGroup->setObjectName(QString::fromUtf8("ColorGroup"));
        horizontalLayout_11 = new QHBoxLayout(ColorGroup);
        horizontalLayout_11->setSpacing(2);
        horizontalLayout_11->setObjectName(QString::fromUtf8("horizontalLayout_11"));
        horizontalLayout_11->setContentsMargins(-1, 4, -1, 3);
        verticalLayout_10 = new QVBoxLayout();
        verticalLayout_10->setObjectName(QString::fromUtf8("verticalLayout_10"));
        TypeRadio = new QRadioButton(ColorGroup);
        TypeRadio->setObjectName(QString::fromUtf8("TypeRadio"));

        verticalLayout_10->addWidget(TypeRadio);

        KineticERadio = new QRadioButton(ColorGroup);
        KineticERadio->setObjectName(QString::fromUtf8("KineticERadio"));

        verticalLayout_10->addWidget(KineticERadio);

        DisplacementRadio = new QRadioButton(ColorGroup);
        DisplacementRadio->setObjectName(QString::fromUtf8("DisplacementRadio"));

        verticalLayout_10->addWidget(DisplacementRadio);

        GrowthRateRadio = new QRadioButton(ColorGroup);
        GrowthRateRadio->setObjectName(QString::fromUtf8("GrowthRateRadio"));

        verticalLayout_10->addWidget(GrowthRateRadio);

        StimulusRadio = new QRadioButton(ColorGroup);
        StimulusRadio->setObjectName(QString::fromUtf8("StimulusRadio"));

        verticalLayout_10->addWidget(StimulusRadio);

        StiffnessPlasticityRadio = new QRadioButton(ColorGroup);
        StiffnessPlasticityRadio->setObjectName(QString::fromUtf8("StiffnessPlasticityRadio"));

        verticalLayout_10->addWidget(StiffnessPlasticityRadio);


        horizontalLayout_11->addLayout(verticalLayout_10);

        verticalLayout_8 = new QVBoxLayout();
        verticalLayout_8->setSpacing(1);
        verticalLayout_8->setObjectName(QString::fromUtf8("verticalLayout_8"));
        StrainERadio = new QRadioButton(ColorGroup);
        StrainERadio->setObjectName(QString::fromUtf8("StrainERadio"));

        verticalLayout_8->addWidget(StrainERadio);

        StressRadio = new QRadioButton(ColorGroup);
        StressRadio->setObjectName(QString::fromUtf8("StressRadio"));

        verticalLayout_8->addWidget(StressRadio);

        StrainRadio = new QRadioButton(ColorGroup);
        StrainRadio->setObjectName(QString::fromUtf8("StrainRadio"));

        verticalLayout_8->addWidget(StrainRadio);

        PressureRadio = new QRadioButton(ColorGroup);
        PressureRadio->setObjectName(QString::fromUtf8("PressureRadio"));

        verticalLayout_8->addWidget(PressureRadio);


        horizontalLayout_11->addLayout(verticalLayout_8);


        verticalLayout_11->addWidget(ColorGroup);

        CoMCheck = new QCheckBox(View);
        CoMCheck->setObjectName(QString::fromUtf8("CoMCheck"));

        verticalLayout_11->addWidget(CoMCheck);

        PlotSourcesRays = new QCheckBox(View);
        PlotSourcesRays->setObjectName(QString::fromUtf8("PlotSourcesRays"));

        verticalLayout_11->addWidget(PlotSourcesRays);

        verticalSpacer_2 = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_11->addItem(verticalSpacer_2);

        PhysTabWidget->addTab(View, QString());
        Environment = new QWidget();
        Environment->setObjectName(QString::fromUtf8("Environment"));
        verticalLayout_5 = new QVBoxLayout(Environment);
        verticalLayout_5->setSpacing(2);
        verticalLayout_5->setObjectName(QString::fromUtf8("verticalLayout_5"));
        verticalLayout_5->setContentsMargins(-1, 3, -1, 3);
        UseTempCheck = new QCheckBox(Environment);
        UseTempCheck->setObjectName(QString::fromUtf8("UseTempCheck"));

        verticalLayout_5->addWidget(UseTempCheck);

        horizontalLayout_4 = new QHBoxLayout();
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        TempSlider = new QSlider(Environment);
        TempSlider->setObjectName(QString::fromUtf8("TempSlider"));
        TempSlider->setMaximum(100);
        TempSlider->setSingleStep(1);
        TempSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_4->addWidget(TempSlider);

        label_5 = new QLabel(Environment);
        label_5->setObjectName(QString::fromUtf8("label_5"));

        horizontalLayout_4->addWidget(label_5);

        TempEdit = new QLineEdit(Environment);
        TempEdit->setObjectName(QString::fromUtf8("TempEdit"));
        TempEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(TempEdit->sizePolicy().hasHeightForWidth());
        TempEdit->setSizePolicy(sizePolicy);
        TempEdit->setMinimumSize(QSize(41, 0));
        TempEdit->setMaximumSize(QSize(41, 16777215));

        horizontalLayout_4->addWidget(TempEdit);


        verticalLayout_5->addLayout(horizontalLayout_4);

        VaryTempCheck = new QCheckBox(Environment);
        VaryTempCheck->setObjectName(QString::fromUtf8("VaryTempCheck"));

        verticalLayout_5->addWidget(VaryTempCheck);

        horizontalLayout_8 = new QHBoxLayout();
        horizontalLayout_8->setObjectName(QString::fromUtf8("horizontalLayout_8"));
        TempPerSlider = new QSlider(Environment);
        TempPerSlider->setObjectName(QString::fromUtf8("TempPerSlider"));
        TempPerSlider->setMaximum(100);
        TempPerSlider->setSingleStep(1);
        TempPerSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_8->addWidget(TempPerSlider);

        label_8 = new QLabel(Environment);
        label_8->setObjectName(QString::fromUtf8("label_8"));

        horizontalLayout_8->addWidget(label_8);

        TempPerEdit = new QLineEdit(Environment);
        TempPerEdit->setObjectName(QString::fromUtf8("TempPerEdit"));
        TempPerEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(TempPerEdit->sizePolicy().hasHeightForWidth());
        TempPerEdit->setSizePolicy(sizePolicy);
        TempPerEdit->setMinimumSize(QSize(41, 0));
        TempPerEdit->setMaximumSize(QSize(41, 16777215));

        horizontalLayout_8->addWidget(TempPerEdit);


        verticalLayout_5->addLayout(horizontalLayout_8);

        UseGravCheck = new QCheckBox(Environment);
        UseGravCheck->setObjectName(QString::fromUtf8("UseGravCheck"));

        verticalLayout_5->addWidget(UseGravCheck);

        horizontalLayout_5 = new QHBoxLayout();
        horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
        GravSlider = new QSlider(Environment);
        GravSlider->setObjectName(QString::fromUtf8("GravSlider"));
        GravSlider->setMaximum(100);
        GravSlider->setSingleStep(1);
        GravSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_5->addWidget(GravSlider);

        label_6 = new QLabel(Environment);
        label_6->setObjectName(QString::fromUtf8("label_6"));

        horizontalLayout_5->addWidget(label_6);

        GravEdit = new QLineEdit(Environment);
        GravEdit->setObjectName(QString::fromUtf8("GravEdit"));
        GravEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(GravEdit->sizePolicy().hasHeightForWidth());
        GravEdit->setSizePolicy(sizePolicy);
        GravEdit->setMinimumSize(QSize(41, 0));
        GravEdit->setMaximumSize(QSize(41, 16777215));

        horizontalLayout_5->addWidget(GravEdit);


        verticalLayout_5->addLayout(horizontalLayout_5);

        UseFloorCheck = new QCheckBox(Environment);
        UseFloorCheck->setObjectName(QString::fromUtf8("UseFloorCheck"));

        verticalLayout_5->addWidget(UseFloorCheck);

        verticalSpacer = new QSpacerItem(20, 191, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_5->addItem(verticalSpacer);

        PhysTabWidget->addTab(Environment, QString());
        Trace = new QWidget();
        Trace->setObjectName(QString::fromUtf8("Trace"));
        verticalLayout_3 = new QVBoxLayout(Trace);
        verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
        horizontalLayout_2 = new QHBoxLayout();
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        verticalLayout_2 = new QVBoxLayout();
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        VariableCombo = new QComboBox(Trace);
        VariableCombo->setObjectName(QString::fromUtf8("VariableCombo"));

        verticalLayout_2->addWidget(VariableCombo);

        label_2 = new QLabel(Trace);
        label_2->setObjectName(QString::fromUtf8("label_2"));

        verticalLayout_2->addWidget(label_2);


        horizontalLayout_2->addLayout(verticalLayout_2);

        verticalLayout = new QVBoxLayout();
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        DirectionCombo = new QComboBox(Trace);
        DirectionCombo->setObjectName(QString::fromUtf8("DirectionCombo"));

        verticalLayout->addWidget(DirectionCombo);

        label_3 = new QLabel(Trace);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        verticalLayout->addWidget(label_3);


        horizontalLayout_2->addLayout(verticalLayout);


        verticalLayout_3->addLayout(horizontalLayout_2);

        horizontalLayout_10 = new QHBoxLayout();
        horizontalLayout_10->setObjectName(QString::fromUtf8("horizontalLayout_10"));
        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_10->addItem(horizontalSpacer);

        LogEachCheck = new QCheckBox(Trace);
        LogEachCheck->setObjectName(QString::fromUtf8("LogEachCheck"));

        horizontalLayout_10->addWidget(LogEachCheck);

        SaveDataButton = new QPushButton(Trace);
        SaveDataButton->setObjectName(QString::fromUtf8("SaveDataButton"));

        horizontalLayout_10->addWidget(SaveDataButton);


        verticalLayout_3->addLayout(horizontalLayout_10);

        PhysTabWidget->addTab(Trace, QString());
        Output = new QWidget();
        Output->setObjectName(QString::fromUtf8("Output"));
        verticalLayout_4 = new QVBoxLayout(Output);
        verticalLayout_4->setObjectName(QString::fromUtf8("verticalLayout_4"));
        OutText = new QTextEdit(Output);
        OutText->setObjectName(QString::fromUtf8("OutText"));

        verticalLayout_4->addWidget(OutText);

        verticalLayout1 = new QVBoxLayout();
        verticalLayout1->setObjectName(QString::fromUtf8("verticalLayout1"));
        label_40 = new QLabel(Output);
        label_40->setObjectName(QString::fromUtf8("label_40"));
        label_40->setMinimumSize(QSize(200, 0));
        label_40->setMaximumSize(QSize(200, 16777215));
        label_40->setWordWrap(true);
        label_40->setIndent(-2);

        verticalLayout1->addWidget(label_40);

        MotionFloorThrEdit = new QLineEdit(Output);
        MotionFloorThrEdit->setObjectName(QString::fromUtf8("MotionFloorThrEdit"));
        MotionFloorThrEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(MotionFloorThrEdit->sizePolicy().hasHeightForWidth());
        MotionFloorThrEdit->setSizePolicy(sizePolicy);
        MotionFloorThrEdit->setMinimumSize(QSize(200, 0));
        MotionFloorThrEdit->setMaximumSize(QSize(200, 16777215));

        verticalLayout1->addWidget(MotionFloorThrEdit);

        label_41 = new QLabel(Output);
        label_41->setObjectName(QString::fromUtf8("label_41"));
        label_41->setMinimumSize(QSize(200, 0));
        label_41->setMaximumSize(QSize(200, 16777215));
        label_41->setWordWrap(true);
        label_41->setIndent(-2);

        verticalLayout1->addWidget(label_41);

        KpEdit = new QLineEdit(Output);
        KpEdit->setObjectName(QString::fromUtf8("KpEdit"));
        KpEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(KpEdit->sizePolicy().hasHeightForWidth());
        KpEdit->setSizePolicy(sizePolicy);
        KpEdit->setMinimumSize(QSize(200, 0));
        KpEdit->setMaximumSize(QSize(200, 16777215));

        verticalLayout1->addWidget(KpEdit);

        label_42 = new QLabel(Output);
        label_42->setObjectName(QString::fromUtf8("label_42"));
        label_42->setMinimumSize(QSize(200, 0));
        label_42->setMaximumSize(QSize(200, 16777215));
        label_42->setWordWrap(true);
        label_42->setIndent(-2);

        verticalLayout1->addWidget(label_42);

        KiEdit = new QLineEdit(Output);
        KiEdit->setObjectName(QString::fromUtf8("KiEdit"));
        KiEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(KiEdit->sizePolicy().hasHeightForWidth());
        KiEdit->setSizePolicy(sizePolicy);
        KiEdit->setMinimumSize(QSize(200, 0));
        KiEdit->setMaximumSize(QSize(200, 16777215));

        verticalLayout1->addWidget(KiEdit);

        label_43 = new QLabel(Output);
        label_43->setObjectName(QString::fromUtf8("label_43"));
        label_43->setMinimumSize(QSize(200, 0));
        label_43->setMaximumSize(QSize(200, 16777215));
        label_43->setWordWrap(true);
        label_43->setIndent(-2);

        verticalLayout1->addWidget(label_43);

        AntiWindupEdit = new QLineEdit(Output);
        AntiWindupEdit->setObjectName(QString::fromUtf8("AntiWindupEdit"));
        AntiWindupEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(AntiWindupEdit->sizePolicy().hasHeightForWidth());
        AntiWindupEdit->setSizePolicy(sizePolicy);
        AntiWindupEdit->setMinimumSize(QSize(200, 0));
        AntiWindupEdit->setMaximumSize(QSize(200, 16777215));

        verticalLayout1->addWidget(AntiWindupEdit);


        verticalLayout_4->addLayout(verticalLayout1);

        PhysTabWidget->addTab(Output, QString());
        Other = new QWidget();
        Other->setObjectName(QString::fromUtf8("Other"));
        verticalLayout_12 = new QVBoxLayout(Other);
        verticalLayout_12->setSpacing(1);
        verticalLayout_12->setObjectName(QString::fromUtf8("verticalLayout_12"));
        verticalLayout_12->setContentsMargins(6, 3, 6, 3);
        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        BondDampSlider = new QSlider(Other);
        BondDampSlider->setObjectName(QString::fromUtf8("BondDampSlider"));
        sizePolicy2.setHeightForWidth(BondDampSlider->sizePolicy().hasHeightForWidth());
        BondDampSlider->setSizePolicy(sizePolicy2);
        BondDampSlider->setMinimumSize(QSize(80, 0));
        BondDampSlider->setMaximum(100);
        BondDampSlider->setSingleStep(1);
        BondDampSlider->setOrientation(Qt::Horizontal);

        horizontalLayout->addWidget(BondDampSlider);

        label_4 = new QLabel(Other);
        label_4->setObjectName(QString::fromUtf8("label_4"));
        label_4->setMinimumSize(QSize(50, 0));
        label_4->setMaximumSize(QSize(50, 16777215));
        label_4->setWordWrap(true);
        label_4->setIndent(-2);

        horizontalLayout->addWidget(label_4);

        BondDampEdit = new QLineEdit(Other);
        BondDampEdit->setObjectName(QString::fromUtf8("BondDampEdit"));
        BondDampEdit->setEnabled(true);
        sizePolicy.setHeightForWidth(BondDampEdit->sizePolicy().hasHeightForWidth());
        BondDampEdit->setSizePolicy(sizePolicy);
        BondDampEdit->setMinimumSize(QSize(41, 0));
        BondDampEdit->setMaximumSize(QSize(41, 16777215));

        horizontalLayout->addWidget(BondDampEdit);


        verticalLayout_12->addLayout(horizontalLayout);

        UseMaxVelLimitCheck = new QCheckBox(Other);
        UseMaxVelLimitCheck->setObjectName(QString::fromUtf8("UseMaxVelLimitCheck"));

        verticalLayout_12->addWidget(UseMaxVelLimitCheck);

        horizontalLayout_13 = new QHBoxLayout();
        horizontalLayout_13->setObjectName(QString::fromUtf8("horizontalLayout_13"));
        MaxVelLimitSlider = new QSlider(Other);
        MaxVelLimitSlider->setObjectName(QString::fromUtf8("MaxVelLimitSlider"));
        sizePolicy2.setHeightForWidth(MaxVelLimitSlider->sizePolicy().hasHeightForWidth());
        MaxVelLimitSlider->setSizePolicy(sizePolicy2);
        MaxVelLimitSlider->setMinimumSize(QSize(120, 0));
        MaxVelLimitSlider->setMaximum(100);
        MaxVelLimitSlider->setSingleStep(1);
        MaxVelLimitSlider->setOrientation(Qt::Horizontal);

        horizontalLayout_13->addWidget(MaxVelLimitSlider);

        label_10 = new QLabel(Other);
        label_10->setObjectName(QString::fromUtf8("label_10"));
        label_10->setMinimumSize(QSize(70, 0));
        label_10->setMaximumSize(QSize(70, 16777215));
        label_10->setWordWrap(true);
        label_10->setIndent(-2);

        horizontalLayout_13->addWidget(label_10);


        verticalLayout_12->addLayout(horizontalLayout_13);

        UseVolumeEffectsCheck = new QCheckBox(Other);
        UseVolumeEffectsCheck->setObjectName(QString::fromUtf8("UseVolumeEffectsCheck"));

        verticalLayout_12->addWidget(UseVolumeEffectsCheck);

        verticalSpacer_3 = new QSpacerItem(20, 363, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_12->addItem(verticalSpacer_3);

        PhysTabWidget->addTab(Other, QString());

        verticalLayout_6->addWidget(PhysTabWidget);


        retranslateUi(PhysicsDialog);

        PhysTabWidget->setCurrentIndex(3);


        QMetaObject::connectSlotsByName(PhysicsDialog);
    } // setupUi

    void retranslateUi(QWidget *PhysicsDialog)
    {
        PhysicsDialog->setWindowTitle(QCoreApplication::translate("PhysicsDialog", "Form", nullptr));
        PauseButton->setText(QCoreApplication::translate("PhysicsDialog", "Pause", nullptr));
        ResetButton->setText(QCoreApplication::translate("PhysicsDialog", "Reset", nullptr));
        RecordButton->setText(QString());
#if QT_CONFIG(tooltip)
        UseEquilibriumCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Accelerates the simulation to find the equilibrium position quickly", nullptr));
#endif // QT_CONFIG(tooltip)
        UseEquilibriumCheck->setText(QCoreApplication::translate("PhysicsDialog", "Find Equilibrium", nullptr));
#if QT_CONFIG(tooltip)
        label_11->setToolTip(QCoreApplication::translate("PhysicsDialog", "Percent of optimal timestep to run at. [0-1.0+]\n"
"Greater values speed up the simulation, but >1.0\n"
"can be unstable.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_11->setText(QCoreApplication::translate("PhysicsDialog", "Stop condition", nullptr));
#if QT_CONFIG(tooltip)
        StopSelectCombo->setToolTip(QCoreApplication::translate("PhysicsDialog", "Sets a condition for auto-stopping the simulation", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        StopValueEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "The value of selected auto-stopping condition to trigger a stop.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        StopValueLabel->setToolTip(QCoreApplication::translate("PhysicsDialog", "Percent of optimal timestep to run at. [0-1.0+]\n"
"Greater values speed up the simulation, but >1.0\n"
"can be unstable.", nullptr));
#endif // QT_CONFIG(tooltip)
        StopValueLabel->setText(QCoreApplication::translate("PhysicsDialog", "Sec", nullptr));
#if QT_CONFIG(tooltip)
        dtSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Percent of optimal timestep to run at. [0-1.0+]\n"
"Greater values speed up the simulation, but >1.0\n"
"can be unstable.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label->setToolTip(QCoreApplication::translate("PhysicsDialog", "Percent of optimal timestep to run at. [0-1.0+]\n"
"Greater values speed up the simulation, but >1.0\n"
"can be unstable.", nullptr));
#endif // QT_CONFIG(tooltip)
        label->setText(QCoreApplication::translate("PhysicsDialog", "timestep (%  optimal dt)", nullptr));
#if QT_CONFIG(tooltip)
        dtEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Percent of optimal timestep to run at. [0-1.0+]\n"
"Greater values speed up the simulation, but >1.0\n"
"can be unstable.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        GNDDampSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Damping ratio relative to ground [0-0.1+].\n"
"0 represents a vacuum, larger values\n"
"represent a more viscous fluid environment.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_9->setToolTip(QCoreApplication::translate("PhysicsDialog", "Damping ratio relative to ground [0-0.1+].\n"
"0 represents a vacuum, larger values\n"
"represent a more viscous fluid environment.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_9->setText(QCoreApplication::translate("PhysicsDialog", "Ground damp ratio (z)", nullptr));
#if QT_CONFIG(tooltip)
        GNDDampEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Damping ratio relative to ground [0-0.1+].\n"
"0 represents a vacuum, larger values\n"
"represent a more viscous fluid environment.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        UseSelfColCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Prevents self penetration when enabled.", nullptr));
#endif // QT_CONFIG(tooltip)
        UseSelfColCheck->setText(QCoreApplication::translate("PhysicsDialog", "Enable Self Collision", nullptr));
#if QT_CONFIG(tooltip)
        ColDampSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Damping ratio of collisions [0-2+].\n"
"Low values make elastic (bouncy) collisions, higher values\n"
"make inelastic (dead) collisions. 1.0 is critically damped.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_7->setToolTip(QCoreApplication::translate("PhysicsDialog", "Damping ratio of collisions [0-2+].\n"
"Low values make elastic (bouncy) collisions, higher values\n"
"make inelastic (dead) collisions. 1.0 is critically damped.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_7->setText(QCoreApplication::translate("PhysicsDialog", "Collision damp ratio (z)", nullptr));
#if QT_CONFIG(tooltip)
        ColDampEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Damping ratio of collisions [0-2+].\n"
"Low values make elastic (bouncy) collisions, higher values\n"
"make inelastic (dead) collisions. 1.0 is critically damped.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        PhysTabWidget->setToolTip(QCoreApplication::translate("PhysicsDialog", "Options", nullptr));
#endif // QT_CONFIG(tooltip)
        DisplayBox->setTitle(QCoreApplication::translate("PhysicsDialog", "Display", nullptr));
        DispDisableRadio->setText(QCoreApplication::translate("PhysicsDialog", "Disable", nullptr));
        DispVoxelsRadio->setText(QCoreApplication::translate("PhysicsDialog", "Voxels", nullptr));
        DispConnRadio->setText(QCoreApplication::translate("PhysicsDialog", "Connections", nullptr));
        ViewOptionsGroup->setTitle(QCoreApplication::translate("PhysicsDialog", "View Options", nullptr));
        ViewDiscreteRadio->setText(QCoreApplication::translate("PhysicsDialog", "Discrete", nullptr));
        ViewDeformedRadio->setText(QCoreApplication::translate("PhysicsDialog", "Deformed", nullptr));
        ViewSmoothRadio->setText(QCoreApplication::translate("PhysicsDialog", "Smooth", nullptr));
#if QT_CONFIG(tooltip)
        ForcesCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Internal forces (currently disabled)", nullptr));
#endif // QT_CONFIG(tooltip)
        ForcesCheck->setText(QCoreApplication::translate("PhysicsDialog", "Forces", nullptr));
#if QT_CONFIG(tooltip)
        LocalCoordCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Origin and axes of each voxel.", nullptr));
#endif // QT_CONFIG(tooltip)
        LocalCoordCheck->setText(QCoreApplication::translate("PhysicsDialog", "Local Coords", nullptr));
        ColorGroup->setTitle(QCoreApplication::translate("PhysicsDialog", "Color", nullptr));
#if QT_CONFIG(tooltip)
        TypeRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Voxel type/evolved scale/stiffness", nullptr));
#endif // QT_CONFIG(tooltip)
        TypeRadio->setText(QCoreApplication::translate("PhysicsDialog", "Type/Evolved Stiffness", nullptr));
#if QT_CONFIG(tooltip)
        KineticERadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Internal material strain", nullptr));
#endif // QT_CONFIG(tooltip)
        KineticERadio->setText(QCoreApplication::translate("PhysicsDialog", "Kinetic Energy", nullptr));
#if QT_CONFIG(tooltip)
        DisplacementRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Distance from starting point of each voxel", nullptr));
#endif // QT_CONFIG(tooltip)
        DisplacementRadio->setText(QCoreApplication::translate("PhysicsDialog", "Displacement", nullptr));
#if QT_CONFIG(tooltip)
        GrowthRateRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Blue: shrinking tissue Red: expanding tissue", nullptr));
#endif // QT_CONFIG(tooltip)
        GrowthRateRadio->setText(QCoreApplication::translate("PhysicsDialog", "Growth rate", nullptr));
#if QT_CONFIG(tooltip)
        StimulusRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Current stimulus from environmental sources", nullptr));
#endif // QT_CONFIG(tooltip)
        StimulusRadio->setText(QCoreApplication::translate("PhysicsDialog", "Stimulus", nullptr));
#if QT_CONFIG(tooltip)
        StiffnessPlasticityRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Blue: stiffening Red: softening", nullptr));
#endif // QT_CONFIG(tooltip)
        StiffnessPlasticityRadio->setText(QCoreApplication::translate("PhysicsDialog", "Stiffness plasticity rate", nullptr));
#if QT_CONFIG(tooltip)
        StrainERadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Internal material strain", nullptr));
#endif // QT_CONFIG(tooltip)
        StrainERadio->setText(QCoreApplication::translate("PhysicsDialog", "Strain Energy", nullptr));
#if QT_CONFIG(tooltip)
        StressRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Internal material stress", nullptr));
#endif // QT_CONFIG(tooltip)
        StressRadio->setText(QCoreApplication::translate("PhysicsDialog", "Engineering\n"
"Stress", nullptr));
#if QT_CONFIG(tooltip)
        StrainRadio->setToolTip(QCoreApplication::translate("PhysicsDialog", "Internal material strain", nullptr));
#endif // QT_CONFIG(tooltip)
        StrainRadio->setText(QCoreApplication::translate("PhysicsDialog", "Engineering\n"
"Strain", nullptr));
        PressureRadio->setText(QCoreApplication::translate("PhysicsDialog", "Pressure", nullptr));
        CoMCheck->setText(QCoreApplication::translate("PhysicsDialog", "Lock view to center of mass", nullptr));
        PlotSourcesRays->setText(QCoreApplication::translate("PhysicsDialog", "Plot environmental sources rays", nullptr));
        PhysTabWidget->setTabText(PhysTabWidget->indexOf(View), QCoreApplication::translate("PhysicsDialog", "View", nullptr));
#if QT_CONFIG(tooltip)
        UseTempCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Enables temperature changes.\n"
"Affects the size of each voxel according to its CTE.", nullptr));
#endif // QT_CONFIG(tooltip)
        UseTempCheck->setText(QCoreApplication::translate("PhysicsDialog", "Enable Temperature", nullptr));
#if QT_CONFIG(tooltip)
        TempSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Current environment temperature.\n"
"Base (no expansion) is 25\302\260.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_5->setText(QCoreApplication::translate("PhysicsDialog", "Temp (\302\260C)", nullptr));
#if QT_CONFIG(tooltip)
        VaryTempCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Periodically varies the environment temperature when enabled.", nullptr));
#endif // QT_CONFIG(tooltip)
        VaryTempCheck->setText(QCoreApplication::translate("PhysicsDialog", "Vary Temperature", nullptr));
#if QT_CONFIG(tooltip)
        TempPerSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Period of temperature variation in environment.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_8->setText(QCoreApplication::translate("PhysicsDialog", "Period (sec)", nullptr));
#if QT_CONFIG(tooltip)
        UseGravCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Enables gravitational acceleration.", nullptr));
#endif // QT_CONFIG(tooltip)
        UseGravCheck->setText(QCoreApplication::translate("PhysicsDialog", "Enable Gravity", nullptr));
#if QT_CONFIG(tooltip)
        GravSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Gravitational acceleration (9.81 for earth).", nullptr));
#endif // QT_CONFIG(tooltip)
        label_6->setText(QCoreApplication::translate("PhysicsDialog", "Grav (m/s\302\262)", nullptr));
#if QT_CONFIG(tooltip)
        UseFloorCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Enables a flat floor.", nullptr));
#endif // QT_CONFIG(tooltip)
        UseFloorCheck->setText(QCoreApplication::translate("PhysicsDialog", "Enable Floor", nullptr));
        PhysTabWidget->setTabText(PhysTabWidget->indexOf(Environment), QCoreApplication::translate("PhysicsDialog", "Environment", nullptr));
        label_2->setText(QCoreApplication::translate("PhysicsDialog", "Plot Variable", nullptr));
        label_3->setText(QCoreApplication::translate("PhysicsDialog", "Plot Direction", nullptr));
        LogEachCheck->setText(QCoreApplication::translate("PhysicsDialog", "Log Every", nullptr));
        SaveDataButton->setText(QCoreApplication::translate("PhysicsDialog", "Save Data", nullptr));
        PhysTabWidget->setTabText(PhysTabWidget->indexOf(Trace), QCoreApplication::translate("PhysicsDialog", "Trace", nullptr));
#if QT_CONFIG(tooltip)
        label_40->setToolTip(QCoreApplication::translate("PhysicsDialog", "MotionFloor", nullptr));
#endif // QT_CONFIG(tooltip)
        label_40->setText(QCoreApplication::translate("PhysicsDialog", "MotionFloor", nullptr));
#if QT_CONFIG(tooltip)
        MotionFloorThrEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Motion floor", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_41->setToolTip(QCoreApplication::translate("PhysicsDialog", "Kp", nullptr));
#endif // QT_CONFIG(tooltip)
        label_41->setText(QCoreApplication::translate("PhysicsDialog", "Kp", nullptr));
#if QT_CONFIG(tooltip)
        KpEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Kp", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_42->setToolTip(QCoreApplication::translate("PhysicsDialog", "Ki", nullptr));
#endif // QT_CONFIG(tooltip)
        label_42->setText(QCoreApplication::translate("PhysicsDialog", "Ki", nullptr));
#if QT_CONFIG(tooltip)
        KiEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Ki", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_43->setToolTip(QCoreApplication::translate("PhysicsDialog", "Anti WindUp", nullptr));
#endif // QT_CONFIG(tooltip)
        label_43->setText(QCoreApplication::translate("PhysicsDialog", "Anti WindUp", nullptr));
#if QT_CONFIG(tooltip)
        AntiWindupEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Anti Wind Up", nullptr));
#endif // QT_CONFIG(tooltip)
        PhysTabWidget->setTabText(PhysTabWidget->indexOf(Output), QCoreApplication::translate("PhysicsDialog", "Output", nullptr));
#if QT_CONFIG(tooltip)
        BondDampSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Bulk material damping. [0-1.0]\n"
"Small values are more jiggly. 0.0 represents no damping\n"
"and is unstable, 1.0 is critical damping.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_4->setToolTip(QCoreApplication::translate("PhysicsDialog", "Bulk material damping. [0-1.0]\n"
"Small values are more jiggly. 0.0 represents no damping\n"
"and is unstable, 1.0 is critical damping.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_4->setText(QCoreApplication::translate("PhysicsDialog", "Bulk damp ratio (z)", nullptr));
#if QT_CONFIG(tooltip)
        BondDampEdit->setToolTip(QCoreApplication::translate("PhysicsDialog", "Bulk material damping. [0-1.0]\n"
"Small values are more jiggly. 0.0 represents no damping\n"
"and is unstable, 1.0 is critical damping.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        UseMaxVelLimitCheck->setToolTip(QCoreApplication::translate("PhysicsDialog", "Enforces a maximum velocity when enabled (rarely used).\n"
"Useful for highly unstable scenarios.", nullptr));
#endif // QT_CONFIG(tooltip)
        UseMaxVelLimitCheck->setText(QCoreApplication::translate("PhysicsDialog", "Enable Velocity Limit", nullptr));
#if QT_CONFIG(tooltip)
        MaxVelLimitSlider->setToolTip(QCoreApplication::translate("PhysicsDialog", "Maximum voxel velocity.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_10->setText(QCoreApplication::translate("PhysicsDialog", "Maximum Voxel Velocity", nullptr));
        UseVolumeEffectsCheck->setText(QCoreApplication::translate("PhysicsDialog", "Enable Volume Effects", nullptr));
        PhysTabWidget->setTabText(PhysTabWidget->indexOf(Other), QCoreApplication::translate("PhysicsDialog", "Other", nullptr));
    } // retranslateUi

};

namespace Ui {
    class PhysicsDialog: public Ui_PhysicsDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VPHYSICS_H
