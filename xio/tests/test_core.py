#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

if __name__ == '__main__':

    from xio.core.lib.db.tests import Tests as dbTests
    from xio.core.lib.data.tests import Tests as dataTests
    from xio.core.lib.crypto.tests import TestCases as cryptoTests
    
    from xio.core.tests.test_resource import TestCases as test_resource
    from xio.core.tests.test_peer import TestCases as test_peer
    from xio.core.tests.test_peers import TestCases as test_peers
    from xio.core.app.tests.test_app import TestCases as test_app
    from xio.core.node.tests.test_node import TestCases as test_node
    
    unittest.main()








  





