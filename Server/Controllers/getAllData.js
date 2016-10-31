
var Todo = require('../db/db').Todo;
module.exports = function(req, res) {
	Todo.find(function(error, resp) {
	console.log('resp', resp);
		res.send({response : resp});
	});
}