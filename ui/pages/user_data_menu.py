"""
Custom page for data filling.
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QTextEdit, QLabel, QDateEdit

class UserData(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout(self)
        name_label = QLabel("Name")
        name_label.setAlignment(Qt.AlignRight)
        name_edit = QTextEdit()
        name_edit.setFixedHeight(25)

        last_name_label = QLabel("Last Name")
        last_name_label.setAlignment(Qt.AlignRight)
        last_name_edit = QTextEdit()
        last_name_edit.setFixedHeight(25)

        birthday_label = QLabel("Date of birth")
        birthday_edit = QDateEdit()

        social_security_label = QLabel("Social Secutiry number")
        social_security_label.setAlignment(Qt.AlignRight)
        social_security_nb = QTextEdit()
        social_security_nb.setFixedHeight(25)

        layout.addWidget(name_label, 0, 0)
        layout.addWidget(name_edit, 0, 1)
        layout.addWidget(last_name_label, 0, 2)
        layout.addWidget(last_name_edit, 0, 3)
        layout.addWidget(birthday_label, 1, 0)
        layout.addWidget(birthday_edit, 1, 1, 1, 1)
        layout.addWidget(social_security_label, 2, 0)
        layout.addWidget(social_security_nb, 2, 1)

        layout.setHorizontalSpacing(4)

        self.setLayout(layout)

