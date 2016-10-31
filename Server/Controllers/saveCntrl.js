
var Todo = require('../db/db').Todo;
module.exports = function(req, res) {
	var todo = new Todo(req.body);
	var promise = todo.save();

	promise.then(function (doc) {
		res.send(doc);
	});

}