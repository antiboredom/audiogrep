#!/usr/bin/env python

# requires ffmpeg and pocketsphinx
# for macs, install pocketsphix with brew following these instructions: https://github.com/watsonbox/homebrew-cmu-sphinx
# $ brew tap watsonbox/cmu-sphinx
# $ brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxbase
# $ brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxtrain # optional
# $ brew install --HEAD watsonbox/cmu-sphinx/cmu-pocketsphinx

from __future__ import print_function

import sys
import os
import subprocess
import argparse
import re
import random
from pydub import AudioSegment


def convert_to_wav(files):
    '''Converts files to a format that pocketsphinx can deal wtih (16khz mono 16bit wav)'''
    converted = []
    for f in files:
        new_name = f + '.temp.wav'
        print(new_name)
        if (os.path.exists(f + '.transcription.txt') is False) and (os.path.exists(new_name) is False):
            subprocess.call(['ffmpeg', '-y', '-i', f, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', new_name])
        converted.append(new_name)
    return converted


def transcribe(files=[], pre=10, post=50):
    '''Uses pocketsphinx to transcribe audio files'''

    total = len(files)

    for i, f in enumerate(files):
        filename = f.replace('.temp.wav', '') + '.transcription.txt'

        if os.path.exists(filename) is False:
            print(str(i+1) + '/' + str(total) + ' Transcribing ' + f)
            transcript = subprocess.check_output(['pocketsphinx_continuous', '-infile', f, '-time', 'yes', '-logfn', '/dev/null', '-vad_prespeech', str(pre), '-vad_postspeech', str(post)])

            with open(filename, 'w') as outfile:
                outfile.write(transcript)

            os.remove(f)


def words_json(sentences):
    import json
    out = []
    for s in sentences:
        for word in s['words']:
            try:
                start = float(word[1])
                end = float(word[2])
                confidence = float(word[3])
                out.append({'start': start, 'end': end, 'word': word[0]})
            except:
                continue
    return json.dumps(out)



def convert_timestamps(files):
    '''Converts pocketsphinx transcriptions to usable timestamps'''

    sentences = []

    for f in files:

        if not f.endswith('.transcription.txt'):
            f = f + '.transcription.txt'

        if os.path.exists(f) is False:
            continue

        with open(f, 'r') as infile:
            lines = infile.readlines()

        lines = [re.sub(r'\(.*?\)', '', l).strip().split(' ') for l in lines]
        lines = [l for l in lines if len(l) == 4]

        seg_start = -1
        seg_end = -1

        for index, line in enumerate(lines):
            word, start, end, conf = line
            if word == '<s>' or word == '<sil>' or word == '</s>':
                if seg_start == -1:
                    seg_start = index
                    seg_end = -1
                else:
                    seg_end = index

                if seg_start > -1 and seg_end > -1:
                    words = lines[seg_start+1:seg_end]
                    start = float(lines[seg_start][1])
                    end = float(lines[seg_end][1])
                    if words:
                        sentences.append({'start': start, 'end': end, 'words': words, 'file': f})
                    if word == '</s>':
                        seg_start = -1
                    else:
                        seg_start = seg_end
                    seg_end = -1

    return sentences


def text(files):
    '''Returns the whole transcribed text'''
    sentences = convert_timestamps(files)
    out = []
    for s in sentences:
        out.append(' '.join([w[0] for w in s['words']]))
    return '\n'.join(out)


def search(query, files, mode='sentence', regex=False):
    '''Searches for words or sentences containing a search phrase'''
    out = []
    sentences = convert_timestamps(files)

    if mode == 'fragment':
        out = fragment_search(query, sentences, regex)
    elif mode == 'word':
        out = word_search(query, sentences, regex)
    elif mode == 'franken':
        out = franken_sentence(query, files)
    else:
        out = sentence_search(query, sentences, regex)


    return out


def extract_words(files):
    ''' Extracts individual words form files and exports them to individual files. '''
    output_directory = 'extracted_words'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for f in files:
        file_format = None
        source_segment = None
        if f.lower().endswith('.mp3'):
            file_format = 'mp3'
            source_segment = AudioSegment.from_mp3(f)
        elif f.lower().endswith('.wav'):
            file_format = 'wav'
            source_segment = AudioSegment.from_wav(f)
        if not file_format or source_segment:
            print('Unsupported audio format for ' + f)
        sentences = convert_timestamps(files)
        for s in sentences:
            for word in s['words']:
                start = float(word[1]) * 1000
                end = float(word[2]) * 1000
                word = word[0]
                total_time = end - start
                audio = AudioSegment.silent(duration=total_time)
                audio = audio.overlay(source_segment[start:end])
                number = 0
                output_path = None
                while True:
                    output_filename = word
                    if number:
                        output_filename += "_" + str(number)
                    output_filename = output_filename + '.' + file_format
                    output_path = os.path.join(output_directory, output_filename)
                    if not os.path.exists(output_path):
                        # this file doesn't exist, so we can continue
                        break
                    # file already exists, increment name and try again
                    number += 1
                print('Exporting to: ' + output_path)
                audio.export(output_path, format=file_format)


def fragment_search(query, sentences, regex):

    def check_pattern(pattern, test):
        if len(test) != len(pattern):
            return False

        found = True
        for p, t in zip(pattern, test):
            if (p != t and p != '*') or t == "[NOISE]":
                found = False
        return found


    query = query.split('|')
    query = [phrase.split(' ') for phrase in query]
    words = []
    for s in sentences:
        for w in s['words']:
            w.append(s['file'])
            words.append(w)

    segments = []

    for i in range(0, len(words)):
        for pattern in query:
            tester = [w[0] for w in words[i: i+len(pattern)]]
            if check_pattern(pattern, tester):
                try:
                    st = float(words[i][1])
                    en = float(words[i+len(pattern)-1][2])
                    if words[i][-1] == words[i+len(pattern)-1][-1] and en-st < 5:
                        filename = words[i][-1]
                        item = {'file': filename, 'start': st, 'end': en, 'words': tester}
                        if not any(s['start'] == st and s['end'] == en for s in segments):
                            segments.append(item)
                except:
                    print('failed', words[i])
                    continue
    return segments


def words(sentences):
    out = []
    for s in sentences:
        for word in s['words']:
            start = float(word[1])
            end = float(word[2])
            out.append({'start': start, 'end': end, 'file': s['file'], 'word': word[0]})
    return out


def word_search(query, sentences, regex):
    out = []
    for s in sentences:
        for word in s['words']:
            found = False
            if regex:
                found = re.search(query, word[0])
            else:
                if query.lower() == word[0]:
                    found = True
            if found:
                try:
                    start = float(word[1])
                    end = float(word[2])
                    confidence = float(word[3])
                    out.append({'start': start, 'end': end, 'file': s['file'], 'words': word[0], 'confidence': confidence})
                except:
                    continue
    return out


def sentence_search(query, sentences, regex):
    out = []
    for s in sentences:
        words = [w[0] for w in s['words']]
        found = False
        if regex:
            found = re.search(query, ' '.join(words))
        else:
            if query.lower() in words:
                found = True
        if found:
            out.append(s)
    return out


def franken_sentence(sentence, files):
    w_results = {}
    out = []
    for word in sentence.split(' '):
        if word in w_results:
            results = w_results[word]
        else:
            results = search(word, files, mode='word')
            w_results[word] = results
        if len(results) > 0:
            #sorted(results, key=lambda k: k['confidence'])
            #out = out + [results[0]]
            out = out + [random.choice(results)]

    return out


def silences(files, min_duration=None, max_duration=None):
    out = []
    for f in files:
        if not f.endswith('.transcription.txt'):
            f = f + '.transcription.txt'

        with open(f, 'r') as infile:
            lines = infile.readlines()

        for line in lines:
            if line.startswith('<sil>'):
                word, start, end, conf = line.split(' ')
                seg = {
                    'start': float(start),
                    'end': float(end),
                    'word': '<SILENCE>',
                    'file': f
                }
                duration = seg['end'] - seg['start']
                if min_duration and duration < min_duration:
                    continue
                if max_duration and duration > max_duration:
                    continue
                out.append(seg)
    return out


def compose(segments, out='out.mp3', padding=0, crossfade=0, layer=False):
    '''Stiches together a new audiotrack'''

    files = {}

    working_segments = []

    audio = AudioSegment.empty()

    if layer:
        total_time = max([s['end'] - s['start'] for s in segments]) * 1000
        audio = AudioSegment.silent(duration=total_time)

    for i, s in enumerate(segments):
        try:
            start = s['start'] * 1000
            end = s['end'] * 1000
            f = s['file'].replace('.transcription.txt', '')
            if f not in files:
                if f.endswith('.wav'):
                    files[f] = AudioSegment.from_wav(f)
                elif f.endswith('.mp3'):
                    files[f] = AudioSegment.from_mp3(f)

            segment = files[f][start:end]

            print(start, end, f)

            if layer:
                audio = audio.overlay(segment, times=1)
            else:
                if i > 0:
                    audio = audio.append(segment, crossfade=crossfade)
                else:
                    audio = audio + segment

            if padding > 0:
                audio = audio + AudioSegment.silent(duration=padding)

            s['duration'] = len(segment)
            working_segments.append(s)
        except:
            continue

    audio.export(out, format=os.path.splitext(out)[1].replace('.', ''))
    return working_segments


def main():
    parser = argparse.ArgumentParser(description='Audiogrep: splice together audio based on search phrases')

    parser.add_argument('--input', '-i', dest='inputfile', required=True, nargs='*', help='Source files to search through')
    parser.add_argument('--search', '-s', dest='search', help='Search term - to use a regular expression, use the -re flag')
    parser.add_argument('--regex', '-re', dest='regex', help='Use a regular expression for search', action='store_true')
    parser.add_argument('--output-mode', '-m', dest='outputmode', default='sentence', choices=['sentence', 'word', 'franken'], help='Splice together phrases, or single words, or "frankenstein" sentences')
    parser.add_argument('--output', '-o', dest='outputfile', default='supercut.mp3', help='Name of output file')
    parser.add_argument('--transcribe', '-t', dest='transcribe', action='store_true', help='Transcribe audio files')
    parser.add_argument('--extract', '-x', dest='extract', help='Extract all individual words from an audio file and write them to disk.', action='store_true')
    parser.add_argument('--padding', '-p', dest='padding', type=int, help='Milliseconds of padding between the audio segments')
    parser.add_argument('--crossfade', '-c', dest='crossfade', type=int, default=0, help='Crossfade between clips')
    parser.add_argument('--demo', '-d', dest='demo', action='store_true', help='Just display the search results without actually making the file')
    parser.add_argument('--layer', '-l', dest='layer', action='store_true', help='Overlay the audio segments')
    parser.add_argument('--json', '-j', dest='json', action='store_true', help='Output words to json')

    args = parser.parse_args()

    if not args.search and not args.transcribe and not args.json and not args.extract:
        parser.error('Please transcribe files [--transcribe] or search [--search SEARCH] already transcribed files')

    if args.transcribe:
        try:
            devnull = open(os.devnull)
            subprocess.Popen(['pocketsphinx_continuous', '--invalid-args'], stdout=devnull, stderr=devnull).communicate()
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print('Error: Please install pocketsphinx to transcribe files.')
                sys.exit()
        files = convert_to_wav(args.inputfile)
        transcribe(files)
    elif args.json:
        sentences = convert_timestamps(args.inputfile)
        print(words_json(sentences))

    elif args.search:
        if args.outputmode == 'franken':
            segments = franken_sentence(args.search, args.inputfile)
        else:
            segments = search(args.search, args.inputfile, mode=args.outputmode, regex=args.regex)

        if len(segments) == 0:
            print('No results for "' + args.search + '"')
            sys.exit()

        print('Generating supercut')
        if args.demo:
            for s in segments:
                if args.outputmode == 'sentence':
                    print(' '.join([w[0] for w in s['words']]))
                else:
                    print(s['words'])
        else:
            compose(segments, out=args.outputfile, padding=args.padding, crossfade=args.crossfade, layer=args.layer)
    elif args.extract:
        extract_words(args.inputfile)

if __name__ == '__main__':
    main()
