Audiogrep
=========

Audiogrep transcribes audio files and then creates "audio supercuts" based on search phrases. It uses [CMU Pocketsphinx](http://cmusphinx.sourceforge.net/) for speech-to-text and [pydub](http://pydub.com/) to stitch things together.

Here's some [sample output](http://lav.io/2015/02/audiogrep-automatic-audio-supercuts/).

## Requirements
Install using pip
```
pip install audiogrep
```
Install [ffmpeg](http://ffmpeg.org/) with Ogg/Vorbis support. If you're on a mac with [homebrew](http://brew.sh/) you can install ffmpeg with:
```
brew install ffmpeg --with-libvpx --with-libvorbis
```
Finally, install [CMU Pocketsphinx](http://cmusphinx.sourceforge.net/). For mac
users I followed [these instructions](https://github.com/watsonbox/homebrew-cmu-sphinx) to get it working:
```
brew tap watsonbox/cmu-sphinx
brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxbase
brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxtrain # optional
brew install --HEAD watsonbox/cmu-sphinx/cmu-pocketsphinx
```

## How to use it
First, transcribe the audio (you'll only need to do this once per audio track, but it can take some time)
```
# transcribes all mp3s in the selected folder
audiogrep --input path/to/*.mp3 --transcribe
```
Then, basic use:
```
# returns all phrases with the word 'word' in them
audiogrep --input path/to/*.mp3 --search 'word'
```
The previous example will extract phrase chunks containing the search term, but you can also just get individual words:
```
audiogrep --input path/to/*.mp3 --search 'word' --output-mode word
```
If you add the '--regex' flag you can use regular expressions. For example:
```
# creates a supercut of every instance of the words "spectre", "haunting" and "europe"
audiogrep --input path/to/*.mp3 --search 'spectre|haunting|europe' --output-mode word --regex
```
You can also construct 'frankenstein' sentences (mileage may vary):
```
# stupid joke
audiogrep --input path/to/*.mp3 --search 'my voice is my passport' --output-mode franken
```
Or you can just extract individual words into files.
```
# extracts each individual word into its own file in a directory called 'extracted_words'
audiogrep --input path/to/*.mp3 --extract

Exporting to: extracted_words/i.mp3
Exporting to: extracted_words/am.mp3
Exporting to: extracted_words/the.mp3
Exporting to: extracted_words/key.mp3
Exporting to: extracted_words/master.mp3
```

### Options

audiogrep can take a number of options:

#### --input / -i
mp3 file or pattern for input

#### --output / -o
Name of the file to generate. By default this is "supercut.mp3"

#### --search / -s
Search term

#### --output-mode / -m
Splice together phrases, single words, fragments with wildcards, or "frankenstein" sentences.
Options are:
* sentence: (this is the default)
* word
* fragment
* franken

#### --padding / -p
Time in milliseconds to add between audio segments. Default is 0.

#### --crossfade / -c
Time in milliseconds to crossfade audio segments. Default is 0.

#### --extract / -x

#### --demo / -d
Show the results of the search without outputing a file
