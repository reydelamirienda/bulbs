# -*- coding: utf-8 -*-
# 
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Base classes for modeling domain objects that wrap vertices and edges.

"""
from bulbs.property import Property
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy
from bulbs.utils import initialize_element, get_one_result

import logging
log = logging.getLogger(__name__)

# utility function used by NodeProxy and RelationshipProxy
def instantiate_model(element_class,resource,kwds):
    model = element_class(resource)
    model._set_keyword_attributes(kwds)
    return model


class ModelMeta(type):
    """Model's metaclass used to set database Property definitions."""

    def __init__(cls, name, base, namespace):
        # store the Property definitions on the class as a dictionary mapping
        # the Property name to the Property instance
        if not hasattr(cls, '_properties'):
            # Model doesn't have any registered properties
            cls._properties = {}
        else:
            # Inherit properties and add more
            cls._properties = cls._properties.copy()
        for key, value in namespace.items():
            # loop through the class namespace looking for Property instances
            # e.g. age = Property(Integer,default=None)
            # key: age, value: Property(Integer,default=None)
            assert key not in cls._properties, "Can't redefine property '%s'" % key
            if isinstance(value, Property):
                property_instance = value     # (for clarity)
                cls._register_property(key,property_instance)
                cls._set_property_default(key,property_instance)

    def _register_property(cls,key,property_instance):
        # Property name will be none unless explicitly set via kwd param
        if property_instance.name is None:
            property_instance.name = key
        cls._properties[key] = property_instance

    def _set_property_default(cls,key,property_instance):
        # now that the property reference is stored away, 
        # initialize its vars to None, the default vale (TODO), or the fget
        if property_instance.default:
            #TODO: Make this work for scalars too
            fget = getattr(cls,value.default)
            default_value = property(fget)
        elif property_instance.fget:
            # wrapped fset and fdel in str() to make the default None work with getattr
            fget = getattr(cls,property_instance.fget)
            fset = getattr(cls,str(property_instance.fset),None)
            fdel = getattr(cls,str(property_instance.fdel),None)
            default_value = property(fget,fset,fdel)
        else:
            default_value = None
        setattr(cls,key,default_value)

    
class Model(object):

    __metaclass__ = ModelMeta

    def __setattr__(self, key, value):
        if key in self._properties:
            if value:
                property_instance = self._properties[key]
                value = property_instance.coerce_value(key,value)
        super(Model, self).__setattr__(key, value)
                
    def _set_keyword_attributes(self,kwds):
        for key, value in kwds.iteritems():
            # Notice that __setattr__ is overloaded
            setattr(self,key,value)

    def _set_property_data(self,result):
        """
        Sets Property data when an element is being initialized, after it is
        retrieved from the DB -- we set it to None if it won't set.        
        """
        for key, property_instance in self._properties.items():
            value = result.data.get(key,None)
            self._set_property_from_db(property_instance,key,value)

    def _set_property_from_db(self,property_instance,key,value):
        try:
            # Notice that __setattr__ is overloaded
            value = self._resource.type_system.to_python(property_instance,value)
            setattr(self,key,value)
        except Exception as ex:
            # TODO: log/warn/email regarding type mismatch
            log.error("Setting property '%s' with value '%s': %s", key, value, ex)
            setattr(self,key,None)        

    def _get_property_data(self):
        """Returns Property data ready to be saved in the DB."""
        data = dict()
        type_var = self._resource.config.type_var
        if hasattr(self,type_var):
            data[type_var] = getattr(self,type_var)
        for key, property_instance in self._properties.items():
            value = getattr(self,key)
            property_instance.validate(key,value)
            data[key] = self._resource.type_system.to_db(value)
        return data

    def _get_index(self,index_name):
        try:
            index = self._resource.registry.get_index(index_name)
        except KeyError:
            index = None
        return index

class Node(Vertex,Model):

    #
    # Override the _create and _update methods to cusomize behavior.
    #


    def _initialize(self,result):
        # this is called by initialize_element; 
        # putting it here to ensure method resolution order
        Vertex._initialize(self,result)
        element_type = self._get_element_type()
        self._set_property_data(result)
        self._index = self._get_index(element_type)

    def _get_element_type(self):
        element_type = getattr(self,self._resource.config.type_var)
        return element_type

    def _create(self,data,index):
        # Override this to use a custom script.
        # Make sure the gremlin script returns the created vertex and nothing else.
        # Moreover, make sure gremlin returns 1 element, not a multi-element list.
        # If you aren't indexing the node, uncomment and use the create_vertex method.
        # return self._resource.create_vertex(data)
        return self._resource.create_indexed_vertex(data,index.index_name)

    def _update(self,_id,data,index):
        # Override this to use a custom script.
        # If you aren't indexing the node, uncomment and use the update_vertex method.
        # return self._resource.update_vertex(_id,data)
        return self._resource.update_indexed_vertex(_id,data,index.index_name)

    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()
        resp = self._update(self._id,data,self._index)
        # maybe called Vertex._initialize directly b/c Neo4j doesn't return data
        self._initialize(resp.results)
        

class Relationship(Edge,Model):

    #
    # Override the _create and _update methods to customize behavior.
    #

    def _initialize(self,result):
        # this is called by initialize_element; 
        # putting it here to ensure method resolution order
        Edge._initialize(self,result)
        label = self._get_label()
        self._set_property_data(result)
        self._index = self._get_index(label)

    def _get_label(self):
        label = getattr(self,self._resource.config.label_var)
        return label

    def _create(self,outV,label,inV,data):
        return self._resource.create_edge(outV,label,inV,data)
        
    def _update(self,_id,data):
        return self._resource.update_edge(_id,data)

    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()      
        resp = self._update(self._id,data)
        #self.initialize(resp.results)

class NodeProxy(VertexProxy):

    def create(self,*args,**kwds):
        node = instantiate_model(self.element_class,self.resource,kwds)
        data = node._get_property_data()
        resp = node._create(data,self.index)
        # see comments in utils.get_one_result for why we're using this
        result = get_one_result(resp)  
        # doing it this way you're losing any extra kwds that may have been set
        return initialize_element(self.resource,result)
        
    def update(self,_id,*args,**kwds):
        node = instantiate_model(self.element_class,self.resource,kwds)
        data = node._get_property_data()
        resp = node._update(_id,data,self.index)
        result = get_one_result(resp)
        # TODO: make this work for neo4j b/c neo4j doesn't return data
        return initialize_element(self.resource,result)

    def get_all(self):
        """Returns all the elements for the model type."""
        key = self.resource.config.type_var
        value = getattr(self.element_class,self.resource.config.type_var)
        return self.index.lookup(key,value)


class RelationshipProxy(EdgeProxy):

    def create(self,*args,**kwds):
        relationship = instantiate_model(self.element_class,self.resource,kwds)
        outV, label, inV = self._parse_args(relationship,args)
        data = relationship._get_property_data()
        log.debug("DATA: %s", data)
        resp = relationship._create(outV,label,inV,data)
        log.debug("RESP: %s", resp.raw)
        result = get_one_result(resp)
        return initialize_element(self.resource,result)

    def update(self,_id,*args,**kwds):
        relationship = instantiate_model(self.element_class,self.resource,kwds)
        data = relationship._get_property_data()
        resp = relationship._update(_id,data)
        result = get_one_result(resp)
        return initialize_element(self.resource,result)

    def get_all(self):
        """Returns all the elements for the model type."""
        key = self.resource.config.label_var
        value = getattr(self.element_class,self.resource.config.label_var)
        return self.index.lookup(key,value)

    def _parse_args(self,relationship,args):
        # Two different args options:
        # 1. generic relationship args: (outV, label, inV)
        # 2. subclassed relationship args: (outV, inV) 
        args = list(args)
        if args and isinstance(args[1],Vertex):
            # no label, so this is the subclassed format;
            # the label is defined on the relationship class
            outV = args.pop(0)
            inV = args.pop(0) 
            outV = self._coerce_vertex_id(outV)
            inV = self._coerce_vertex_id(inV)
            args = (outV,relationship.label,inV)
        return args



    
    
    
