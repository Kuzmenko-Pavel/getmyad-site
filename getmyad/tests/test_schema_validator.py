# encoding: utf-8
import unittest
from getmyad.lib.schema_validator import *


class TestAdmakerValidator(unittest.TestCase):

    def should_be(self, obj, schema):
        validate(obj, schema)

    def should_not_be(self, obj, schema):
        self.assertRaises(ValidationError, validate, obj=obj, schema=schema)

    def test_string(self):
        self.should_be("str", String)
        self.should_be(u"юникод", String)
        self.should_not_be([1, 2, 3], String)
        self.assertEquals("string", validate({}, String(default="string")))

    def test_integer(self):
        self.should_be(42, Integer)
        self.should_be("42", Integer(allow_convert=True))
        self.should_not_be("42", Integer)
        self.should_not_be("42", Integer(allow_convert=False))

    def test_bool(self):
        self.should_be(True, Boolean)
        self.should_not_be("42", Boolean)
        self.assertEquals(True, validate("asd", Boolean(default=True)))

    def test_function(self):
        def func():
            pass

        class Functor():
            def __call__(self):
                pass

        self.should_be(lambda x: 42, Function)
        self.should_be(func, Function)
        self.should_be(Functor(), Function)
        self.should_not_be("str", Function)

    def test_nevermind(self):
        self.should_be(42, Nevermind)
        self.should_be("str", Nevermind)

    def test_type_name_as_object(self):
        self.should_be(True, Boolean)
        self.should_be(True, Boolean())

    def test_list(self):
        self.should_be([1, 2, 3], List(item=Integer))
        self.should_not_be("str", List(item=Integer))
        self.should_be([1, 'f', True], List)
        self.assertEquals([1, 2], validate("bad", List(default=[1, 2])))

    def test_list_item_type(self):
        self.should_not_be(['a', 'b', 'c'], List(item=Integer))
        self.should_not_be([1, 2, 'bad'], List(item=Integer))

    def test_dict(self):
        self.should_be({'a': 1, 'b': 2}, Dictionary)
        self.should_not_be(['a', 'b', 'c'], Dictionary)
        self.assertEquals({'k': 'v'},
                          validate("bad", Dictionary(default={'k': 'v'})))

    def test_implicit_dict(self):
        self.should_be({'a': 1, 'b': 2},
                       {'a': Integer, 'b': Integer})
        self.should_not_be({'a': 1, 'b': 'str'},
                           {'a': Integer, 'b': Integer})
        self.should_be({'a': {'b': 3}},
                       {'a': {'b': Integer}})
        self.should_not_be({'a': {'b': 3}},
                           {'a': {'b': String}})

    def test_dict_items_type(self):
        self.should_be({'str': 'Hello world!',
                        'int': 42,
                        'list': [1, 2, 3],
                        'other': lambda x: 42
                        },
                       Dictionary({
                        'str': String,
                        'int': Integer,
                        'list': List(item=Integer),
                        'other': Nevermind
                        }))
        self.should_not_be({
                        'str': 'Hello world!',
                        'int': 42,
                        'list': [1, 2, 3],
                        'other': lambda x: 42
                        },
                       Dictionary({
                        'str': Integer,
                        'int': String,
                        'list': Dictionary,
                        'other': Nevermind
                        }))
        self.should_not_be({}, Dictionary({'int': Integer}))
        # Если ключ отсутствует, берём значение по умолчанию
        self.assertEquals({'k': 'default'}, validate(
                          {}, Dictionary({'k': String(default='default')})))
        self.assertEquals({'k': False}, validate(
                          {}, Dictionary({'k': Boolean(default=False)})))

    def test_dict_update(self):
        schema = Dictionary({'first': Integer})
        self.assertTrue(schema['first'] == Integer)
        schema['second'] = Boolean
        schema['first'] = String
        self.should_be({'first': 'str', 'second': True}, schema)

    def test_dict_arg_aliasing(self):
        # Передаём в Dictionary схему и меняем её
        schema_obj = {'first': Integer}
        schema = Dictionary(schema_obj)
        self.assertTrue(schema['first'] == Integer)
        del schema_obj['first']
        self.assertTrue(schema['first'] == Integer)

    def test_dict_aliasing(self):
        schema1 = Dictionary({'first': Integer})
        schema2 = schema1
        schema1['second'] = Nevermind
        self.assertTrue(schema2['second'] == Nevermind)        # aliasing

        schema2 = schema1.copy()
        schema1['third'] = Nevermind
        self.assertTrue(schema2['second'] == Nevermind)
        self.assertRaises(KeyError, schema2.__getitem__, 'third')

    def test_one_of(self):
        self.should_be('center', String(one_of=["center", "left", "right"]))
        self.should_be('left', String(one_of=["center", "left", "right"]))
        self.should_not_be('top', String(one_of=["center", "left", "right"]))
        self.assertEquals('center',
                          validate("ERROR",
                                   String(one_of=["center", "left", "right"],
                                          default="center")))

    def test_regexp(self):
        self.should_be('12px', Regex(r"\d+px$"))
        self.should_be('12px TRAIL', Regex(r"\d+px"))
        self.should_not_be('100 %', Regex(r"\d+px"))
        self.should_not_be(None, Regex(""))

    def test_nested(self):
        schema = List(Dictionary(
            {'id': Integer,
             'sizes': List(Regex(r'\d+px')),
             'font': Dictionary(
                {'bold': Boolean,
                 'name': String(one_of=('Arial', 'Times', 'Verdana')),
                 'size': Integer
                })
            }))

        valid_object = \
            [{'id': 0,
              'sizes': ['192px', '200px', '100px', '300px'],
              'font': {'bold': False,
                       'name': 'Arial',
                       'size': 12}
             },
             {'id': 1,
              'sizes': ['200px', '100px', '150px', '300px'],
              'font': {'bold': True,
                       'name': 'Times',
                       'size': 14}
             }]

        from copy import deepcopy
        broken_object = deepcopy(valid_object)
        broken_object[1]['sizes'][3] = 'BAD VALUE'

        self.should_be(valid_object, schema)
        self.should_not_be(broken_object, schema)

    def test_cleaned_return_values(self):
        self.assertEquals(42, validate(42, Integer))
        self.assertEquals(43, validate("43", Integer(allow_convert=True)))
        self.assertEquals(44, validate("str", Integer(default=44)))
        self.assertEquals("str", validate("str", String))
        self.assertEquals([1, 2], validate([1, 2], List(item=Integer)))
        self.assertEquals({'k': 'v'}, validate({'k': 'v'}, Dictionary))


class TestValidationErrorMessage(unittest.TestCase):

    def check_message(self, broken_object, schema, message, where):
        ''' Проверяет, что сообщение во время проверки некорректного объекта
            ``broken_object`` схемой ``schema`` возникло исключение,
            содержащее сообщение ``message`` в точке проверки ``where``. '''
        try:
            validate(broken_object, schema)
        except ValidationError as ex:
            self.assertEquals(ex.message, message)
            self.assertEquals(ex.error_path, where)
        else:
            self.fail("Validation error not raised!")

    def test_simple_types(self):
        self.check_message("str", Boolean, "'str' is not Boolean", ["Boolean"])
        self.check_message("str", Integer, "'str' is not Integer", ["Integer"])
        self.check_message(42, String, "42 is not String", ["String"])
        self.check_message("100px", Regex(r"\d+$"),
                           "'100px' doesn't matches Regex", ["Regex"])
        self.check_message("str", List, "'str' is not List", ["List"])
        self.check_message("str", Dictionary, "'str' is not Dictionary",
                           ["Dictionary"])
        self.check_message("str", Function, "'str' is not Function",
                           ["Function"])

    def test_string_one_of(self):
        self.check_message("top", String(one_of=['left', 'right', 'center']),
                           "'top' is not String one of ['left', 'right', "
                           "'center']", ["String"])

    def test_dict_errors(self):
        self.check_message({'a': 1}, Dictionary({'b': Integer}),
                           "Dictionary has no key 'b'", ["Dictionary"])

    def test_dict_items(self):
        self.check_message({'key': 'str'}, Dictionary({'key': Integer}),
                           "'str' is not Integer",
                           ["Integer", "Dictionary['key']"])

    def test_list_items(self):
        self.check_message([0, 1, 'str'], List(Integer),
                           "'str' is not Integer",
                           ['Integer', 'List[2]'])

    def test_nested_structures(self):
        self.check_message({
            'lst': [{'id': 10},
                    {'id': 20},
                    {'id': 'str'}]},
            Dictionary(
                {'lst': List(Dictionary({'id': Integer}))}),
            "'str' is not Integer",
            ['Integer', "Dictionary['id']", 'List[2]', "Dictionary['lst']"])


if __name__ == '__main__':
    unittest.main()
