
var Todo = require('../db/db').Todo;
module.exports = function(req, res) {
	console.log('in route.js /bingo', req.body);
	var taskPrev = req.body[1].task;
	var id = req.params.id;
	console.log('taskPrev', taskPrev);
	Todo.update({task : taskPrev}, {task : req.body[0].task},function(error, resp) {
			res.send(resp);
		});

	

}