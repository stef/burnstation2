#!/usr/bin/env python

## @package ExamplePlugin
# Example Plugin Module.
# Every single plugin needs to come as a module in a directory.
# Every folder containing a file named "FOLDERNAME.info"
# will be recogniced as a plugin.
# Furthermore the folder needs to contain a file "__init__.py"
# which holds a class named "main".
# When loading a plugin pyjama will pass the object "pyjama"
# which holds all the other objects.
#
# For more informations have a look at the <a href = "Plugins.html"><b>plugin interface.</b></a> 

try:
    import gtk
except:
    print "Error: Gtk not found"
    raise

## Example Plugin class main called by Pyjama
class main():
    ## The Constructor
    # @param self Object pointer
    # @param pyjama Reference to the pyjama object
    def __init__(self, pyjama):
        ## Here we store the pyjama object reference
    	self.pyjama = pyjama

        # Let's register a preferences page:
        self.pyjama.preferences.register_plugin("Example", self.create_preferences, self.save_preferences)

        ## You cannot directly access the plugins
        # object of pyjama in your init function
        # since it is created after all plugins
        # have been initialised.
        # Following line will fail:\n
        # <i>plugins = self.pyjama.plugins</i> <-- ERROR\n
        # Connect to the <a href = "Events.html">"alldone"</a> event, if you
        # want pyjama to call your plugin after
        # everythin else is done!
        self.Events = self.pyjama.Events
        self.Events.connect_event("alldone", self.ev_alldone)

    

    ## This function will be called after pyjama
    # has been loaded and you have connected to
    # the "alldone" event
    # Now you can access any other plugins...
    def ev_alldone(self):
        if "nowplaying" in self.pyjama.plugins.loaded:
            # print "Plugin 'nowplaying' can be found!'
            pass 

    ## This function creates a vbox,
    # puts some widgets on it and returns
    # it.
    # @param self Object Pointer
    def create_preferences(self):
        # get some infos about the plugin
        plugin_infos = self.pyjama.plugins.plugins_by_name["example"]
        txt = "This is an exmaple preferences dialog\nor at least could be one.\nI can tell you something about me:\n\nAuthor: %s\nName: %s\nDescription: %s" % (plugin_infos['author'], plugin_infos['name'], plugin_infos['description'])

        #
        # Create the vbox and some widgets
        #
        vbox = gtk.VBox()
        
        lbl = gtk.Label()
        lbl.set_markup(txt)
        
        # as I need to access the entry widget
        # when the values needs to be saved,
        # i connect it to the class-object
        self.entry = gtk.Entry()
        self.entry.set_text("I am the default text")

        vbox.pack_start(lbl, False, True, 10)
        vbox.pack_start(self.entry, False, False, 10)

        vbox.show_all()
        return vbox

    ## Will be called when the user closed
    # the preferences dialog with "ok" and
    # when this plugin's vbox was shown before.
    # @param self Object Pointer
    def save_preferences(self):
        print("'%s' was entered into the entry-widget" % self.entry.get_text())

        # We could now also save this value:
        #self.pyjama.settings.set_value("EXAMPLE_PLUGIN", "entry_value", self.entry.get_text())

        
        
