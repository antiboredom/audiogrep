Audiogrep
=========

Audiogrep transcribes audio files and then creates "audio supercuts" based on search phrases. It uses [CMU Pocketsphinx](http://cmusphinx.sourceforge.net/) for speech-to-text and [pydub](http://pydub.com/) to stitch things together.

##Requirements
Clone this repository, and then install the other requirements.
```
pip install -r requirements.txt
```

Install [ffmpeg](http://ffmpeg.org/) with Ogg/Vorbis support. If you're on a mac with [homebrew](http://brew.sh/) you can install ffmpeg with:
```
brew install ffmpeg --with-libvpx --with-libvorbis
```

Install [CMU Pocketsphinx](http://cmusphinx.sourceforge.net/). For mac
users I followed [these instructions](https://github.com/watsonbox/homebrew-cmu-sphinx) to get it working:
```
brew tap watsonbox/cmu-sphinx
brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxbase
brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxtrain # optional
brew install --HEAD watsonbox/cmu-sphinx/cmu-pocketsphinx
```

##How to use it
First, transcribe the audio (you'll only need to do this once per audio track, but it can take some time)
```
# transcribes all mp3s in the selected folder
python audiogrep.py --input path/to/*.mp3 --transcribe
```
Then, basic use:
```
# returns all phrases with the word 'word' in them
python audiogrep.py --input path/to/*.mp3 --search 'word'
```
The previous example will extract phrase chunks containing the search term, but you can also just get individual words:
```
python audiogrep.py --input path/to/*.mp3 --search 'word' --output-mode word
```
If you add the '--regex' flag you can use regular expressions. For example:
```
# creates a supercut of every instance of the words "spectre", "haunting" and "europe"
python audiogrep.py --input path/to/*.mp3 --search 'spectre|haunting|europe' --output-mode word
```
You can also construct 'frankenstein' sentences (mileage may vary):
```
# stupid joke
python audiogrep.py --input path/to/*.mp3 --search 'my voice is my passport' --output-mode franken
```

###Options

audiogrep can take a number of options:

####--input / -i
mp3 file or pattern for input

####--output / -o
Name of the file to generate. By default this is "supercut.mp3"

####--search / -s
Search term

####--output-mode / -m
Splice together phrases, single words, or "frankenstein" sentences.
Options are:
* sentence: (this is the default)
* word
* franken

####--padding / -p
Time in milliseconds to add between audio segments. Default is 0.

####--crossfade / -c
Time in milliseconds to crossfade audio segments. Default is 0.

####--demo / -d
Show the results of the search without outputing a file
