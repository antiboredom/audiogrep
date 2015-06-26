import os

import audiogrep


def test_convert_timestamps():
    filename = os.path.join(os.path.dirname(__file__), 'data/test.mp3')
    sentences = audiogrep.convert_timestamps([filename])
    words = {}
    for sentence in sentences:
        for word in sentence['words']:
            words[word[0]] = True
    assert 'fashion' in words
    assert len(sentences) == 9
