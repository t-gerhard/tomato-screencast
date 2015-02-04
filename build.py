#!/usr/bin/python
__author__ = 't-gerhard'
import os
import shutil
import subprocess
import sys
import json
import argparse
import inspect

basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def avconv(inputfilename, outputfilename):
    cmd = ['avconv', '-i', inputfilename, outputfilename]
    print " ".join(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), ''):
        sys.stdout.write(c)
    errcode = process.returncode
    return errcode


class ScreencastBuilder:
    tracks = []
    video_formats = []
    downloads = []
    descriptor_content = {'tracks': [], 'sources': [], 'downloads': []}

    # key: the key this is referenced to.
    # title: onscreen title of the screencast
    # description: description of the screencast
    # input_video_file: video file to use as source
    # target_dir: the target dir. files will be saved in target_dir/key/ and target_dir/key.json
    def __init__(self, key, title, description, input_video_file, target_dir):
        self.key = key
        self.descriptor_content['title'] = title
        self.descriptor_content['description'] = description
        self.input_video_filename = input_video_file
        self.target_dir = target_dir

    #convert the video
    def _create_video_format(self, form):
        print "Converting to %s" % form
        input = self.input_video_filename
        (outputfilename, _) = os.path.splitext(os.path.basename(input))
        outputfilename += (".%s" % form)
        output = os.path.join(self.media_dir, outputfilename)
        avconv(input, output)
        return outputfilename

    #prepare all target directories so that files can be written directly.
    def _prepare_dir(self):
        self.media_dir = os.path.join(self.target_dir, self.key)
        assert not os.path.exists(self.media_dir)
        os.makedirs(self.media_dir)

    #copy all tracks to the media directory
    def _copy_tracks(self):
        for track in self.tracks:
            trackfilename = os.path.basename(track['filename'])
            print "Copying track %s" % trackfilename
            shutil.copy(track['filename'],os.path.join(self.media_dir, trackfilename))
            desc_entry={'src': trackfilename, 'default': track['default'], 'kind': track['kind']}
            desc_entry.update(track['data'])
            self.descriptor_content['tracks'].append(desc_entry)

    #copy all downloads to the media directory.
    def _copy_downloads(self):
        for dl in self.downloads:
            filename = os.path.basename(dl['filename'])
            print "Copying download %s" % filename
            shutil.copy(dl['filename'], os.path.join(self.media_dir, filename))
            self.descriptor_content['downloads'].append({'title': dl['title'], 'src': filename})

    #write the descriptor file. should be the final action.
    def _write_descriptor(self):
        print "Writing descriptor file"
        with open(os.path.join(self.target_dir, "%s.json" % key), "w+") as f:
            f.write(json.dumps(self.descriptor_content))
        print "Done."




    # add a track to the screencast
    # kind: kind of the track
    # data: additional HTML5 data. Should not contain the keys src, default, kind
    # filename: src of the track
    # default: if True, set track as default in player
    def add_track(self, kind, data, filename, default):
        sub = {'kind': kind, 'data': data, 'filename': filename, 'default': default}
        self.tracks.append(sub)

    # add a video format
    # extension: filename extension. should not start with ".". Example: "mp4"
    # mimetype: MIME type. example: "video/mp4"
    def add_video_format(self, extension, mimetype):
        self.video_formats.append({'mimetype': mimetype, 'extension': extension})

    def add_downloadable_content(self, title, filename):
        self.downloads.append({'title': title, 'filename': filename})

    # convert videos, copy files, etc.
    def build(self):
        self._prepare_dir()
        for form in self.video_formats:
            filename = self._create_video_format(form['extension'])
            self.descriptor_content['sources'].append({'type': form['mimetype'], 'src': filename})
        self._copy_tracks()
        self._copy_downloads()
        self._write_descriptor()



def build_screencast(key, target_dir):
    print "Creating '%s' at '%s'" % (key, target_dir)
    screencast_root = os.path.join(basedir, "sources", key)
    with open(os.path.join(screencast_root, "%s.json" % key), "r") as f:
        descriptor = json.loads(f.read())
    video_filename = os.path.join(screencast_root, descriptor['video_file'])
    builder = ScreencastBuilder(key=key, title=descriptor['title'], description=descriptor['description'], input_video_file=video_filename, target_dir=target_dir)
    for form in target_formats:
        builder.add_video_format(form['extension'], form['mimetype'])
    #TODO: add downloads, tracks
    builder.build()



def parseArgs():
    parser = argparse.ArgumentParser(prog="Screencasts Builder",
                                     description="Converts videos, copies tracks and downloads, and puts them into a final format for the player",
                                     add_help=False)
    parser.add_argument('--help', action='help')
    parser.add_argument("--screencast" , "-i", required=True, help="Screencast directory in sources")
    parser.add_argument("--targetdir", "-t", required=True, help="The target directory. The output will be created in a subfolder specified via --i")
    options = parser.parse_args()
    return options


target_formats = [{'extension': "webm", 'mimetype': "video/webm"}]
opts = parseArgs()
key = opts.screencast
target_dir = opts.targetdir
build_screencast(key, target_dir)

