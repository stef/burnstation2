#!/usr/bin/env python

import os
import gtk
import gtk.glade
import gobject
import webbrowser

import functions
import clWidgets


def _(txt): return txt

class Pref():
    pass

## A theme-selection gtk.ComboBox
class theme_selection(gtk.ComboBox):
    def __init__(self, value="None"):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBox.__init__(self, liststore)
        cell = gtk.CellRendererText()

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_wrap_width(2)

        self.insert_text(0, "None")
        self.insert_text(1, value)
        self.set_active(1)

        counter = 1
        themes = functions.sorteddirlist()
        for theme in themes:
            counter += 1
            self.insert_text(counter, theme)
        self.show()
   

## This class is used only to hold several
# vboxes for default modules.
# You won't actually need it
class DefaultPrefs():
    def __init__(self, pyjama=None):
        self.pyjama = pyjama

    def create_main(self):
        #
        # Pyjama's main settings
        #
        self.main = Pref()
        self.main.vbox = gtk.VBox()
        self.main.vbox.show()

        # Similar Albums
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Number of similar Albums to\nshow on album pages")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.spin_similar_albums = gtk.SpinButton()
        self.main.spin_similar_albums.set_increments(1, 10)
        self.main.spin_similar_albums.set_range(0, 15)
        self.main.spin_similar_albums.set_value(5)
        self.main.spin_similar_albums.show()
        hbox.pack_end(self.main.spin_similar_albums, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)
        self.main.spin_similar_albums.set_value(self.pyjama.settings.get_value("PYJAMA", "similar_albums", 5, float))

        sep = gtk.HSeparator()
        sep.show()
        self.main.vbox.pack_start(sep, False, False, 10)

        #Theme
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Select a theme")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.old_theme = self.pyjama.settings.get_value("PYJAMA", "standard_theme", "None")
        self.main.theme = theme_selection(self.main.old_theme)# pass current theme here!
        self.main.theme.show()
        hbox.pack_end(self.main.theme, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)

        # Show toolbar text
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Show toolbar text")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.check_show_toolbar_text = gtk.CheckButton()
        self.main.check_show_toolbar_text.show()
        hbox.pack_end(self.main.check_show_toolbar_text, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)
        show_toolbar_text = self.pyjama.settings.get_value("PYJAMA", "show_toolbar_text", False)
        self.main.check_show_toolbar_text.set_active(show_toolbar_text)

        # Show entry in taskbar
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Show pyjama in taskbar")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.check_show_taskbar = gtk.CheckButton()
        self.main.check_show_taskbar.show()
        hbox.pack_end(self.main.check_show_taskbar, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)
        show_window_in_taskbar = self.pyjama.settings.get_value("PYJAMA", "show_window_in_taskbar", False)
        self.main.check_show_taskbar.set_active(show_window_in_taskbar)

        # Show AlbumInfo Frames
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Show albuminfo frames")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.check_show_albuminfo_frames = gtk.CheckButton()
        self.main.check_show_albuminfo_frames.show()
        hbox.pack_end(self.main.check_show_albuminfo_frames, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)
        show_albuminfo_frames = self.pyjama.settings.get_value("PYJAMA", "show_albuminfo_frames", True)
        self.main.check_show_albuminfo_frames.set_active(show_albuminfo_frames)

        # Cover size
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Cover size in notifications")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.spin_notification_size = gtk.SpinButton()
        self.main.spin_notification_size.set_increments(1, 10)
        self.main.spin_notification_size.set_range(0, 400)
        self.main.spin_notification_size.show()
        hbox.pack_end(self.main.spin_notification_size, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)
        self.main.spin_notification_size.set_value(self.pyjama.settings.get_value("PYJAMA", "notification_cover_size", 75, float))

        # Notification Delay
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("How long should notifications been shown?\nValue in ms")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.main.spin_notification_delay = gtk.SpinButton()
        self.main.spin_notification_delay.set_increments(1, 100)
        self.main.spin_notification_delay.set_range(0, 30000)
        self.main.spin_notification_delay.set_value(5000)
        self.main.spin_notification_delay.show()
        hbox.pack_end(self.main.spin_notification_delay, False, False, 30)
        self.main.vbox.pack_start(hbox, False, False, 10)
        self.main.spin_notification_delay.set_value(self.pyjama.settings.get_value("PYJAMA", "notification_delay", 5000, float))
        return self.main.vbox

    #
    # Jamendo
    #
    def create_jamendo(self):
        self.jamendo = Pref()
        self.jamendo.vbox = gtk.VBox()
        self.jamendo.vbox.show()

        # caching time short
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label()
        l.set_markup("How many <b>days</b> should queries been stores\nthat <b>will change from time to time</b>.")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.jamendo.spin_caching_time_short = gtk.SpinButton()
        self.jamendo.spin_caching_time_short.set_increments(1, 100)
        self.jamendo.spin_caching_time_short.set_range(1, 365)
        self.jamendo.spin_caching_time_short.show()
        hbox.pack_end(self.jamendo.spin_caching_time_short, False, False, 30)
        self.jamendo.vbox.pack_start(hbox, False, False, 10)
        self.jamendo.spin_caching_time_short.set_value(self.pyjama.settings.get_value("JAMENDO", "caching_time_short", 2*86400.0, float)/86400.0)


        # caching time long
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label()
        l.set_markup("How many <b>days</b> should queries been stores\nthat <b>won't change</b> probably.")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.jamendo.spin_caching_time_long = gtk.SpinButton()
        self.jamendo.spin_caching_time_long.set_increments(1, 100)
        self.jamendo.spin_caching_time_long.set_range(1, 365)
        self.jamendo.spin_caching_time_long.show()
        hbox.pack_end(self.jamendo.spin_caching_time_long, False, False, 30)
        self.jamendo.vbox.pack_start(hbox, False, False, 10)
        self.jamendo.spin_caching_time_long.set_value(self.pyjama.settings.get_value("JAMENDO", "caching_time_long", 90*86400.0, float)/86400.0)

        # stream format
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label()
        l.set_markup("<b>Streaming</b> format\nOGG has a better quality, MP3 supports seeking.")
        l.show() 
        vbox = gtk.VBox()
        vbox.show()
        hbox.pack_start(l, False, False, 15)
        self.jamendo.rbutton_format_stream_mp3 = gtk.RadioButton(None, "MP3")
        self.jamendo.rbutton_format_stream_mp3.show()
        vbox.pack_start(self.jamendo.rbutton_format_stream_mp3, False, False, 10)
        self.jamendo.rbutton_format_stream_ogg = gtk.RadioButton(self.jamendo.rbutton_format_stream_mp3, "OGG")
        self.jamendo.rbutton_format_stream_ogg.show()
        vbox.pack_end(self.jamendo.rbutton_format_stream_ogg, False, False, 10)
        hbox.pack_end(vbox, False, False, 30 )
        self.jamendo.vbox.pack_start(hbox, False, False, 10)
        is_mp3 = self.pyjama.settings.get_value("JAMENDO", "format_stream", "mp31").lower() == "mp31"
        self.jamendo.rbutton_format_stream_mp3.set_active(is_mp3)
        self.jamendo.rbutton_format_stream_ogg.set_active(not is_mp3)
        
        # download format
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label()
        l.set_markup("<b>Download</b> format\nWhich format should be downloaded?")
        l.show()
        vbox = gtk.VBox()
        vbox.show()
        hbox.pack_start(l, False, False, 15)
        self.jamendo.rbutton_format_torrent_mp3 = gtk.RadioButton(None, "MP3")
        self.jamendo.rbutton_format_torrent_mp3.show()
        vbox.pack_start(self.jamendo.rbutton_format_torrent_mp3, False, False, 10)
        self.jamendo.rbutton_format_torrent_ogg = gtk.RadioButton(self.jamendo.rbutton_format_torrent_mp3, "OGG")
        self.jamendo.rbutton_format_torrent_ogg.show()
        vbox.pack_end(self.jamendo.rbutton_format_torrent_ogg, False, False, 10)
        hbox.pack_end(vbox, False, False, 30 )
        self.jamendo.vbox.pack_start(hbox, False, False, 10)
        is_mp3 = self.pyjama.settings.get_value("JAMENDO", "format", "mp32").lower() == "mp32"
        self.jamendo.rbutton_format_torrent_mp3.set_active(is_mp3)
        self.jamendo.rbutton_format_torrent_ogg.set_active(not is_mp3)
        return self.jamendo.vbox

    #
    # Sound
    #
    def create_sound(self):
        self.sound = Pref()
        self.sound.vbox = gtk.VBox()
        self.sound.vbox.show()
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Volume on startup")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.sound.spin_default_volume = gtk.SpinButton()
        self.sound.spin_default_volume.set_increments(1, 10)
        self.sound.spin_default_volume.set_range(0, 250)
        self.sound.spin_default_volume.show()
        hbox.pack_end(self.sound.spin_default_volume, False, False, 30)
        self.sound.vbox.pack_start(hbox, False, False, 10)
        self.sound.spin_default_volume.set_value(self.pyjama.settings.get_value("SOUND", "default_vol", 75, float))

        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label("Max Volume")
        l.show()
        hbox.pack_start(l, False, False, 15)
        self.sound.spin_max_volume = gtk.SpinButton()
        self.sound.spin_max_volume.set_increments(1, 10)
        self.sound.spin_max_volume.set_range(0, 250)
        self.sound.spin_max_volume.show()
        hbox.pack_end(self.sound.spin_max_volume, False, False, 30)
        self.sound.vbox.pack_start(hbox, False, False, 10)
        self.sound.spin_max_volume.set_value(self.pyjama.settings.get_value("SOUND", "vol_max", 150, float))

        ## SOUND SERVER
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label()
        l.set_markup("Soundserver to use\n<small>(Restart required)</small>")
        l.show() 
        vbox = gtk.VBox()
        vbox.show()
        hbox.pack_start(l, False, False, 15)
        self.sound.Pulseaudio = gtk.RadioButton(None, "Pulseaudio")
        self.sound.Pulseaudio.show()
        vbox.pack_start(self.sound.Pulseaudio, False, False, 10)
        self.sound.ALSA = gtk.RadioButton(self.sound.Pulseaudio, "ALSA")
        self.sound.ALSA.show()
        vbox.pack_end(self.sound.ALSA, False, False, 10)
        hbox.pack_end(vbox, False, False, 30 )
        self.sound.vbox.pack_start(hbox, False, False, 10)
        is_alsa = self.pyjama.settings.get_value("SOUND", "audiointerface", "alsa").lower() == "alsa"
        self.sound.Pulseaudio.set_active(not is_alsa)
        self.sound.ALSA.set_active(is_alsa)


        ##equalizer
        if self.pyjama.player.equalizer_available:
            self.sound.show_equalizer_box = False
            if self.sound.show_equalizer_box:
                self.sound.equalizer = clWidgets.EqualizerBox(self.pyjama)
                self.sound.vbox.pack_start(self.sound.equalizer, False, False, 10)
            else:
                self.sound.bEqualizer = clWidgets.ImageButton("view-media-equalizer.png", 50, 50)
                self.sound.bEqualizer.set_label("Equalizer")
                self.sound.bEqualizer.set_tooltip_text("Show Pyjama's Equalizer")
                self.sound.bEqualizer.connect("clicked", self.cb_button_pressed, "eq")
                self.sound.bEqualizer.show()
                self.sound.vbox.pack_start(self.sound.bEqualizer, False, False, 10)

        return self.sound.vbox


    #
    # Performance
    #
    def create_performance(self):
        self.perf = Pref()
        self.perf.vbox = gtk.VBox()
        self.perf.vbox.show()
        img = gtk.Image()
        img.show()
        img.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
        self.perf.vbox.pack_start(img, False, False, 10)
        txt = gtk.Label()
        txt.show()
        txt.set_markup("Only advanced user should set performance \
        reladed preferences. For this reason I decided not to let \
        someone set those settings via this dialog. \
        Please edit <b>pyjama.cfg</b> in order to set \
        <i>history size</i>, <i>search limitis</i> or <i>thread related</i> settings.".replace(8*" ", "\n"))
        self.perf.vbox.pack_start(txt, False, False, 10)
        return self.perf.vbox


    #
    # Plugins
    #
    def create_plugin(self):
        self.plugin_vbox = gtk.VBox()
        self.plugin_vbox.show()
        img = gtk.Image()
        img.set_from_file(os.path.join(functions.install_dir(), "images", "plugin.png"))
        img.show()
        self.plugin_vbox.pack_start(img, False, True,10)
        l = gtk.Label(_("<-- To configure a plugins, select if from the list on the left side."))
        l.show()
        self.plugin_vbox.pack_start(l, False, True,10)

        # Plugins Button
        hbox = gtk.HBox()
#        hbox.show()
#        l = gtk.Label("(Un)select plugins with\nthe plugin dialog:")
#        l.show()
#        hbox.pack_start(l)
        l = clWidgets.MyLinkButton("", "Select and unselect plugins")
        l.set_tooltip_text("Click here to choose which plugin should be loaded")
        l.connect("clicked", self.pyjama.show_plugins)
        l.show()
#        hbox.pack_start(l)
        self.plugin_vbox.pack_start(l, False, True, 20)


        # Documentation button
        url = "http://xn--ngel-5qa.de/pyjama/html"
        hbox = gtk.HBox()
        hbox.show()
        l = gtk.Label(_("Learn more about\npyjama's plugin interface:"))
        l.show()
        hbox.pack_start(l)
        l = clWidgets.MyLinkButton(url, _("Pyjama's Documentation"))
        l.set_tooltip_text(url)
        l.connect("clicked", self.cb_visit_documentation)
        l.show()
        hbox.pack_start(l)
        self.plugin_vbox.pack_end(hbox, False, True, 20)
        return self.plugin_vbox

    #######################################################
    #
    # Save Callbacks
    #
    def pyjama_save_preferences(self):
        # Applying needed
        self.pyjama.settings.set_value("PYJAMA", "similar_albums", int(self.main.spin_similar_albums.get_value()))
        self.pyjama.settings.set_value("PYJAMA", "show_toolbar_text", self.main.check_show_toolbar_text.get_active())
        self.pyjama.settings.set_value("PYJAMA", "show_albuminfo_frames",  self.main.check_show_albuminfo_frames.get_active())
        self.pyjama.settings.set_value("PYJAMA", "notification_delay", int(self.main.spin_notification_delay.get_value()))
        self.pyjama.settings.set_value("PYJAMA", "notification_cover_size", int(self.main.spin_notification_size.get_value()))
        self.pyjama.settings.set_value("PYJAMA", "notification_delay", int(self.main.spin_notification_delay.get_value()))
        
        newtheme = self.pyjama.window.get_active_text(self.main.theme)
        self.pyjama.settings.set_value("PYJAMA", "standard_theme", newtheme)
#        print newtheme, self.main.old_theme
#        if self.main.old_theme != newtheme: 
#            print("Theme changed")
#            print functions.showtheme(newtheme, reparse=True)
##            dirname = os.path.dirname(sys.argv[0])
##            abspath =  os.path.abspath(dirname)
##            run = os.path.join(abspath, sys.argv[0])
##            self.pyjama.window.really_quit()
##            os.system("%s -t %s &" % (run, newtheme))



    def sound_save_preferences(self):
        # ok
        self.pyjama.settings.set_value("SOUND", "vol_max", self.sound.spin_max_volume.get_value(), int)
        self.pyjama.settings.set_value("SOUND", "default_vol", self.sound.spin_default_volume.get_value(), int)


        if self.sound.Pulseaudio.get_active():
            self.pyjama.settings.set_value("SOUND", "audiointerface", "pulse")
        else:
            self.pyjama.settings.set_value("SOUND", "audiointerface", "alsa")

        if self.sound.show_equalizer_box:
            self.sound.equalizer.save()

    def perf_save_preferences(self):
        # None
        pass

    def jamendo_save_preferences(self):
        # ok
        self.pyjama.settings.set_value("JAMENDO", "caching_time_long", self.jamendo.spin_caching_time_long.get_value()*86400.0, int)
        self.pyjama.settings.set_value("JAMENDO", "caching_time_short", self.jamendo.spin_caching_time_short.get_value()*86400.0, int)


        if self.jamendo.rbutton_format_stream_mp3.get_active():
            self.pyjama.settings.set_value("JAMENDO", "format_stream", "mp31")
        else:
            self.pyjama.settings.set_value("JAMENDO", "format_stream", "ogg2")

        if self.jamendo.rbutton_format_torrent_mp3.get_active():
            self.pyjama.settings.set_value("JAMENDO", "format", "mp32")
        else:
            self.pyjama.settings.set_value("JAMENDO", "format", "ogg3")


        print "Jamendo prefs still need to be saved"

    def plugin_save_preferences(self):
        pass


    #######################################################
    #
    # Various Callbacks
    #
    #~ def cb_eq_clear_clicked(self, widget, num):
        #~ self.values[num]=0
        #~ self.adjs[num].set_value(0)
#~ 
        #~ self.pyjama.player.set_equalizer(self.values)
                #~ 
    #~ def cb_eq_value_changed(self, widget, num):
        #~ self.values[num]=widget.get_value()
#~ 
        #~ self.pyjama.player.set_equalizer(self.values)
        
    def cb_visit_documentation(self, widget):
        webbrowser.open_new_tab(widget.uri)

    def cb_button_pressed(self, widget, name=None):
        if name == "eq":
            eq = clWidgets.EqualizerBox(self.pyjama)
            eq.dialog()


PLUGIN_STRING = _("Plugins")

class Preferences():
    def __init__(self, pyjama=None):
        # Lists containing the plugins and the main modules
        self.plugins = []   # Preferences pages for plugins
        self.modules = []   # Some essential preferences pages
#        self.loaded_containers = {}
        self.currently_shown_box_name = None

        default = DefaultPrefs(pyjama)
        self.start_page = self.register_module("Pyjama", default.create_main, default.pyjama_save_preferences, "General Pyjama Preferences")
        self.register_module("Sound", default.create_sound, default.sound_save_preferences)
        self.register_module("Jamendo", default.create_jamendo, default.jamendo_save_preferences)
        self.register_module("Performance", default.create_performance, default.perf_save_preferences)

        self.register_module(PLUGIN_STRING, default.create_plugin, default.plugin_save_preferences, "Plugins")

    ## Prepare the dialog by loading
    # the widgets from a glade file
    def __init_widgets(self):
        # Get the widgets from preferences.glade and
        # do some usefull stuff with them
        xml = gtk.glade.XML(os.path.join(functions.install_dir(), "preferences.glade"))
        self.dialog = xml.get_widget('dialog1')
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
        self.dialog.set_icon(pixbuf)
        self.dialog.set_default_size(640,480)


        self.caption =  xml.get_widget('caption')


        self.viewport = xml.get_widget('viewport1')
        sw = xml.get_widget('scrolledwindow1')
        self.treeview = xml.get_widget('treeview1')

        #TREEVIEW
        self.model = gtk.TreeStore(gobject.TYPE_STRING)
        self.treeview.set_model(self.model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Module", renderer, markup=0)
        self.treeview.append_column(column)

        self.treeview.connect("button-press-event", self.cb_treeview_button_press)
        self.treeview.connect("row-activated", self.cb_treeview_row_activated)

    ## Shows the preferences dialog
    def show_preferences(self, page_to_show=None):
        self.__init_widgets()
        self.loaded_boxes = {}

        ## Default Preferences
        for module in self.modules:
            if module['name'] != PLUGIN_STRING:
                self.model.append(None, (module['name'], ))

        ## Plugin Preferences
        TreeIterPlugins = self.model.append(None,(PLUGIN_STRING,))
        for pref in self.plugins:
            self.model.append(TreeIterPlugins, (pref['name'], ))

        self.treeview.expand_all()

        if page_to_show is None:
            self.show_box(self.start_page)
        else:
            self.find_box(page_to_show)

        ret = self.dialog.run()
#        ch = self.viewport.get_child()
#        if ch:
#            self.viewport.remove(ch)

#        self.loaded_containers = {}
        self.currently_shown_box_name = None

        if ret > 0:
            for module in self.modules:
                if module['name'] in self.loaded_boxes:
                    module["callback"]()
            for plugin in self.plugins:
                if plugin['name'] in self.loaded_boxes:
                    plugin["callback"]()

        for box in self.loaded_boxes:
            self.loaded_boxes[box].destroy()
        self.dialog.destroy()

    ## Register a preferences page
    # use this for your plugins
    # @param self The Object Pointer
    # @param name Name to show (your plugin's name). Please use
    # your real plugins directoryname - you may change
    # capitalization
    # @param func A function that returns a container (e.g. vbox)
    # with all your widgets in it.
    # @param cb A function to call when the preferences are saves
    def register_plugin(self, name, func, cb, caption=None):
#        if not isinstance(container, gtk.Container):
#            raise Exception, "The container you add must be a subclass " \
#            "of gtk.Container - Try gtk.VBox() for example."
#            return -1
        if caption is None: 
            caption = "%s %s" % (name.capitalize(), _("Preferences"))
        for plugin in self.plugins:
            if plugin['name'] == name:
                self.pyjama.Events.raise_event("error", None, "You tried to add a plugin named '%s' to the preferences dialog. A plugin with this name is already existant." % name)
                return
        ret = {"name":name, "func":func, "callback":cb, "caption":caption}
        self.plugins.append(ret)
        return ret

    ## Register a preferences page for builtin preferences
    # Use register_plugin() instead.
    # use this for your plugins
    # @param self The Object Pointer
    # @param name Name to show (your plugin's name)
    # @param func A function that returns a container (e.g. vbox)
    # with all your widgets in it.
    # @param cb A function to call when the preferences are saves
    def register_module(self, name, func, cb, caption=None):
#        if not isinstance(container, gtk.Container):
#            raise Exception, "The container you add must be a subclass " \
#            "of gtk.Container - Try gtk.VBox() for example."
#            return -1
        if caption is None:
            caption = "%s %s" % (name.capitalize(), _("Preferences"))
        for module in self.modules:
            if module['name'] == name:
                self.pyjama.Events.raise_event("error", None, "You tried to add a module named '%s' to the preferences dialog. A module with this name is already existant." % name)
                return
        ret = {"name":name, "func":func, "callback":cb, "caption":caption}
        self.modules.append(ret)
        return ret

    ## Use this to check if a certain plugin 
    # has registered a preferences page
    # @param self OP
    # @param name The plugin's name
    # @return Boolean
    def has_preferences(self, name):
        for plugin in self.plugins:
            if plugin['name'].lower() == name.lower():
                return True
        return False

    ## Compute which item belongs to a certain path
    # and shows it
    # Internal methode
    # @param widget Container to show
    # @param path Path that has been selected
    def __show_items_pref(self, widget, path):
        if path:
            iter = widget.get_model().get_iter(path)
        else:
            return

        title = widget.get_model().get_value(iter, 0)
#        if title == PLUGIN_STRING:
#            self.show_box(module['container'])
#            return
        for module in self.modules:
            if module['name'] == title:
                self.show_box(module)
                return
        for pref in self.plugins:
            if pref['name'] == title:
                self.show_box(pref)
                return

    ## finds a preferences box when only the plugin-string
    # is known
    def find_box(self, name):
        for plugin in self.plugins:
            if plugin['name'].lower() == name.lower():
                self.show_box(plugin)
        for module in self.modules:
            if module['name'].lower() == name.lower():
                self.show_box(module)

    ## Show a certain Container
    # as a preferences page
    def show_box(self, box):
        name = box['name']
        container = box['func']()
        caption = box['caption']

        if name == self.currently_shown_box_name: 
            return
        ch = self.viewport.get_child()
        if ch:
            self.viewport.remove(ch)
        if name in self.loaded_boxes:
            self.viewport.add(self.loaded_boxes[name])
        else:
            self.loaded_boxes[name] = container
            self.viewport.add(self.loaded_boxes[name])
        self.caption.set_markup('<span font_desc="Arial Italic 16" font_weight="bold">%s</span>' % caption)

#        ch = self.viewport.get_child()
#        if ch:
#            self.loaded_containers[self.currently_shown_box_name] = ch
#            self.viewport.remove(ch)
#        if name in self.loaded_containers:
#            self.viewport.add(self.loaded_containers[name])
#            print "old"
#        else:
#            self.viewport.add(box)
#            print "new"
        self.currently_shown_box_name = name


    #
    # Callbacks
    #
    def cb_treeview_row_activated(self, treeview, path, view_column):
        self.__show_items_pref(treeview, path)

    def cb_treeview_button_press(self, widget, event):
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        if path is not None:
            self.__show_items_pref(widget, path[0])


#if __name__ == "__main__":
#    p = Preferences()
#    class plugin_pref():
#        def __init__(self):
#            self.vbox = gtk.VBox()
#            l = gtk.Label("Dies ist ein Plugin-test")
#            l.show()
#            self.vbox.pack_start(l)
#            self.vbox.show()

#        def save_preferences(self):
#            print "Hallo"
#    ppref = plugin_pref()
#    p.register_plugin("Plugin1", ppref.vbox, ppref.save_preferences)

#    p.show_preferences()
