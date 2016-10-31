
var Todo = require('../db/db').Todo;
module.exports = function(req, res) {
	console.log('in delete controlller', req.params.taskToDelete);
	Todo.remove({task : req.params.taskToDelete}, function(error) {
			res.send("Deleted");
		});

	

}