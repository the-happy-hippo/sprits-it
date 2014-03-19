/*

Spritz Speed Reader by Charlotte Dann
Local storage implementation by Keith Wyland

---

Spritz Speed Reading V2 - Bookmarklet Edition by Oleg P

Mixed and matched from a fork of http://codepen.io/pouretrebelle/full/reGKw and readability text extraction js from https://github.com/Miserlou/OpenSpritz.

Use the bookmarklet code from the pen JS to speed-read any web page (tested in Chrome and mobile Safari) with the following API:

http://codepen.io/the-happy-hippo/full/aDHrl?url=<web_page_url>

*/

var $wpm = $('#spritz_wpm');
var interval = 60000/$wpm.val();
var paused = false;
var $space = $('#spritz_word');
var i = 0;
var night = false;
var zoom = 1;
var autosave = false;
var $words = $('#spritz_words');
var local_spritz = {};

function words_load() {
  if (!localStorage.jqspritz) {
    words_set();
    word_show(0);
    word_update();
    spritz_pause(true);
  } else {
    local_spritz = JSON.parse(localStorage['jqspritz']);
    $words.val(local_spritz.words);
    i = local_spritz.word;
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
    words_set();
    word_show(i);
    word_update();
    spritz_pause(true);
    spritz_alert('loaded');
  }
}
function words_save() {
  local_spritz = {
    word: i,
    words: $words.val(),
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
  words = $words.val().trim()
  .replace(/([\u2010-\u2014])(\S)/g, '$1 $2')    // detach some dashes.
  .replace(/([\.\?\!\;\:\)])/g, '$1 • ') // stumble on punctuation.
  .split(/\s+/); // shrink long whitespaces and split.
}

/* ON EACH WORD */
function word_show(i) {
  $('#spritz_progress').width(100*i/words.length+'%');
  var word = words[i];
  var stop = Math.round((word.length+1)*0.4)-1;
  if (word != '•') {
    $space.html('<div>'+word.slice(0,stop)+'</div><div>'+word[stop]+'</div><div>'+word.slice(stop+1)+'</div>');
  }
}
function word_next() {
  i++;
  word_show(i);
}
function word_prev() {
  i--;
  word_show(i);
}

/* ITERATION FUNCTION */
function word_update() {
  spritz = setInterval(function() {
    word_next();
    if (i+1 == words.length) {
      setTimeout(function() {
        $space.html('');
        spritz_pause(true);
        i = 0;
        word_show(0);
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
  if (i >= 1) {
    word_prev();
  };
}
function spritz_forward() {
  spritz_pause();
  if (i < words.length) {
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
  i = 0;
  spritz_pause();
  word_show(0);
};
function spritz_select() {
  $words.select();
};
function spritz_expand() {
  $('html').toggleClass('fullscreen');
}

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
  return $('#alert').text(msg);
}

/* ALERT FUNCTION */
function spritz_alert(type) {
  var msg = '';
  switch (type) {
    case 'loaded':
      msg = 'Data loaded from local storage';
      break;
    case 'saved':
      msg = 'Words, Position and Settings have been saved in local storage for the next time you visit';
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
    case 'spritz_select':
      spritz_select(); break;
    case 'spritz_expand':
      spritz_expand(); break;
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

function get_url_param(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

// Please don't abuse this.
var readability_token = '29d6e9893943faca8e084f5085c327a6860ed771';

// Uses the Readability API to get the juicy content of the current page.
function spritzify_url(url) {
  $.getJSON("https://www.readability.com/api/content/v1/parser?url="+ url +"&token=" + readability_token +"&callback=?",
    function (data) {
      if(data.error) {
        spritz_error('Article extraction failed. Try selecting text instead.');
        return;
      }

      var title = '';
      if(data.title !== ''){
        title = data.title + ' ';
      }

      var author = '';
      if(data.author !== null){
        author = "By " + data.author + '. ';
      }

      var body = jQuery(data.content).text(); // Textify HTML content.
      body = $.trim(body); // Trip trailing and leading whitespace.
      body = body.replace(/\s+/g, ' '); // Shrink long whitespaces.

      var text_content = title + author + body;
      text_content = text_content.replace(/\./g, '. '); // Make sure punctuation is apprpriately spaced.
      text_content = text_content.replace(/\?/g, '? ');
      text_content = text_content.replace(/\!/g, '! ');
      $words.val(text_content);

      words_set();
      word_show(0);
      spritz_pause(true);

    }).error(function() {
      spritz_error('Article extraction failed. Try selecting text instead.'); });
}

function create_bookmarklet() {
  var this_page_permalink = location.origin + location.pathname;
  var code = 'javascript:' + encodeURIComponent(
    'function iptxt(){var d=document;try{if(!d.body)throw(0);window.location' +
    '="' + this_page_permalink +
    '?url="+encodeURIComponent(d.location.href);' +
    '}catch(e){alert("Please wait until the page has loaded.");}}iptxt();void(0)');
  $('#bm').attr('href', code);
  $('#bm').click(function(){ return false; });
  $('#bmc').val(code);
  $('#bmc').click(function(){this.focus();this.select();});
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
  console.log('pageshow');
  spritz_pause(true);
}, false);
window.addEventListener("pagehide", function(evt){
  console.log('pagehide');
  spritz_pause(true);
}, false);


