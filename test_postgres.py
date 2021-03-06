import os
import unittest
from mod_postgres import Postgres
import common
test1_dump_file = "test1_dump"

def setUpModule():
	print("PostgresTest")


class PostgresTest(unittest.TestCase):

	def test1_dump(self):
		#if exists remove test1_dump* file
		for file in os.listdir("."):
					if file.startswith("test1_dump"):
						if os.path.exists("./" + file.title()):
							os.remove("./" + file.title())
		
		pg = Postgres()
		pg.master = "test"
		test = pg.do_dump("lista_test.ShouldBeOK.pgBase_test " + test1_dump_file)
		
		#test if file exists
		counter = 0
		for file in os.listdir("."):
					if file.startswith("test1_dump"):
						counter += 1
						if os.path.exists("./" + file.title()):
							os.remove("./" + file.title())
		self.assertNotEqual(counter,0)
	
	def test2_query(self):
		pg = Postgres()
		pg.do_query("lista1.nsn \"select * from shepherd\"")
		
if __name__ == '__main__':
	unittest.main(verbosity=2)#