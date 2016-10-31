var ToDoApp = angular.module('ToDoApp', ['ui.router']);

ToDoApp.config(function($stateProvider, $urlRouterProvider, $locationProvider) {
	$urlRouterProvider.otherwise('/');
	$stateProvider
	.state('allTodos', {
		'url' : '/allTodos',
		templateUrl : '/views/todos.html'
	}).
	state('about', {
		url : '/about',
		templateUrl : '/views/about.html'
	});

	$locationProvider.html5Mode(true);
});