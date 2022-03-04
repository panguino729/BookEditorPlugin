#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
# Base code provided by Kovid Goyal (Calibre API Documentation)

__license__   = 'GPL v3'
__copyright__ = '2022, Katarina Tretter <kft3635@rit.edu>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

#---------IMPORTS---------
from functools import partial
from qt.core import QTimer

#---------FROM JIM MILLER AND BENJAMIN PETERSON---------

import functools
import itertools
import operator
import sys
import types

# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)

if PY3:
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes

    MAXSIZE = sys.maxsize
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str

    if sys.platform.startswith("java"):
        # Jython always uses 32 bits.
        MAXSIZE = int((1 << 31) - 1)
    else:
        # It's possible to have sizeof(long) != sizeof(Py_ssize_t).
        class X(object):

            def __len__(self):
                return 1 << 31
        try:
            len(X())
        except OverflowError:
            # 32-bit
            MAXSIZE = int((1 << 31) - 1)
        else:
            # 64-bit
            MAXSIZE = int((1 << 63) - 1)
        del X


# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.book_editor.main import DemoDialog

class BookEditor(InterfaceAction):

    name = 'BookEditorPlugin'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('Book Editor Plugin', None,
            'Run the Book Editor Plugin', None)

    accepts_drops = True

    def genesis(self):
        # This method is called once per plugin, do initial setup here

        # Set the icon for this interface action
        # The get_icons function is a builtin function defined for all your
        # plugin code. It loads icons from the plugin zip file. It returns
        # QIcon objects, if you want the actual data, use the analogous
        # get_resources builtin function.
        #
        # Note that if you are loading more than one icon, for performance, you
        # should pass a list of names to get_icons. In this case, get_icons
        # will return a dictionary mapping names to QIcons. Names that
        # are not found in the zip file will result in null QIcons.
        icon = get_icons('images/icon.png')

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        # The base plugin object defined in __init__.py
        base_plugin_object = self.interface_action_base_plugin
        # Show the config dialog
        # The config dialog can also be shown from within
        # Preferences->Plugins, which is why the do_user_config
        # method is defined on the base plugin class
        do_user_config = base_plugin_object.do_user_config

        # self.gui is the main calibre GUI. It acts as the gateway to access
        # all the elements of the calibre user interface, it should also be the
        # parent of the dialog
        d = DemoDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()

    def apply_settings(self):
        from calibre_plugins.book_editor.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

    #---------CODE FROM JIM MILLER---------
    # Code from Jim Miller https://github.com/JimmXinu/FanFicFare/blob/main/calibre-plugin/fff_plugin.py
    # fucntion that handles what happens on enter
    def accept_enter_event(self, event, mime_data):
        if mime_data.hasFormat("application/calibre+from_library") or \
                mime_data.hasFormat("text/plain") or \
                mime_data.hasFormat("text/uri-list"):
            print('true')
            return True

        return False

    # accepts first part of drag/drop and calls next function
    def accept_drag_move_event(self, event, mime_data):
        return self.accept_enter_event(event, mime_data)

    # the drop event
    def drop_event(self, event, mime_data):

        dropped_ids=None
        urllist=[]

        libmime = 'application/calibre+from_library'
        print ("mime_data.data(libmim).data(): {}".format(mime_data.data(libmime).data()))

        #if mime_data.hasFormat(libmime):
        #    print("success")
        #    dropped_ids = [ int(x) for x in self.ensure_text(mime_data.data(libmime).data()).split() ]
        if mime_data.hasFormat(libmime):
            print("success")
            dropped_ids = [ int(x) for x in mime_data.data(libmime).data().split() ]

        if urllist or dropped_ids:
            QTimer.singleShot(1, partial(self.do_drop,
                                         dropped_ids=dropped_ids,
                                         urllist=urllist))
            print ('QTimer true')
            return True

        return False

    # funtion to call when dropping
    def do_drop(self,dropped_ids=None,urllist=None):
        # shouldn't ever be both.
        if dropped_ids:
            #self.update_dialog(False,dropped_ids)
            print('dropped ids')

    #-----HELPER FUNCTIONS---------
    # ensure the input is actually text, decode it if not, or throw an error
    def ensure_text(s, encoding='utf-8', errors='strict'):
        if isinstance(s, binary_type):
            return s.decode(encoding, errors)
        elif isinstance(s, text_type):
            return s
        else:
            raise TypeError("not expecting type '%s'" % type(s))

    # update the window popup with the book
    def update_dialog(self,checked,id_list=None,extraoptions={}):
        if not self.is_library_view():
            print('Cannot Update Books from Device View')
            return

        if not id_list:
            id_list = self.gui.library_view.get_selected_ids()

        if len(id_list) == 0:
            print('No Selected Books to Update')
            return

        self.check_valid_collision(extraoptions)

        db = self.gui.current_db
        books = [ self.make_book_id_only(x) for x in id_list ]

        for j, book in enumerate(books):
            book['listorder'] = j


    # basic book, plus calibre_id.  Assumed bad until proven
    # otherwise.
    def make_book_id_only(self, idval):
        book = self.make_book()
        book['good'] = False
        book['calibre_id'] = idval
        return book