# Copyright (c) 2015-2017, Felix Fontein <felix@fontein.de>
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

from ansible.plugins.lookup import LookupBase
from ansible.template import Templar


class LookupModule(LookupBase):
    def __evaluate(self, expression, templar, variables={}):
        """Evaluate expression with templar.

        ``expression`` is the expression to evaluate.
        ``variables`` are the variables to use.
        """
        templar.set_available_variables(variables)
        return templar.template("{}{}{}".format("{{", expression, "}}"), cache=False)

    def __process(self, result, terms, index, current, templar, variables):
        """Fills ``result`` list with evaluated items.

        ``result`` is a list where the resulting items are placed.
        ``terms`` is the list of terms provided to the plugin.
        ``index`` is the current index to be processed in the list.
        ``current`` is a list, where the first ``index`` items are filled
            with the values of ``item[i]`` for ``i < index``.
        ``variables`` are the variables currently available.
        """
        # Prepare current state (value of 'item')
        data = {i: current[i] for i in range(index)}

        # If we are done, add to result list:
        if index == len(terms):
            result.append(data)
            return

        # Evaluate expression in current context
        vars = variables.copy()
        vars['item'] = data
        try:
            items = self.__evaluate(terms[index], templar, variables=vars)
        except Exception as e:
            raise Exception('Caught "{0}" while evaluating "{1}" with item == {2}'.format(e, terms[index], data))

        # Continue
        if isinstance(items, dict):
            for i, v in items.items():
                current[index] = {'key': i, 'value': v}
                self.__process(result, terms, index + 1, current, templar, variables)
        else:
            for i in items:
                current[index] = i
                self.__process(result, terms, index + 1, current, templar, variables)

    def run(self, terms, variables=None, **kwargs):
        result = []
        if len(terms) > 0:
            templar = Templar(loader=self._templar._loader)
            self.__process(result, terms, 0, [None] * len(terms), templar, variables)
        return result
