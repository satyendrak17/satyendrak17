var express = require("express");
var app = express();
var PORT = process.env.PORT || 3000;
var routes = require('./Server/routes');

var bodyParser = require("body-parser");

app.use(bodyParser.json());

app.use(bodyParser.urlencoded({ extended: false }));
routes(app);

app.use(express.static(__dirname + '/Client'));

app.listen(PORT, function() {
	console.log("We are connected to PORT-", PORT);
});