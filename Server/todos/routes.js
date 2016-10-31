var mongoose = require('mongoose');
var express = require('express');
var Todo = require('../db/db').Todo;
var router = express.Router();

router.get('/todos', function (req, res) {
	console.log('in Server/todos/routes');
	// body...
	res.send(res);
	res.send('Hello from todos/router.js');
});

router.post('/bingo', function (req, res) {
	// body...
	console.log('Post call for /', req.body);
	var todo = new Todo(req.body);
	todo.save(function (err) {
		// body...
		console.log('Error saving sdata');
	});
})

module.exports = router;