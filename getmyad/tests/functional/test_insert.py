from getmyad.tests import *

class TestInsertController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='insert', action='index'))
        # Test response...
