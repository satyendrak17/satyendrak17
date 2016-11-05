var MovieModel = require('../ModelDB/db').Movie;

module.exports = function(req, res) {
	var moviename = req.params.movieName;
	MovieModel.remove({movieName : moviename}, function(err) {
		if(!err) {
			res.send('Doc deleted successfully!!!');
		}
	});
}