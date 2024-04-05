# poc-audio-pedalboard

Proof of Concept (PoC) code/notes exploring using the [spotify/pedalboard](https://github.com/spotify/pedalboard) library for interacting with audio plugin VSTs/etc.

<!-- TOC start (generated with https://derlin.github.io/bitdowntoc/) -->
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [See Also](#see-also)
   - [My Other Related Deepdive Gist's and Projects](#my-other-related-deepdive-gists-and-projects)
<!-- TOC end -->

## Prerequisites

- Python 3.7+
- pip
- virtualenv

## Installation

First, clone the repository and navigate to the project directory:

```bash
git clone [repository-url]
cd [repository-directory]
```

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Or:
#   pyenv virtualenv 3.10.2 poc-audio-pedalboard
#   pyenv local poc-audio-pedalboard
```

Install the required dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Update the script with the correct path to your Vital VST3 or Component file. Then run the script within the virtual environment to load Vital and process MIDI through the synthesizer.

```bash
python synth_vst_loader.py
```

Make sure to check the Pedalboard documentation for more detailed usage and advanced features.

## See Also

### My Other Related Deepdive Gist's and Projects

- [Generating Synth Patches with AI (0xdevalias' gist)](https://gist.github.com/0xdevalias/5a06349b376d01b2a76ad27a86b08c1b#generating-synth-patches-with-ai)
- [Music APIs and DBs (0xdevalias' gist)](https://gist.github.com/0xdevalias/eba698730024674ecae7f43f4c650096#music-apis-and-dbs)
- [AI Voice Cloning / Transfer (eg. RVCv2) (0xdevalias' gist)](https://gist.github.com/0xdevalias/359f4265adf03b0142e4d0543c156a3e#ai-voice-cloning--transfer-eg-rvcv2)
- [Singing Voice Synthesizers (eg. Vocaloid, etc) (0xdevalias' gist)](https://gist.github.com/0xdevalias/0b64b25d72cbbc784042a9fdff713129#singing-voice-synthesizers-eg-vocaloid-etc)
- [Audio Pitch Correction (eg. autotune, melodyne, etc) (0xdevalias' gist)](https://gist.github.com/0xdevalias/7f4a5c31758e04aea5c2f5520e53accb#audio-pitch-correction-eg-autotune-melodyne-etc)
- [Compare/Diff Audio Files (0xdevalias' gist)](https://gist.github.com/0xdevalias/91ae33e0c9290e69b457ce5034956fb7#comparediff-audio-files)
