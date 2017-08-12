A brief history of MySQL
########################

:date: 2017-08-12
:tags: Database, MySQL
:slug: a-brief-history-of-mysql

在开源软件中，一提到关系型数据库，大家最先想到的是一定是 MySQL, MySQL在过去由于性能高、成本低、可靠性好，在很早的时候，就占据了数据库的霸主的地位，成为最流行的开源数据库。非常流行的开源软件组合LAMP中的“M”指的就是MySQL。但是有开源的地方，就有江湖, 一言不合就 fork 。现在以 MySQL 为基础的变种数据库也有好几个，下面我们来依次认识下。

MySQL
=====

MySQL 最早始于 1995 年，到现在已经有 22 年的历史了。原开发者为瑞典的MySQL AB公司，该公司于2008年被昇阳微系统（Sun Microsystems）收购。2009年，甲骨文公司（Oracle）收购昇阳微系统公司，MySQL成为Oracle旗下产品。

但被甲骨文公司收购后，Oracle大幅调涨MySQL商业版的售价，自由软件社区们对于Oracle是否还会持续支持MySQL社区版（MySQL之中唯一的免费版本）有所隐忧，MySQL的创始人麦克尔·维德纽斯以MySQL为基础，成立分支计划MariaDB。而原先一些使用MySQL的开源软件逐渐转向MariaDB或其它的数据库。

MariaDB
=======

MariaDB的目的是完全兼容MySQL，包括API和命令行，使之能轻松成为MySQL的代替品。在存储引擎方面，10.0.9版起使用XtraDB来代替MySQL的InnoDB。
XtraDB 是 InnoDB 存储引擎的增强版，被设计用来更好的使用更新计算机硬件系统的性能，同时还包含有一些在高性能环境下的新特性。XtraDB 存储引擎是完全的向下兼容，在 MariaDB 中，XtraDB 存储引擎被标识为"ENGINE=InnoDB"，这个与 InnoDB 是一样的，所以你可以直接用XtraDB 替换掉 InnoDB 而不会产生任何问题。XtraDB 现在由主要由 Percona 公司维护，也是 Percona Server 的核心组件。
MariaDB直到5.5版本，均依照MySQL的版本。因此，使用MariaDB5.5的人会从MySQL 5.5中了解到MariaDB的所有功能。从2012年11月12日起发布的10.0.0版开始，不再依照MySQL的版号。10.0.x版以5.5版为基础，加上移植自MySQL 5.6版的功能和自行开发的新功能。

Percona Server for MySQL
========================

Percona Server 也是一个 MySQL 的 fork 版本，由 Percona 公司维护。 Percona Server 相比 MySQL 包含许多性能上的提升[1]_，如上面提到的 XtraDB 就是 Percona 公司的。 而且还有丰富的 MySQL 周边工具

- Percona XtraDB Cluster, 基于 Galera 的 Percona 集群解决方案
- Percona XtraBackup， 支持 MySQL 在线全量或增量备份工具， 相比 mysqldump 性能再好
- Percona Toolkit，大量  MySQL 的管理工具

Galera
======

Galera 并不是 MySQL 的变种，而是由 Codeship 公司于 2007 发布的支持多主同步备份的 MySQL 组件。 由于简单实用，性能高效，现在被广泛使用，并已经集成到 MariaDB 和 Percona XtraDB cluster 中。 他的特点如下
同步复制

- 多主服务器的拓扑结构
- 可以在任意节点上进行读写
- 自动剔除故障节点
- 自动加入新节点
- 真正行级别的并发复制
- 客户端连接跟操作单台MySQL数据库的体验一致

OpenStack 社区推荐的 MySQL 高可用方案就是利用 Galera

REF
===

.. [1] https://www.percona.com/software/mysql-database/percona-server/benchmarks
