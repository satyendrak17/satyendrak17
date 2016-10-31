
var routesCntrl = require('../Server/todos/routes');
var bingoCntrl = require('../Server/Controllers/controllerOne');
deleteCntrl = require('../Server/Controllers/deleteTodo');
var getAllData = require('../Server/Controllers/getAllData');

var saveCntrl = require('../Server/Controllers/saveCntrl');

module.exports = function routes(app) {
	app.get('/todos', getAllData);
	//app.use('/bingo', bingoCntrl);
	app.put('/bingo/:id', bingoCntrl);

	app.post('/saveTask', saveCntrl);

	app.delete('/todo/delete/:taskToDelete', deleteCntrl);
};