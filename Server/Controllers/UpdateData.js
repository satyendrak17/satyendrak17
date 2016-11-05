var MovieModel = require('../ModelDB/db').Movie;

module.exports = function(req, res) {
	
	MovieModel.update({movieName : req.body[1].movieName}, {movieName : req.body[0].movieName}, function(err, response) {
		if(!err) {
			res.send(response);
		}
	});
}