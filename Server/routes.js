var getAllDataCntl = require('../Server/Controllers/GetAllData');
var saveCntrl = require('../Server/Controllers/SaveData');
var updateCntrl = require('../Server/Controllers/UpdateData');
var deleteCntrl = require('../Server/Controllers/DeleteData');

module.exports = function route(app) {
	app.get('/movies', getAllDataCntl);
	app.post('/saveData', saveCntrl);
	app.put('/update', updateCntrl);
	app.delete('/delete/:movieName', deleteCntrl);
}