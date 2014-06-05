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
- eBook reading (_ePub_ format, experimental);
- _PDF_ text extraction (experimental);
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

## Installation instructions

### Prerequisites

1. Get your Readability™ API token at https://www.readability.com/developers/api;
1. Optionally, if you'd like to track your site with [Google Analytics](http://www.google.com/analytics) then get a Tracking ID at http://www.google.com/analytics.

### Cloning the repo

Clone with `--recursive` flag — this flag is needed for `git` to recursively fetch all the submodule dependencies for the project. E.g.:

    git clone --recursive https://github.com/my-user/sprits-it.git

### Running locally with Flask dev server

- Change to project root folder:

```
cd sprits-it/
```

- Create `virtualenv` for the project:

```
> virtualenv venv
> . venv/bin/activate
> pip install -r app/requirements.txt
```

- Set your Readability API token and, optionally, Google Analytics Tracking ID in `app/.env` like so:

```
READABILITY_API_KEY=1234567890123456789012345678901234567890
GOOG_ANALYTICS_ID=UU-12345678-9
```

- Run Flask dev server from the `app` folder:

```
> cd app/
> python spritsit.py

```

- Visit `http://localhost:8080` in your browser.


### Deploying on [Heroku](https://www.heroku.com)

If you are new to [Heroku](https://www.heroku.com) platform, visit the "Getting Started" guide at https://devcenter.heroku.com/articles/quickstart. Here we'll assume you have already set up your app's _empty_ Heroku repo under `heroku-app/`.

> Note: `git` manipulations below are needed due to the fact that the code should be imported from a _foreign_ `git` repo (hosted on `GitHub`) to native `Heroku` repo, and moreover, because the sources (such as `Procfile`, etc.) **must** be placed in the root folder instead of in `app/` subfolder 

```
heroku-app/> git remote -v
heroku  git@heroku.com:heroku-app.git (fetch)
heroku  git@heroku.com:heroku-app.git (push)
```

- Import `sprits-it` sources from the `GitHub` repo:

```
heroku-app/> git remote add -f sprits-it  https://github.com/my-user/sprits-it.git
heroku-app/> git merge -s ours --no-commit sprits-it/master
```

- Move app sources to the root:

```
heroku-app/> git mv app/* app/.env .
```

- Now, edit `.gitmodules` to fix module locations. That is, open `.gitmodules` and replace _every_ occurence of `app/lib/` with `lib/`;

- Re-initialize submodules:

```
heroku-app/> git submodule init
heroku-app/> git submodule sync
heroku-app/> git submodule update
```

- Create `venv` as described in `Heroku` documentation:

```
heroku-app/> virtualenv venv
heroku-app/> . venv/bin/activate
heroku-app/> pip install -r requirements.txt
```

- Set your Readability API token and, optionally, Google Analytics Tracking ID in `.env` like so:

```
READABILITY_API_KEY=1234567890123456789012345678901234567890
GOOG_ANALYTICS_ID=UU-12345678-9
```

- Run local dev server:

```
heroku-app/> foreman start
```

- To test the result, visit `http://localhost:5000` in your browser.

- Before deploying the app to `Heroku` server, set the following config var to instruct the app that it is running in 'production' environment (as opposed to the local dev server):

```
heroku-app/> heroku config:set HEROKU=1
```

- Commit and deploy regularly as described at https://devcenter.heroku.com/articles/getting-started-with-python, e.g.:

```
heroku-app/> git add -A .
heroku-app/> git commit
heroku-app/> git push heroku master
```

### Deploying on [Google App Engine](https://cloud.google.com/products/app-engine)

The following assumes `GAE` SDK is located in `google_appengine/`.

- Clone the repo as described above:

```
google_appengine/> git clone --recursive https://github.com/my-user/sprits-it.git
google_appengine/> cd sprits-it/
```

- Install the requirements to `app/lib/`:

```
sprits-it/> pip install -r app/requirements.txt -t app/lib/
```

- Set your Readability API token and, optionally, Google Analytics Tracking ID in `app/.env` like so:

```
READABILITY_API_KEY=1234567890123456789012345678901234567890
GOOG_ANALYTICS_ID=UU-12345678-9
```

- Run local dev server:

```
sprits-it/> pip install -r app/requirements.txt -t app/lib/
sprits-it/> python ../dev_appserver.py app
```

- To test the result, visit `http://localhost:8080` in your browser.

- Deploy to `GAE` (for instructions see [here](https://developers.google.com/appengine/docs/python/gettingstartedpython27/uploading)).

## Changelog

Currently development betas only — simply because the project lacks sufficient user base to be tested extensively. Sorry… and you can help fixing that!

- [v0.5-beta](https://github.com/the-happy-hippo/sprits-it/releases/tag/v0.5-beta) (pre-release)
  - Added `PDF` handling;
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
