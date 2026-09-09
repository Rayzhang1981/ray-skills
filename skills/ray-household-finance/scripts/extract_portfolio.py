# -*- coding: utf-8 -*-
"""向后兼容入口：转发到 adapters/excel.py。

新代码请直接调用 scripts/adapters/excel.py。
此文件仅保留旧路径调用习惯（extract_portfolio.py）。
"""
import os
import runpy

_here = os.path.dirname(os.path.abspath(__file__))
_adapter = os.path.join(_here, 'adapters', 'excel.py')
runpy.run_path(_adapter, run_name='__main__')
