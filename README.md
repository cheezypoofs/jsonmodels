A module of classes useful for defining object models that are serialized
and deserialized via JSON.

One specific use case would be when using a REST client. In python,
dicts and lists are easy to use, and the stock json library is quite good
and creating and using them. However, if you want to define actual object
Models, possibly with some logic in them, it becomes cumbersome having to
insert each property on deserialization and extracting only set properties
on serialization.

These classes attempt to solve this problem.

```
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
```
