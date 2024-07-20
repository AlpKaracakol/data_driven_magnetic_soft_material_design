/********************************************************************************
** Form generated from reading UI file 'vVideoGen.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VVIDEOGEN_H
#define UI_VVIDEOGEN_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_VideoDialog
{
public:
    QVBoxLayout *verticalLayout_7;
    QGroupBox *groupBox;
    QHBoxLayout *horizontalLayout_2;
    QLineEdit *OutputFolderEdit;
    QPushButton *SelectFolderButton;
    QGroupBox *groupBox_2;
    QVBoxLayout *verticalLayout;
    QHBoxLayout *horizontalLayout;
    QLineEdit *WidthPixEdit;
    QLabel *label;
    QLineEdit *HeightPixEdit;
    QLabel *label_2;
    QGridLayout *gridLayout;
    QRadioButton *r320x240Radio;
    QRadioButton *r800x600Radio;
    QRadioButton *r1280x720Radio;
    QRadioButton *r640x480Radio;
    QRadioButton *r1024x768Radio;
    QRadioButton *r1920x1080Radio;
    QGroupBox *groupBox_5;
    QVBoxLayout *verticalLayout_2;
    QHBoxLayout *horizontalLayout_3;
    QRadioButton *vsDisplayTimeRadio;
    QRadioButton *vsSimTimeRadio;
    QRadioButton *vsEveryFrameRadio;
    QHBoxLayout *horizontalLayout_4;
    QLineEdit *OutputFpsEdit;
    QLabel *label_3;
    QLineEdit *OutputSpeedFactorEdit;
    QLabel *label_4;
    QGroupBox *groupBox_3;
    QVBoxLayout *verticalLayout_6;
    QCheckBox *AutoStopEnabledCheck;
    QHBoxLayout *horizontalLayout_5;
    QVBoxLayout *verticalLayout_5;
    QRadioButton *TimeStepsRadio;
    QRadioButton *SimTimeRadio;
    QRadioButton *TempCycleRadio;
    QVBoxLayout *verticalLayout_4;
    QLineEdit *TimeStepsEdit;
    QLineEdit *SimTimeEdit;
    QLineEdit *TempCycleEdit;
    QVBoxLayout *verticalLayout_3;
    QLabel *label_5;
    QLabel *label_6;
    QLabel *label_7;
    QHBoxLayout *horizontalLayout_6;
    QSpacerItem *horizontalSpacer;
    QCheckBox *ResetSimCheck;
    QPushButton *BeginButton;
    QPushButton *CancelButton;

    void setupUi(QWidget *VideoDialog)
    {
        if (VideoDialog->objectName().isEmpty())
            VideoDialog->setObjectName(QString::fromUtf8("VideoDialog"));
        VideoDialog->resize(308, 444);
        verticalLayout_7 = new QVBoxLayout(VideoDialog);
        verticalLayout_7->setObjectName(QString::fromUtf8("verticalLayout_7"));
        groupBox = new QGroupBox(VideoDialog);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        horizontalLayout_2 = new QHBoxLayout(groupBox);
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        OutputFolderEdit = new QLineEdit(groupBox);
        OutputFolderEdit->setObjectName(QString::fromUtf8("OutputFolderEdit"));
        OutputFolderEdit->setEnabled(false);

        horizontalLayout_2->addWidget(OutputFolderEdit);

        SelectFolderButton = new QPushButton(groupBox);
        SelectFolderButton->setObjectName(QString::fromUtf8("SelectFolderButton"));

        horizontalLayout_2->addWidget(SelectFolderButton);


        verticalLayout_7->addWidget(groupBox);

        groupBox_2 = new QGroupBox(VideoDialog);
        groupBox_2->setObjectName(QString::fromUtf8("groupBox_2"));
        verticalLayout = new QVBoxLayout(groupBox_2);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        WidthPixEdit = new QLineEdit(groupBox_2);
        WidthPixEdit->setObjectName(QString::fromUtf8("WidthPixEdit"));

        horizontalLayout->addWidget(WidthPixEdit);

        label = new QLabel(groupBox_2);
        label->setObjectName(QString::fromUtf8("label"));

        horizontalLayout->addWidget(label);

        HeightPixEdit = new QLineEdit(groupBox_2);
        HeightPixEdit->setObjectName(QString::fromUtf8("HeightPixEdit"));

        horizontalLayout->addWidget(HeightPixEdit);

        label_2 = new QLabel(groupBox_2);
        label_2->setObjectName(QString::fromUtf8("label_2"));

        horizontalLayout->addWidget(label_2);


        verticalLayout->addLayout(horizontalLayout);

        gridLayout = new QGridLayout();
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        r320x240Radio = new QRadioButton(groupBox_2);
        r320x240Radio->setObjectName(QString::fromUtf8("r320x240Radio"));

        gridLayout->addWidget(r320x240Radio, 0, 0, 1, 1);

        r800x600Radio = new QRadioButton(groupBox_2);
        r800x600Radio->setObjectName(QString::fromUtf8("r800x600Radio"));

        gridLayout->addWidget(r800x600Radio, 0, 1, 1, 1);

        r1280x720Radio = new QRadioButton(groupBox_2);
        r1280x720Radio->setObjectName(QString::fromUtf8("r1280x720Radio"));

        gridLayout->addWidget(r1280x720Radio, 0, 2, 1, 1);

        r640x480Radio = new QRadioButton(groupBox_2);
        r640x480Radio->setObjectName(QString::fromUtf8("r640x480Radio"));

        gridLayout->addWidget(r640x480Radio, 1, 0, 1, 1);

        r1024x768Radio = new QRadioButton(groupBox_2);
        r1024x768Radio->setObjectName(QString::fromUtf8("r1024x768Radio"));

        gridLayout->addWidget(r1024x768Radio, 1, 1, 1, 1);

        r1920x1080Radio = new QRadioButton(groupBox_2);
        r1920x1080Radio->setObjectName(QString::fromUtf8("r1920x1080Radio"));

        gridLayout->addWidget(r1920x1080Radio, 1, 2, 1, 1);


        verticalLayout->addLayout(gridLayout);


        verticalLayout_7->addWidget(groupBox_2);

        groupBox_5 = new QGroupBox(VideoDialog);
        groupBox_5->setObjectName(QString::fromUtf8("groupBox_5"));
        verticalLayout_2 = new QVBoxLayout(groupBox_5);
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        horizontalLayout_3 = new QHBoxLayout();
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        vsDisplayTimeRadio = new QRadioButton(groupBox_5);
        vsDisplayTimeRadio->setObjectName(QString::fromUtf8("vsDisplayTimeRadio"));

        horizontalLayout_3->addWidget(vsDisplayTimeRadio);

        vsSimTimeRadio = new QRadioButton(groupBox_5);
        vsSimTimeRadio->setObjectName(QString::fromUtf8("vsSimTimeRadio"));

        horizontalLayout_3->addWidget(vsSimTimeRadio);

        vsEveryFrameRadio = new QRadioButton(groupBox_5);
        vsEveryFrameRadio->setObjectName(QString::fromUtf8("vsEveryFrameRadio"));

        horizontalLayout_3->addWidget(vsEveryFrameRadio);


        verticalLayout_2->addLayout(horizontalLayout_3);

        horizontalLayout_4 = new QHBoxLayout();
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        OutputFpsEdit = new QLineEdit(groupBox_5);
        OutputFpsEdit->setObjectName(QString::fromUtf8("OutputFpsEdit"));

        horizontalLayout_4->addWidget(OutputFpsEdit);

        label_3 = new QLabel(groupBox_5);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        horizontalLayout_4->addWidget(label_3);

        OutputSpeedFactorEdit = new QLineEdit(groupBox_5);
        OutputSpeedFactorEdit->setObjectName(QString::fromUtf8("OutputSpeedFactorEdit"));

        horizontalLayout_4->addWidget(OutputSpeedFactorEdit);

        label_4 = new QLabel(groupBox_5);
        label_4->setObjectName(QString::fromUtf8("label_4"));

        horizontalLayout_4->addWidget(label_4);


        verticalLayout_2->addLayout(horizontalLayout_4);


        verticalLayout_7->addWidget(groupBox_5);

        groupBox_3 = new QGroupBox(VideoDialog);
        groupBox_3->setObjectName(QString::fromUtf8("groupBox_3"));
        verticalLayout_6 = new QVBoxLayout(groupBox_3);
        verticalLayout_6->setObjectName(QString::fromUtf8("verticalLayout_6"));
        AutoStopEnabledCheck = new QCheckBox(groupBox_3);
        AutoStopEnabledCheck->setObjectName(QString::fromUtf8("AutoStopEnabledCheck"));

        verticalLayout_6->addWidget(AutoStopEnabledCheck);

        horizontalLayout_5 = new QHBoxLayout();
        horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
        verticalLayout_5 = new QVBoxLayout();
        verticalLayout_5->setObjectName(QString::fromUtf8("verticalLayout_5"));
        TimeStepsRadio = new QRadioButton(groupBox_3);
        TimeStepsRadio->setObjectName(QString::fromUtf8("TimeStepsRadio"));

        verticalLayout_5->addWidget(TimeStepsRadio);

        SimTimeRadio = new QRadioButton(groupBox_3);
        SimTimeRadio->setObjectName(QString::fromUtf8("SimTimeRadio"));

        verticalLayout_5->addWidget(SimTimeRadio);

        TempCycleRadio = new QRadioButton(groupBox_3);
        TempCycleRadio->setObjectName(QString::fromUtf8("TempCycleRadio"));

        verticalLayout_5->addWidget(TempCycleRadio);


        horizontalLayout_5->addLayout(verticalLayout_5);

        verticalLayout_4 = new QVBoxLayout();
        verticalLayout_4->setObjectName(QString::fromUtf8("verticalLayout_4"));
        TimeStepsEdit = new QLineEdit(groupBox_3);
        TimeStepsEdit->setObjectName(QString::fromUtf8("TimeStepsEdit"));

        verticalLayout_4->addWidget(TimeStepsEdit);

        SimTimeEdit = new QLineEdit(groupBox_3);
        SimTimeEdit->setObjectName(QString::fromUtf8("SimTimeEdit"));

        verticalLayout_4->addWidget(SimTimeEdit);

        TempCycleEdit = new QLineEdit(groupBox_3);
        TempCycleEdit->setObjectName(QString::fromUtf8("TempCycleEdit"));

        verticalLayout_4->addWidget(TempCycleEdit);


        horizontalLayout_5->addLayout(verticalLayout_4);

        verticalLayout_3 = new QVBoxLayout();
        verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
        label_5 = new QLabel(groupBox_3);
        label_5->setObjectName(QString::fromUtf8("label_5"));

        verticalLayout_3->addWidget(label_5);

        label_6 = new QLabel(groupBox_3);
        label_6->setObjectName(QString::fromUtf8("label_6"));

        verticalLayout_3->addWidget(label_6);

        label_7 = new QLabel(groupBox_3);
        label_7->setObjectName(QString::fromUtf8("label_7"));

        verticalLayout_3->addWidget(label_7);


        horizontalLayout_5->addLayout(verticalLayout_3);


        verticalLayout_6->addLayout(horizontalLayout_5);


        verticalLayout_7->addWidget(groupBox_3);

        horizontalLayout_6 = new QHBoxLayout();
        horizontalLayout_6->setObjectName(QString::fromUtf8("horizontalLayout_6"));
        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_6->addItem(horizontalSpacer);

        ResetSimCheck = new QCheckBox(VideoDialog);
        ResetSimCheck->setObjectName(QString::fromUtf8("ResetSimCheck"));

        horizontalLayout_6->addWidget(ResetSimCheck);

        BeginButton = new QPushButton(VideoDialog);
        BeginButton->setObjectName(QString::fromUtf8("BeginButton"));

        horizontalLayout_6->addWidget(BeginButton);

        CancelButton = new QPushButton(VideoDialog);
        CancelButton->setObjectName(QString::fromUtf8("CancelButton"));

        horizontalLayout_6->addWidget(CancelButton);


        verticalLayout_7->addLayout(horizontalLayout_6);


        retranslateUi(VideoDialog);

        QMetaObject::connectSlotsByName(VideoDialog);
    } // setupUi

    void retranslateUi(QWidget *VideoDialog)
    {
        VideoDialog->setWindowTitle(QCoreApplication::translate("VideoDialog", "Video Capture Settings", nullptr));
        groupBox->setTitle(QCoreApplication::translate("VideoDialog", "Output Folder", nullptr));
#if QT_CONFIG(tooltip)
        OutputFolderEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Output folder for jpg frames. Use ffmpeg, virtualDub, etc. to convert to movie file.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        SelectFolderButton->setToolTip(QCoreApplication::translate("VideoDialog", "Output folder for jpg frames. Use ffmpeg, virtualDub, etc. to convert to movie file.", nullptr));
#endif // QT_CONFIG(tooltip)
        SelectFolderButton->setText(QCoreApplication::translate("VideoDialog", "Select", nullptr));
        groupBox_2->setTitle(QCoreApplication::translate("VideoDialog", "Resolution", nullptr));
#if QT_CONFIG(tooltip)
        WidthPixEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Video width", nullptr));
#endif // QT_CONFIG(tooltip)
        label->setText(QCoreApplication::translate("VideoDialog", "Width (pixels)", nullptr));
#if QT_CONFIG(tooltip)
        HeightPixEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Video height", nullptr));
#endif // QT_CONFIG(tooltip)
        label_2->setText(QCoreApplication::translate("VideoDialog", "Height (pixels)", nullptr));
        r320x240Radio->setText(QCoreApplication::translate("VideoDialog", "320x240", nullptr));
        r800x600Radio->setText(QCoreApplication::translate("VideoDialog", "800x600", nullptr));
        r1280x720Radio->setText(QCoreApplication::translate("VideoDialog", "1280x720", nullptr));
        r640x480Radio->setText(QCoreApplication::translate("VideoDialog", "640x480", nullptr));
        r1024x768Radio->setText(QCoreApplication::translate("VideoDialog", "1024x768", nullptr));
        r1920x1080Radio->setText(QCoreApplication::translate("VideoDialog", "1920x1080", nullptr));
        groupBox_5->setTitle(QCoreApplication::translate("VideoDialog", "Video speed", nullptr));
#if QT_CONFIG(tooltip)
        vsDisplayTimeRadio->setToolTip(QCoreApplication::translate("VideoDialog", "Records video at the speed the simulation is displayed on your screen.", nullptr));
#endif // QT_CONFIG(tooltip)
        vsDisplayTimeRadio->setText(QCoreApplication::translate("VideoDialog", "Display time", nullptr));
#if QT_CONFIG(tooltip)
        vsSimTimeRadio->setToolTip(QCoreApplication::translate("VideoDialog", "Records video at the speed of the simulation.\n"
"One second of simulation time is one second of\n"
"video. Use \"Output speed factor\" to vary this ratio.", nullptr));
#endif // QT_CONFIG(tooltip)
        vsSimTimeRadio->setText(QCoreApplication::translate("VideoDialog", "Simulation time", nullptr));
#if QT_CONFIG(tooltip)
        vsEveryFrameRadio->setToolTip(QCoreApplication::translate("VideoDialog", "The video contains a frame from every single timestep of the simulation.", nullptr));
#endif // QT_CONFIG(tooltip)
        vsEveryFrameRadio->setText(QCoreApplication::translate("VideoDialog", "Every frame", nullptr));
#if QT_CONFIG(tooltip)
        OutputFpsEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Desired framerate of output video in frames per second. [Usually 30 or so]", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_3->setToolTip(QCoreApplication::translate("VideoDialog", "Desired framerate of output video in frames per second. [Usually 30 or so]", nullptr));
#endif // QT_CONFIG(tooltip)
        label_3->setText(QCoreApplication::translate("VideoDialog", "Output fps", nullptr));
#if QT_CONFIG(tooltip)
        OutputSpeedFactorEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Speed up or slow down output video. [0.001-1000.0]\n"
"2.0 is double speed, 0.5 is half speed.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_4->setToolTip(QCoreApplication::translate("VideoDialog", "Speed up or slow down output video. [0.001-1000.0]\n"
"2.0 is double speed, 0.5 is half speed.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_4->setText(QCoreApplication::translate("VideoDialog", "Output\n"
"speed factor", nullptr));
        groupBox_3->setTitle(QCoreApplication::translate("VideoDialog", "AutoStop", nullptr));
#if QT_CONFIG(tooltip)
        AutoStopEnabledCheck->setToolTip(QCoreApplication::translate("VideoDialog", "Enables auto-stopping of the simulation.", nullptr));
#endif // QT_CONFIG(tooltip)
        AutoStopEnabledCheck->setText(QCoreApplication::translate("VideoDialog", "Enabled", nullptr));
#if QT_CONFIG(tooltip)
        TimeStepsRadio->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed number of timesteps.", nullptr));
#endif // QT_CONFIG(tooltip)
        TimeStepsRadio->setText(QCoreApplication::translate("VideoDialog", "Time steps", nullptr));
#if QT_CONFIG(tooltip)
        SimTimeRadio->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed amount of simulation time in seconds.", nullptr));
#endif // QT_CONFIG(tooltip)
        SimTimeRadio->setText(QCoreApplication::translate("VideoDialog", "Simulation time", nullptr));
#if QT_CONFIG(tooltip)
        TempCycleRadio->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed number of temperature variation cycles.", nullptr));
#endif // QT_CONFIG(tooltip)
        TempCycleRadio->setText(QCoreApplication::translate("VideoDialog", "Temperature cycles", nullptr));
#if QT_CONFIG(tooltip)
        TimeStepsEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed number of timesteps.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        SimTimeEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed amount of simulation time in seconds.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        TempCycleEdit->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed number of temperature variation cycles.", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        label_5->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed number of timesteps.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_5->setText(QCoreApplication::translate("VideoDialog", "# steps", nullptr));
#if QT_CONFIG(tooltip)
        label_6->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed amount of simulation time in seconds.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_6->setText(QCoreApplication::translate("VideoDialog", "sec", nullptr));
#if QT_CONFIG(tooltip)
        label_7->setToolTip(QCoreApplication::translate("VideoDialog", "Stops the simulation after a fixed number of temperature variation cycles.", nullptr));
#endif // QT_CONFIG(tooltip)
        label_7->setText(QCoreApplication::translate("VideoDialog", "# cyc", nullptr));
#if QT_CONFIG(tooltip)
        ResetSimCheck->setToolTip(QCoreApplication::translate("VideoDialog", "Resets the simulation upon \"Begin\" when enabled.", nullptr));
#endif // QT_CONFIG(tooltip)
        ResetSimCheck->setText(QCoreApplication::translate("VideoDialog", "Reset Sim", nullptr));
#if QT_CONFIG(tooltip)
        BeginButton->setToolTip(QCoreApplication::translate("VideoDialog", "Begin recording.", nullptr));
#endif // QT_CONFIG(tooltip)
        BeginButton->setText(QCoreApplication::translate("VideoDialog", "Begin", nullptr));
#if QT_CONFIG(tooltip)
        CancelButton->setToolTip(QCoreApplication::translate("VideoDialog", "Cancels the record operation.", nullptr));
#endif // QT_CONFIG(tooltip)
        CancelButton->setText(QCoreApplication::translate("VideoDialog", "Cancel", nullptr));
    } // retranslateUi

};

namespace Ui {
    class VideoDialog: public Ui_VideoDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VVIDEOGEN_H
