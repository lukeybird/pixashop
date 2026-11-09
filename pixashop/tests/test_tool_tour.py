"""Keep the user-facing tour aligned with the real editor toolbox."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

class ToolTourTests(unittest.TestCase):
    def test_every_registered_tool_has_one_explanation(self):
        steps = json.loads((ROOT / 'pixashop/manual/tools.json').read_text())
        source = (ROOT / 'crates/engine/src/shell_commands.rs').read_text()
        tools = re.findall(r'\("(tools\.select\.[^"]+)", "([^"]+)",', source)
        self.assertEqual(len(steps), len({s['id'] for s in steps}))
        self.assertEqual({s['id'] for s in steps}, {i for i, _ in tools})
        names = dict(tools)
        for step in steps:
            self.assertEqual(step['title'], names[step['id']])
            self.assertTrue(step['description'].strip())
            self.assertTrue(step['try_it'].strip())
            self.assertLessEqual(len(step['description'].split()), 25)
            self.assertLessEqual(len(step['try_it'].split()), 35)

    def test_tour_follows_actual_toolbar_groups(self):
        source = (ROOT / 'crates/ui-egui/src/panels/toolbar.rs').read_text().split('pub(crate) const TOOL_SECTIONS:', 1)[1].split('];', 1)[0]
        ids = ['tools.select.' + n[0].lower() + n[1:] for n in re.findall(r'Tool::(\w+)', source)]
        steps = json.loads((ROOT / 'pixashop/manual/tools.json').read_text())
        self.assertEqual([s['id'] for s in steps], ids)

if __name__ == '__main__':
    unittest.main()
