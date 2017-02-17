var UserDetails = UserDetails || (function() {
	
	var tabs;
	
	/**
	 * Создаёт интерфейс подробной информации пользователя 
	 */
	function UserDetails() {
		var tabs = $("<div />").appendTo($('body'));
		tabs.tabs();
		$(tabs).tabs('add', '/test.html', 'Overview');
//		return "asdf";
		return tabs;
	}
	
	
	return {
		UserDetails: UserDetails
	}
	
})();
