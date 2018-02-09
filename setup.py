from setuptools import setup

setup(
    name='audiogrep',
    version='0.1.4',
    author='Sam Lavigne',
    author_email='splavigne@gmail.com',
    packages=['audiogrep'],
    scripts=['bin/audiogrep'],
    url='http://antiboredom.github.io/audiogrep',
    license='LICENSE',
    description='Creates audio supercuts',
    long_description=open('README.md').read(),
    keywords='audio supercut pydub transcribe transcription',
    install_requires=["pydub"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Editors',
        'Topic :: Multimedia :: Sound/Audio :: Speech'
    ]
)
