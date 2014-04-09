/*

Spritz Speed Reader by Charlotte Dann
Local storage implementation by Keith Wyland

---

Spritz Speed Reading V2 - Bookmarklet Edition by Oleg P

Mixed and matched from a fork of http://codepen.io/pouretrebelle/full/reGKw
and readability text extraction js from https://github.com/Miserlou/OpenSpritz.

Use the bookmarklet code from the pen JS to speed-read any web page (tested in
Chrome and mobile Safari) with the following API:

http://codepen.io/the-happy-hippo/full/aDHrl?url=<web_page_url>

*/

var $wpm = $('#spritz_wpm');
var interval = 60000/$wpm.val();
var paused = false;
var $space = $('#spritz_word');
var night = false;
var zoom = 1;
var autosave = false;
var local_spritz = {};
var content = {};
var words = [];
var word_index = 0;

function init_default_content() {
  content = {
    title: words_default[0],
    text: []
  };
  for (var i = 1; i < words_default.length; i++) {
    content.text.push(words_default[i]);
  }
}

function set_content_html() {
    $('#spritz_words')
      .empty();
    $('#spritz_words')
      .append( '<header>' + content.title + '</header>' );
    content.text.forEach( function(text) {
      $('#spritz_words')
        .append('<p>' + text + '</p>');
    });
}

function words_load() {
  if (!localStorage.jqspritz) {
    init_default_content();
    word_index = 0;
    words_set();
    word_show();
    word_update();
    spritz_pause(true);
  } else {
    local_spritz = JSON.parse(localStorage['jqspritz']);
    if (local_spritz.night) {
      night = true
      $('html').addClass('night');
    };
    if (local_spritz.autosave) {
      autosave = true;
      $('html').addClass('autosave');
      $('#autosave_checkbox').prop('checked', true);
    };
    $wpm.val(local_spritz.wpm);
    interval = 60000/local_spritz.wpm;
    spritz_zoom(0);
    content = local_spritz.content;
    word_index = local_spritz.word;
    words_set();
    word_show();
    word_update();
    spritz_pause(true);
    spritz_alert('loaded');
  }
}
function words_save() {
  local_spritz = {
    word: word_index,
    content: content,
    wpm: $wpm.val(),
    night: night,
    autosave: autosave,
    zoom: zoom
  };
  localStorage['jqspritz'] = JSON.stringify(local_spritz);
  if (!autosave) {
    spritz_alert('saved');
  } else {
    button_flash('save', 500);
  }
}


/* TEXT PARSING */
function words_set() {
  set_content_html();
  words = content.text
    .join(' ')
    .trim()
    .replace(/([\u2010-\u2014])(\S)/g, '$1 $2') // detach some dashes.
    .replace(/([\.\?\!\;\:\)])/g, '$1 • ') // stumble on punctuation.
    .split(/\s+/); // shrink long whitespaces and split.
}

/* ON EACH WORD */
function word_show() {
  if (word_index < 0) word_index = 0;
  if (word_index >= words.length) word_index = words.length-1;
  $('#spritz_progress').width(100*word_index/words.length+'%');
  var word = words[word_index];
  var stop = Math.round((word.length+1)*0.4)-1;
  if (word != '•') {
    $space.html('<div>'+word.slice(0,stop)+'</div><div>'+word[stop]+'</div><div>'+word.slice(stop+1)+'</div>');
  }
}
function word_next() {
  word_index++;
  word_show();
}
function word_prev() {
  word_index--;
  word_show();
}

/* ITERATION FUNCTION */
function word_update() {
  spritz = setInterval(function() {
    word_next();
    if (word_index+1 == words.length) {
      setTimeout(function() {
        $space.html('');
        spritz_pause(true);
        word_index = 0;
        word_show();
      }, interval);
      clearInterval(spritz);
    };
  }, interval);
}

/* PAUSING FUNCTIONS */
function spritz_pause(ns) {
    if (!paused) {
    clearInterval(spritz);
    paused = true;
    $('html').addClass('paused');
    if (autosave && !ns) {
      words_save();
    };
  }
}
function spritz_play() {
  word_update();
  paused = false;
  $('html').removeClass('paused');
}
function spritz_flip() {
  if (paused) {
    spritz_play();
  } else {
    spritz_pause();
  };
}

/* SPEED FUNCTIONS */
function spritz_speed() {
  interval = 60000/$('#spritz_wpm').val();
  if (!paused) {
    clearInterval(spritz);
    word_update();
  };
  $('#spritz_save').removeClass('saved loaded');
}
function spritz_faster() {
  $('#spritz_wpm').val(parseInt($('#spritz_wpm').val())+50);
  spritz_speed();
}
function spritz_slower() {
  if ($('#spritz_wpm').val() >= 100) {
    $('#spritz_wpm').val(parseInt($('#spritz_wpm').val())-50);
  }
  spritz_speed();
}

/* JOG FUNCTIONS */
function spritz_back() {
  spritz_pause();
  if (word_index >= 1) {
    word_prev();
  };
}
function spritz_forward() {
  spritz_pause();
  if (word_index < words.length) {
    word_next();
  };
}

/* WORDS FUNCTIONS */
function spritz_zoom(c) {
  zoom = zoom+c
  $('#spritz').css('font-size', zoom+'em');
}
function spritz_refresh() {
  clearInterval(spritz);
  words_set();
  spritz_pause();
  word_index = 0;
  word_show();
};

function spritz_home() {
  window.location = location.origin + location.pathname;
};

/* AUTOSAVE FUNCTION */
function spritz_autosave() {
  $('html').toggleClass('autosave');
  autosave = !autosave;
  if (autosave) {
    $('#autosave_checkbox').prop('checked', true);
  } else {
    $('#autosave_checkbox').prop('checked', false);
  }
};

/* STATUS FUNCTION */
function spritz_status(msg) {
  $('#img-loading').hide();
  return $('#alert').attr('title', '').text(msg);
}

/* ALERT FUNCTION */
function spritz_alert(type) {
  var msg = '';
  switch (type) {
    case 'loaded':
      msg = 'Data loaded from local storage';
      break;
    case 'saved':
      msg = 'Settings have been saved in local storage for the next time you visit';
      break;
    case 'erased':
      msg = 'Your saved settings have been erased';
      break;
  }
  return spritz_status(msg).fadeIn().delay(2000).fadeOut();
}

/* ERROR FUNCTION */
function spritz_error(msg) {
  return spritz_status(msg).fadeIn().delay(5000).fadeOut();
}

/* CONTROLS */
$('#spritz_wpm').on('input', function() {
  spritz_speed();
});
$('.controls').on('click', 'a, label', function() {
  switch (this.id) {
    case 'spritz_slower':
      spritz_slower(); break;
    case 'spritz_faster':
      spritz_faster(); break;
    case 'spritz_save':
      words_save(); break;
    case 'spritz_pause':
      spritz_flip(); break;
    case 'spritz_smaller':
      spritz_zoom(-0.1); break;
    case 'spritz_bigger':
      spritz_zoom(0.1); break;
    case 'spritz_autosave':
      spritz_autosave(); break;
    case 'spritz_refresh':
      spritz_refresh(); break;
    case 'spritz_home':
      spritz_home(); break;
  };
  return false;
});
$('.controls').on('mousedown', 'a', function() {
  switch (this.id) {
    case 'spritz_back':
      spritz_jog_back = setInterval(function() {
        spritz_back();
      }, 100);
      break;
    case 'spritz_forward':
      spritz_jog_forward = setInterval(function() {
        spritz_forward();
      }, 100);
      break;
  };
});
$('.controls').on('mouseup', 'a', function() {
  switch (this.id) {
    case 'spritz_back':
      clearInterval(spritz_jog_back); break;
    case 'spritz_forward':
      clearInterval(spritz_jog_forward); break;
  };
});

/* KEY EVENTS */
function button_flash(btn, time) {
  var $btn = $('.controls a.'+btn);
  $btn.addClass('active');
  if (typeof(time) === 'undefined') time = 100;
  setTimeout(function() {
    $btn.removeClass('active');
  }, time);
}
$(document).on('keyup', function(e) {
  if (e.target.tagName.toLowerCase() != 'body') {
    return;
  };
  switch (e.keyCode) {
    case 32:
      spritz_flip(); button_flash('pause'); break;
    case 37:
      spritz_back(); button_flash('back'); break;
    case 38:
      spritz_faster(); button_flash('faster'); break;
    case 39:
      spritz_forward(); button_flash('forward'); break;
    case 40:
      spritz_slower(); button_flash('slower'); break;
  };
});
$(document).on('keydown', function(e) {
  if (e.target.tagName.toLowerCase() != 'body') {
    return;
  };
  switch (e.keyCode) {
    case 37:
      spritz_back(); button_flash('back'); break;
    case 39:
      spritz_forward(); button_flash('forward'); break;
  };
});

/* LIGHT/DARK THEME */
$('.light').on('click', function() {
  $('html').toggleClass('night');
  night = !night;
  return false;
});

$('a.toggle').on('click', function() {
  $(this).siblings('.togglable').slideToggle();
  return false;
});

/* Erase Local Storage */
$('.erase-storage').on('click', function() {
  delete localStorage['jqspritz'];
  spritz_alert('erased');
  return false;
});

function get_url_param(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

// FIXME: decide what to do with this func
function preproc_text(title, author, body) {
  body = $
    .trim(body)             // Trip trailing and leading whitespace.
    .replace(/\s+/g, ' ');  // Shrink long whitespaces.

  var text_content = title + author + body;

  // Make sure punctuation is apprpriately spaced.
  return text_content
    .replace(/\./g, '. ')
    .replace(/\?/g, '? ')
    .replace(/\!/g, '! ');
}

function spritzify_url(url) {
  var PREFIX = 'http'; // poor-man's URL parsing
  if (url.length > PREFIX.length)
  {
    var urlprefix = url.substring(0, PREFIX.length).toLowerCase();
    if(urlprefix != PREFIX) {
      url = PREFIX + '://' + url;
    }
  }

  article_url = document.getElementById('article-url');
  article_url.href = url;

  var max_len = 20;
  var display_url_path = article_url.pathname === '/' ? '' : article_url.pathname;
  var display_url_full  = article_url.hostname + display_url_path;
  var display_url_shoft = display_url_full.substring(0, max_len);

  $('#alert')
    .text('Loading ' + display_url_shoft + ' ...')
    .attr('title', 'Loading ' + display_url_full)
    .add('#img-loading')
    .fadeIn();

  spritzify_url_with(url, ['Readability', 'SpritsIt']);
}

// Uses the Readability API to get the juicy content of the current page.
function spritzify_url_with(url, parser_names) {
  try {

    if(parser_names.length == 0) {
      throw "No parsers remaining!";
    }

    var parser_name = parser_names.shift();
    var parser = get_parser(parser_name);

    var apireq = parser.uri + '?token=' + parser.get_token()
      + '&url=' + encodeURIComponent(url) + '&callback=?';

    parser_name = 'Parser "' + parser.name + '"';
    console.log(parser_name + ': requesting ' + apireq);

    jQuery
    .getJSON(apireq, function (data) {

        if(data.error) {
          spritz_error('Article extraction failed.');
          return;
        }

        if(data.word_count == 0) {
          console.log(parser_name + ': word count is zero, trying alternative API...');
          return spritzify_url_with(url, parser_names);
        }

        var title = '';

        if(data.title !== '') {
          title = data.title;

          if(data.author !== null) {
            title = title + ', by ' + data.author;
          }
        }

        var body = jQuery(data.content).text(); // Textify HTML content.
        var text_content = jQuery.trim(body);

        if (text_content === '') {
          text_content = data.content;
        }

        content = {
          title: title,
          text: text_content.split(/\n\n/)
        };

        spritz_status('');

        words_set();

        word_index = 0;
        word_show();

        spritz_pause(true);
    })
    .done(function() {
      console.log(parser_name + ': done.' );
    })
    .fail(function( jqxhr, status_msg, error ) {
      var errmsg = status_msg + ", " + error;
      console.log(parser_name + ': fail: ' + errmsg);
      spritz_error('Article extraction failed.');
    })
    .always(function() {
      console.log(parser_name + ': always.' );
    })
  } catch (e) {
     console.log('Error in spritzify_url: ' + e);
     spritz_error('Article extraction failed.');
  }
}

function create_bookmarklet() {
  var this_page_permalink = location.origin + location.pathname;
  var code = 'javascript:' + encodeURIComponent(
    'function iptxt(){var d=document;try{if(!d.body)throw(0);window.location' +
    '="' + this_page_permalink +
    '?url="+encodeURIComponent(d.location.href);' +
    '}catch(e){alert("Please wait until the page has loaded.");}}iptxt();void(0)');
  $('#bookmarklet').attr('href', code);
  $('#bookmarklet').click(function(){ return false; });
  $('#bookmarklet-code').val(code);
  $('#bookmarklet-code').click(function(){this.focus();this.select();});
}

/* INITIATE */
$(document).ready(function() {

  create_bookmarklet();

  custom_url = get_url_param('url');

  if(custom_url) {
    spritzify_url(custom_url);
  } else {
    words_load();
  }
});

window.addEventListener("pageshow", function(evt){
  spritz_pause(true);
}, false);

window.addEventListener("pagehide", function(evt){
  spritz_pause(true);
}, false);

