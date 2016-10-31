var mongoose = require('mongoose');
var express = require('express');
//var Todo = require('./Server/db/db');
var router = express().Router();
console.log('router', router);
router.get('/', function (req, res) {
	// body...
	res.send('Hello from todos/router.js');
});

module.exports = router;