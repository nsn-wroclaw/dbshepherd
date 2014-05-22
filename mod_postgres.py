from prettytable import from_db_cursor
from mod_core import ModuleCore, ParseArgsException
import common
from configmanager import ConfigManager, ConfigManagerError
import psycopg2
import os

class Postgres(ModuleCore):
    def __init__(self,completekey='tab', stdin=None, stdout=None):
        super().__init__()
        self.set_name('Postgres')

    def query(self, file_name, serv_name, base_name, db_query):
        cnf = ConfigManager("config/" + file_name + ".yaml").get(serv_name)
        conn = cnf["connection"]
        database = cnf["databases"][base_name]

        if conn["type"] == "ssh":
            cmd = conn["adress"]+"_"+conn["user"]+"_"+conn["passwd"]+"_"+str(conn["sshport"])+"_"+str(conn["remoteport"])+"_no"
            common.conn.send(cmd)
            ans = None
            while ans == None:
                ans = common.conn.get_state()

            status, hostname, db_port = ans.split("_")
            adr = "localhost"

            if status == "ok":  #udało się utworzyć tunel
                try:
                    pg_conn = psycopg2.connect(dbname=database["name"],user=database["user"],host=adr,password=database["passwd"],port=db_port)
                    cur = pg_conn.cursor()
                    cur.execute(db_query)

                    pt = from_db_cursor(cur)
                    if(pt != None):
                        print(pt)
                    pg_conn.commit()
                except psycopg2.Error as e:
                    print('Error: ', e)
                except psycopg2.Warning as w:
                    print('Warning: ', w)
                except psycopg2.InterfaceError as e:
                    print('Error: ', e)
                except psycopg2.DatabaseError as e:
                    print('Error: ', e)
            else:
                pass

            pass
        else:
            pass


    def do_t(self, arg):
        self.query("lista1", "nsn", "pgBase1", "SELECT * FROM shepherd")

    def do_query(self, args):
        try:
            (values,values_num) = self.parse_args(args, 1, 2)

            if values_num == 2:                      #wyróżniamy do czego chcemy się połączyć
                conn_params = values[0].split('.')
                if len(conn_params) == 3:   #połącz do konkretnej bazy na liście
                    self.query(conn_params[0],conn_params[1], conn_params[2], values[1])

                elif len(conn_params) == 2: #połącz do konkretnego serwera na liście
                    conf = ConfigManager("config/" + conn_params[0] + ".yaml").get(conn_params[1])
                    databases = conf["databases"] #konfiguracje baz danych
                    # print(dbs)
                    for db in databases:
                        print("[" + db + "]")
                        self.query(conn_params[0],conn_params[1], db, values[1])
                        print()
                elif len(conn_params) == 1: #połącz do wszystkiego na liście
                    servers = ConfigManager("config/" + conn_params[0] + ".yaml").get_all()
                    for srv in servers:
                        print("[---- " + srv + " ----]")
                        databases = servers[srv]["databases"]
                        for db in databases:
                            print("+[" + db + "]")
                            self.query(conn_params[0], srv, db, values[1])
                            print()
                        print()
                else:
                    raise  ParseArgsException("Niepoprawny parametr połączenia!")
            elif values_num == 1:                    #wykonujemy na wszystkich
                files = []
                for file in os.listdir("./config"):
                    if file.endswith(".yaml"):
                        files.append(file.split(".")[0])

                print("Query to:")
                for file in files:
                    print(file)

                ans = input("Are you sure? [NO/yes/info]: ")
                if ans == "yes":
                    for file in files:
                        servers = ConfigManager("config/" + file + ".yaml").get_all()
                        for srv in servers:
                            print("[---- " + srv + " ----]")
                            databases = servers[srv]["databases"]
                            for db in databases:
                                print("+[" + db + "]")
                                self.query(file, srv, db, values[0])
                                print()
                        print()
                elif ans == "info":
                    for file in files:
                        servers = ConfigManager("config/" + file + ".yaml").get_all()
                        for srv in servers:
                            print("[---- " + srv + " ----]")
                            databases = servers[srv]["databases"]
                            for db in databases:
                                print("+" + db)
                        print()
                    print()
                else:
                    print("aborted")

        except ConfigManagerError as e:
            print(e)
        except ParseArgsException as e:
            print(e)

    def do_raw_query(self, args):
        try:
            (values,X) = self.parse_args(args, 3)
            [server_name, base_name] = values[1].split('.')
            file_name = values[0]

            try:
                conf = ConfigManager(file_name).get(server_name)
                adr = conf["connection"]["adress"]
                pwd = conf[base_name]["passwd"]
                usr = conf[base_name]["user"]
                db_name = conf[base_name]["name"]

                try:
                    conn = psycopg2.connect(dbname=db_name,user=usr,host=adr,password=pwd, port=5432)
                    cur = conn.cursor()
                    cur.execute(values[2])
                    conn.commit()

                    return cur.fetchall();

                except psycopg2.Error as e:
                    print('Error: ', e)
                except psycopg2.Warning as w:
                    print('Warning: ', w)
                except psycopg2.InterfaceError as e:
                    print('Error: ', e)
                except psycopg2.DatabaseError as e:
                    print('Error: ', e)

            except ConfigManagerError as e:
                print(e)
            except Exception as e:
                print(e)


        except ParseArgsException as e:
            print(e)
        except Exception as e:
            print(e)