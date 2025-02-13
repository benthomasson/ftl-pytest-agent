

from ftl_agent.default_tools import Package
import os
import faster_than_light as ftl


HERE = os.path.dirname(os.path.abspath(__file__))

def test_package():
    os.chdir(HERE)
    state= {'inventory': ftl.load_inventory('inventory.yml'), 'modules': ['modules']}
    package = Package(state)
    package.forward('httpd', 'present')


