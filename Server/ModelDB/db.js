var mongoose = require('mongoose');

mongoose.Promise = global.Promise;

mongoose.connect('mongodb://localhost:27017/movies');

var Movie = mongoose.model('Movie', {
	movieName : String,
	index : Number
});

module.exports.Movie = Movie;