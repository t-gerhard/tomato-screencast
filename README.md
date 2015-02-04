# tomato-screencast

This project includes the source files and final output of the screencasts which will be used to demonstrate ToMaTo.

## the sources directory

Each screencast has a subdirectory.
This contains all sources, and the compiled versions of these (i.e., video files). It does not need to contain these in different formats.

In this directory, there is a json file of the same name as its directory, The descriptor file. This lists all files which will be included in the published version. The descriptor is of the format:

```
{
  "title": "Human-Readable screencast title",
  "description": "description text for the screencast. What is this about?",
  "video_file": "filename of the raw video, which will be converted to the required formats",
  "tracks": [], #undefined. Will include some tracks like chapters or subtitles
  "downloads": [] #undefined. Will include files used by the tutorial for the user to download
}
```

## build.py
Depends on the avconv command to be installed on the computer.
usage: build.py -i [directory in sources] -t [target directory]

## the output of the builder

It creates a directory containing all media for each screencast. It additionally creates a descriptor file in the following format:
```
{
  "title": "Basic Usage",
  "description": "Create and start your first topology.",
  "sources": [
              {"src": "basic.webm", 
               "type": "video/webm"}
             ],
  "tracks": [], #undefined
  "downloads": [] #undefined
}
```
