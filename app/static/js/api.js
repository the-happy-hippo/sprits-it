
$(':submit').on('click', function() {

  var url = $('#url').val();

  if (url.trim()) {
    var targeturl = location.origin + '/' + this.id;

    var parser = get_parser('SpritsIt');

    targeturl += '?url=' + url + '&token=' + parser.get_token();

    window.location = targeturl;
  }

  return false;
});
