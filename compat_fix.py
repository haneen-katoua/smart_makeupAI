# -*- coding: utf-8 -*-
"""
compat_fix.py — Python 3.10+ Compatibility Fix
===============================================

هذا الملف يجب أن يُستخدم قبل استيراد أي مكتبات أخرى
خاصة experta و frozendict

الاستخدام:
  import compat_fix  # يجب أن يكون الاستيراد الأول
  from experta import *
"""

import sys
import collections

# Python 3.10+ removed collections.abc aliases from collections module
# frozendict uses collections.Mapping which no longer exists
if sys.version_info >= (3, 10):
    if not hasattr(collections, 'Mapping'):
        import collections.abc
        collections.Mapping = collections.abc.Mapping
    if not hasattr(collections, 'MutableMapping'):
        import collections.abc
        collections.MutableMapping = collections.abc.MutableMapping
    if not hasattr(collections, 'Sequence'):
        import collections.abc
        collections.Sequence = collections.abc.Sequence
    if not hasattr(collections, 'MutableSequence'):
        import collections.abc
        collections.MutableSequence = collections.abc.MutableSequence
    if not hasattr(collections, 'Set'):
        import collections.abc
        collections.Set = collections.abc.Set
    if not hasattr(collections, 'MutableSet'):
        import collections.abc
        collections.MutableSet = collections.abc.MutableSet
    if not hasattr(collections, 'Iterable'):
        import collections.abc
        collections.Iterable = collections.abc.Iterable
    if not hasattr(collections, 'Iterator'):
        import collections.abc
        collections.Iterator = collections.abc.Iterator
    if not hasattr(collections, 'Callable'):
        import collections.abc
        collections.Callable = collections.abc.Callable
    if not hasattr(collections, 'Hashable'):
        import collections.abc
        collections.Hashable = collections.abc.Hashable
    if not hasattr(collections, 'Sized'):
        import collections.abc
        collections.Sized = collections.abc.Sized
    if not hasattr(collections, 'Container'):
        import collections.abc
        collections.Container = collections.abc.Container

print("✓ Python 3.10+ compatibility fix applied")