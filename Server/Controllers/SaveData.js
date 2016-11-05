var MovieModel = require('../ModelDB/db').Movie;

module.exports = function(req, res) {
	var movieModel = new MovieModel(req.body);
	var promise = movieModel.save();
	promise.then(function(response) {
		res.send(response);
	});
}