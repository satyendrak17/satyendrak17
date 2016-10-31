var mongoose = require('mongoose');
var express = require('express');
var Todo = require('../db/db').Todo;
var router = express.Router();
router.get('/bingo', function (req, res) {
	// body...
	console.log('get call for /bingo');
	var todo = new Todo(req.body);
	todo.save(function (err) {
		// body...
		console.log('Error saving sdata');
	});
})

router.post('/bingo', function (req, res) {
	// body...
	console.log('Post call for /');
	var todo = new Todo(req.body);
	todo.save(function (err) {
		// body...
		console.log('Error saving sdata');
	});
})

module.exports = router;