# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

import unittest
from testcase import BulbsTestCase

from bulbs import config
from bulbs.element import Vertex, VertexProxy, EdgeProxy, Edge


class VertexProxyTestCase(BulbsTestCase):

    def setUp(self):
        self.vertices = VertexProxy(Vertex,self.resource)

    def test_create(self):
        james = self.vertices.create({'name':'James'})
        assert isinstance(james,Vertex)
        assert type(james._id) == int
        assert james._type == "vertex"
        assert james.name == "James"

    def test_update_and_get(self):
        james1 = self.vertices.create({'name':'James'})
        self.vertices.update(james1._id, {'name':'James','age':34})
        james2 = self.vertices.get(james1._id)
        assert james2._id == james1._id
        assert james2.name == "James"
        assert james2.age == 34


    #def test_get_all(self):
     #   vertices = self.vertices.get_all()
    #    vertices = list(vertices)
    #    assert len(vertices) > 0

    #def test_remove_property(self):
    #    query_time = self.vertices.remove(self.james._id,'age')
    #    assert type(query_time) == float
    #    assert self.james.age is None

    def test_delete_vertex(self):
        james = self.vertices.create({'name':'James'})
        resp = self.vertices.delete(james._id)
        j2 = self.vertices.get(james._id)
        assert j2 == None


class VertexTestCase(BulbsTestCase):
    
    def setUp(self):
        self.vertices = VertexProxy(Vertex,self.resource)
        self.edges = EdgeProxy(Edge,self.resource)
        self.james = self.vertices.create({'name':'James'})
        self.julie = self.vertices.create({'name':'Julie'})
        assert isinstance(self.james,Vertex)
        self.edges.create(self.james,"test",self.julie)
        self.edges.create(self.julie,"test",self.james)
        
    def test_init(self):
        int(self.james._id)
        assert self.james._type == "vertex"
        assert self.james.name == "James"

    def test_get_out_edges(self):
        edges = self.james.outE()
        edges = list(edges)
        assert len(edges) == 1

    def test_get_in_edges(self):
        edges = self.james.inE()
        edges = list(edges)
        assert len(edges) == 1

    def test_get_both_edges(self):
        # ok
        edges = self.james.bothE()
        edges = list(edges)
        assert len(edges) == 2

    def test_get_both_labeled_edges(self):
        edges = self.james.bothE("test")
        edges = list(edges)
        assert len(edges) == 2

class EdgeProxyTestCase(BulbsTestCase):

    def setUp(self):
        self.vertices = VertexProxy(Vertex,self.resource)
        self.edges = EdgeProxy(Edge,self.resource)
        self.james = self.vertices.create({'name':'James'})
        self.julie = self.vertices.create({'name':'Julie'})
        
    def test_create(self):
        edge = self.edges.create(self.james,"test",self.julie)
        assert edge._outV == self.james._id
        assert edge._label == "test"
        assert edge._inV == self.julie._id
        
    def test_update_and_get(self):
        e1 = self.edges.create(self.james,"test",self.julie,{'time':'today'})
        assert e1.time == 'today'
        self.edges.update(e1._id,{'time':'tomorrow'})
        e2 = self.edges.get(e1._id)
        assert e1._id == e2._id
        assert e1._inV == e2._inV
        assert e1._label == e2._label
        assert e1._outV == e2._outV
        assert e2.time == 'tomorrow'


    #def test_get_all(self):
    #    edges = self.edges.get_all()
    #    edges = list(edges)
    #    assert type(edges) == list

    #def test_remove_property(self):
    #    e1 = self.edges.create(self.james,"test",self.julie,{'time':'today'})
    #    query_time = self.edges.remove(e1._id,{'time'})
    #    assert type(query_time) == float
    #    assert e1.time is None

    def test_delete_edge(self):
        e1 = self.edges.create(self.james,"test",self.julie)
        resp = self.edges.delete(e1._id)
        e2 = self.edges.get(e1._id)
        assert e2 == None
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VertexProxyTestCase))
    suite.addTest(unittest.makeSuite(VertexTestCase))
    suite.addTest(unittest.makeSuite(EdgeProxyTestCase))
    # NOTE: there are no tests for the Edge because it doesn't have methods.

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

