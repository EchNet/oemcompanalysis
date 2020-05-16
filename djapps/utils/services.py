#
# utils/services.py
# Support for application services.
#

import inspect


class ServiceAggregator:
  """
    THE PROBLEMS

    Suppose you have an application with a moderately complex data graph, with a good 
    number of service methods that work with various sections of the data graph.  A typical
    service method starts at some entity in the graph and may then  travel to other points
    in the course.  

    The "what" belongs to the context.  The parameters are "how".  Example: set some
    property of a user.  The user is in the context and the new property value is the
    parameter.

    Similarly, the values that make up the context for a service method should not be
    expressed as method parameters.  Instead, the client code should be able to establish
    context once and issue a series of service method calls with respect to that context.

    Time is another dimension.

    ServiceAggregator separates the details of context management from the service methods
    themselves, offering a one-stop shop for all service methods.  Client code doesn't need
    knowledge of which methods belong to which mixins.  
    The methods can be packaged any old way.

    is unsufficient, a clear error is raised.  It's also verifying that entity relationships
    are sane.

    MyServiceAggregatorSubclass(context_key1=value1, context_key2=value2).method()


    What a context element is.  They are exposed as read-only properties on the
    ServiceAggregator itself.

    To use: write your mixin classes and test them.  subclass this class, and inherit from your mixin classes.  Define your context elements as described below.  Roll them all up in a get_context_elements function.
  """

  class ContextElement:
    """
      A ContextElement describes the semantics of an entry in the context dictionary.
      This class must be subclassed for each element of the service context. 
    """

    class Meta:
      """
        At the minimum, every ContextElement subtype must have an inner Meta class 
        that defines KEY and TYPE. 
      """
      KEY = ""  # The property name, a string (e.g. "user").
      TYPE = object  # The property class.  A ValueError is raised if a value is incompatible.

    def get_implicit_elements(self, obj):
      """
        A ContextElement may identify additional associated values to be inserted
        into the context whenever this type of element is inserted.  For example, a
        User implies its Company.  Return a dictionary of element key to property
        value.  In the case of a User implying its company, this would be
        dict(company=obj.company).

        If a conflicting element already exists in the context, a ValueError is 
        raised.
      """
      return None

    def get_default_elements(self, obj):
      """
        A ContextElement may provide default values for other elements.  For example,
        a User might provide a default time zone.  Default values cannot conflict 
        with each other.  Return a dictionary of element key to property value, as
        get_implicit_elements does.
      """
      return None

  class _Context:
    """
      Implementation class, responsible for validating and maintaining context values.
    """

    def __init__(self, element_registry, values=None, defaults=None):
      self.element_registry = element_registry
      self.values = values or dict()
      self.defaults = defaults or dict()

    def assimilate(self, **kwargs):
      for key, value in kwargs.items():
        element = self.element_registry.get(key, None)
        if not element:
          raise ValueError(f"Unrecognized context element {key}.")
        if value is not None and not isinstance(value, element.Meta.TYPE):
          raise ValueError(f"{value} is not of type {element.Meta.TYPE}")
        elif key in self.values:
          if self.values.get(key) != value:
            raise ValueError(f"Conflicting {key} values: {value} vs {self.values[key]}.")
        else:
          self.values[key] = value
          if value:
            implicit_elements = element.get_implicit_elements(value)
            if implicit_elements:
              self.assimilate(**implicit_elements)
            # Apply defaults after implicits, so that defaults set by implicits are overwritten
            # by our defaults.
            default_elements = element.get_default_elements(value)
            if default_elements:
              self.assimilate_defaults(**default_elements)
      return self

    def assimilate_defaults(self, **kwargs):
      for key, value in kwargs.items():
        element = self.element_registry.get(key, None)
        if not element:
          raise ValueError(f"Unrecognized context element {key}.")
        if value is not None and not isinstance(value, element.Meta.TYPE):
          raise ValueError(f"{value} is not of type {element.Meta.TYPE}")
        self.defaults[key] = value
      return self

    def get(self, key):
      try:
        return (self.values if key in self.values else self.defaults).get(key)
      except KeyError:
        raise AttributeError(f"There is no {key} in context.")

    def clone(self):
      return self.__class__(self.element_registry, dict(**self.values), dict(**self.defaults))

  # Back to ServiceAggregator...

  _context_registry = None

  def __init__(self, context=None, **kwargs):
    """
      Construct a ServiceAggregator from context elements specified in kwargs.
    """
    self._context = (context or self._Context(self.get_context_registry())).assimilate(**kwargs)

  def add_context(self, **kwargs):
    """
      Add elements specified in kwargs to the context.
    """
    self._context.assimilate(**kwargs)

  def drill_down(self, **kwargs):
    """
      Create a new ServiceAggregator of the same type with additional context elements
      specified in kwargs.
    """
    print(self.__class__)
    return self.__class__(self._context.clone(), **kwargs)

  def __getattr__(self, key):
    """
      Expose context elements as read-only properties of the ServiceAggregator itself.
    """
    if key in self.get_context_registry():
      return self._context.get(key)
    raise AttributeError(key)

  @classmethod
  def get_context_registry(myclass):
    """ Implementation method. """
    if not myclass._context_registry:
      registry = {}
      # Every subclass is expected to have a Meta class that contains its context elements.
      for member in myclass.Meta.__dict__.values():
        if inspect.isclass(member) and issubclass(member, myclass.ContextElement):
          # Every context element class is expected to have a Meta class that defines its key.
          registry[member.Meta.KEY] = member()
      myclass._context_registry = registry
    return myclass._context_registry
