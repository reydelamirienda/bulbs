# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for interacting with indices on Rexster.

"""

from bulbs.utils import initialize_element, initialize_elements, get_one_result

import logging
log = logging.getLogger(__name__)


class VertexIndexProxy(object):
    """
    An interface for interacting with indices on Rexster.

    :param resource: The Resource object for the database.
    :param index_class: The index class for this proxy, e.g. RexsterIndex.

    """

    def __init__(self,index_class,resource):
        self.index_class = index_class
        self.resource = resource
                        
    def create(self,index_name,*args,**kwds):
        """ 
        Adds an index to the database and returns it. 

        index_keys must be a string in this format: '[k1,k2]'
        Don't pass actual list b/c keys get double quoted.

        :param index_name: The name of the index to create.

        :param index_class: The class of the elements stored in the index. 
                            Either vertex or edge.
        
        """
        resp = self.resource.create_vertex_index(index_name,*args,**kwds)
        index = self.index_class(self.resource,resp.results)
        self.resource.registry.add_index(index_name,index)
        return index

    def get(self,index_name):
        """Returns the Index object with the specified name or None if not found."""
        resp = self.resource.get_vertex_index(index_name)
        if resp.results:
            index = self.index_class(self.resource,resp.results)
            self.register(index_name,index)
            return index

    def get_or_create(self,index_name,*args,**kwds):
        # get it, create if doesn't exist, then register it
        index = self.get(index_name)
        if not index:
            index = self.create(index_name,*args,**kwds)
        return index

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        return self.resource.delete_vertex_index(index_name)


class EdgeIndexProxy(object):
    """
    An interface for interacting with indices on Rexster.

    :param resource: The Resource object for the database.
    :param index_class: The index class for this proxy, e.g. RexsterIndex.

    """

    def __init__(self,index_class,resource):
        self.index_class = index_class
        self.resource = resource
                        
    def create(self,index_name,*args,**kwds):
        """ 
        Adds an index to the database and returns it. 

        index_keys must be a string in this format: '[k1,k2]'
        Don't pass actual list b/c keys get double quoted.

        :param index_name: The name of the index to create.

        :param index_class: The class of the elements stored in the index. 
                            Either vertex or edge.
        
        """
        resp = self.resource.create_edge_index(index_name,*args,**kwds)
        index = self.index_class(self.resource,resp.results)
        self.resource.registry.add_index(index_name,index)
        return index

    def get(self,index_name):
        """Returns the Index object with the specified name or None if not found."""
        resp = self.resource.get_edge_index(index_name)
        if resp.results:
            index = self.index_class(self.resource,resp.results)
            self.register(index_name,index)
            return index

    def get_or_create(self,index_name,*args,**kwds):
        # get it, create if doesn't exist, then register it
        index = self.get(index_name)
        if not index:
            index = self.create(index_name,*args,**kwds)
        return index

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        return self.resource.delete_edge_index(index_name)

# Deprecated / Not Fully Implemented
class IndexProxy(object):

    def __init__(self,index_class,resource):
        self.index_class = index_class
        self.resource = resource
        self.indicesV = VertexIndexProxy(index_class,resource)
        self.indicesE = EdgeIndexProxy(index_class,resource)

    def create(self,index_name,*args,**kwds):
        """ 
        Adds an index to the database and returns it. 

        index_keys must be a string in this format: '[k1,k2]'
        Don't pass actual list b/c keys get double quoted.

        :param index_name: The name of the index to create.

        :param index_class: The class of the elements stored in the index. 
                            Either vertex or edge.
        
        """
        return indices.create(index_name,*args,**kwds)

    def get(self,index_name):
        """Returns the Index object with the specified name or None if not found."""
        return indices.get(index_name)

    def get_or_create(self,index_name,*args,**kwds):
        # get it, create if doesn't exist, then register it
        return indices.get_or_create(index_name,*args,**kwds)

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        return indices.delete(index_name)


class Index(object):

    def __init__(self,resource,results):
        self.resource = resource
        self._results = results

    @property
    def index_name(self):
        """Returns the index name."""
        return self._results.data['name']

    @property
    def index_class(self):
        """Returns the index class, which will either be vertex or edge."""
        return self._results.data['class']

    @property
    def index_type(self):
        """Returns the index type, which will either be automatic or manual."""
        return self._results.data['type']

    # TODO: change to lookup?
    def get(self,key=None,value=None,**pair):
        """
        Return a generator containing all the elements with key property equal 
        to value in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize the results. Defaults to False. 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        key, value = self._parse_args(key,value,pair)
        resp = self.resource.lookup_vertex(self.index_name,key,value)
        return initialize_elements(self.resource,result)

    def _parse_args(self,key,value,pair):
        if pair:
            key, value = pair.popitem()
        return key, value
 
    def count(self,key=None,value=None,**pair):
        """
        Return a count of all elements with 'key' equal to 'value' in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        key, value = self._parse_args(key,value,pair)
        resp = self.resource.index_count(self.index_name,key,value)
        return resp.content['totalSize']

    def keys(self):
        """Return the index's keys."""
        resp = self.resource.index_keys(self.index_name)
        return list(resp.results)


class AutomaticIndex(Index):
    
    def rebuild(self):
        # need class_map b/c the Blueprints need capitalized class names, 
        # but Rexster returns lower-case class names for index_class
        method_map = dict(vertex=self.resource.rebuild_vertex_index,
                          edge=self.resource.rebuild_edge_index)
        rebuild_method = method_map.get(self.index_class)
        resp = rebuild_method(self.index_name)
        return list(resp.results)


class ManualIndex(Index):
    """
    Creates, retrieves, and deletes indices provided by the graph database.

    Use this class to get, put, and update items in an index.
    

    :param resource: The Resource object for the database.

    :param results: The results list returned by Rexster.

    :param classes: Zero or more subclasses of Element to use when 
                    initializing the the elements returned by the query. 
                    For example, if Person is a subclass of Node (which 
                    is defined in model.py and is a subclass of Vertex), 
                    and the query returns person elements, pass in the 
                    Person class and the method will use the element_type
                    defined in the class to initialize the returned items
                    to a Person object.

    Example that creates an index for Web page URL stubs, 
    adds an page element to it, and then retrieves it from the index::

        >>> graph = Graph()
        >>> graph.indices.create("page","vertex","automatic","[stub]")
        >>> index = graph.indices.get("page")
        >>> index.put("stub",stub,page._id)
        >>> page = index.get("stub",stub)

    """

    
    def put(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and return Rexster's 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.

        """
        # NOTE: if you ever change the _id arg to element, change remove() too
        key, value = self._parse_args(key,value,pair)
        method_map = dict(vertex=self.resource.put_vertex,
                          edge=self.resource.put_edge)
        put_method = method_map.get(self.index_class)
        resp = put_method(self.index_name,key,value,_id)
        return resp

    def put_unique(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and overwrite it if an 
        element already exists at that key and value; thus, there will be a max
        of 1 element returned for that key/value pair. Return Rexster's 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in 
                       the form of name='James'.

        """
        key, value = self._parse_args(key,value,pair)
        method_map = dict(vertex=self.resource.remove_vertex,
                          edge=self.resource.remove_edge)
        remove_method = method_map.get(self.index_type)
        for result in self.get(key,value):
            remove_method(self.index_name,result._id,key,value)
        resp = self.put(_id,key,value)
        return resp

    def update(self,_id,key=None,value=None,**pair):
        """
        Update the element ID for the key and value and return Rexsters' 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        return self.put_unique(_id,key,value,**pair)

         
    def get_unique(self,key=None,value=None,**pair):
        """
        Returns a max of 1 elements matching the key/value pair in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        key, value = self._parse_args(key,value,pair)
        resp = self.resource.lookup_vertex(self.index_name,key,value)
        result = get_one_result(resp)
        return initialize_element(self.resource,result)

    def remove(self,_id,key=None,value=None,**pair):
        """
        Remove the element from the index located by key/value.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        key, value = self._parse_args(key,value,pair)
        method_map = dict(vertex=self.resource.remove_vertex,
                          edge=self.resource.remove_edge)
        remove_method = method_map.get(self.index_class)
        return remove_method(self.index_name,_id,key,value)



 
