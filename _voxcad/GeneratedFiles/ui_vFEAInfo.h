/********************************************************************************
** Form generated from reading UI file 'vFEAInfo.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VFEAINFO_H
#define UI_VFEAINFO_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSlider>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_FEAInfoDlg
{
public:
    QVBoxLayout *verticalLayout_4;
    QHBoxLayout *horizontalLayout_3;
    QComboBox *ViewTypeCombo;
    QLabel *ViewTypeLabel;
    QHBoxLayout *horizontalLayout_2;
    QVBoxLayout *verticalLayout_3;
    QSlider *DefSlider;
    QSlider *IsoThreshSlider;
    QSlider *SectionSlider;
    QVBoxLayout *verticalLayout_2;
    QLabel *DefLabel;
    QLabel *IsoThreshLabel;
    QLabel *SectionLabel;
    QGroupBox *DirGroup;
    QVBoxLayout *verticalLayout;
    QHBoxLayout *horizontalLayout;
    QRadioButton *DirMaxRadio;
    QRadioButton *DirXRadio;
    QRadioButton *DirYRadio;
    QRadioButton *DirZRadio;
    QLabel *FEAInfoLabel;
    QHBoxLayout *horizontalLayout_4;
    QPushButton *DoneButton;

    void setupUi(QWidget *FEAInfoDlg)
    {
        if (FEAInfoDlg->objectName().isEmpty())
            FEAInfoDlg->setObjectName(QString::fromUtf8("FEAInfoDlg"));
        FEAInfoDlg->resize(188, 384);
        verticalLayout_4 = new QVBoxLayout(FEAInfoDlg);
        verticalLayout_4->setObjectName(QString::fromUtf8("verticalLayout_4"));
        horizontalLayout_3 = new QHBoxLayout();
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        ViewTypeCombo = new QComboBox(FEAInfoDlg);
        ViewTypeCombo->setObjectName(QString::fromUtf8("ViewTypeCombo"));

        horizontalLayout_3->addWidget(ViewTypeCombo);

        ViewTypeLabel = new QLabel(FEAInfoDlg);
        ViewTypeLabel->setObjectName(QString::fromUtf8("ViewTypeLabel"));

        horizontalLayout_3->addWidget(ViewTypeLabel);


        verticalLayout_4->addLayout(horizontalLayout_3);

        horizontalLayout_2 = new QHBoxLayout();
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        verticalLayout_3 = new QVBoxLayout();
        verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
        DefSlider = new QSlider(FEAInfoDlg);
        DefSlider->setObjectName(QString::fromUtf8("DefSlider"));
        DefSlider->setMaximum(1000);
        DefSlider->setSingleStep(10);
        DefSlider->setPageStep(100);
        DefSlider->setOrientation(Qt::Horizontal);

        verticalLayout_3->addWidget(DefSlider);

        IsoThreshSlider = new QSlider(FEAInfoDlg);
        IsoThreshSlider->setObjectName(QString::fromUtf8("IsoThreshSlider"));
        IsoThreshSlider->setMaximum(1000);
        IsoThreshSlider->setSingleStep(10);
        IsoThreshSlider->setPageStep(100);
        IsoThreshSlider->setOrientation(Qt::Horizontal);

        verticalLayout_3->addWidget(IsoThreshSlider);

        SectionSlider = new QSlider(FEAInfoDlg);
        SectionSlider->setObjectName(QString::fromUtf8("SectionSlider"));
        SectionSlider->setMaximum(1000);
        SectionSlider->setSingleStep(10);
        SectionSlider->setPageStep(100);
        SectionSlider->setOrientation(Qt::Horizontal);

        verticalLayout_3->addWidget(SectionSlider);


        horizontalLayout_2->addLayout(verticalLayout_3);

        verticalLayout_2 = new QVBoxLayout();
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        DefLabel = new QLabel(FEAInfoDlg);
        DefLabel->setObjectName(QString::fromUtf8("DefLabel"));

        verticalLayout_2->addWidget(DefLabel);

        IsoThreshLabel = new QLabel(FEAInfoDlg);
        IsoThreshLabel->setObjectName(QString::fromUtf8("IsoThreshLabel"));

        verticalLayout_2->addWidget(IsoThreshLabel);

        SectionLabel = new QLabel(FEAInfoDlg);
        SectionLabel->setObjectName(QString::fromUtf8("SectionLabel"));

        verticalLayout_2->addWidget(SectionLabel);


        horizontalLayout_2->addLayout(verticalLayout_2);


        verticalLayout_4->addLayout(horizontalLayout_2);

        DirGroup = new QGroupBox(FEAInfoDlg);
        DirGroup->setObjectName(QString::fromUtf8("DirGroup"));
        verticalLayout = new QVBoxLayout(DirGroup);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        DirMaxRadio = new QRadioButton(DirGroup);
        DirMaxRadio->setObjectName(QString::fromUtf8("DirMaxRadio"));

        horizontalLayout->addWidget(DirMaxRadio);

        DirXRadio = new QRadioButton(DirGroup);
        DirXRadio->setObjectName(QString::fromUtf8("DirXRadio"));

        horizontalLayout->addWidget(DirXRadio);

        DirYRadio = new QRadioButton(DirGroup);
        DirYRadio->setObjectName(QString::fromUtf8("DirYRadio"));

        horizontalLayout->addWidget(DirYRadio);

        DirZRadio = new QRadioButton(DirGroup);
        DirZRadio->setObjectName(QString::fromUtf8("DirZRadio"));

        horizontalLayout->addWidget(DirZRadio);


        verticalLayout->addLayout(horizontalLayout);


        verticalLayout_4->addWidget(DirGroup);

        FEAInfoLabel = new QLabel(FEAInfoDlg);
        FEAInfoLabel->setObjectName(QString::fromUtf8("FEAInfoLabel"));
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(FEAInfoLabel->sizePolicy().hasHeightForWidth());
        FEAInfoLabel->setSizePolicy(sizePolicy);
        FEAInfoLabel->setAlignment(Qt::AlignLeading|Qt::AlignLeft|Qt::AlignTop);
        FEAInfoLabel->setWordWrap(true);

        verticalLayout_4->addWidget(FEAInfoLabel);

        horizontalLayout_4 = new QHBoxLayout();
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        DoneButton = new QPushButton(FEAInfoDlg);
        DoneButton->setObjectName(QString::fromUtf8("DoneButton"));

        horizontalLayout_4->addWidget(DoneButton);


        verticalLayout_4->addLayout(horizontalLayout_4);


        retranslateUi(FEAInfoDlg);

        QMetaObject::connectSlotsByName(FEAInfoDlg);
    } // setupUi

    void retranslateUi(QWidget *FEAInfoDlg)
    {
        FEAInfoDlg->setWindowTitle(QCoreApplication::translate("FEAInfoDlg", "FEA Info", nullptr));
        ViewTypeLabel->setText(QCoreApplication::translate("FEAInfoDlg", "View Mode", nullptr));
        DefLabel->setText(QCoreApplication::translate("FEAInfoDlg", "Deflection", nullptr));
        IsoThreshLabel->setText(QCoreApplication::translate("FEAInfoDlg", "Iso Threshhold", nullptr));
        SectionLabel->setText(QCoreApplication::translate("FEAInfoDlg", "Section Height", nullptr));
        DirGroup->setTitle(QCoreApplication::translate("FEAInfoDlg", "View Component", nullptr));
        DirMaxRadio->setText(QCoreApplication::translate("FEAInfoDlg", "Max", nullptr));
        DirXRadio->setText(QCoreApplication::translate("FEAInfoDlg", "X", nullptr));
        DirYRadio->setText(QCoreApplication::translate("FEAInfoDlg", "Y", nullptr));
        DirZRadio->setText(QCoreApplication::translate("FEAInfoDlg", "Z", nullptr));
        FEAInfoLabel->setText(QCoreApplication::translate("FEAInfoDlg", "FEA Info", nullptr));
        DoneButton->setText(QCoreApplication::translate("FEAInfoDlg", "Finished Analyzing", nullptr));
    } // retranslateUi

};

namespace Ui {
    class FEAInfoDlg: public Ui_FEAInfoDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VFEAINFO_H
