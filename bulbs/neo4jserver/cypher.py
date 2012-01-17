# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

import logging
log = logging.getLogger(__name__)

import os
import re
import yaml 
from string import Template

from bulbs.utils import initialize_elements

class Cypher(object):

    def __init__(self,resource):
        self.resource = resource
        
    def query(self, query, params=None):
        resp = self.resource.cypher(query,params)
        return initialize_elements(self.resource, resp)


class ScriptError(Exception):
    pass


class YamlScripts(object):
    """Load Gremlin scripts from a YAML source file."""

    def __init__(self,file_name=None):
        self.file_name = self._get_file_name(file_name)
        self.templates = self._get_templates(self.file_name)

    def get(self,name,params={}):
        """Return a Gremlin script, generated from the params."""
        template = self.templates.get(name)
        #params = self._quote_params(params)
        return template.substitute(params)
        
    def refresh(self):
        """Refresh the stored templates from the YAML source."""
        self.templates = self._get_templates()

    def override(self,file_name):
        new_templates = self._get_templates(file_name)
        self.templates.update(new_templates)

    def _get_file_name(self,file_name):
        if file_name is None:
            dir_name = os.path.dirname(__file__)
            file_name = utils.get_file_path(dir_name,"gremlin.yaml")
        return file_name

    def _get_templates(self,file_name):
        templates = dict()
        log.debug(file_name)
        f = open(file_name)
        yaml_map = yaml.load(f)    
        for name, template in yaml_map.items():
            #template = ';'.join(lines.split('\n'))
            method_signature = self._get_method_signature(template)
            log.debug(method_signature)
            templates[name] = Template(template)
        return templates

    def _get_method_signature(self,template):
        lines = template.split('\n')
        first_line = lines[0]
        log.debug("FIRST LINE: %s", first_line)
        pattern = 'def(.*){'
        try:
            method_signature = re.search(pattern,first_line).group(1).strip()
            return method_signature
        except AttributeError:
            raise ScriptError("Each Gremln script in the YAML file must be defined as a Groovy method.")

    def _quote_params(self,params):
        quoted_tuple = map(self._quote,params.items())
        params = dict(quoted_tuple)
        return params

    def _quote(self,pair):
        key, value = pair
        if type(value) == str:
            value = "'%s'" % value
        elif value is None:
            value = ""
        return key, value
