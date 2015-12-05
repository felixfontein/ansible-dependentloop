# Copyright (c) 2015, Felix Fontein <felix@fontein.de>
#
# Based on runner/lookup_plugins/items.py from the original Ansible
# distribution, which is
# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
#
#
# This plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this plugin.  If not, see <http://www.gnu.org/licenses/>.

import ansible.utils as utils
import ansible.errors as errors
from ansible.utils import safe_eval
from ansible.utils import template

class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def __lookup_injects(self, terms, inject):
        results = []
        for x in terms:
            intermediate = utils.listify_lookup_plugin_terms(x, self.basedir, inject)
            results.append(intermediate)
        return results

    def process(self, result, terms, index, current, inject):
        d = {i: current[i] for i in range(index)}
        if index == len(terms):
            result.append(d)
            return
        if type(terms[index]) in {str, unicode}:
            inject_ = {}
            inject_.update(inject)
            inject_['item'] = d
            items = safe_eval(template.template_from_string(self.basedir, terms[index], inject_, fail_on_undefined=True))
        else:
            items = terms[index]
        if type(items) == dict:
            for i in items:
                current[index] = {'key': i, 'value': items[i]}
                self.process(result, terms, index + 1, current, inject)
        else:
            for i in items:
                current[index] = i
                self.process(result, terms, index + 1, current, inject)

    def run(self, terms, inject=None, **kwargs):
        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)
        terms = self.__lookup_injects(terms, inject)[:]
        if len(terms) == 0:
            raise errors.AnsibleError("with_dependent requires at least one element in the nested list")

        result = []
        self.process(result, terms, 0, [None] * len(terms), inject)
        return result
