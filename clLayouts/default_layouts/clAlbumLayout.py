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
# Album Layout - shows an album
#

import gtk
import os
import hashlib
import urllib
import time

from modules import clWidgets
from modules import functions
from modules import clThreadedDownload

class AlbumLayout(gtk.Layout):

    def __init__(self, pyjama):
        self.pyjama = pyjama
        
        gtk.Layout.__init__(self)
        self.set_size(700,200)

        # Holds similar albums
        self.albuminfos = {}

        # Labels shown in Album- View
        self.AlbumLabels={}

        # Labels on Album Widget
        y = 10
        xspace = 250
        yspace = 20
        self.AlbumInfos = ['name', 'artist_name', 'trackcount', 'lengths', 'genre', 'releasedate', 'review_note', 'url']
        self.AlbumCaptions = [_("Album's title"), _("Artist"), _("#Tracks"), _("Length"), _("Genre"), _("Releasedate"), _('Rating'), _('link')]
        for info in xrange(0, len(self.AlbumInfos)):
            self.AlbumLabels[self.AlbumInfos[info]] = gtk.Label("")
            self.AlbumLabels[self.AlbumInfos[info]].set_single_line_mode(True)
            self.put(self.AlbumLabels[self.AlbumInfos[info]], xspace, y)
            self.AlbumLabels[self.AlbumInfos[info]].show()
            if self.AlbumInfos[info] == "review_note":
                # USER WIDGET Rating
                self.rtRating = clWidgets.Rating()
                self.put(self.rtRating, 350, y)
                self.rtRating.show() # for some reason this is not done by self.show_all()
            y+=yspace

        hb = gtk.HBox()
        self.put(hb, 20, 240)
        self.lblSimilar = gtk.Label()
        self.lblSimilar.set_markup(_("<b>Similar Albums:</b>"))
        hb.pack_start(self.lblSimilar, True, True)
        #btn = clWidgets.StockButton(gtk.STOCK_PREFERENCES)
        #btn.connect("pressed", self.pyjama.show_preferences, "Pyjama")
        #btn.set_tooltip_text("Go to preferences page and set 'similar albums'")
        #hb.pack_start(btn, False, True)
        hb.show_all()

        self.image_album = gtk.Image()
        self.put(self.image_album, 30, 10)
        self.image_album.show()

        # might be obsolet
        self.pyjama.window.setcolor(self)
        self.show()

        self.pyjama.Events.connect_event("scrolled_window_resized", self.ev_scrolled_window_resized)

    def on_zumAlbum_clicked(self, ev):
        url = self.AlbumLabels['url'].get_text()
        self.pyjama.Events.raise_event("open_url", url)


    def draw(self, data1, data2, data3, data4):
        #
        # Setting label
        #
#        markup = self.pyjama.window.markuplbCaption.replace("TEXT", _("Show album infos for '%s'") % data1['name'])
        txt =  _("Showing album infos for '%s'") % data1['name']
#        self.pyjama.window.lbCaption.set_markup(markup)
        self.pyjama.window.LayoutInfo.set_text(txt)
        self.pyjama.window.LayoutInfo.set_image("cd.png")

        #self.toolbar = self.pyjama.layouts.toolbars['album']

        albuminfos = data1

        tracks = self.pyjama.db.albumtracks(albuminfos['id'])
        track_count = len(tracks)

        if track_count == 0:
            print ("Album not in database, yet.")
            print albuminfos['public_date']
            dia = clWidgets.MyDialog(_('Album non existant.'),
                              self.pyjama.window.get_toplevel(), gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_WARNING, _('This album is not in the database.\nPerhaps Jamendo did not unloack that album, yet\n or you are using a old local database.'))
            dia.run()
            dia.destroy()
            self.pyjama.window.toolbar.on_bHistoryBack_clicked(None)
            return None


        #tags = albuminfos['id3genre']

        genre = albuminfos['id3genre']
        #desc = albuminfos['desc_str']
        #referrer_count = albuminfos['referrer_count']
            #playlisted_count = albuminfos['playlisted_count']
            #favourited_count = albuminfos['favourited_count']
        #lowfi_count = albuminfos['lowfi_count']
        releasedate = albuminfos['public_date']
        lengths = albuminfos['lengths']
            #license_id = albuminfos['license_id']
            #review_num = albuminfos['review_num']
        review_note = albuminfos['review_note']
            #review_num_week = albuminfos['review_num_week']
            #review_note_week = albuminfos['review_note_week']
        name = albuminfos['name']
        artist_id = albuminfos['artist_id']
        artist_name = tracks[0].artist_name
        album_id = albuminfos['id']
            #img = albuminfos['images'][0]['url']
        img = albuminfos['root_images'] + "1.200.jpg"
        url = self.pyjama.settings.get_value("URLs", "ALBUM_URL").replace("URL", "%s" % album_id)
        albuminfos['tracks'] = tracks

        self.pyjama.window.TVListFrame.get_label_widget().set_markup(_("Tracks of the album '<b>%s</b>'" % data1['name']))

        self.pyjama.window.tvList.clear()
        for track in tracks:
            results = [artist_name, name, track.numalbum,track.name, track.license, artist_id, album_id, track.id]
            self.pyjama.window.tvList.add_item(results)


        self.pyjama.window.toolbar.lbAppendAlbum.tag = tracks #self.tracks = tracks


        md5hash = hashlib.md5(img).hexdigest()
        fh = os.path.join(self.pyjama.home, "images", md5hash)
        if not os.path.exists(fh):
            try:
                urllib.urlretrieve(img, fh)
            except IOError:
                print ("Could not load image")
                return None


        self.image_album.clear()
        if img == "" or img == None:
            pixbuf = self.image_album.render_icon(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG, detail=None)
            self.image_album.set_from_pixbuf(pixbuf)
        else:
            self.image_album.set_from_file(fh)


        content = [ name, functions.decode_htmlentities(artist_name), track_count, functions.sec2time(lengths), functions.id2genre(genre), releasedate, review_note, url ]
        x = 0
        infos = self.AlbumInfos
        namen = self.AlbumCaptions
        for x in xrange(0, len(infos)):
            if infos[x] == "review_note":
                if self.pyjama.nocolor:
                    self.AlbumLabels[infos[x]].set_markup("<span><b>%s: </b></span>" % (namen[x]))
                else:
                    self.AlbumLabels[infos[x]].set_markup("<span foreground=\"white\"><b>%s: </b></span>" % (namen[x]))
                self.rtRating.set_rating(content[x])
            elif infos[x] == "url":
                    self.AlbumLabels[infos[x]].set_label(url)
            else:
                if self.pyjama.nocolor:
                    self.AlbumLabels[infos[x]].set_markup("<span><b>%s: %s</b></span>" % (namen[x], content[x]))
                else:
                    self.AlbumLabels[infos[x]].set_markup("<span foreground=\"white\"><b>%s: %s</b></span>" % (namen[x], content[x]))


        # NEW ATTRIBUTE 'FLAG' IN STOCKBUTTON
        # NEED TO USE THIS FOR OTHER BUTTONS
        # HERE, TOO!
        #self.toolbar.sbGotoWeb.tag = url #stf
        
        self.pyjama.window.toolbar.lbMoreAlbumsFromThisArtist2.tag = artist_id
        self.pyjama.window.toolbar.lbMoreAlbumsFromThisArtist2.set_tooltip_text(_("Showing informations and albums from '%s'") % artist_name)
        self.pyjama.window.toolbar.lbMoreAlbumsFromThisArtist2.show()
        self.pyjama.window.toolbar.lbAppendAlbum.show()
        self.pyjama.window.toolbar.lbArtistsAlbumsToPlaylist.hide()
        self.pyjama.window.toolbar.Separator2.show()
        #self.toolbar.sbDownloadAlbum.tag = album_id

        for albuminfo in self.albuminfos:
            self.albuminfos[albuminfo].destroy()
        
        self.albuminfos = {}

        ### Similar Album's ###
        threads = {}
        counter = 0

        albums_dic = {}

        num = self.pyjama.settings.get_value("PYJAMA", "similar_albums", 5)

        ## This hack prevents the jamendo class from aborting the query
        # with a "to fast" message - there should be a better solution
        self.pyjama.jamendo.last_query_hack()
        ret = self.pyjama.jamendo.get_similar_albums( album_id, num )
        if ret is not None and ret != [] and ret != -1 and num > 0:
            ALBUM_ID = 0
            ALBUM_NAME = 1
            ARTIST_ID = 2
            ARTIST_NAME=3

            # get infos fo the returnes albums:
            albums = self.pyjama.db.multiple_albuminfos(ret)
            if albums is not None and albums != []:

                for album in albums:
                    #image = "http://imgjam.com/albums/%s/covers/1.100.jpg" % album[ALBUM_ID]
                    image = "http://api.jamendo.com/get2/image/album/redirect/?id=%s&imagesize=%i" % (album[ALBUM_ID], 100)
                    threads[counter] = clThreadedDownload.Download(self.pyjama, image, counter)
                    threads[counter].start()
                    albums_dic[counter] = {'arist_id':album[ARTIST_ID], 'album_id':album[ALBUM_ID], 'artist_name':album[ARTIST_NAME], 'album_name':album[ALBUM_NAME], 'album_image':image}
                    counter += 1
                ## i added another loop
                ## so that threaded download
                ## won't collide with
                ## creating the albuminfos
                counter = 0
                for album in albums:
                    self.albuminfos[counter] = clWidgets.AlbumInfo(self.pyjama, albums_dic[counter])
                    self.albuminfos[counter].show()
                    self.put(self.albuminfos[counter], 1, 1)
                    counter += 1
            self.lblSimilar.set_markup(_("<b>Similar Albums:</b>"))
        elif ret == -1:
            print ("Some Problems with Jamendo")
        elif ret == []:
            self.lblSimilar.set_markup(_("<b>No similar albums found</b>"))


        self.arrange_albumdetail()
#        self.set_size(self.pyjama.window.scrolledwindow_width-20,230)#350)#y+200
        self.pyjama.Events.raise_event("showing_album_page", albuminfos)

    def arrange_albumdetail(self):
        if self.albuminfos == {}: 
            self.set_size(700,300)
            return None
        width = self.pyjama.window.scrolledwindow_width
        hspace = 10
        vspacer = 10
        
        imgwidth = 110
        imgheight = 150
        starty = 270
        
        y = 0
        x = 0
        self.hide()

        for counter in self.albuminfos:
            if ((x+1) * imgwidth) + hspace*(x+1) >= width:
                y += 1
                x = 0
            self.move(self.albuminfos[counter], (imgwidth * x) + hspace*(x+1), (vspacer*(y+1) + (y * imgheight))+starty)
            x += 1
        height = (y+1) * (imgheight + vspacer) + starty

        self.set_size(width-20,height+vspacer)
        self.show()

    def ev_scrolled_window_resized(self):
        #
        # Rearrange layout
        #
        self.arrange_albumdetail()
        self.show()

    #
    # Actually this toolbar is just a hbox...
    #
    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['album']

            # ADD ALBUM TO PLAYLIST
            #self.lbAppendAlbum = clWidgets.StockButton(gtk.STOCK_ADD, gtk.ICON_SIZE_DND)
            #self.lbAppendAlbum.set_tooltip_text(_("Append this album on playlist"))
            #self.lbAppendAlbum.show()
            #self.pack_start(self.lbAppendAlbum, False, True, 2)
            #self.lbAppendAlbum.connect("clicked", self.on_lbAppendAlbum_clicked)
            ## GET MORE ALBUMS FROM THIS PLAYLIST
            #self.lbMoreAlbumsFromThisArtist2 = clWidgets.ImageButton(os.path.join(functions.install_dir(), "images", "personal.png"), gtk.ICON_SIZE_DND )
            #self.pack_start(self.lbMoreAlbumsFromThisArtist2, False, True, 2)
            #self.lbMoreAlbumsFromThisArtist2.connect("clicked", self.on_lbMoreAlbumsFromThisArtist_clicked)
            #self.lbMoreAlbumsFromThisArtist2.show()


            # DOWNLOAD ALBUM VIA TORRENT
            #self.sbDownloadAlbum = clWidgets.StockButton(gtk.STOCK_GOTO_BOTTOM, gtk.ICON_SIZE_LARGE_TOOLBAR)
            #self.sbDownloadAlbum.set_tooltip_text(_("Download Album as Torrent"))
            #self.sbDownloadAlbum.set_size_request(50,50)
            #self.sbDownloadAlbum.show()
            #self.pack_end(self.sbDownloadAlbum, False, True, 2)
            #self.sbDownloadAlbum.connect("clicked", self.on_sbDownloadAlbum_clicked)    
            # GO TO ALBUM'S PAGE ON JAMENDO
            #self.sbGotoWeb = clWidgets.StockButton(gtk.STOCK_NETWORK, gtk.ICON_SIZE_LARGE_TOOLBAR)
            #self.sbGotoWeb.set_tooltip_text(_("Goto to album's page on jamendo"))
            #self.pack_end(self.sbGotoWeb, False, True, 2)
            #self.sbGotoWeb.set_size_request(50,50)
            #self.sbGotoWeb.show()
            #self.sbGotoWeb.connect("clicked", self.on_sbGotoWeb_clicked)        
            # WRITE A REVIEW
            #self.sbWriteReview = clWidgets.StockButton(gtk.STOCK_EDIT, gtk.ICON_SIZE_LARGE_TOOLBAR)
            #self.sbWriteReview.set_tooltip_text(_("Write a review for this album"))
            #self.sbWriteReview.set_size_request(50,50)
            #self.sbWriteReview.show()
            #self.pack_end(self.sbWriteReview, False, True, 2)
            #self.sbWriteReview.connect("clicked", self.on_sbWriteReview_clicked)    


        def on_sbWriteReview_clicked(self, ev):
            self.pyjama.Events.raise_event("open_url", "http://www.jamendo.com/album/%s/writereview" % self.sbDownloadAlbum.tag)

        def on_lbMoreAlbumsFromThisArtist_clicked(self, ev):
            # query db for artist informations and more albums
            self.pyjama.start_pulsing(text = _("Requesting local database"))
            ret = self.pyjama.db.artistinfos(self.lbMoreAlbumsFromThisArtist2.tag, time.time())        
            self.pyjama.stop_pulsing()
            self.pyjama.layouts.show_layout("artist", ret, who_called = "on_lbMoreAlbumsFromThisArtist_clicked")


        def on_lbAppendAlbum_clicked(self, ev):
            tracks = self.lbAppendAlbum.tag
            for track in tracks: # for track in self.main.tracks:
                track.uid = "%f%s" % (time.time(), track.id)
                self.pyjama.add2playlist(track)
                status = self.pyjama.player.status
                if status == "Error" or status == "End" or status == None:
                    self.pyjama.window.on_bPlay_clicked(None)

        def on_sbGotoWeb_clicked(self, ev):
            self.pyjama.Events.raise_event("open_url",  self.sbGotoWeb.tag)

        def on_sbDownloadAlbum_clicked(self, ev):
            url = "http://api.jamendo.com/get2/bittorrent/file/redirect/?album_id=%s&type=archive&class=%s" % (self.sbDownloadAlbum.tag, self.pyjama.settings.get_value("JAMENDO", "FORMAT"))
            self.pyjama.Events.raise_event("open_url", url, force_default=True)        

