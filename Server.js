var express = require('express');
var app = express();
var PORT = process.env.PORT || 3000;
var bodyParser = require('body-parser');
var routes = require('./Server/routes');

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
routes(app);


app.use(express.static(__dirname + '/public'));
app.listen(PORT, function() {
	// body...
	console.log('Listening on port number '+PORT);
});