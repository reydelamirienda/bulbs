# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Bulbs supports plugabble type systems.

"""
from bulbs.property import String, Integer, Float, List, Dictionary, Null


class TypeSystem(object):
    """Abstract base class for plugabble database type systems."""

    #: The backend resource's content type.
    content_type = None

    #: Converter object used to convert Python values to database values.
    database = None

    #: Converter object used to covert database values to Python values.
    python = None

    def __init__(self):

        # Python type mappings, format: Python type -> DataType Class
        self.type_map = dict()
        self.type_map[str] = String
        self.type_map[int] = Integer
        self.type_map[float] = Float
        self.type_map[list] = List
        self.type_map[dict] = Dictionary
        self.type_map[type(None)] = Null

        # You don't need the DB-type to Class mappings because for to_python() 
        # we get the DataType class from the property_instance in Model.

    def to_db(self,value):
        """Returns a database-property value coerced to its database type."""
        python_type = type(value)
        datatype_class = self.type_map[python_type]
        return datatype_class.to_db(self,value)

    def to_python(self,property_instance,value):
        """Returns a database-property value coerced to its Python type."""
        # TODO: warn or log errors
        datatype_class = property_instance.datatype
        return datatype_class.to_python(self,value)


class Converter(object):
    """Abstract base class of conversion methods called by DataType classes."""

    def to_string(self,value):
        raise NotImplementedError

    def to_integer(self,value):
        raise NotImplementedError
    
    def to_long(self,value):
        raise NotImplementedError

    def to_float(self,value):
        raise NotImplementedError

    def to_list(self,value):
        raise NotImplementedError

    def to_dictionary(self,value):
        raise NotImplementedError

    def to_null(self,value):
        raise NotImplementedError


#
# The JSON Type System
#

class Database(Converter):
    """Converts Python values to database values."""

    # The JSON type system is just a simple pass through.

    def to_string(self,value):
        return value

    def to_integer(self,value):
        return value
    
    def to_long(self,value):
        return value

    def to_float(self,value):
        return value

    def to_list(self,value):
        return value

    def to_dictionary(self,value):
        return value

    def to_null(self,value):
        return value


class Python(Converter):
    """Converts database values to Python values."""
    
    def to_string(self,value):
        return self._coerce(str,value)

    def to_integer(self,value):
        return self._coerce(int,value)

    def to_long(self,value):
        return self._coerce(long,value)

    def to_float(self,value):
        return self._coerce(float,value)              

    def to_list(self,value):
        return self._coerce(list,value)

    def to_dictionary(self,value):
        return self._coerce(dict,value)

    def to_null(self,value):
        return None

    def _coerce(self,datatype,value):
        # TODO: warn or log conversion errors
        try: return datatype(value)
        except: return None


class JSONTypeSystem(TypeSystem):

    content_type = "application/json"
    database = Database()
    python = Python()
    











