#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
# Base code provided by Kovid Goyal (Calibre API Documentation)

__license__   = 'GPL v3'
__copyright__ = '2022, Katarina Tretter <kft3635@rit.edu>'
__docformat__ = 'restructuredtext en'

from qt.core import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton

from calibre.utils.config import JSONConfig

import os
from calibre.constants import iswindows
from calibre.gui2 import choose_files

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/book_editor')

# Set defaults
prefs.defaults['ebook_file_path'] = "file path"


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.path = QLabel('File Path')
        self.l.addWidget(self.path)

        self.open_external_button = QPushButton(
            'Text External Tool', self)
        self.open_external_button.clicked.connect(self.open_external)
        self.l.addWidget(self.open_external_button)

        self.save_settings_button = QPushButton(
            'Save Settings', self)
        self.save_settings_button.clicked.connect(self.save_settings)
        self.l.addWidget(self.save_settings_button)

    def open_external(self):
        app_path = None

        apps = choose_files(None, 'open with dialog', 'Select the application to execute for this format', all_files=True, select_only_single_file=True)
        if not apps:
            return
        app_path = apps[0]
        if iswindows:
            app_path = os.path.normpath(app_path)
        prefs['ebbok_file_path'] = app_path
        self.path.setText(app_path)

    def save_settings(self):
        prefs['ebook_file_path'] = self.path.text()
