



$.ajax(this.href, {
	success: function(data) {
	$('#main').html($(data).find('#main *'));
	$('#notification-bar').text('The page has been successfully loaded');
	},
	error: function() {
	$('#notification-bar').text('An error occurred');
	}
});
