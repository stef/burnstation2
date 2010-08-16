#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2009 Daniel Nögel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------

import gtk
import sys
import os
from threading import Thread
import urllib2
import time
import tarfile
import shutil
import gobject

from modules import functions


if not os.path.exists(os.path.join(functions.install_dir(), "plugins", "PVC", "PVC.glade")):
    print ("PVC.glade wasn't found. Will not load PVC")
    raise Exception


def threaded(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper

#@threaded
class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama

        self.home = functions.preparedirs()

        self.firstrun = False
        self.release = None
        self.file = None
        self.remote_version = None
        self.curpage = "http://xn--ngel-5qa.de/pvc.html"

        self.progress = 0

        self.pyjama.Events.connect_event("alldone", self.ev_alldone)
        self.pyjama.Events.connect_event("alldone", self.ev_firstrun)

    def create_dialog(self):
        if not os.path.exists(os.path.join(functions.install_dir(), "plugins", "PVC", "PVC.glade")):
            print ("PVC.glade wasn't found.")
        else:
#            ##gtk.gdk.threads_enter()##
            xml = gtk.glade.XML(os.path.join(functions.install_dir(), "plugins", "PVC", "PVC.glade"))
            self.dialog = xml.get_widget('dialog1')
            self.dialog.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
            self.dialog.set_title("Pyjama Version Control")
            self.dialog.connect('delete_event', self.cb_quit)
            self.textview = xml.get_widget('textview1')
            self.buffer = self.textview.get_buffer()
            self.bOK = xml.get_widget('button1')
            self.bOK.connect("clicked", self.cb_button_clicked, "ok")

            self.bUpdate = xml.get_widget('button2')
            self.bUpdate.connect("clicked", self.cb_button_clicked, "update")
            self.bPermissions = xml.get_widget('button3')
            self.bPermissions.connect("clicked", self.cb_button_clicked, "permissions")
#            ##gtk.gdk.threads_leave()##
            self.change_stock_button_text(self.bPermissions, "      Set\npermissions")
            self.change_stock_button_text(self.bUpdate, "Update")

            if self.check_permissions() is not None and not os.access(functions.install_dir(), os.W_OK):
#                ##gtk.gdk.threads_enter()##
                self.bPermissions.show()
#                ##gtk.gdk.threads_leave()##
            else:
#                ##gtk.gdk.threads_enter()##
                self.bPermissions.hide()
#                ##gtk.gdk.threads_leave()##
#            ##gtk.gdk.threads_enter()##
            self.buffer.create_tag("monospace", font="courier")
#            ##gtk.gdk.threads_leave()##

    def show(self, widget=None):
#        gtk.gdk.threads_enter()##
        self.dialog.run()
        gtk.gdk.threads_leave()##
        self.dialog.destroy()

    def change_stock_button_text(self, button, text):
        ##gtk.gdk.threads_enter()##
        alignment = button.get_children()[0]
        hbox = alignment.get_children()[0]
        image, label = hbox.get_children()
        label.set_markup(text)
        ##gtk.gdk.threads_leave()##

    def show_progress_dialog(self):
        if not os.path.exists(os.path.join(functions.install_dir(), "plugins", "PVC", "progressdialog.glade")):
            print ("progressdialog.glade wasn't found.")
        else:
#            ##gtk.gdk.threads_enter()##
            xml = gtk.glade.XML(os.path.join(functions.install_dir(), "plugins", "PVC", "progressdialog.glade"))
            self.progressdialog = xml.get_widget('dialog1')
            self.progressdialog.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
            self.progressdialog.set_title("Downloading Pyjama")
            self.progressbar = xml.get_widget('progressbar1')
            self.progressdialog.show()
            self.pyjama.window.do_events()
#            ##gtk.gdk.threads_leave()##
            

    ## react on button click events
    def cb_button_clicked(self, widget, btn):
        #
        # ok
        #
        if btn == "ok":
            self.dialog.destroy()
        #
        # Download pyjama, untar and install if (if possible)
        #
        elif btn == "update":
            #
            # Check Permissions
            #
            if not os.access(functions.install_dir(), os.W_OK):
                username = os.getenv("LOGNAME", "USERNAME")
#                ##gtk.gdk.threads_enter()##
                dia = gtk.MessageDialog(self.pyjama.window, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK, message_format="")

                dia.set_markup(_("You have no write permission for '%s'\nIf you want to use the auto update funcionallity, please make sure, that you have write permission for that folder.\n\nIn order to set those permissions, you could run:\n<b>chown -R %s %s</b>\nas root." %  (functions.install_dir(), username, functions.install_dir())))
                result = dia.run()
#                ##gtk.gdk.threads_leave()##

                dia.destroy()

                return

#            ##gtk.gdk.threads_enter()##
            self.dialog.hide()
#            ##gtk.gdk.threads_leave()##
            self.show_progress_dialog()

            #
            # Download and extract
            #
            local_file = os.path.join(self.home, "temp.tar.gz")
            ret = self.download(self.file, local_file)
            extracted_archive = os.path.join(self.home, "extracted_archive")
#            ##gtk.gdk.threads_enter()##
            self.progressdialog.hide()
            self.pyjama.window.do_events()
#            ##gtk.gdk.threads_leave()##

            if ret is None:
                th = tarfile.open(name=local_file, mode='r:gz')
                if os.path.exists(extracted_archive):
                    shutil.rmtree(extracted_archive)
                try:
                    th.extractall(extracted_archive)
                except Exception, inst:
#                    ##gtk.gdk.threads_enter()##
                    self.pyjama.Events.raise_event("error", inst, "Error extracting the archive")
#                    ##gtk.gdk.threads_leave()##
                    return

                filelist = os.listdir(extracted_archive)
                if len(filelist)> 0:
                    pyjamafiles = os.path.join(extracted_archive, filelist[0], "src")
#                    shutil.move(pyjamafiles, os.path.join(self.home, "updated_version"))
                    try:
                        if ".bzr" in os.listdir(functions.install_dir()):
#                            ##gtk.gdk.threads_enter()##
                            self.pyjama.Events.raise_event("error", None, "Error - won't copy files to branched folder\nPlease install pyjama first and run that installed version or update your branch by running 'bzr pull'")
#                            ##gtk.gdk.threads_leave()## 
                            if os.path.exists(extracted_archive):
                                shutil.rmtree(extracted_archive)
                            if os.path.exists(local_file):
                                os.remove(local_file)
                            return
                        else:
                            # Using a modified version of copytree
                            # and copy due to some bugs(?) in these
                            # functions
                            # have a look at the bottom of the page
                            ret = copytree(pyjamafiles, functions.install_dir())
                            if ret is not None:
#                                ##gtk.gdk.threads_enter()##
                                self.pyjama.Events.raise_event("error", None, "Error copying the extracted files to '%s' - check the permissions of that folder"%functions.install_dir())
#                                ##gtk.gdk.threads_leave()##
                            else:
#                                ##gtk.gdk.threads_enter()##
                                dia = gtk.MessageDialog(self.pyjama.window, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_YES_NO, message_format="Your pyjama version has been updated.\nDo you want to restart pyjama now? [recommended]")
                                result = dia.run()
#                                ##gtk.gdk.threads_leave()##
                                dia.destroy()
                                if result == gtk.RESPONSE_YES:
                                    if os.path.exists(extracted_archive):
                                        shutil.rmtree(extracted_archive)
                                    if os.path.exists(local_file):
                                        os.remove(local_file)
                                    os.system("pyjama &")
                                    gtk.main_quit()
                    except Exception, inst:
#                        ##gtk.gdk.threads_enter()##
                        self.pyjama.Events.raise_event("error", inst, "Error copying the extracted files to '%s' - check the permissions of that folder"%functions.install_dir())
#                        ##gtk.gdk.threads_leave()##
                        if os.path.exists(extracted_archive):
                            shutil.rmtree(extracted_archive)
                        if os.path.exists(local_file):
                            os.remove(local_file)
                        return
                else:
#                    ##gtk.gdk.threads_enter()##
                    self.pyjama.Events.raise_event("error", None, "Archive should have been extracted to '%s' but that folder is empty" % extracted_archive )
#                    ##gtk.gdk.threads_leave()##
            if os.path.exists(extracted_archive):
                shutil.rmtree(extracted_archive)
            if os.path.exists(local_file):
                os.remove(local_file)
        #
        # Set permissions
        #
        elif btn == "permissions":
            ret = self.check_permissions()
            if ret != False:
                app, username = ret

                ret = os.system("%s 'chown -R %s %s'" % (app, username, functions.install_dir()))
                if ret != 0:
                    # error
                    message = "An error occured, could not set permissions for '%s'" % functions.install_dir()
                    type = gtk.MESSAGE_WARNING
                elif not os.access(functions.install_dir(), os.W_OK):
                    message = "There was no actual error but you have still no permission to write '%s'" % functions.install_dir()
                    type = gtk.MESSAGE_WARNING
                else:
                    message = "Permissions successfully set - you can now try to auto-update Pyjama"
                    type = gtk.MESSAGE_INFO
#                    ##gtk.gdk.threads_enter()##
                    dia = gtk.MessageDialog(self.pyjama.window, flags=gtk.DIALOG_MODAL, type=type, buttons=gtk.BUTTONS_OK, message_format=message)
                    result = dia.run()
#                    ##gtk.gdk.threads_leave()##
                    dia.destroy()

    def check_permissions(self):
        sudo_gtk = os.path.join("/", "usr", "bin", "gksudo")
        sudo_kde = os.path.join("/", "usr", "bin", "kdesudo")
        app = None
        if os.path.exists(sudo_kde):
            app = sudo_kde
        elif os.path.exists(sudo_gtk):
            app = sudo_gtk

        username = os.getenv("LOGNAME", None)

        if username is not None and app is not None:
            return app, username
        else:
            return False

    def ev_firstrun(self):
        self.firstrun = True

    ## whatever
    def ev_alldone(self):
        menu = self.pyjama.window.menubar
        entry = menu.append_entry(menu.get_rootmenu("Extras"), "%s (PVC)"  % _("Show Autoupdater"), "pvc")
        entry.connect("activate", self.get_data)
        menu.set_item_image(entry, gtk.STOCK_REFRESH)
#        ##gtk.gdk.threads_enter()##
#        ##gtk.gdk.threads_leave()##

        gobject.timeout_add(1000, self.get_data)
        

    ## set textview
    def set_text(self, txt):
        ##gtk.gdk.threads_enter()##
        self.buffer.set_text("\n%s" % txt)
        start, end = self.buffer.get_bounds()
        self.buffer.apply_tag_by_name("monospace", start, end)
        ##gtk.gdk.threads_leave()##

#    ## start get_data threaded
#    def load_news(self):
#        thr = Thread(target = self.get_data, args = ())
#        thr.start()
##        self.get_data()
#        return False

    ## get PVC new, parse it and show it
    def get_data(self, ev=None):
        while self.pyjama.need_attention:
            sys.stdout.write(".")
            sys.stdout.flush()
            return True
        self.pyjama.need_attention = True
        print("Checking for PVC news")
        text = self.get_content(self.curpage)
        if text == None:
            print "An error occured: will not load PVC"
            self.pyjama.need_attention = False
            return False
        print("done")

        self.remote_version = self.read_tag(text, "version") # current version of pyjama
        self.release = self.read_tag(text, "release") # id of pvc-new
        self.file = self.read_tag(text, "file") # url of the latest version
        text = self.read_tag(text, None, "<!--START-->", "<!--END-->")
        localver = self.pyjama.version

        self.create_dialog()
        self.set_text(text)

        run = False
        if ev is not None:
            run = True

        if not "noupdate" in sys.argv and not self.firstrun:
            # show if a new message is available
            if not self.pyjama.settings.option_exists("PVC", "release"):
                self.pyjama.settings.set_value("PVC", "RELEASE", self.release)
                run = True
            elif int(self.pyjama.settings.get_value("PVC", 'release', 0)) < int(self.release):
                self.pyjama.settings.set_value("PVC", "RELEASE", self.release)
                run = True

        # show if a new version is available
        if self.remote_version > localver and self.file is not None:
            ##gtk.gdk.threads_enter()##
            self.bUpdate.show()
            ##gtk.gdk.threads_leave()##
            run = True
        else:
            ##gtk.gdk.threads_enter()##
            self.bUpdate.hide()
            self.bPermissions.hide()
            ##gtk.gdk.threads_leave()##

        if "pvc" in sys.argv:
            run = True

        if run:
            self.show()
        self.pyjama.need_attention = False

        return False

    ## get content of an url
    def get_content(self, url):
        try:
            content = urllib2.urlopen(url)
        except urllib2.URLError:
            print ("Error reading %s" %url)
            return None

        content = content.read()
        return content

    ## Get content of a tag
    def read_tag(self, text, tag=None, start=None, end=None):
        # this is kind of ugly, but i did not like the regex....
        if start is None and end is None:
            start = "<%s>" %tag 
            end = "</%s>" %tag
        start_pos = text.find(start) + len(start)
        end_pos = text.find(end)
        return text[start_pos:end_pos].strip()

    #
    # Download related methodes
    #
    def set_bar(self): #, fraction=None, text=""):
#        ##gtk.gdk.threads_enter()##
        self.progressbar.set_fraction(self.progress/100)
#        ##gtk.gdk.threads_leave()##
#        else:
#            pass
###            self.progressbar.pulse()
##        self.progressbar.set_text(text)
        self.pyjama.window.do_events()

        return True

    ## Start a download
    # @param self
    # @param url Url of the file to download
    # @param local_filename Local filename
    def download(self, url, local_filename):

        try:

            local_file = open(local_filename, "wb")
            stream, length = self.create_download(url, proxy=None)

            if not length:
                length = "unknown"
            else:
                length = int(length)
#            print "Lade %s (%s bytes).." % (url, length)
            curbyte = 0.0

            content = stream.read(1024)
            local_file.write(content)
            curbyte += len(content)

            milli= time.time()*1000

            while content:
                content = stream.read(1024)
                curbyte += len(content)

                if length != "unknown":
                    if time.time()*1000 > milli + 100: 
                        milli = time.time() *1000
                        self.progress = 100*curbyte/length
#                        self.set_bar(self.progress/100, "%d%%"% self.progress)
                        self.set_bar()
#                        print self.progress
                    output =  "%s: %.02f/%.02f kb (%d%%)" % ( local_filename, curbyte/1024.0, length/1024.0, 100*curbyte/length)
                    # remove last line
                    sys.stdout.write('\r')
                    sys.stdout.flush()

                    # write new line
                    sys.stdout.write(output)

                local_file.write(content)
            stream.close()
            local_file.close()
#            self.set_bar(1.0, "Done")
        except Exception, inst:
#            self.dialog.hide()
            print "Fehler beim Laden von %s: %s" % (url, inst)
            self.pyjama.Events.raise_event("error", inst, "Fehler beim Laden von %s" % url)
            return -1

    ## Opens a download stream
    # @param self The Object Pointer
    # @param url Url of the ressource to download
    # @param proxy Default=None - Proxy to use for download
    # @return: stream, filename as tuple
    def create_download(self, url, proxy = None):
        proxy_handler = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_handler)
        stream = opener.open(url)
        filename=stream.info().getheader("Content-Length")

        if not filename:
            filename = "temp"

        return (stream, filename)

    def cb_quit(self, widget, event):
        return True

def copy(src, dst):
    """Copy data and mode bits ("cp src dst").

    The destination may be a directory.

    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    shutil.copyfile(src, dst)

def copytree(src, dst, symlinks=0):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    Error are reported to standard output.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.mkdir(dst)
    for name in names:
        if not ".pyc" in name:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    copytree(srcname, dstname, symlinks)
                else:
                    copy(srcname, dstname)
                # XXX What about devices, sockets etc.?
            except (IOError, os.error), why:
                print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why)) 
                return -1


