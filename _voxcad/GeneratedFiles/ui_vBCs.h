/********************************************************************************
** Form generated from reading UI file 'vBCs.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VBCS_H
#define UI_VBCS_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QFrame>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QScrollArea>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_BCDlg
{
public:
    QVBoxLayout *verticalLayout_3;
    QHBoxLayout *horizontalLayout_6;
    QComboBox *BCPresetsCombo;
    QLabel *PresetLabel;
    QFrame *line;
    QLabel *BCLabel;
    QListWidget *BCList;
    QHBoxLayout *horizontalLayout_5;
    QPushButton *AddBCButton;
    QPushButton *DelBCButton;
    QPushButton *LoadBCButton;
    QPushButton *SaveBCButton;
    QSpacerItem *horizontalSpacer;
    QTabWidget *BCTabWidget;
    QWidget *ModeTab;
    QVBoxLayout *verticalLayout;
    QHBoxLayout *horizontalLayout;
    QPushButton *FixAllButton;
    QPushButton *FixNoneButton;
    QSpacerItem *horizontalSpacer_2;
    QGroupBox *TranslationGroup;
    QGridLayout *gridLayout;
    QLabel *label_3;
    QLabel *label;
    QLabel *label_2;
    QLabel *XLabel;
    QCheckBox *XFixed;
    QLineEdit *XForceEdit;
    QLineEdit *XDispEdit;
    QLabel *YLabel;
    QCheckBox *YFixed;
    QLineEdit *YForceEdit;
    QLineEdit *YDispEdit;
    QLabel *ZLabel;
    QCheckBox *ZFixed;
    QLineEdit *ZForceEdit;
    QLineEdit *ZDispEdit;
    QGroupBox *RotationGroup;
    QGridLayout *gridLayout_2;
    QLabel *label_4;
    QLabel *label_5;
    QLabel *label_6;
    QLabel *TXLabel;
    QCheckBox *TXFixed;
    QLineEdit *TXTorqueEdit;
    QLineEdit *TXDispEdit;
    QLabel *TYLabel;
    QCheckBox *TYFixed;
    QLineEdit *TYTorqueEdit;
    QLineEdit *TYDispEdit;
    QLabel *TZLabel;
    QCheckBox *TZFixed;
    QLineEdit *TZTorqueEdit;
    QLineEdit *TZDispEdit;
    QSpacerItem *verticalSpacer;
    QWidget *ShapeTab;
    QVBoxLayout *verticalLayout_2;
    QScrollArea *ShapeScrollArea;
    QWidget *scrollAreaWidgetContents;
    QPushButton *BCDonePushButton;

    void setupUi(QWidget *BCDlg)
    {
        if (BCDlg->objectName().isEmpty())
            BCDlg->setObjectName(QString::fromUtf8("BCDlg"));
        BCDlg->resize(200, 620);
        verticalLayout_3 = new QVBoxLayout(BCDlg);
        verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
        horizontalLayout_6 = new QHBoxLayout();
        horizontalLayout_6->setObjectName(QString::fromUtf8("horizontalLayout_6"));
        BCPresetsCombo = new QComboBox(BCDlg);
        BCPresetsCombo->setObjectName(QString::fromUtf8("BCPresetsCombo"));

        horizontalLayout_6->addWidget(BCPresetsCombo);

        PresetLabel = new QLabel(BCDlg);
        PresetLabel->setObjectName(QString::fromUtf8("PresetLabel"));

        horizontalLayout_6->addWidget(PresetLabel);


        verticalLayout_3->addLayout(horizontalLayout_6);

        line = new QFrame(BCDlg);
        line->setObjectName(QString::fromUtf8("line"));
        line->setFrameShape(QFrame::HLine);
        line->setFrameShadow(QFrame::Sunken);

        verticalLayout_3->addWidget(line);

        BCLabel = new QLabel(BCDlg);
        BCLabel->setObjectName(QString::fromUtf8("BCLabel"));
        QSizePolicy sizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(BCLabel->sizePolicy().hasHeightForWidth());
        BCLabel->setSizePolicy(sizePolicy);

        verticalLayout_3->addWidget(BCLabel);

        BCList = new QListWidget(BCDlg);
        BCList->setObjectName(QString::fromUtf8("BCList"));
        QSizePolicy sizePolicy1(QSizePolicy::Expanding, QSizePolicy::Expanding);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(BCList->sizePolicy().hasHeightForWidth());
        BCList->setSizePolicy(sizePolicy1);
        BCList->setMaximumSize(QSize(16777215, 100));

        verticalLayout_3->addWidget(BCList);

        horizontalLayout_5 = new QHBoxLayout();
        horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
        AddBCButton = new QPushButton(BCDlg);
        AddBCButton->setObjectName(QString::fromUtf8("AddBCButton"));
        QSizePolicy sizePolicy2(QSizePolicy::Minimum, QSizePolicy::Fixed);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(AddBCButton->sizePolicy().hasHeightForWidth());
        AddBCButton->setSizePolicy(sizePolicy2);
        AddBCButton->setMaximumSize(QSize(25, 16777215));

        horizontalLayout_5->addWidget(AddBCButton);

        DelBCButton = new QPushButton(BCDlg);
        DelBCButton->setObjectName(QString::fromUtf8("DelBCButton"));
        DelBCButton->setMaximumSize(QSize(25, 16777215));

        horizontalLayout_5->addWidget(DelBCButton);

        LoadBCButton = new QPushButton(BCDlg);
        LoadBCButton->setObjectName(QString::fromUtf8("LoadBCButton"));
        LoadBCButton->setMaximumSize(QSize(40, 16777215));

        horizontalLayout_5->addWidget(LoadBCButton);

        SaveBCButton = new QPushButton(BCDlg);
        SaveBCButton->setObjectName(QString::fromUtf8("SaveBCButton"));
        SaveBCButton->setMaximumSize(QSize(40, 16777215));

        horizontalLayout_5->addWidget(SaveBCButton);

        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_5->addItem(horizontalSpacer);


        verticalLayout_3->addLayout(horizontalLayout_5);

        BCTabWidget = new QTabWidget(BCDlg);
        BCTabWidget->setObjectName(QString::fromUtf8("BCTabWidget"));
        sizePolicy1.setHeightForWidth(BCTabWidget->sizePolicy().hasHeightForWidth());
        BCTabWidget->setSizePolicy(sizePolicy1);
        ModeTab = new QWidget();
        ModeTab->setObjectName(QString::fromUtf8("ModeTab"));
        verticalLayout = new QVBoxLayout(ModeTab);
        verticalLayout->setSpacing(3);
        verticalLayout->setContentsMargins(3, 3, 3, 3);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        FixAllButton = new QPushButton(ModeTab);
        FixAllButton->setObjectName(QString::fromUtf8("FixAllButton"));

        horizontalLayout->addWidget(FixAllButton);

        FixNoneButton = new QPushButton(ModeTab);
        FixNoneButton->setObjectName(QString::fromUtf8("FixNoneButton"));

        horizontalLayout->addWidget(FixNoneButton);

        horizontalSpacer_2 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer_2);


        verticalLayout->addLayout(horizontalLayout);

        TranslationGroup = new QGroupBox(ModeTab);
        TranslationGroup->setObjectName(QString::fromUtf8("TranslationGroup"));
        gridLayout = new QGridLayout(TranslationGroup);
        gridLayout->setSpacing(3);
        gridLayout->setContentsMargins(3, 3, 3, 3);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        label_3 = new QLabel(TranslationGroup);
        label_3->setObjectName(QString::fromUtf8("label_3"));
        label_3->setAlignment(Qt::AlignCenter);

        gridLayout->addWidget(label_3, 0, 1, 1, 1);

        label = new QLabel(TranslationGroup);
        label->setObjectName(QString::fromUtf8("label"));
        label->setAlignment(Qt::AlignCenter);

        gridLayout->addWidget(label, 0, 2, 1, 1);

        label_2 = new QLabel(TranslationGroup);
        label_2->setObjectName(QString::fromUtf8("label_2"));
        label_2->setAlignment(Qt::AlignCenter);

        gridLayout->addWidget(label_2, 0, 3, 1, 1);

        XLabel = new QLabel(TranslationGroup);
        XLabel->setObjectName(QString::fromUtf8("XLabel"));

        gridLayout->addWidget(XLabel, 1, 0, 1, 1);

        XFixed = new QCheckBox(TranslationGroup);
        XFixed->setObjectName(QString::fromUtf8("XFixed"));

        gridLayout->addWidget(XFixed, 1, 1, 1, 1);

        XForceEdit = new QLineEdit(TranslationGroup);
        XForceEdit->setObjectName(QString::fromUtf8("XForceEdit"));

        gridLayout->addWidget(XForceEdit, 1, 2, 1, 1);

        XDispEdit = new QLineEdit(TranslationGroup);
        XDispEdit->setObjectName(QString::fromUtf8("XDispEdit"));

        gridLayout->addWidget(XDispEdit, 1, 3, 1, 1);

        YLabel = new QLabel(TranslationGroup);
        YLabel->setObjectName(QString::fromUtf8("YLabel"));

        gridLayout->addWidget(YLabel, 2, 0, 1, 1);

        YFixed = new QCheckBox(TranslationGroup);
        YFixed->setObjectName(QString::fromUtf8("YFixed"));

        gridLayout->addWidget(YFixed, 2, 1, 1, 1);

        YForceEdit = new QLineEdit(TranslationGroup);
        YForceEdit->setObjectName(QString::fromUtf8("YForceEdit"));

        gridLayout->addWidget(YForceEdit, 2, 2, 1, 1);

        YDispEdit = new QLineEdit(TranslationGroup);
        YDispEdit->setObjectName(QString::fromUtf8("YDispEdit"));

        gridLayout->addWidget(YDispEdit, 2, 3, 1, 1);

        ZLabel = new QLabel(TranslationGroup);
        ZLabel->setObjectName(QString::fromUtf8("ZLabel"));

        gridLayout->addWidget(ZLabel, 3, 0, 1, 1);

        ZFixed = new QCheckBox(TranslationGroup);
        ZFixed->setObjectName(QString::fromUtf8("ZFixed"));

        gridLayout->addWidget(ZFixed, 3, 1, 1, 1);

        ZForceEdit = new QLineEdit(TranslationGroup);
        ZForceEdit->setObjectName(QString::fromUtf8("ZForceEdit"));

        gridLayout->addWidget(ZForceEdit, 3, 2, 1, 1);

        ZDispEdit = new QLineEdit(TranslationGroup);
        ZDispEdit->setObjectName(QString::fromUtf8("ZDispEdit"));

        gridLayout->addWidget(ZDispEdit, 3, 3, 1, 1);


        verticalLayout->addWidget(TranslationGroup);

        RotationGroup = new QGroupBox(ModeTab);
        RotationGroup->setObjectName(QString::fromUtf8("RotationGroup"));
        gridLayout_2 = new QGridLayout(RotationGroup);
        gridLayout_2->setSpacing(3);
        gridLayout_2->setContentsMargins(3, 3, 3, 3);
        gridLayout_2->setObjectName(QString::fromUtf8("gridLayout_2"));
        label_4 = new QLabel(RotationGroup);
        label_4->setObjectName(QString::fromUtf8("label_4"));
        label_4->setAlignment(Qt::AlignCenter);

        gridLayout_2->addWidget(label_4, 0, 1, 1, 1);

        label_5 = new QLabel(RotationGroup);
        label_5->setObjectName(QString::fromUtf8("label_5"));
        label_5->setAlignment(Qt::AlignCenter);

        gridLayout_2->addWidget(label_5, 0, 2, 1, 1);

        label_6 = new QLabel(RotationGroup);
        label_6->setObjectName(QString::fromUtf8("label_6"));
        label_6->setAlignment(Qt::AlignCenter);

        gridLayout_2->addWidget(label_6, 0, 3, 1, 1);

        TXLabel = new QLabel(RotationGroup);
        TXLabel->setObjectName(QString::fromUtf8("TXLabel"));

        gridLayout_2->addWidget(TXLabel, 1, 0, 1, 1);

        TXFixed = new QCheckBox(RotationGroup);
        TXFixed->setObjectName(QString::fromUtf8("TXFixed"));

        gridLayout_2->addWidget(TXFixed, 1, 1, 1, 1);

        TXTorqueEdit = new QLineEdit(RotationGroup);
        TXTorqueEdit->setObjectName(QString::fromUtf8("TXTorqueEdit"));

        gridLayout_2->addWidget(TXTorqueEdit, 1, 2, 1, 1);

        TXDispEdit = new QLineEdit(RotationGroup);
        TXDispEdit->setObjectName(QString::fromUtf8("TXDispEdit"));

        gridLayout_2->addWidget(TXDispEdit, 1, 3, 1, 1);

        TYLabel = new QLabel(RotationGroup);
        TYLabel->setObjectName(QString::fromUtf8("TYLabel"));

        gridLayout_2->addWidget(TYLabel, 2, 0, 1, 1);

        TYFixed = new QCheckBox(RotationGroup);
        TYFixed->setObjectName(QString::fromUtf8("TYFixed"));

        gridLayout_2->addWidget(TYFixed, 2, 1, 1, 1);

        TYTorqueEdit = new QLineEdit(RotationGroup);
        TYTorqueEdit->setObjectName(QString::fromUtf8("TYTorqueEdit"));

        gridLayout_2->addWidget(TYTorqueEdit, 2, 2, 1, 1);

        TYDispEdit = new QLineEdit(RotationGroup);
        TYDispEdit->setObjectName(QString::fromUtf8("TYDispEdit"));

        gridLayout_2->addWidget(TYDispEdit, 2, 3, 1, 1);

        TZLabel = new QLabel(RotationGroup);
        TZLabel->setObjectName(QString::fromUtf8("TZLabel"));

        gridLayout_2->addWidget(TZLabel, 3, 0, 1, 1);

        TZFixed = new QCheckBox(RotationGroup);
        TZFixed->setObjectName(QString::fromUtf8("TZFixed"));

        gridLayout_2->addWidget(TZFixed, 3, 1, 1, 1);

        TZTorqueEdit = new QLineEdit(RotationGroup);
        TZTorqueEdit->setObjectName(QString::fromUtf8("TZTorqueEdit"));

        gridLayout_2->addWidget(TZTorqueEdit, 3, 2, 1, 1);

        TZDispEdit = new QLineEdit(RotationGroup);
        TZDispEdit->setObjectName(QString::fromUtf8("TZDispEdit"));

        gridLayout_2->addWidget(TZDispEdit, 3, 3, 1, 1);


        verticalLayout->addWidget(RotationGroup);

        verticalSpacer = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout->addItem(verticalSpacer);

        BCTabWidget->addTab(ModeTab, QString());
        ShapeTab = new QWidget();
        ShapeTab->setObjectName(QString::fromUtf8("ShapeTab"));
        verticalLayout_2 = new QVBoxLayout(ShapeTab);
        verticalLayout_2->setContentsMargins(0, 0, 0, 0);
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        ShapeScrollArea = new QScrollArea(ShapeTab);
        ShapeScrollArea->setObjectName(QString::fromUtf8("ShapeScrollArea"));
        ShapeScrollArea->setFrameShape(QFrame::NoFrame);
        ShapeScrollArea->setFrameShadow(QFrame::Plain);
        ShapeScrollArea->setLineWidth(0);
        ShapeScrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
        ShapeScrollArea->setWidgetResizable(true);
        scrollAreaWidgetContents = new QWidget();
        scrollAreaWidgetContents->setObjectName(QString::fromUtf8("scrollAreaWidgetContents"));
        scrollAreaWidgetContents->setGeometry(QRect(0, 0, 176, 354));
        ShapeScrollArea->setWidget(scrollAreaWidgetContents);

        verticalLayout_2->addWidget(ShapeScrollArea);

        BCTabWidget->addTab(ShapeTab, QString());

        verticalLayout_3->addWidget(BCTabWidget);

        BCDonePushButton = new QPushButton(BCDlg);
        BCDonePushButton->setObjectName(QString::fromUtf8("BCDonePushButton"));

        verticalLayout_3->addWidget(BCDonePushButton);


        retranslateUi(BCDlg);

        BCTabWidget->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(BCDlg);
    } // setupUi

    void retranslateUi(QWidget *BCDlg)
    {
        BCDlg->setWindowTitle(QCoreApplication::translate("BCDlg", "Boundary Condition Editor", nullptr));
        PresetLabel->setText(QCoreApplication::translate("BCDlg", "Presets", nullptr));
#if QT_CONFIG(tooltip)
        BCLabel->setToolTip(QCoreApplication::translate("BCDlg", "(X Y Z \316\230x \316\230y \316\230z) * = fixed, _ = free", nullptr));
#endif // QT_CONFIG(tooltip)
        BCLabel->setText(QCoreApplication::translate("BCDlg", "Boundary Conditions:", nullptr));
#if QT_CONFIG(tooltip)
        BCList->setToolTip(QCoreApplication::translate("BCDlg", "(X Y Z \316\230x \316\230y \316\230z) * = fixed, _ = free", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        AddBCButton->setToolTip(QCoreApplication::translate("BCDlg", "Adds new boundary condition", nullptr));
#endif // QT_CONFIG(tooltip)
        AddBCButton->setText(QCoreApplication::translate("BCDlg", "+", nullptr));
#if QT_CONFIG(tooltip)
        DelBCButton->setToolTip(QCoreApplication::translate("BCDlg", "Deletes selected boundary condition", nullptr));
#endif // QT_CONFIG(tooltip)
        DelBCButton->setText(QCoreApplication::translate("BCDlg", "-", nullptr));
#if QT_CONFIG(tooltip)
        LoadBCButton->setToolTip(QCoreApplication::translate("BCDlg", "Loads boundary condition file", nullptr));
#endif // QT_CONFIG(tooltip)
        LoadBCButton->setText(QCoreApplication::translate("BCDlg", "Load", nullptr));
#if QT_CONFIG(tooltip)
        SaveBCButton->setToolTip(QCoreApplication::translate("BCDlg", "Saves boundary condition file", nullptr));
#endif // QT_CONFIG(tooltip)
        SaveBCButton->setText(QCoreApplication::translate("BCDlg", "Save", nullptr));
#if QT_CONFIG(tooltip)
        BCTabWidget->setToolTip(QCoreApplication::translate("BCDlg", "Boundary condition settings", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        FixAllButton->setToolTip(QCoreApplication::translate("BCDlg", "Fix all degrees of freedom", nullptr));
#endif // QT_CONFIG(tooltip)
        FixAllButton->setText(QCoreApplication::translate("BCDlg", "Fix All", nullptr));
#if QT_CONFIG(tooltip)
        FixNoneButton->setToolTip(QCoreApplication::translate("BCDlg", "Unfix all degrees of freedom", nullptr));
#endif // QT_CONFIG(tooltip)
        FixNoneButton->setText(QCoreApplication::translate("BCDlg", "Fix None", nullptr));
        TranslationGroup->setTitle(QCoreApplication::translate("BCDlg", "Translation", nullptr));
        label_3->setText(QCoreApplication::translate("BCDlg", "Fixed", nullptr));
        label->setText(QCoreApplication::translate("BCDlg", "Force\n"
"(N)", nullptr));
        label_2->setText(QCoreApplication::translate("BCDlg", "Displacement\n"
"(mm)", nullptr));
        XLabel->setText(QCoreApplication::translate("BCDlg", "X", nullptr));
        XFixed->setText(QString());
        YLabel->setText(QCoreApplication::translate("BCDlg", "Y", nullptr));
        YFixed->setText(QString());
        ZLabel->setText(QCoreApplication::translate("BCDlg", "Z", nullptr));
        ZFixed->setText(QString());
        RotationGroup->setTitle(QCoreApplication::translate("BCDlg", "Rotation", nullptr));
        label_4->setText(QCoreApplication::translate("BCDlg", "Fixed", nullptr));
        label_5->setText(QCoreApplication::translate("BCDlg", "Torque\n"
"(Nmm)", nullptr));
        label_6->setText(QCoreApplication::translate("BCDlg", "Displacement\n"
"(degrees\302\255)", nullptr));
        TXLabel->setText(QCoreApplication::translate("BCDlg", "\316\230x", nullptr));
        TXFixed->setText(QString());
        TYLabel->setText(QCoreApplication::translate("BCDlg", "\316\230y", nullptr));
        TYFixed->setText(QString());
        TZLabel->setText(QCoreApplication::translate("BCDlg", "\316\230z", nullptr));
        TZFixed->setText(QString());
        BCTabWidget->setTabText(BCTabWidget->indexOf(ModeTab), QCoreApplication::translate("BCDlg", "Mode", nullptr));
        BCTabWidget->setTabText(BCTabWidget->indexOf(ShapeTab), QCoreApplication::translate("BCDlg", "Shape", nullptr));
        BCDonePushButton->setText(QCoreApplication::translate("BCDlg", "Finished Editing", nullptr));
    } // retranslateUi

};

namespace Ui {
    class BCDlg: public Ui_BCDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VBCS_H
