Title: MySQL Errno 150
Date: 2015-1-14
Tags: MySQL


做OpenStack icehouse 升级到 Juno过程中，升级Neutron数据库时遇到这个错误。

```
$ python -m neutron.db.migration.migrate_to_ml2 openvswitch mysql://USER:PASSWORD@10.251.1.8/neutron
Traceback (most recent call last):
  File "/usr/lib/python2.7/runpy.py", line 162, in _run_module_as_main
    "__main__", fname, loader, pkg_name)
  File "/usr/lib/python2.7/runpy.py", line 72, in _run_code
    exec code in run_globals
  File "/usr/lib/python2.7/dist-packages/neutron/db/migration/migrate_to_ml2.py", line 462, in <module>
    main()
  File "/usr/lib/python2.7/dist-packages/neutron/db/migration/migrate_to_ml2.py", line 458, in main
    args.vxlan_udp_port)
  File "/usr/lib/python2.7/dist-packages/neutron/db/migration/migrate_to_ml2.py", line 138, in __call__
    metadata.create_all(engine)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/schema.py", line 2848, in create_all
    tables=tables)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 1479, in _run_visitor
    conn._run_visitor(visitorcallable, element, **kwargs)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 1122, in _run_visitor
    **kwargs).traverse_single(element)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/sql/visitors.py", line 122, in traverse_single
    return meth(obj, **kw)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/ddl.py", line 70, in visit_metadata
    self.traverse_single(table, create_ok=True)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/sql/visitors.py", line 122, in traverse_single
    return meth(obj, **kw)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/ddl.py", line 89, in visit_table
    self.connection.execute(schema.CreateTable(table))
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 662, in execute
    params)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 720, in _execute_ddl
    compiled
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 874, in _execute_context
    context)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 1024, in _handle_dbapi_exception
    exc_info
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/util/compat.py", line 196, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/base.py", line 867, in _execute_context
    context)
  File "/usr/lib/python2.7/dist-packages/sqlalchemy/engine/default.py", line 324, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/lib/python2.7/dist-packages/MySQLdb/cursors.py", line 174, in execute
    self.errorhandler(self, exc, value)
  File "/usr/lib/python2.7/dist-packages/MySQLdb/connections.py", line 36, in defaulterrorhandler
    raise errorclass, errorvalue
sqlalchemy.exc.OperationalError: (OperationalError) (1005, "Can't create table 'neutron.ml2_network_segments' (errno: 150)") '\nCREATE TABLE ml2_network_segments (\n\tid VARCHAR(36) NOT NULL, \n\tnetwork_id VARCHAR(36) NOT NULL, \n\tnetwork_type VARCHAR(32) NOT NULL, \n\tphysical_network VARCHAR(64), \n\tsegmentation_id INTEGER, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(network_id) REFERENCES networks (id) ON DELETE CASCADE\n)\n\n' ()
```

原因是 Mysql 有对外键约束[1]，仔细查数据里发现 networks 表的 collcation 和新建上述表时的默认数据库 collcation 不一样。以下是Mysql对外键约束的描述[1]，我遇到的是第二条错误(加粗的部分)。


> * Foreign key relationships involve a parent table that holds the central data values, and a child table with identical values pointing back to its parent. The FOREIGN KEY clause is specified in the child table. The parent and child tables must use the same storage engine. They must not be TEMPORARY tables.
* Corresponding columns in the foreign key and the referenced key must have similar data types. The size and sign of integer types must be the same. The length of string types need not be the same. For nonbinary (character) string columns, the character set and collation must be the same.
* MySQL requires indexes on foreign keys and referenced keys so that*  foreign key checks can be fast and not require a table scan. In the referencing table, there must be an index where the foreign key columns are listed as the first columns in the same order. Such an index is created on the referencing table automatically if it does not exist. This index might be silently dropped later, if you create another index that can be used to enforce the foreign key constraint. index_name, if given, is used as described previously.
* InnoDB permits a foreign key to reference any index column or group of columns. However, in the referenced table, there must be an index where the referenced columns are listed as the first columns in the same order.
* Index prefixes on foreign key columns are not supported. One consequence of this is that BLOB and TEXT columns cannot be included in a foreign key because indexes on those columns must always include a prefix length.
* If the CONSTRAINT symbol clause is given, the symbol value, if used, must be unique in the database. A duplicate symbol will result in an error similar to: ERROR 1005 (HY000): Can't create table 'test.#sql-211d_3' (errno: 121). If the clause is not given, or a symbol is not included following the CONSTRAINT keyword, a name for the constraint is created automatically.
* InnoDB does not currently support foreign keys for tables with user-defined partitioning. This includes both parent and child tables.


**解决方法是**：将 database 及 table 的 character 和 collcation 改成一样的就行了。

```mysql
alter database neutron DEFAULT character set utf8;
```

# REF

1. <https://bugs.launchpad.net/neutron/+bug/1332564>
2. <http://dev.mysql.com/doc/refman/5.1/en/create-table-foreign-keys.html>
