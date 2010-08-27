#!/usr/bin/env python

import re, sys
import os, os.path
import mp3info, ogg.vorbis, functions
from string import replace
from popen2 import popen3
from time import sleep
if (sys.platform != "win32"):
    from popen2 import Popen3


logPath=os.path.join(functions.install_dir(), "log")
spoolPath=os.path.join(functions.install_dir(), "spool")
tmpPath=os.path.join(functions.install_dir(), "tmp/")
logfile = 'decoder.log'
RE=re.compile('cdrskin: Media : (.*)')

class Logger:
    def debug(self,msg):
        print 'debug-',msg
    def error(self,msg):
        print 'error-',msg
    def info(self,msg):
        print 'info-',msg
    def warn(self,msg):
        print 'warn-',msg
logger=Logger()

def cmdexec(cmd):
    """ Executes a command in a subshell and returns (return_value, (stdout, stderr)). """

    my_popen3 = Popen3(cmd, True)

    # wait until the sub process has finished
    while (my_popen3.poll() == -1):
        sleep(0.01)

    stderr_output = my_popen3.fromchild.readlines()
    stdout_output = my_popen3.childerr.readlines()

    # read the result value
    result = my_popen3.poll()
    if (my_popen3.fromchild != None):
        my_popen3.fromchild.close()
    if (my_popen3.childerr != None):
        my_popen3.childerr.close()
    if (my_popen3.tochild != None):
        my_popen3.tochild.close()

    return (result, (stdout_output, stderr_output))

def escapedfilename(filename):
    """ escapes special characters in filenames (currently "`") """
    filename = replace(filename, "`", "\`")
    return filename

class Decoder:
    def __init__(self):
        """ Converts mp3/ogg-files to wav-files. """
        pass

    def convert2wav(self, files, targetPath):
        """walk files list and apply decode() to each"""

        res=[]
        i = 0
        for source in files:
            target = targetPath + "/" + str(i) + ".wav"
            logger.info("Decoding %s to %s ..." % (source, target))
            self.decode(source, target)
            res.append(target)
            i += 1

        logger.info("Decoding finished")
        return res

    def decode(self, filename, target):
        """decode a file to wav"""
        if not os.path.isfile(filename):
            logger.error("Decoding failed: %s not found" % filename)
            return False

        mp3count = 0
        if (filename[-4:].lower() == ".mp3"):
            mp3count = mp3count + 1

        # Check whether mpg123 and oggdec exists
        mpg123_command = "/usr/bin/mpg123"
        if (mp3count > 0):
            if (filename[-4:].lower() == ".mp3"):
                # Make sure that conversion is done with the correct sample rate
                file = open(filename, "rb")
                mpeg3info = mp3info.MP3Info(file)
                file.close()
                samplerate = mpeg3info.mpeg.samplerate
                command = "(%s --stereo -w \"%s\" \"%s\") 2>&1" % (mpg123_command, escapedfilename(target), escapedfilename(filename))
            (result, (stdout_output, stderr_output)) = cmdexec(command)
            #logger.info("res: %s, output\n%s\n%s" % (result, "\n".join(stdout_output), "\n".join(stderr_output)))
            logger.debug("res: %s" % (result))

            if (result != 0):
                return False
            else: return True

class Burner():
    def __init__(self):
        #logger.debug("starting burner")
        self.decodelog = logPath + "/decoder.log"
        if os.path.isfile(self.decodelog): os.unlink(self.decodelog)

        self.burnlog   = logPath + "/burn.log"
        if os.path.isfile(self.burnlog): os.unlink(self.burnlog)

        self.Burning    = False
        self.Finished   = False

        self.burning  = False
        self.decoding = False

        # make sure the temp (spool) dir is clean before we start
        self.Cleanup()
    #--------------------------------------------------------------------
    def GetStatus(self):
        if not self.decoding and not self.burning: return
        if self.decoding: return self.GetDecodingStatus()
        elif self.burning: return self.GetBurningStatus()

    #--------------------------------------------------------------------
    def GetDecodingStatus(self):
        # TODO fix this - if necessary
        return _("Decoding to wav")
        #try:
        #    log = open(self.decodelog)
        #    #logger.debug5("GetDecodingStatus() opened decode log: %s" % log)
        #    lines = log.readlines()
        #    lines_count = len(lines)
        #    try:
        #        line = lines[lines_count-1].strip()
        #        line_length = len(line)
        #        status = line
        #        if status == 'Decoding finished':
        #            self.decoding = False
        #            self.burning = True
        #            os.unlink(self.decodelog)
        #    except Exception, e:
        #        logger.warn("Impossible to read lines from decode log: %s" % str(e))
        #    log.close()
        #    return status
        #except Exception, e:
        #    logger.warn("Decode log file not accessible: %s" % str(e))

    #--------------------------------------------------------------------
    def GetBurningStatus(self):
        if not self.burning or not os.path.isfile(self.burnlog): return
        log = open(self.burnlog)
        lines = log.readlines()
        lines_count = len(lines)
        amount = 64
        status=""
        try:
            line = lines[lines_count-1].strip()
            line_length = len(line)
            status = line[line_length-amount:line_length]
            #logger.info(status)
            if status == 'BURN-Free was never needed.':
                self.burning = False
                status = 'Finished burning! Please, take your CD.'
                self.Finished = True
            if self.Finished:
                self.Cleanup()
                os.unlink(self.burnlog)
        except Exception, e:
            logger.warn("burning log file not accessible: %s" % str(e))
        """
        for line in lines:
            line_length = len(line)
            print line[line_length-amount:line_length][lines_count-10]
        """
        log.close()
        return status

    #--------------------------------------------------------------------
    def BurnCD(self, tracks, mode='DATA'):
        # if there is no CD, do not start burning
        if not self.cdIsWritable()[0]: return

        track_count = len(tracks)

        if mode == 'AUDIO':
            self.decoding = True
            t=Decoder().convert2wav(tracks,tmpPath)
            self.decoding = False
        elif mode == 'DATA' :
            t=tracks
        self.burning = True
        self.burnCD(t,mode)
        #self.Cleanup()

    #--------------------------------------------------------------------
    def cdIsWritable(self):
        status = os.system("cdrskin --tell_media_space >" + self.burnlog + " 2>" + self.burnlog)
        if not os.path.isfile(self.burnlog): return
        log = open(self.burnlog)
        lines = log.readlines()
        log.close()
        os.unlink(self.burnlog)
        try:
            return (True,int(lines[0].strip())) # *2048)/(1024*1024)
        except Exception, e:
            pass
        for line in lines:
            m=RE.search(line)
            if m:
                return (False,m.group(1))
        return (None,"")

    def BlankCD(self):
        os.system("cdrskin blank=as_needed")
        #os.system("cdrskin blank=as_needed 2>" + self.burnlog)
        #log = open(self.burnlog)
        #lines = log.readlines()
        #print lines
        #log.close()
        #os.unlink(self.burnlog)

    def Cleanup(self):
        temp_files = os.listdir(spoolPath)
        logger.debug("Found temp files: %s" % str(temp_files))
        for f in temp_files:
            file = spoolPath + '/' + f
            logger.debug("Removing file: %s" % file)
            try: os.unlink(file)
            except Exception, e: logger.error("EXCEPTION occurred while trying to cleanup spool dir: %s" % str(e))

    def burnCD(self,tracks,mode='AUDIO'):
        #-----------------------------------------------------------
        cdrecord_cmd_args = ' -v'
        cdrecord_cmd_args += ' -driveropts=burnfree'
        cdrecord_cmd_args += ' -eject'
        #-----------------------------------------------------------
        if mode == 'AUDIO':
            count = len(tracks)
            tracks_list = " ".join(tracks)
            cdrecord_cmd = "(cdrskin %s -sao -swab -pad %s) " % (cdrecord_cmd_args, tracks_list)
            logger.info("Executing cdrecord with the following options: %s" % cdrecord_cmd)
            CdrecordStatus = os.system(cdrecord_cmd + " > " + logPath + "/burn.log 2> " + logPath + "/burn.err")
        elif mode == 'DATA':
            # join tracks array for command line
            tracks_list = '"' + '" "'.join(tracks) + '"'
            # define where to dump the created .iso to be burnt
            ISOfile = spoolPath + '/burnstation.iso'
            logger.debug("*** ISOfile: %s" % ISOfile)

            # prepare mkisofs command to create image
            mkiso_cmd = 'mkisofs -R -o'
            mkiso_cmd += ' ' + ISOfile
            mkiso_cmd += ' -graft-points ' + tracks_list

            logger.debug("* Running mkisofs: %s" % mkiso_cmd)

            # now run it
            mkisoResult = os.system(mkiso_cmd + " > " + logPath + "/burn.log 2> " + logPath + "/burn.err")
            logger.debug('* mkisoResult: %s' % mkisoResult)

            cdrecord_cmd = "cdrskin %s -eject -data %s" % (cdrecord_cmd_args, ISOfile)
            logger.debug("* Running cdrskin: %s" % cdrecord_cmd)
            CdrecordStatus = os.system(cdrecord_cmd + " > " + logPath + "/burn.log 2> " + logPath + "/burn.err")

if __name__ == "__main__":
    a=Burner()
    #(isWritable,msg)=a.cdIsWritable()
    #print msg
    #a.BlankCD()
    #(isWritable,msg)=a.cdIsWritable()
    #print msg
    #if True:
    #    a.BurnCD(tracks, 'AUDIO')
    a.GetStatus()
    a.GetStatus()
