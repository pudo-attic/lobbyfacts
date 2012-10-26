$(function() {

  var Person = Backbone.Model.extend({
    urlRoot: '/api/1/person'
    });

  var PersonCollection = Backbone.Collection.extend({
    model: Person,
    url: '/api/1/person',
    parse: function(response) {
      return response.results;
    }
  });

  var Persons = new PersonCollection();

  var Workspace = Backbone.Router.extend({

    routes: {
      "":                     "index",
      "person/:id":           "person"
    },

    index: function() {
      console.log("Nothing.");
    },

    person: function(id) {
      window.Persons = Persons;
      var person = Persons.get(id);
      console.log(person);
    }

  });

  new Workspace();
  Backbone.history.start({pushState: true});

});
