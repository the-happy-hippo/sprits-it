sprits-it! — Awesome Speed-Reading
==================================

`sprits-it!` is an open source web application which allows speed-reading of arbitrary web pages in a browser.

The speed reading technique is currently based on the ideas of [Spritz](http://www.spritzinc.com/) described in their [blog](http://www.spritzinc.com/blog). At the time of this writing [Spritz](http://www.spritzinc.com/) had virtually nothing to offer to [iOs](http://www.apple.com/ios) device users to play with. This project is targeted specifically on usability in Safari and Chrome mobile browsers but should ultimately work well on other platforms.

## Screenshots

<img src='https://github.com/the-happy-hippo/sprits-it/raw/gh-pages/app/static/img/cap_alice.gif'
    width='300px' height='450px' alt='English-language Demo'></img>
    &nbsp;
<img src='https://github.com/the-happy-hippo/sprits-it/raw/gh-pages/app/static/img/cap_geroi.gif'
    width='300px' height='450px' alt='Russian-language Demo'></img>

## Features

- Speed-read any web page in your browser (well, _almost_ any) — also on mobile;
- Configurable reading speed, play/pause/rewind, nite mode, reading progress bar;
- Settings, text and reading position can be saved in browser local storage and restored next time you visit;
- Uses Readability™ technology for text extraction and cleanup (HTML boilerplate removal);
- Hyphenation for long words with language auto-detection;
- Punctuation aware;
- Easy-to-install _bookmarklet_;
- Right-to-left language support (עברית and العربية);
- eBook reading (_ePub_ format, experimental)
- _Coming soon_: _PDF_ text extraction;
- _Coming soon_: word and context highlighting and navigation.

## Demo

Live demo is hosted on [Heroku](https://www.heroku.com) here:

> http://sprits-it.herokuapp.com/read

To read a web page at ``page_url`` use the following GET query:
`http://sprits-it.herokuapp.com/read?url=page_url`

For example:

> http://sprits-it.herokuapp.com/read?url=http%3A%2F%2Fwww.spritzinc.com%2Fthe-science

Alternatively, you migh just grab a _bookmarklet_ in the settings section of the demo.

Official project homepage is hosted by GitHub Pages [here](http://the-happy-hippo.github.io/sprits-it).

## Changelog

Currently development betas only — simply because the project lacks sufficient user base to be tested extensively. Sorry… and you can help fixing that!

- [v0.4-beta](https://github.com/the-happy-hippo/sprits-it/releases/tag/v0.4-beta) (pre-release)
  - Added basic `ePub` handling;
  - Minor fixes in RLT support and browser detection;
- [v0.3-beta](https://github.com/the-happy-hippo/sprits-it/releases/tag/v0.3-beta)
  - Right-to-left language support (Hebrew and Arabic);
  - Improved language auto-detection;
  - “Modern” browser detection, reject old browsers such as IE8;
- [v0.2-beta](https://github.com/the-happy-hippo/sprits-it/releases/tag/v0.2-beta)
  - Hyphenation and punctuation handling;
  - Improved text extraction;
- [v0.1-beta](https://github.com/the-happy-hippo/sprits-it/releases/tag/v0.1-beta) — Initial release.

## Project Motto

This project is managed according to the following book (in Russian):

<img src='https://github.com/the-happy-hippo/sprits-it/raw/gh-pages/app/static/img/book.jpg'
    width='70%' alt='The Project Book' title='The Project Book'></img>

Cheers!

## Contributors

The bootstrap code was imported from a [CodePen](http://codepen.io) snippet at http://codepen.io/the-happy-hippo/pen/aDHrl which in turn had been forked from a great Pen by [Charlotte Dann](http://codepen.io/pouretrebelle) at http://codepen.io/pouretrebelle/pen/reGKw with javascript cherrypicking for [Readability](https://www.readability.com) text extraction from [OpenSpritz](https://github.com/Miserlou/OpenSpritz) project by [Rich Jones](https://github.com/Miserlou)(@miserlou).

Up-to-date Gist from codepen can be found at https://gist.github.com/the-happy-hippo/9474002.

Here is the description from [Charlotte Dann](http://codepen.io/pouretrebelle) for her original [Pen](http://codepen.io/pouretrebelle/pen/reGKw):
> Use [Spritz](http://www.spritzinc.com/) right now! Options for speed, localStorage saving, jog forward/backward, text size and dark/light theme, also with keyboard controls and progress bar. You'll never need to read conventionally again. 
> localStorage implementation by [Keith Wyland](http://codepen.io/keithwyland/), thanks Keith!

### Contributing Projects

* [OpenSpritz](https://github.com/Miserlou/OpenSpritz) - OpenSpritz project by [@miserlou](https://github.com/miserlou)
* [Spritz Speed Reading V2](http://codepen.io/pouretrebelle/pen/reGKw) - Codepen Spritz project by [@Charlotte Dann](http://codepen.io/pouretrebelle)
* [Spray](https://github.com/chaimpeck/spray) - Bootstrap extension of OpenSpritz by [@chaimpeck](https://github.com/chaimpeck)

### Notice to Contributors

I have started this project purely for educational purposes while having virtually no prior background in web design (apart from plain old HTML tables of 90's).

If you find something stupid that I did &mdash; please don't blame me and never hesitate to point those things out so I can learn from them.

## Disclaimer

`sprits-it!` is not affilated with [Spritz Inc](http://www.spritzinc.com/) in any way. This is an open source, community created project based on publicly available information. We love you!
