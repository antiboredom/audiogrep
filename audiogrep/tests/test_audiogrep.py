from os.path import join, dirname

from audiogrep import convert_timestamps


def test_convert_timestamps():
    filename = join(dirname(__file__), 'data/test.mp3')
    sentences = convert_timestamps([filename])
    words = {}
    for sentence in sentences:
        for word in sentence['words']:
            words[word[0]] = True
    assert 'fashion' in words
    assert len(sentences) == 9
