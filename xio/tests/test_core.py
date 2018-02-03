#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

if __name__ == '__main__':

    from xio.core.lib.db.tests import Tests as dbTests
    from xio.core.lib.data.tests import Tests as dataTests
    from xio.core.lib.crypto.tests import TestCases as cryptoTests
    
    from xio.core.tests.test_resource import TestCases as test_resource
    from xio.core.tests.test_user import TestCases as test_user
    from xio.core.app.tests.test_app import TestCases as test_app

    unittest.main()








  





