from unittest.mock import patch

from flask import Markup

from storage.binary_service import BinaryService
from test.unit.compare.compare_plugin_test_class import ComparePluginTest  # pylint: disable=wrong-import-order
from ..code.file_header import ComparePlugin


class TestComparePluginSoftware(ComparePluginTest):
    PLUGIN_NAME = 'File_Header'

    def setup_plugin(self):
        return ComparePlugin(self, config=self.config, plugin_path=None)

    @patch.object(target=ComparePlugin, attribute="_add_binaries_to_fos", new=lambda s, x: None)
    def test_compare(self):
        result = self.c_plugin.compare_function([self.fw_one, self.fw_two, self.fw_three])

        assert all(key in result for key in ['hexdiff', 'ascii', 'offsets']), 'not all result keys given'
        assert all(isinstance(result[key], Markup) for key in ['hexdiff', 'ascii', 'offsets']), 'partial results should be flask.Markup strings'

        assert '>4B<' in result['hexdiff'], 'no bytes in hexdump or bad upper case conversion'
        assert '<br />' in result['hexdiff'], 'no linebreaks found'

    @patch.object(target=BinaryService, attribute="get_binary_and_file_name", new=lambda s, uid: (b'1234', '/my/way/or/the/highway'))
    def test_add_binaries(self):
        self.c_plugin._add_binaries_to_fos([self.fw_one, self.fw_two])  # pylint: disable=no-member,protected-access

        assert self.fw_one.binary == self.fw_two.binary
        assert self.fw_two.binary == b'1234'

    def test_at_least_two_are_common(self):
        should_be_true = [3, 2, 1, 2]
        should_be_false = [5, 4, 3, 1, 2, 6]
        assert self.c_plugin._at_least_two_are_common(should_be_true), 'should find a commonality'
        assert not self.c_plugin._at_least_two_are_common(should_be_false), 'should not find a commonality'