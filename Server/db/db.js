var mongoose = require('mongoose');

mongoose.Promise = global.Promise; // To use query as a promise..

mongoose.connect('mongodb://localhost/todos'); // todos is the data base name will create one if not existing

// create a schema for todos.. to store objects
// New comments
var Todo = mongoose.model('Todo', {
	task : String,
	seq : Number
});

module.exports.Todo = Todo;
