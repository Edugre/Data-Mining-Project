"""
Pages module for the Supermarket Shopping System.
Contains individual page implementations.
"""

from . import home as home
from . import shopping as shopping
from . import data_import as data_import
from . import preprocessing as preprocessing
from . import mining as mining
from . import transactions as transactions

__all__ = [
    'home',
    'shopping',
    'data_import',
    'preprocessing',
    'mining',
    'transactions'
]