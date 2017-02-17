from getmyad.tests import *

class TestManagerController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='manager', action='index'))
        # Test response...
