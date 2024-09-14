"""
Custom page for data filling.
"""

from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QTextEdit,
    QLabel,
    QDateEdit,
    QRadioButton,
)


class UserData(QWidget):
    def __init__(self):
        super().__init__()

        # layout = QGridLayout(self)
        # name_label = QLabel("Name")
        # name_label.setAlignment(Qt.AlignRight)
        # name_edit = QTextEdit()
        # name_edit.setFixedHeight(25)

        # last_name_label = QLabel("Last Name")
        # last_name_label.setAlignment(Qt.AlignRight)
        # last_name_edit = QTextEdit()
        # last_name_edit.setFixedHeight(25)

        # birthday_label = QLabel("Date of birth")
        # birthday_edit = QDateEdit()

        # social_security_label = QLabel("Social Secutiry number")
        # social_security_label.setAlignment(Qt.AlignRight)
        # social_security_nb = QTextEdit()
        # social_security_nb.setFixedHeight(25)

        # layout.addWidget(name_label, 0, 0)
        # layout.addWidget(name_edit, 0, 1)
        # layout.addWidget(last_name_label, 0, 2)
        # layout.addWidget(last_name_edit, 0, 3)
        # layout.addWidget(birthday_label, 1, 0)
        # layout.addWidget(birthday_edit, 1, 1, 1, 1)
        # layout.addWidget(social_security_label, 2, 0)
        # layout.addWidget(social_security_nb, 2, 1)

        # layout.setHorizontalSpacing(4)

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setObjectName("gridLayout")
        gridLayout.setRowStretch(20, 1)
        label_3 = QLabel()
        label_3.setObjectName("label_3")
        label_3.setText("Nom")
        gridLayout.addWidget(label_3, 4, 0, 1, 1)
        label = QLabel()
        label.setEnabled(True)
        label.setAlignment(Qt.AlignRight)
        label.setLayoutDirection(Qt.LeftToRight)
        label.setObjectName("label")
        label.setText("Prénom")
        gridLayout.addWidget(label, 0, 0, 1, 1)
        label_2 = QLabel()
        label_2.setObjectName("label_2")
        label_2.setText("Sexe")
        gridLayout.addWidget(label_2, 0, 3, 1, 1)
        self.textEdit_2 = QTextEdit()
        self.textEdit_2.setObjectName("textEdit_2")
        gridLayout.addWidget(self.textEdit_2, 0, 4, 1, 1)
        self.radioButton = QRadioButton()
        self.radioButton.setObjectName("radioButton")
        gridLayout.addWidget(self.radioButton, 3, 1, 1, 1)
        self.textEdit = QTextEdit()
        self.textEdit.setObjectName("textEdit")
        gridLayout.addWidget(self.textEdit, 0, 1, 1, 2)
        self.radioButton_2 = QRadioButton()
        self.radioButton_2.setObjectName("radioButton_2")
        gridLayout.addWidget(self.radioButton_2, 3, 2, 1, 1)
        label_4 = QLabel()
        label_4.setObjectName("label_4")
        label_4.setText("Date de naissance")
        gridLayout.addWidget(label_4, 3, 0, 1, 1)
        label_5 = QLabel()
        label_5.setObjectName("label_5")
        label_5.setText("N° de Sécurité Sociale")
        gridLayout.addWidget(label_5, 5, 0, 1, 1)
        self.dateEdit = QDateEdit()
        self.dateEdit.setObjectName("dateEdit")
        gridLayout.addWidget(self.dateEdit, 4, 1, 1, 2)
        self.textEdit_3 = QTextEdit()
        self.textEdit_3.setObjectName("textEdit_3")
        gridLayout.addWidget(self.textEdit_3, 5, 1, 1, 2)

        self.setLayout(gridLayout)
        self.resize(620, 460)
