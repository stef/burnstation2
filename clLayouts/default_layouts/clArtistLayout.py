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
# Top Layout - main album browser
#

import gtk
import hashlib
import os
import urllib

from modules import clWidgets
from modules import functions
from modules import clThreadedDownload

class ArtistLayout(gtk.Layout):

    def __init__(self, pyjama):
        self.pyjama = pyjama
        
        gtk.Layout.__init__(self)
        self.set_size(700,400)
        
        # Labels shown in Artist- View
        self.ArtistLabels={}

        # Holds artist's ablums
        self.albuminfos = {}

        # Labels for Artist- View

        y = 10          # current y position
        xspace = 250    # spacing on x- axes
        yspace = 20     # spacing on y- axes
        self.ArtistInfos = ['name', 'country', 'albums', 'url']
        self.ArtistCaptions = [_("Name"), _("Country"), _("#Albums"), _("link")]
        for info in xrange(0, len(self.ArtistInfos)):
            self.ArtistLabels[self.ArtistInfos[info]] = gtk.Label("")
            self.ArtistLabels[self.ArtistInfos[info]].set_single_line_mode(True)
            self.put(self.ArtistLabels[self.ArtistInfos[info]], xspace, y)
            self.ArtistLabels[self.ArtistInfos[info]].show()
            y+=yspace
            
        self.image_artist = gtk.Image()
        self.put(self.image_artist, 30, 10)
        self.image_artist.show()

        self.show()
        self.pyjama.window.setcolor(self)

        self.pyjama.Events.connect_event("scrolled_window_resized", self.ev_scrolled_window_resized)

    def ev_scrolled_window_resized(self):
        #
        # Rearrange layout
        #
        self.arrange_artistdetail()
        self.show()

    def draw(self, data1, data2, data3, data4):
        #
        # Setting label
        #
        try:
            #markup = self.pyjama.window.markuplbCaption.replace("TEXT", _("Showing infos and albums concerning '%s'") % data1[0]['artist_name'])
            txt =  _("Showing infos and albums concerning '%s'") % data1[0]['artist_name']
        except KeyError:
            print ("Artist not in database, yet.")
            dia = clWidgets.MyDialog(_('Artist non existant.'),
                                self.pyjama.window.get_toplevel(),
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_WARNING, _('This artist is not in the database.\nPerhaps you are using a old local database\nor Jamendo did not update their dump, yet'))
            dia.run()
            dia.destroy()
#        self.pyjama.window.lbCaption.set_markup(markup)
        self.pyjama.window.LayoutInfo.set_text(txt)
        self.pyjama.window.LayoutInfo.set_image("personal.png")

        artistinfos = data1
        self.toolbar = self.pyjama.layouts.toolbars['artist']

        for albuminfo in self.albuminfos:
            self.albuminfos[albuminfo].destroy()
            
        self.albuminfos = {}

        img = artistinfos[0]['artist_image']
        name = artistinfos[0]['artist_name']
        artistID = artistinfos[0]['artist_id']
        #genre = artistinfos[0]['artist_genre']
        country = artistinfos[0]['artist_country']
        #link = artistinfos[0]['artist_link']
        url = artistinfos[0]['artist_url']
        albums = artistinfos[0]['artist_albumcount']

        md5hash = hashlib.md5(img).hexdigest()
        fh = os.path.join(self.pyjama.home, "images", md5hash)
        if not os.path.exists(fh) and img != "":
            try:
                urllib.urlretrieve(img, fh)
            except IOError:
                print ("Could not load image")
                return None

        self.pyjama.window.toolbar.lbMoreAlbumsFromThisArtist2.tag = artistID
        #self.toolbar.ibDonate.tag = url #stf
        #self.toolbar.sbGotoWebArtist.tag = url #stf

        self.image_artist.clear()
        if img == "" or img == None:
            pixbuf = self.image_artist.render_icon(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG, detail=None)
            self.image_artist.set_from_pixbuf(pixbuf)
        else:
            self.image_artist.set_from_file(fh)
        

        content = [functions.decode_htmlentities(name), country, albums,  url]
        x = 0
        infos = self.ArtistInfos
        captions = self.ArtistCaptions
        for x in xrange(0, len(infos)):
            #self.window.layout['artist'].move(self.labels[infos[x]], xspace, y)
            if self.pyjama.nocolor and infos[x] != "url":
                self.ArtistLabels[infos[x]].set_markup("<span><b>%s: %s</b></span>" % (captions[x], content[x]))
            elif infos[x] == "url":
                    self.ArtistLabels[infos[x]].set_label(url)
            else:
                self.ArtistLabels[infos[x]].set_markup("<span foreground=\"white\"><b>%s: %s</b></span>" % (captions[x], content[x]))
            #self.labels[infos[x]].set_line_wrap(True)
            #y+=yspace
            
        #### ARTIST'S ALBUMS ####
        threads = {}
        albums = []
        counter = 0
        for album in artistinfos:
            albums.append(str(artistinfos[counter]['album_id']))
            ## todo ##
            ## Replace Image-URL with constants!!!! ##
#            artistinfos[counter]['album_image'] =  "http://imgjam.com/albums/%s/covers/1.100.jpg" % artistinfos[counter]['album_id']
            artistinfos[counter]['album_image'] = "http://api.jamendo.com/get2/image/album/redirect/?id=%s&imagesize=%i" % (artistinfos[counter]['album_id'], 100)
            threads[counter] = clThreadedDownload.Download(self.pyjama, artistinfos[counter]['album_image'], counter)
            threads[counter].start()
            counter += 1
        ## i added another loop
        ## so that threaded download
        ## won't collide with
        ## creating the albuminfos
        counter = 0
        for album in artistinfos:
            self.albuminfos[counter] = clWidgets.AlbumInfo(self.pyjama, artistinfos[counter])
            self.albuminfos[counter].show()
            self.put(self.albuminfos[counter], 1, 1)
            counter += 1

        ### Add Artist's Tracks to List ###

        self.pyjama.window.TVListFrame.get_label_widget().set_markup(_("Tracks of the artist '<b>%s</b>'" % name))

        self.pyjama.window.tvList.clear()
        tracks = self.pyjama.db.artisttracks(artistID)
        for track in tracks:
            results = [name, track.album_name, track.numalbum, track.name, track.license, artistID, track.album_id, track.id]
            self.pyjama.window.tvList.add_item(results)

#        ### this is more than slow since
#        ### every artists' album is requested
#        ### on its own, need multiple cross- joins!!!
#        for album in albums:
#            tracks = self.db.albumtracks(album)
#            for track in tracks:
#                results = [tracks[track]['artist_name'], tracks[track]['album_name'], tracks[track]['numalbum'], tracks[track]['name'], tracks[track]['license'], tracks[track]['artist_id'], tracks[track]['album_id'], tracks[track]['id']]
#                self.window.tvList.add_item(results)

        self.arrange_artistdetail()
        self.pyjama.Events.raise_event("showing_artist_page", artistinfos)
        self.show()
        self.pyjama.window.toolbar.lbMoreAlbumsFromThisArtist2.hide()
        self.pyjama.window.toolbar.lbAppendAlbum.hide()
        self.pyjama.window.toolbar.lbArtistsAlbumsToPlaylist.show()
        self.pyjama.window.toolbar.Separator2.show()

    def arrange_artistdetail(self):
        if self.albuminfos == {}: return None
        width = self.pyjama.window.scrolledwindow_width
        hspace = 20
        vspacer = 20
        
        imgwidth = 150
        imgheight = 160
        starty = 200
        
        y = 0
        x = 0
        self.hide()
        for counter in self.albuminfos:
            if ((x+1) * imgwidth) + hspace*(x+1) >= width:
                y += 1
                x = 0
            self.move(self.albuminfos[counter], (imgwidth * x) + hspace*(x+1), (vspacer*(y+1) + (y * imgheight))+starty)
            x += 1
        height = (y+1) * (imgheight + vspacer) +starty

        self.set_size(width-20,height+vspacer)

    def on_zumArtist_clicked(self, ev):
        url = self.ArtistLabels['url'].get_text()
        self.pyjama.Events.raise_event("open_url",  url )


    #
    # Actually this toolbar is just a hbox...
    #
    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['artist']

            #stf
            #self.sbGotoWebArtist = clWidgets.StockButton(gtk.STOCK_NETWORK, gtk.ICON_SIZE_LARGE_TOOLBAR)
            #self.sbGotoWebArtist.set_tooltip_text(_("Goto to artist's page on jamendo"))
            #self.sbGotoWebArtist.set_size_request(50,50)
            #self.sbGotoWebArtist.show()
            #self.pack_end(self.sbGotoWebArtist, False, True, 2)
            #self.sbGotoWebArtist.connect("clicked", self.on_sbGotoWebArtist_clicked)        

            #self.ibDonate = clWidgets.ImageButton("%s/images/money.png"  % functions.install_dir(), 26, 26)
            #self.ibDonate.set_size_request(50,50)
            #self.ibDonate.set_tooltip_text(_("Support this artist"))
            #self.ibDonate.show()
            #self.pack_end(self.ibDonate, False, True, 2)
            #self.ibDonate.connect("clicked", self.on_ibDonate_clicked)

        def on_sbGotoWebArtist_clicked(self, ev):
            self.pyjama.Events.raise_event("open_url",  self.sbGotoWebArtist.tag)

        def on_ibDonate_clicked(self, ev):
            url = self.ibDonate.tag + "/donate"
            self.pyjama.Events.raise_event("open_url", url)        

