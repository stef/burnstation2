#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2008 Daniel Nögel
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

######################################################################
#                                                                    #
#                     Some default Layouts                           #
#                                                                    #
######################################################################    
#
# Star Layout
#

import gtk
import os
from time import strftime, gmtime, time, sleep
from math import floor, ceil
from modules import clWidgets, clThreadedDownload, clEntry

from modules import functions

import webbrowser

class StarLayout(gtk.Layout):

    def __init__(self, pyjama):
        self.pyjama = pyjama
        
        gtk.Layout.__init__(self)
        self.set_size(700,400)                
        
        # Some default values        
        self.results_per_page = 10
        self.cur_page = 1     

        self.ordering = "data"
        self.tag = "all"

        
        self.albuminfos={}    
        
        self.pyjama.Events.connect_event("scrolled_window_resized", self.ev_scrolled_window_resized)

        # might be obsolet
        self.pyjama.window.setcolor(self)

    ###################################################################
    #
    # get NUM top ORDER albums from Jamendo out of TAG
    # RETURNS: dictionary
    #
    def top(self, ids, num = 10, order = "tag", page=1, tag="all"):
        if tag == "all": 
            if self.pyjama.verbose:
                print ("Getting top %i ordered by '%s'") % (num, order)
            ret = self.pyjama.jamendo.query("artist_name+artist_idstr+artist_id+album_name+album_id+album_image+album_genre/album/json/?id=%s&order=%s_desc&n=%i&pn=%s" % (ids, order, num, page), self.pyjama.settings.get_value("JAMENDO", "CACHING_TIME_SHORT"))
        else:
            if self.pyjama.verbose:
                print ("Getting %i albums tagged '%s' ordered by '%s'") % (num, tag, order)
            ret = self.pyjama.jamendo.query("artist_name+artist_idstr+artist_id+album_name+album_id+album_image+album_genre/album/json/?id=%s&tag_idstr=%s&n=%i&pn=%s&order=%s_desc" % (ids, tag, num, page, order), self.pyjama.settings.get_value("JAMENDO", "CACHING_TIME_SHORT"))
        return ret

    def draw(self, num=None, mode="data", page=1, tag="all"):
#    def draw(self, data, data2, data3, data4):
#        num=data['num'], mode = data['mode'], page = data['page'], tag=data['tag']
        ids = self.pyjama.settings.get_value("STAR PLUGIN", "STARED ALBUMS", -1)
        if ids == -1: ids = 0
        # Checking if next / prev page are available
        self.check_next_possible(page, num)
        self.check_prev_possible(page)
        # Got to be fixed: Setting CBs in History- Mode
        # causes "changed" event, which destroys the
        # current history- session
        # Switched off HistoryForwart- Deletion,
        # as this seems to be the smaller issue
        self.pyjama.layouts.toolbars['star'].cbOrder.set_item(mode)
        show_tag = tag
        if tag == "all": show_tag = _("--all--")
        if not tag in self.pyjama.layouts.toolbars['star'].cbTags.modelist and tag != "all": 
            self.pyjama.layouts.toolbars['star'].cbTags.entry.set_text(tag.replace("+", " "))
        else:
            self.pyjama.layouts.toolbars['star'].cbTags.set_item(show_tag)            
        self.pyjama.layouts.toolbars['star'].cbResultsPerPage.set_item(num)
        # Setting the label
        if tag == "all":
            ids = self.pyjama.settings.get_value("STAR PLUGIN", "STARED ALBUMS", -1)
            if ids == -1:
                count = 0
            else:
                count = ids.count("+")*1.0
#            markup = self.pyjama.window.markuplbCaption.replace("TEXT", _("Show %i stared albums in '%s'") % (int(num), mode))
            txt = _("Show %i stared albums in '%s'") % (int(num), mode)
            self.pyjama.layouts.toolbars['star'].lCurPage.set_text(_("Page %i of %i") % (page, ceil(count/num)))
        else:
#            markup = self.pyjama.window.markuplbCaption.replace("TEXT", _("Show %i stared albums tagged '%s' ordered by '%s'") % (int(num), tag, mode))
            txt = _("Show %i stared albums tagged '%s' ordered by '%s'") % (int(num), tag, mode)
            self.pyjama.layouts.toolbars['star'].lCurPage.set_text(_("Page %i") % page)

        self.cur_page = page
#        self.pyjama.window.lbCaption.set_markup(markup)
        self.pyjama.window.LayoutInfo.set_text(txt)
        self.pyjama.window.LayoutInfo.set_image(os.path.join(functions.install_dir(), "images", "star.png"))

        if ids == 0 or ids == "": return

        if num==None:num=self.results_per_page
        for albuminfo in self.albuminfos:
            self.albuminfos[albuminfo].destroy()
        
        self.albuminfos = {}
        

        top = self.top(ids, num, mode, page, tag)
        if top == None:
            clWidgets.tofast(self.pyjama.window)
            return None
        elif top == -1:
            return None
        ## Again:
        ## 2 loops in order to
        ## first burst download
        ## and then create AlbumInfo
        counter = 0
        threads = {}
        for album in top:
            if self.pyjama.debug:
                print "(%i/%i)" % (counter + 1, len(top))
            # if more than 10 threads...
            if clThreadedDownload.threadLimiter(threads):
                print ("Waiting for threads (%i seconds)") % self.pyjama.settings.get_value("PERFORMANCE", "THREAD_WAIT")
                sleep(self.pyjama.settings.get_value("PERFORMANCE", "THREAD_WAIT"))
            threads[counter] = clThreadedDownload.Download(self.pyjama, album['album_image'], counter)
            threads[counter].start()
            counter += 1
        counter = 0
        for album in top:
            self.albuminfos[counter] = clWidgets.AlbumInfo(self.pyjama, album)
            self.albuminfos[counter].show()
            self.put(self.albuminfos[counter], counter, counter)
            counter += 1

        self.arrange_topoftheweek()
        self.show()
        
    def arrange_topoftheweek(self):
        if self.albuminfos == {}: return None
        width = self.pyjama.window.scrolledwindow_width
        hspace = 10
        vspacer = 10
        
        imgwidth = 110
        imgheight = 150
        
        starty = -10
        
        y = 0
        x = 0
        for counter in self.albuminfos:
            if ((x+1) * imgwidth) + hspace*(x+1) >= width:
                y += 1
                x = 0
            self.move(self.albuminfos[counter], (imgwidth * x) + hspace*(x+1), (vspacer*(y+1) + (y * imgheight))+starty)
            x += 1
        height = (y+1) * (imgheight + vspacer) +starty
        self.set_size(width-20,height+vspacer)

    # Possible Modi:
    #
    # rating, data, ratingmonth
    # date
    # downloaded, listened, starred, playlisted
    #

    def check_next_possible(self, page=None, rpp=None):
        if page == None: page = self.cur_page
        if rpp == None: rpp = self.results_per_page
        if page >= floor(self.pyjama.db.albums / rpp) - 2:
            self.pyjama.layouts.toolbars['star'].sbNextPage.set_sensitive(False)
        else:
            self.pyjama.layouts.toolbars['star'].sbNextPage.set_sensitive(True)

    def check_prev_possible(self, page=None):
        if page == None: page = self.cur_page
        if page == 1:
            self.pyjama.layouts.toolbars['star'].sbPrevPage.set_sensitive(False)
        else:
            self.pyjama.layouts.toolbars['star'].sbPrevPage.set_sensitive(True)
        
    def ev_scrolled_window_resized(self):
        #
        # Rearrange layout
        #
        self.arrange_topoftheweek()
    #
    # Actually this toolbar is just a hbox...
    #
    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['star']
            
            
            #
            # Toolbar
            #
            #self.ToolBar = gtk.VBox()
            #self.pack_end(self.ToolBar, False, True)

            #self.hbTop = gtk.HBox()
            #self.ToolBar.pack_end(self.hbTop, False, True,0)
            
            # ComboBoxes for TOP- View
            self.cbOrder = clWidgets.OrderCombo()
            self.cbOrder.connect("changed", self.cbOrder_changed)
            self.pack_start(self.cbOrder, False, True, 0)
#            self.cbOrder.show()

            # RESULTS PER PAGE
            self.cbResultsPerPage = clWidgets.ResultsPerPageCombo()
            self.cbResultsPerPage.connect("changed", self.cbResultsPerPage_changed)
            self.pack_start(self.cbResultsPerPage, False, True, 0)
            self.cbResultsPerPage.show()

            # Combo for Tags
            self.cbTags = clWidgets.TagsCombo(self.pyjama)
    #        self.cbTags.connect("key_press_event", self.cbTags_key_press_event)
    #        self.cbTags.set_events(gtk.gdk.KEY_PRESS_MASK)
            self.cbTags.connect("changed", self.cbTags_changed)
            self.cbTags.entry.connect("activate", self.cbTagsEntry_activate)
            self.pack_start(self.cbTags, False, True, 0)
            self.cbTags.show()

            #Export Button
            self.sbExportFavs = clWidgets.StockButton(gtk.STOCK_CONVERT)
            self.sbExportFavs.set_tooltip_text(_("Export stared Albums to Jamendo"))
            self.sbExportFavs.connect("clicked", self.on_sbExportFavs_clicked)
            self.pack_end(self.sbExportFavs, False, True, 0)
            self.sbExportFavs.show()

            # Page- Buttons:
            self.sbNextPage = clWidgets.StockButton(gtk.STOCK_GO_FORWARD)
            self.sbNextPage.set_tooltip_text(_("Next page"))
            self.sbNextPage.connect("clicked", self.on_sbNextPage_clicked)
            self.pack_end(self.sbNextPage, False, True, 0)
            self.sbNextPage.show()

            self.lCurPage = gtk.Label("")
            self.pack_end(self.lCurPage, False, True, 0)
            self.lCurPage.show()

            self.sbPrevPage = clWidgets.StockButton(gtk.STOCK_GO_BACK)
            self.sbPrevPage.set_tooltip_text(_("Previous page"))
            self.sbPrevPage.connect("clicked", self.on_sbPrevPage_clicked)
            self.sbPrevPage.set_sensitive(False)
            self.pack_end(self.sbPrevPage, False, True, 0)
            self.sbPrevPage.show()

            self.sbJumpToPage = clWidgets.StockButton(gtk.STOCK_JUMP_TO)
            self.sbJumpToPage.set_tooltip_text(_("Jump to page..."))
            self.sbJumpToPage.connect("clicked", self.on_sbJumpToPage_clicked)
            self.pack_end(self.sbJumpToPage, False, True, 0)
            self.sbJumpToPage.show()
            
#            self.show_all()
            
            
        #
        # Events
        #
        def on_sbExportFavs_clicked(self, ev):
            result = clEntry.input_box(title=_('Enter your Jamendo username'),
                message=_('Exporting stared albums to jamendo DOES NOT WORK automatically.\n \
                1) Visit jamendo.com and login with your default webbrowser\n \
                2) Enter your username in this box \n \
                Pyjama will now open any album you have stared in pyjama and which is not stared on jamendo.com.\n \
                3) Now you can star each album manually within your browser.'),
                default_text="USERNAME")
            if result is None:
                return None
                
            name = str(result).replace(" ", "+")
            
            self.pyjama.jamendo.set_ignore_cache(True)
            albums = self.pyjama.plugins.loaded['starred_albums'].import_stared_albums(name)
            stared = self.pyjama.settings.get_value("STAR PLUGIN", "STARED ALBUMS", "")
            stared = stared.split("+")[1:]

            open_uris = []

            try:
                for stared_album in stared:
                    if not int(stared_album) in albums:
                        uri = self.pyjama.settings.get_value("URLs", "ALBUM_URL").replace("URL", "%s" % stared_album)
                        open_uris.append(uri)
            except Exception, inst:
                print ("Fehler", inst)
                return

            dialog = gtk.MessageDialog(self.pyjama.window, \
                gtk.DIALOG_MODAL, \
                gtk.MESSAGE_QUESTION, \
                gtk.BUTTONS_YES_NO, \
                "")
                
            dialog.format_secondary_markup(_("Jamendo reports, that only <b>%i of your %i</b> stared albums are also stared on jamendo.com.\nNotice that jamendo caches such results - so if you recently exported some albums to jamendo, these might already be stared there.\n\nDo you want Pyjama to open <b>%i</b> tabs in your webbrowser?" % (len(albums), len(stared), len(stared)-len(albums))))
            dialog.set_title("Open %i pages in your webbrowser?" % len(open_uris))
            ret = dialog.run()
            dialog.destroy()
            if ret == gtk.RESPONSE_YES:
                for uri in open_uris:
                    #self.pyjama.Events.raise_event("open_url", uri, True)
                    webbrowser.open_new_tab(uri) # 


        def cbOrder_changed(self, ev1=None):
            self.layout.ordering = self.pyjama.window.get_active_text(self.cbOrder)
            self.pyjama.layouts.show_layout('star', self.layout.results_per_page, self.layout.ordering, 1, self.layout.tag)

        def cbResultsPerPage_changed(self, ev1=None):
            self.layout.results_per_page = int(self.pyjama.window.get_active_text(self.cbResultsPerPage))
            self.pyjama.layouts.show_layout('star', self.layout.results_per_page, self.layout.ordering, 1, self.layout.tag, who_called = "cbResultsPerPage_changed")
            #print self.results_per_page

        def cbTags_key_press_event(self, ev1, ev2=None):
            print "KEYPRESS"

        def cbTagsEntry_activate(self, widget):
            self.cbTags_changed(None, force=True)

        def cbTags_changed(self, ev1=None, force=False):
            tag_entry = self.cbTags.entry.get_text()
            tag_box = self.pyjama.window.get_active_text(self.cbTags)
            if tag_entry != tag_box and force == False: return
            tag_box = tag_entry
            if tag_box == _("--all--"): tag_box = "all"
#            if tag == _("--custom--"):
#                # Show a custom tag
#                # ask for name
#                result = clEntry.input_box(title=_('Custom Tag'),
#                    message=_('Please enter a tag you want to browse'),
#                    default_text=_("ambient"))
#                if result is None:
#                    self.cbTags.set_item(_("--all--"))
#                    return
#                tag = str(result)
            self.layout.tag = tag_box
            self.pyjama.layouts.show_layout('star', self.layout.results_per_page, self.layout.ordering, 1, self.layout.tag.replace(" ", "+"), who_called = "cbTags_changed")        
            
        def on_sbJumpToPage_clicked(self, ev):
            result = clEntry.input_box(title=_('Jump to page'),
                message=_('Enter Page'),
                default_text="%i" % (self.layout.cur_page+10))
            if result is None:
                return None
            elif not result.isdigit():
                dia = clWidget.MyDialog(_('invalid expression'),
                                  self.get_toplevel(),
                                  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                    (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT),        gtk.STOCK_DIALOG_WARNING, _('\'%s\' is not a valid page') % str(result))
                dia.run()
                dia.destroy()
                return None
            else:
                page = int(result)
            self.pyjama.layouts.show_layout('star', self.layout.results_per_page, self.layout.ordering, page, self.layout.tag, who_called = "on_sbjumptopage_clicked")
            self.layout.check_next_possible()
            self.layout.check_prev_possible()
                
        def on_sbNextPage_clicked(self, ev):
            self.pyjama.layouts.show_layout('star', self.layout.results_per_page, self.layout.ordering, self.layout.cur_page+1, self.layout.tag, who_called = "on_sbnextpage_clicked")
            self.layout.check_next_possible()

        def on_sbPrevPage_clicked(self, ev):
            self.pyjama.layouts.show_layout('star', self.layout.results_per_page, self.layout.ordering, self.layout.cur_page-1, self.layout.tag, who_called = "on_sbprevpage_clicked")
            self.layout.check_prev_possible()
