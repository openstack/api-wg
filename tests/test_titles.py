# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import glob
import os

import docutils.core
import testtools


class TestTitles(testtools.TestCase):
    def _get_title(self, section_tree):
        section = {
            'subtitles': [],
        }
        for node in section_tree:
            if node.tagname == 'title':
                section['name'] = node.rawsource
            elif node.tagname == 'section':
                subsection = self._get_title(node)
                section['subtitles'].append(subsection['name'])
        return section

    def _get_titles(self, spec):
        titles = {}
        for node in spec:
            if node.tagname == 'section':
                # Note subsection subtitles are thrown away
                section = self._get_title(node)
                titles[section['name']] = section['subtitles']
        return titles

    def _check_titles(self, filename, expect, actual):
        missing_sections = [x for x in expect.keys() if x not in actual.keys()]
        extra_sections = [x for x in actual.keys() if x not in expect.keys()]

        msgs = []
        if len(missing_sections) > 0:
            msgs.append("Missing sections: %s" % missing_sections)
        if len(extra_sections) > 0:
            msgs.append("Extra sections: %s" % extra_sections)

        for section in expect.keys():
            missing_subsections = [x for x in expect[section]
                                   if x not in actual[section]]
            # extra subsections are allowed
            if len(missing_subsections) > 0:
                msgs.append("Section '%s' is missing subsections: %s"
                            % (section, missing_subsections))

        if len(msgs) > 0:
            self.fail("While checking '%s':\n  %s"
                      % (filename, "\n  ".join(msgs)))

    def test_template(self):
        filenames = glob.glob("guidelines/*")
        for filename in filenames:
            if filename.endswith('~'):
                continue
            if os.path.isdir(filename):
                continue
            self.assertTrue(
                filename.endswith(".rst") or filename.endswith(".json"),
                "guideline file must use 'rst' or 'json'"
                "extension: {filename}".format(filename=filename))
            with open(filename) as f:
                data = f.read()

            docutils.core.publish_doctree(data)
