var app = angular.module('movieApp');


app.controller('MovieCntrl', function($scope, $http) {
	$scope.isEditting  = true;
	var index = -1;
	$scope.movies = [];
	function fetchAllMovies() {
		$http.get('/movies').success(function(response) {
			$scope.movies = response.response;
		});
	}
	fetchAllMovies();
	console.log($scope.movies);
	
	$scope.createMovie = function(a_movieName) {
		var obj = {movieName : a_movieName, index : ++index};
		$scope.movieName = '';
		//$scope.movies.push(obj);
		$http.post('/saveData', obj).success(function(resData) {
			console.log("Data saved succesfully!!!", resData);
			$scope.movies.push(resData);
		});
	}
	
	$scope.edit = function(a_obj) {
		$scope.movieName = a_obj.movieName;
		index = a_obj.index;
		$scope.isEditting = false;
		$scope.prevObj = a_obj;
	}
	
	$scope.updateMovie = function(a_movieName) {
		var obj = {movieName : a_movieName, index : index};
		
		$http.put('/update', [obj, $scope.prevObj]).success(function(resData) {
			console.log('res in update ', resData);
			//$scope.movies[index] = obj;
			fetchAllMovies();
			$scope.isEditting  = true;
		});
		
		
	}
	$scope.delete = function(movieObj) {
		
		$http.delete('/delete/'+movieObj.movieName).success(function(res) {
			console.log("delete response--", res);
			fetchAllMovies();
			index--;
		});
		
		
	}
	
	
	
	
	
	
	
	
	
	
});