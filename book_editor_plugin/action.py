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
from calibre_plugins.book_editor.config import prefs

from functools import partial
from qt.core import QApplication, QMenu, QTimer

from calibre.ebooks.metadata import MetaInformation
from calibre.ebooks.metadata.meta import get_metadata as calibre_get_metadata

import os, subprocess
from calibre.constants import iswindows, isosx, DEBUG
from calibre.gui2 import error_dialog

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

    # ---------APP ARGS---------
    arg_list = []
    arg_list.append("open")

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

        self.is_library_selected = True

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
        else:
            self.is_library_selected = False

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
            books = self.update_dialog(False,dropped_ids)
            print('dropped ids')
            self.open_with(books, prefs['ebook_file_path'], None)

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
        #if not self.is_library_view():
        #    print('Cannot Update Books from Device View')
        #    return

        if not id_list:
            id_list = self.gui.library_view.get_selected_ids()

        if len(id_list) == 0:
            print('No Selected Books to Update')
            return

        #self.check_valid_collision(extraoptions)

        db = self.gui.current_db
        books = [ self.make_book_id_only(x) for x in id_list ]
        
        self.populate_book_from_calibre_id(books[0], db)

        print ("Book: ", books[0]['title'])

        for j, book in enumerate(books):
            book['listorder'] = j

        print ('end update_dialog')
        return books
        

    # basic book, plus calibre_id.  Assumed bad until proven
    # otherwise.
    def make_book_id_only(self, idval):
        book = self.make_book()
        book['good'] = False
        book['calibre_id'] = idval
        return book

    # Can't make book a class because it needs to be passed into the
    # bg jobs and only serializable things can be.
    def make_book(self):
        book = {}
        book['title'] = 'Unknown'
        book['author_sort'] = book['author'] = ['Unknown'] # list
        book['comments'] = '' # note this is the book comments.

        book['good'] = True
        book['status'] = 'Bad'
        book['showerror'] = True # False when NotGoingToDownload is
                                 # not-overwrite / not-update / skip
                                 # -- what some would consider 'not an
                                 # error'
        book['calibre_id'] = None
        book['begin'] = None
        book['end'] = None
        book['comment'] = '' # note this is a comment on the d/l or update.
        book['url'] = ''
        book['site'] = ''
        book['series'] = ''
        book['added'] = False
        book['pubdate'] = None
        book['publisher'] = None
        return book

    # populate book data based in calibre_id
    def populate_book_from_calibre_id(self, book, db=None):
        mi = db.get_metadata(book['calibre_id'], index_is_id=True)
        book['good'] = True
        self.populate_book_from_mi(book,mi)

    # populate book data from mi
    def populate_book_from_mi(self,book,mi):
        book['title'] = mi.title
        book['author'] = mi.authors
        book['author_sort'] = mi.author_sort
        if hasattr(mi,'publisher'):
            book['publisher'] = mi.publisher
        if hasattr(mi,'path'):
            book['path'] = mi.path
        if hasattr(mi,'id'):
            book['calibre_id'] = mi.id

    #---------CODE FROM GRANT DRAKE---------
    # Base code from Grant Drake https://www.mobileread.com/forums/showthread.php?t=118761
    def open_with(self, book, external_app_path, app_args):
        if not self.is_library_selected:
            return
        row = self.gui.library_view.currentIndex()
        if not row.isValid():
            return error_dialog(self.gui, 'Cannot open with', 'No book selected', show=True)
        db = self.gui.library_view.model().db
        book_id = self.gui.library_view.model().id(row)

        # Confirm format selected in formats
        try:
            path_to_book = db.format_abspath(book_id, 'RTF', index_is_id=True)
        except:
            path_to_book = None

        if not path_to_book:
            return error_dialog(self.gui, 'Cannot open: ' + book[0]['title'],
                    'No format available.',
                    show=True)

        # Confirm we have defined an application for that format in tweaks
        if external_app_path is None:
            return error_dialog(self.gui, 'Cannot open with',
                    'Path not specified for this format in your configuration.',
                    show=True)
        self.launch_app(external_app_path, app_args, path_to_book, book)

    def launch_app(self, external_app_path, app_args, path_to_file, book, wrap_args=True):
        external_app_path = os.path.expandvars(external_app_path)
#         path_to_file = path_to_file.encode('utf-8')
        external_app_path = prefs['ebook_file_path']
        if DEBUG:
            print('Open: ', external_app_path, '(file): ', path_to_file, ' (args): ', app_args)

        if isosx:
            # For OSX we will not support optional command line arguments currently
            if external_app_path.lower().endswith(".app"):
                args = 'open -a "%s" "%s"' % (external_app_path, path_to_file)
            else:
                args = '"%s" "%s"' % (external_app_path, path_to_file)
            subprocess.Popen(args, shell=True)

        else:
            # For Windows/Linux merge any optional command line args with the app/file paths
            app_args_list = []
            if app_args:
                app_args_list = app_args.split(' ')
            app_args_list.insert(0, external_app_path)

            # ---------ARGS---------
            arg = '%s open "%s" "%s"' % (external_app_path, path_to_file, book[0]['title'])

            if iswindows:
                # Add to the recently opened files list to support windows jump lists etc.
                from calibre.gui2 import add_to_recent_docs
                add_to_recent_docs(path_to_file)

                DETACHED_PROCESS = 0x00000008
                print('About to run a command:', arg)
                clean_env = dict(os.environ)
                del clean_env['PATH']
                subprocess.Popen(arg, creationflags=DETACHED_PROCESS, env=clean_env)

            else: #Linux
                clean_env = dict(os.environ)
                clean_env['LD_LIBRARY_PATH'] = ''
                subprocess.Popen(app_args_list, env=clean_env)
        