#!/usr/bin/env python

'''
A module of classes useful for defining object models that are serialized
and deserialized via JSON.

One specific use case would be when using a REST client. In python,
dicts and lists are easy to use, and the stock json library is quite good
and creating and using them. However, if you want to define actual object
Models, possibly with some logic in them, it becomes cumbersome having to
insert each property on deserialization and extracting only set properties
on serialization.

These classes attempt to solve this problem.

Sample Usage:

class Model1(jsonmodels.JsonModel):
    # These are simple types (like strings and ints) that JSON can already handle ok.
    Field1 = jsonmodels.JsonProperty('Field1')  # You can use the same name
    Field2 = jsonmodels.JsonProperty('field_2') # Or a different name

class Model2(jsonmodels.JsonModel):
    # If you need a nested Model:
    Nested = jsonmodels.JsonModelProperty('Nested', Model1)

    # Or even a list of nested Models..
    ListOfNested = jsonmodels.JsonModelListProperty('Nested2', Model1)


some_json_thingy = .... # A dict object returned from something like json.loads(...)

# Assuming the dict in some_json_thingy represents a Model2, you can...
model = Model2.from_json_entity(some_json_thing)

# Only the properties it recognizes will be populated and unkonwn values will be ignored.

print model.Nested.Field1 # Assuming it was there, this will print the Field1 of the Nested model.

# Go ahead and use the setter properties
model.ListOfNested = [Model2(), Model2(Nested=Model1())]

# And you can send it off via JSON again!

json.dumps(model.to_json_entity()) # A string fit for whatever

'''
import inspect
import logging

logger = logging.getLogger(__name__)

class JsonProperty(property):
    '''
    Base class implementation for declaring any property in a JsonModel.

    Some subclasses will be used to implement more intelligent things (like nesting)
    or complex types
    '''

    def __init__(self, json_name):
        '''
        json_name: What name should be used when dealing with JSON entities?
            Allows the implementation to use a different name if the default is not desirable
        '''
        property.__init__(self, self.__get, self.__set)
        self.__name = json_name

    @property
    def name(self):
        '''
        The json property name
        '''
        return self.__name

    @property
    def default(self):
        '''
        What should the default value be (before a set happens)?
        '''
        return None

    def __get(self, obj):
        '''
        Installed to the parent property class as the getter

        the 'obj' here is the instance of the JsonModel
        '''
        return obj.json_properties.get(self.name)
    def __set(self, obj, value):
        '''
        Installed to the parent property class as the setter

        the 'obj' here is the instance of the JsonModel
        '''
        obj.json_properties[self.name] = value

    def to_json_entity(self, value):
        '''
        Default implementation. Simple types can be used as-is
        '''
        return value

    def from_json_entity(self, value):
        '''
        Default implementation. Simple types can be used as-is
        '''
        return value

class JsonModelProperty(JsonProperty):
    '''
    A more complex version of JsonProperty that handles a JsonModel as the property type (nesting)
    '''
    def __init__(self, name, model_class):
        super(JsonModelProperty, self).__init__(name)
        self.__model_class = model_class

    def to_json_entity(self, value):
        '''
        Tell the model to turn itself to a json object
        '''
        return value.to_json_entity()

    def from_json_entity(self, value):
        '''
        Use the class' method to convert the json object into an instance of itself
        '''
        return self.__model_class.from_json_entity(value)

class JsonModelListProperty(JsonProperty):
    '''
    A more complex version of JsonProperty that handles a list of JsonModel as the property type
    '''
    def __init__(self, name, model_class):
        super(JsonModelListProperty, self).__init__(name)
        self.__model_class = model_class

    def to_json_entity(self, value):
        '''
        Convert to a list of json objects
        '''
        return [v.to_json_entity() for v in value]

    def from_json_entity(self, value):
        '''
        Convert from a list of json objects into model instances
        '''
        return [self.__model_class.from_json_entity(v) for v in value]

class JsonModel(object):
    '''
    Base class for any model definition that will need to be (de)serialized via JSON.

    Implementations will look like:

    class MyModel(JsonModel):

        Field1 = JsonProperty('Field1')
        Field2 = JsonModelProperty('Field2', SomeOtherModel)

    This defines a simple model with a couple fields that will understand how to 
    prepare for json via to_json_entity and how to create from json via from_json_entity
    '''

    def __init__(self, **property_initializers):
        '''
        property_initializers: keyword's to set as initial values for the json_properties
        '''
        self.__props = {}
        for prop, value in property_initializers.iteritems():
            setattr(self, prop, value)

    @property
    def json_properties(self):
        return self.__props

    def to_json_entity(self):
        '''
        Return this instance as a dictionary ready for JSON conversion

        Does *not* serialize to JSON at this level. The intent is to convert this instance into an
        object ready for json consumption but because of nesting it needs to happen at the top level.
        '''
        result = {}

        for name, prop in inspect.getmembers(self.__class__, lambda x: isinstance(x, JsonProperty)):
            if not self.__props.has_key(name):
                continue
            result[name] = prop.to_json_entity(self.__props[name])
        return result

    @classmethod
    def from_json_entity(cls, obj):
        '''
        Create a new instance of this class (or subclass) based on the json object 'obj'.
        '''
        assert isinstance(obj, dict)

        instance = cls()
        # For each property defined, see if there is a value in obj
        for name, prop in inspect.getmembers(cls, lambda x: isinstance(x, JsonProperty)):
            if not obj.has_key(name):
                continue
            instance.json_properties[prop.name] = prop.from_json_entity(obj[name])
        return instance


