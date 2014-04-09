
$(':submit').on('click', function() {

  var url = $('#url').val();

  if (url.trim()) {
    var targeturl = location.origin + '/' + this.id;
    var token = '112358' + (new Date()).getTime();

    targeturl += '?url=' + url + '&token=' + token;

    window.location = targeturl;
  }

  return false;
});
