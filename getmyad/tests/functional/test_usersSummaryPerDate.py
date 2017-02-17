from getmyad.tests import *

class TestUserssummaryperdateController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='usersSummaryPerDate', action='index'))
        # Test response...
