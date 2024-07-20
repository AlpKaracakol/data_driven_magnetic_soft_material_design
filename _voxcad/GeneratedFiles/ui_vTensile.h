/********************************************************************************
** Form generated from reading UI file 'vTensile.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VTENSILE_H
#define UI_VTENSILE_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_TensileDlg
{
public:
    QVBoxLayout *verticalLayout_3;
    QHBoxLayout *horizontalLayout_3;
    QSpinBox *NumStepSpin;
    QLabel *label;
    QLabel *label_3;
    QHBoxLayout *horizontalLayout_8;
    QHBoxLayout *horizontalLayout_4;
    QLineEdit *XMixRadiusEdit;
    QLabel *label_5;
    QHBoxLayout *horizontalLayout_5;
    QLineEdit *YMixRadiusEdit;
    QLabel *label_6;
    QHBoxLayout *horizontalLayout_7;
    QLineEdit *ZMixRadiusEdit;
    QLabel *label_7;
    QGroupBox *groupBox;
    QVBoxLayout *verticalLayout_2;
    QRadioButton *FastRadio;
    QRadioButton *BalancedRadio;
    QRadioButton *AccurateRadio;
    QRadioButton *ManualRadio;
    QHBoxLayout *horizontalLayout_6;
    QLineEdit *ConvThreshEdit;
    QLabel *label_2;
    QGroupBox *MixModelGroup;
    QVBoxLayout *verticalLayout;
    QRadioButton *mm_LinearButton;
    QRadioButton *mm_ExpButton;
    QHBoxLayout *horizontalLayout_2;
    QRadioButton *mm_PolyButton;
    QSpacerItem *horizontalSpacer;
    QLineEdit *PolyExpEdit;
    QLabel *label_4;
    QSpacerItem *verticalSpacer;
    QHBoxLayout *horizontalLayout;
    QPushButton *StartButton;
    QPushButton *DoneButton;

    void setupUi(QWidget *TensileDlg)
    {
        if (TensileDlg->objectName().isEmpty())
            TensileDlg->setObjectName(QString::fromUtf8("TensileDlg"));
        TensileDlg->resize(218, 490);
        verticalLayout_3 = new QVBoxLayout(TensileDlg);
        verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
        horizontalLayout_3 = new QHBoxLayout();
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        NumStepSpin = new QSpinBox(TensileDlg);
        NumStepSpin->setObjectName(QString::fromUtf8("NumStepSpin"));
        NumStepSpin->setMinimum(1);
        NumStepSpin->setMaximum(10000);
        NumStepSpin->setSingleStep(10);

        horizontalLayout_3->addWidget(NumStepSpin);

        label = new QLabel(TensileDlg);
        label->setObjectName(QString::fromUtf8("label"));

        horizontalLayout_3->addWidget(label);


        verticalLayout_3->addLayout(horizontalLayout_3);

        label_3 = new QLabel(TensileDlg);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        verticalLayout_3->addWidget(label_3);

        horizontalLayout_8 = new QHBoxLayout();
        horizontalLayout_8->setObjectName(QString::fromUtf8("horizontalLayout_8"));
        horizontalLayout_4 = new QHBoxLayout();
        horizontalLayout_4->setSpacing(0);
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        XMixRadiusEdit = new QLineEdit(TensileDlg);
        XMixRadiusEdit->setObjectName(QString::fromUtf8("XMixRadiusEdit"));

        horizontalLayout_4->addWidget(XMixRadiusEdit);

        label_5 = new QLabel(TensileDlg);
        label_5->setObjectName(QString::fromUtf8("label_5"));

        horizontalLayout_4->addWidget(label_5);


        horizontalLayout_8->addLayout(horizontalLayout_4);

        horizontalLayout_5 = new QHBoxLayout();
        horizontalLayout_5->setSpacing(0);
        horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
        YMixRadiusEdit = new QLineEdit(TensileDlg);
        YMixRadiusEdit->setObjectName(QString::fromUtf8("YMixRadiusEdit"));

        horizontalLayout_5->addWidget(YMixRadiusEdit);

        label_6 = new QLabel(TensileDlg);
        label_6->setObjectName(QString::fromUtf8("label_6"));

        horizontalLayout_5->addWidget(label_6);


        horizontalLayout_8->addLayout(horizontalLayout_5);

        horizontalLayout_7 = new QHBoxLayout();
        horizontalLayout_7->setSpacing(0);
        horizontalLayout_7->setObjectName(QString::fromUtf8("horizontalLayout_7"));
        ZMixRadiusEdit = new QLineEdit(TensileDlg);
        ZMixRadiusEdit->setObjectName(QString::fromUtf8("ZMixRadiusEdit"));

        horizontalLayout_7->addWidget(ZMixRadiusEdit);

        label_7 = new QLabel(TensileDlg);
        label_7->setObjectName(QString::fromUtf8("label_7"));

        horizontalLayout_7->addWidget(label_7);


        horizontalLayout_8->addLayout(horizontalLayout_7);


        verticalLayout_3->addLayout(horizontalLayout_8);

        groupBox = new QGroupBox(TensileDlg);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        verticalLayout_2 = new QVBoxLayout(groupBox);
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        FastRadio = new QRadioButton(groupBox);
        FastRadio->setObjectName(QString::fromUtf8("FastRadio"));

        verticalLayout_2->addWidget(FastRadio);

        BalancedRadio = new QRadioButton(groupBox);
        BalancedRadio->setObjectName(QString::fromUtf8("BalancedRadio"));

        verticalLayout_2->addWidget(BalancedRadio);

        AccurateRadio = new QRadioButton(groupBox);
        AccurateRadio->setObjectName(QString::fromUtf8("AccurateRadio"));

        verticalLayout_2->addWidget(AccurateRadio);

        ManualRadio = new QRadioButton(groupBox);
        ManualRadio->setObjectName(QString::fromUtf8("ManualRadio"));

        verticalLayout_2->addWidget(ManualRadio);

        horizontalLayout_6 = new QHBoxLayout();
        horizontalLayout_6->setObjectName(QString::fromUtf8("horizontalLayout_6"));
        ConvThreshEdit = new QLineEdit(groupBox);
        ConvThreshEdit->setObjectName(QString::fromUtf8("ConvThreshEdit"));

        horizontalLayout_6->addWidget(ConvThreshEdit);

        label_2 = new QLabel(groupBox);
        label_2->setObjectName(QString::fromUtf8("label_2"));

        horizontalLayout_6->addWidget(label_2);


        verticalLayout_2->addLayout(horizontalLayout_6);


        verticalLayout_3->addWidget(groupBox);

        MixModelGroup = new QGroupBox(TensileDlg);
        MixModelGroup->setObjectName(QString::fromUtf8("MixModelGroup"));
        verticalLayout = new QVBoxLayout(MixModelGroup);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        mm_LinearButton = new QRadioButton(MixModelGroup);
        mm_LinearButton->setObjectName(QString::fromUtf8("mm_LinearButton"));

        verticalLayout->addWidget(mm_LinearButton);

        mm_ExpButton = new QRadioButton(MixModelGroup);
        mm_ExpButton->setObjectName(QString::fromUtf8("mm_ExpButton"));

        verticalLayout->addWidget(mm_ExpButton);

        horizontalLayout_2 = new QHBoxLayout();
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        mm_PolyButton = new QRadioButton(MixModelGroup);
        mm_PolyButton->setObjectName(QString::fromUtf8("mm_PolyButton"));

        horizontalLayout_2->addWidget(mm_PolyButton);

        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_2->addItem(horizontalSpacer);

        PolyExpEdit = new QLineEdit(MixModelGroup);
        PolyExpEdit->setObjectName(QString::fromUtf8("PolyExpEdit"));
        QSizePolicy sizePolicy(QSizePolicy::Maximum, QSizePolicy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(PolyExpEdit->sizePolicy().hasHeightForWidth());
        PolyExpEdit->setSizePolicy(sizePolicy);

        horizontalLayout_2->addWidget(PolyExpEdit);

        label_4 = new QLabel(MixModelGroup);
        label_4->setObjectName(QString::fromUtf8("label_4"));

        horizontalLayout_2->addWidget(label_4);


        verticalLayout->addLayout(horizontalLayout_2);


        verticalLayout_3->addWidget(MixModelGroup);

        verticalSpacer = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_3->addItem(verticalSpacer);

        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        StartButton = new QPushButton(TensileDlg);
        StartButton->setObjectName(QString::fromUtf8("StartButton"));

        horizontalLayout->addWidget(StartButton);

        DoneButton = new QPushButton(TensileDlg);
        DoneButton->setObjectName(QString::fromUtf8("DoneButton"));

        horizontalLayout->addWidget(DoneButton);


        verticalLayout_3->addLayout(horizontalLayout);


        retranslateUi(TensileDlg);

        QMetaObject::connectSlotsByName(TensileDlg);
    } // setupUi

    void retranslateUi(QWidget *TensileDlg)
    {
        TensileDlg->setWindowTitle(QCoreApplication::translate("TensileDlg", "Tensile Test", nullptr));
        label->setText(QCoreApplication::translate("TensileDlg", "Number of Steps", nullptr));
        label_3->setText(QCoreApplication::translate("TensileDlg", "Mixing distance (mm) (1/2 mix layer)", nullptr));
        label_5->setText(QCoreApplication::translate("TensileDlg", "X", nullptr));
        label_6->setText(QCoreApplication::translate("TensileDlg", "Y", nullptr));
        label_7->setText(QCoreApplication::translate("TensileDlg", "Z", nullptr));
        groupBox->setTitle(QCoreApplication::translate("TensileDlg", "Step Convergence", nullptr));
        FastRadio->setText(QCoreApplication::translate("TensileDlg", "Fast", nullptr));
        BalancedRadio->setText(QCoreApplication::translate("TensileDlg", " Balanced", nullptr));
        AccurateRadio->setText(QCoreApplication::translate("TensileDlg", "Accurate", nullptr));
        ManualRadio->setText(QCoreApplication::translate("TensileDlg", "Manual", nullptr));
        label_2->setText(QCoreApplication::translate("TensileDlg", "Converge Threshhold\n"
"(mm/timestep)", nullptr));
        MixModelGroup->setTitle(QCoreApplication::translate("TensileDlg", "Material Mixing Model", nullptr));
        mm_LinearButton->setText(QCoreApplication::translate("TensileDlg", "Linear (x)", nullptr));
        mm_ExpButton->setText(QCoreApplication::translate("TensileDlg", "Exponential (2^x-1)", nullptr));
        mm_PolyButton->setText(QCoreApplication::translate("TensileDlg", "Polynomial (x^n)", nullptr));
        label_4->setText(QCoreApplication::translate("TensileDlg", "n", nullptr));
        StartButton->setText(QCoreApplication::translate("TensileDlg", "Start", nullptr));
        DoneButton->setText(QCoreApplication::translate("TensileDlg", "Done", nullptr));
    } // retranslateUi

};

namespace Ui {
    class TensileDlg: public Ui_TensileDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VTENSILE_H
