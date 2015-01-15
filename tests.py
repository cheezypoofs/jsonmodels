#!/usr/bin/env python

import json
import logging
import pprint
import sys
import unittest

import jsonmodels

logger = logging.getLogger(__name__)


class ModelTests(unittest.TestCase):

    def test_simple_get_set(self):
        class TestModel1(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')

        model = TestModel1()
        self.assertEquals(None, model.Field1)
        model.Field1 = 2
        self.assertEquals(2, model.Field1)

    def test_simple_toentity(self):
        class TestModel1(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')
            Field2 = jsonmodels.JsonProperty('Field2')

        model = TestModel1(Field1=2)

        obj = model.to_json_entity()
        logger.info(pprint.pformat(obj))
        self.assertEquals(2, obj['Field1'])
        self.assertFalse(obj.has_key('Field2'), "An unset value should not be present")

        model.Field2 = "a string!"

        obj = model.to_json_entity()
        logger.info(pprint.pformat(obj))
        self.assertTrue(obj.has_key('Field2'), "Now the string should be present")

    def test_simple_fromentity(self):
        class TestModel1(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')
            Field2 = jsonmodels.JsonProperty('Field2')

        model = TestModel1.from_json_entity({'Field1': 2})
        self.assertIsNotNone(model)
        self.assertEquals(2, model.Field1)
        self.assertEquals(None, model.Field2, "Field 2 should not have been set")

        model = TestModel1.from_json_entity({'Field2': "is set", 'Field1': 3})
        self.assertEquals(3, model.Field1)
        self.assertEquals("is set", model.Field2)

    def test_nested(self):
        class TestModel1(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')
            Field2 = jsonmodels.JsonProperty('Field2')

        class TestModel2(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')
            Field2 = jsonmodels.JsonProperty('Field2')
            Field3 = jsonmodels.JsonModelProperty('Field3', TestModel1)

        jsonstr = '''{
            "Field1": 2,
            "Field2": 5,
            "Field3": {
                "Field1": "field one",
                "Field2": "field two"
            }
        }'''

        model = TestModel2.from_json_entity(json.loads(jsonstr))
        self.assertEquals(2, model.Field1)
        self.assertEquals(5, model.Field2)
        self.assertEquals("field two", model.Field3.Field2)

        # Can we put this into json again?
        logger.info(pprint.pformat(model.to_json_entity()))
        logger.info(json.dumps(model.to_json_entity()))

    def test_list_models(self):
        class TestModel1(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')
            Field2 = jsonmodels.JsonProperty('Field2')

        class TestModel2(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonModelListProperty('Field1', TestModel1)

        model = TestModel2.from_json_entity({
            'Field1': [
            {'Field1': 1}, {'Field2': 2}
            ]
        })

        self.assertEquals(2, len(model.Field1))
        self.assertEqual(1, model.Field1[0].Field1)
        self.assertEqual(2, model.Field1[1].Field2)

        # Can we turn this into valid JSON now?
        logger.info("test_list_models to json: %s" % model.to_json_entity())


    def test_ignore_unknowns(self):
        '''
        Are values we don't know ignored on from_json_entity ?
        '''
        class TestModel1(jsonmodels.JsonModel):
            Field1 = jsonmodels.JsonProperty('Field1')
            Field2 = jsonmodels.JsonProperty('Field2')

        model = TestModel1.from_json_entity({'Field3': 'unknown'})
        self.assertIsNone(model.Field1)
        self.assertIsNone(model.Field2)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        stream=sys.stderr,
    )

    logging.getLogger().setLevel(logging.DEBUG)

    unittest.main()
