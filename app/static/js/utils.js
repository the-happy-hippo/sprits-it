
function get_parser(name) {
  if (typeof parsers === 'string') {
    parsers = JSON.parse(parsers);
  }

  parser = parsers[name];
  parser.name = name;

  parser.get_token = function() {
    var token = this.token;

    if(this.addtime) {
      token += (new Date()).getTime();
    }

    return token;
  }

  return parser;
}

