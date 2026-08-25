import pymysql
from django.template.context import BaseContext


def _copy_base_context(self):
	duplicate = self.__class__.__new__(self.__class__)
	duplicate.__dict__ = self.__dict__.copy()
	duplicate.dicts = self.dicts[:]
	return duplicate


BaseContext.__copy__ = _copy_base_context


pymysql.install_as_MySQLdb()
