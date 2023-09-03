# lapl_latimes
Generates an ebook of the LA times for the current day by querying the LA Public Library research database

## Why
Did you know that you have access to the LA times with an LA Public Library card? I didn't until recently! It is in research database format though. This is a small script that will collect the day's articles into an ebook for you so that you could hypothetically read it on your phone or ereader. I just made this for educational purposes though.

## Setup

First install all required dependencies:
```shell
pip3 install -r requirements.txt
```

You will then need to replace the following two lines (11 and 12) in `latimes.py` with your library card number and pin:
```python
USER = "REPLACEME"
PASS = "REPLACEME"
```

You can then run the shell script which will retrieve the articles and build the ebook for you:
```shell
chmod +x run.sh
./run.sh
```

The generated ebook will be in the `output` folder.

## Credit
This utilizes [ebookmaker](https://github.com/setanta/ebookmaker) to make the ebook - the necessary components are included in this repo. Thanks [setanta](https://github.com/setanta)!
