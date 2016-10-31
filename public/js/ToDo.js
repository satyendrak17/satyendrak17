var ToDoApp = angular.module('ToDoApp');
ToDoApp.controller('ToDoCntrl', function ($scope, $http) {
	// body...
	$scope.tasks = []; 
	function getAllTasks() {
		console.log('Get All called!!');
		$http.get('/todos').success(function(response) {
			$scope.tasks = response.response;
			console.log('All response', response.response);
		});
	
	}
	getAllTasks();
	

	
	var seq=-1;
	$scope.isEditting = true;
	$scope.createTask = function () {
		var obj = {task : $scope.task, seq : ++seq};
		$scope.tasks.push(obj);

		$http.post('/saveTask', obj).success(function (res) {
			console.log(' saving the response data', res);
			$scope.task = '';
		});

	}

	$scope.edit = function(data) {
		$scope.isEditting = false;
		$scope.task = data.task;
		seq = data.seq;
		$scope.currentEditing = data;
	}

	$scope.updateTask = function (task, isSave) {

		var obj = {task : task, seq : seq};
		$scope.tasks[seq] = obj;
		seq = seq;
		$scope.isEditting = true;
		$http.put('/bingo/:id', [obj, $scope.currentEditing]).success(function(data) {
			console.log('Response data after updating the doc', data);
			$scope.task = '';
		});

	}

	$scope.delete = function(task) {
		console.log('Data to be delted--', task);
		var taskToDelete = task.task;
		$http.delete('/todo/delete/'+taskToDelete).success(function(res) {
			console.log('res in delete fun', res);
			getAllTasks(); // get the latest tasks after deletion..
		});
	}

})