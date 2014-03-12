spritz-it!
==========

The goal is to enable using [Spritz](http://www.spritzinc.com/) awesome speed-reading technology available in mobile browsers (specifically, to the time of this writing [Spritz](http://www.spritzinc.com/) had nothing to offer to `iOs` device users :confused:).

The bootstrap code was imported from my codepen snippet at http://codepen.io/the-happy-hippo/pen/aDHrl which in turn had been forked from a great pen by [Charlotte Dann](http://codepen.io/pouretrebelle) at http://codepen.io/pouretrebelle/pen/reGKw with javascript cherrypicking for [Readability](https://www.readability.com) text extraction from [OpenSpritz](https://github.com/Miserlou/OpenSpritz) project by [Rich Jones](https://github.com/Miserlou) (@miserlou).

Up-to-date Gist from codepen can be found at https://gist.github.com/the-happy-hippo/9474002.

Currently, the API for reading a web article is:
```
      http://codepen.io/the-happy-hippo/full/aDHrl?url=page_url
```

Example:

> http://codepen.io/the-happy-hippo/full/aDHrl?url=http%3A%2F%2Fwww.spritzinc.com%2Fthe-science

Alternatively, you migh just grab a bookmarklet from the bottom of the [pen](http://codepen.io/the-happy-hippo/full/aDHrl) page or create yours manually by pasting the javascript code below:
```javascript
javascript:function iptxt()%7Bvar d%3Ddocument%3Btry%7Bif(!d.body)throw(0)%3Bwindow.location%3D"http%3A%2F%2Fcodepen.io%2Fthe-happy-hippo%2Ffull%2FaDHrl%3Furl%3D"%2BencodeURIComponent(d.location.href)%3B%7Dcatch(e)%7Balert("Please wait until the page has loaded.")%3B%7D%7Diptxt()%3Bvoid(0)
```

Here is the original description from [Charlotte Dann](http://codepen.io/pouretrebelle):
> Use [Spritz](http://www.spritzinc.com/) right now! Options for speed, localStorage saving, jog forward/backward, text size and dark/light theme, also with keyboard controls and progress bar. You'll never need to read conventionally again. 
> localStorage implementation by [Keith Wyland](http://codepen.io/keithwyland/), thanks Keith!

