import unittest
from getmyad.lib.template_convertor import js2mako

class TestTemplateConvertor(unittest.TestCase):

    def cmp(self, js_template, mako_template):
        converted = js2mako(js_template).splitlines()
        original = mako_template.splitlines()
        lines = zip(converted, original, xrange(1, len(original) + 1))
        for l1, l2, i in lines: 
            self.assertEquals(l1, l2, 
                            'Lines #%d are not equal:\n%s\n%s' % (i, l1, l2))

    def test_variable_substitution(self):
        self.cmp('''Hello ${who}''',
                 '''Hello ${who}''')

    def test_objects_to_dict(self):
        self.cmp('''Hello ${who.subvar}''',
                 '''Hello ${who['subvar']}''')
        self.cmp('''border: ${v.v1}px solid ${v.v2};''',
                 '''border: ${v['v1']}px solid ${v['v2']};''')

    def test_if(self):
        self.cmp('''{if Description.hide} \n'''
                 '''    display: hide; \n'''
                 '''{elseif inline}\n'''
                 '''    display: inline; \n'''
                 '''{else}\n'''
                 '''    display: block; \n'''
                 '''{/if}''',
                 '''% if Description.hide:\n'''
                 '''    display: hide; \n'''
                 '''% elif inline:\n'''
                 '''    display: inline; \n'''
                 '''% else:\n'''
                 '''    display: block; \n'''
                 '''% endif''') 

    def test_logical_operators(self):
        self.cmp('''{if var1 || var2 && var3} \n'''
                 '''    doit(); \n'''
                 '''{/if}''',
                 '''% if var1 or var2 and var3:\n'''
                 '''    doit(); \n'''
                 '''% endif''')

if __name__ == '__main__':
    unittest.main()
