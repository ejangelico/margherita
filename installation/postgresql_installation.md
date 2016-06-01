POSTGRESQL INSTALLATION
-----------------------

These instructions are for postgresql on RHEL6. This is the operating system
running on psec2.

 

### Install the postgresql repo

`[~]# wget
https://download.postgresql.org/pub/repos/yum/9.4/redhat/rhel-6-x86_64/pgdg-redhat94-9.4-2.noarch.rpm
`

`[~]# rpm -ivh pgdg-redhat94-9.4-2.noarch.rpm`

 

### Install postgresql packages required

`[~]# yum install postgresql94 postgresql94-server postgresql94-libs
postgresql94-contrib postgresql94-python`

 

### Start postgres and allow people to login

`[~]# service postgresql-9.4 initdb `

`Initializing database: [ OK ]`

In order to allow people to login, need to edit the file
/var/lib/pgsql/9.4/data/pg\_hba.conf

Find the line:

`local all all ident`

Change to:

`local all all trust`  (setting this to trust allows any user to connect to any
database without passwords)

To require passwords use:

`local all all md5`

 

### Check that it's running

`[~]$ ps -ef|grep postgres`

`postgres 15333     1  0 Apr25 ?        00:00:12 /usr/pgsql-9.4/bin/postmaster
-D /var/lib/pgsql/9.4/data`

`postgres 15335 15333  0 Apr25 ?        00:00:00 postgres: logger process      
                       `

`postgres 15337 15333  0 Apr25 ?        00:00:00 postgres: checkpointer process
                         `

`postgres 15338 15333  0 Apr25 ?        00:00:02 postgres: writer process      
                         `

`postgres 15339 15333  0 Apr25 ?        00:00:02 postgres: wal writer process  
                         `

`postgres 15340 15333  0 Apr25 ?        00:00:07 postgres: autovacuum launcher
process                   `

`postgres 15341 15333  0 Apr25 ?        00:00:12 postgres: stats collector
process              `

### Make sure it automatically starts on boot

`[~]# chkconfig --list postgresql-9.4`

`postgresql-9.4  0:off 1:off 2:off 3:off 4:off 5:off 6:off`

`[~]# chkconfig postgresql-9.4 on`

`[~]# chkconfig --list postgresql-9.4`

`postgresql-9.4  0:off 1:off 2:on 3:on 4:on 5:on 6:off`

 

### Set a default password for postgres user

`[~] sudo -u postgres psql postgres`

`\password postgres`

 

### Create a user and database to use

`[~]# createuser -U postgres --interactive`

`Enter name of role to add: marg`

`Shall the new role be a superuser? (y/n) n`

`Shall the new role be allowed to create databases? (y/n) y`

`Shall the new role be allowed to create more new roles? (y/n) n`

`[~]# psql -U postgres`

`psql (9.4.7)`

`Type "help" for help.`

`postgres=# create database marg;`

`CREATE DATABASE`

`postgres=# \q`

 

### Test that the new user can login

`[root@psec2 ~]# psql -U marg `(will need -W flag if want to check password and
have logins set to trust)

`psql (9.4.7)`

`Type "help" for help.`

`marg=> `

 

### Set a password for the account

`[~]# psql -U marg`

`psql (9.4.7)`

`Type "help" for help.`

`marg=> alter role marg with password 'newpassword';`

`ALTER ROLE`

`marg=> \q`

`[~]# `

 

### Check that the new user can login

`[~]$ psql -U marg -W`

`Password for user marg: `

`psql (9.4.7)`

`Type "help" for help.`

`marg=> `

 

That's it for postgres installation.

 

Notes on how to do things
-------------------------

 

### List and delete users

`[~]$ psql -U postgres`

`psql (9.4.7)`

`Type "help" for help.`

`postgres=# select * from pg_user;`

` usename  | usesysid | usecreatedb | usesuper | usecatupd | userepl |  passwd 
| valuntil | useconfig `

`----------+----------+-------------+----------+-----------+---------+----------+----------+-----------`

` postgres |       10 | t           | t        | t         | t       | ********
|          | `

` marg     |    16387 | t           | f        | f         | f       | ********
|          | `

` lappd    |    16473 | t           | f        | f         | f       | ********
|          | `

`(3 rows)`

`postgres=# drop user lappd;`

`DROP ROLE`

`postgres=# select * from pg_user;`

` usename  | usesysid | usecreatedb | usesuper | usecatupd | userepl |  passwd 
| valuntil | useconfig `

`----------+----------+-------------+----------+-----------+---------+----------+----------+-----------`

` postgres |       10 | t           | t        | t         | t       | ********
|          | `

` marg     |    16387 | t           | f        | f         | f       | ********
|          | `

`(2 rows)`

 

### List and delete databases

`postgres=# \l`

`                                  List of databases`

`    Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access
privileges   `

`------------+----------+----------+-------------+-------------+-----------------------`

` lappd      | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` marg       | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` margherita | marg     | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` postgres   | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` template0  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres   
      +`

`            |          |          |             |             |
postgres=CTc/postgres`

` template1  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres   
      +`

`            |          |          |             |             |
postgres=CTc/postgres`

`(6 rows)`

`postgres=# drop database lappd;`

`DROP DATABASE`

`postgres=# \l`

`                                  List of databases`

`    Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access
privileges   `

`------------+----------+----------+-------------+-------------+-----------------------`

` marg       | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` margherita | marg     | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` postgres   | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | `

` template0  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres   
      +`

`            |          |          |             |             |
postgres=CTc/postgres`

` template1  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres   
      +`

`            |          |          |             |             |
postgres=CTc/postgres`

`(5 rows)`

 

### Show tables in a database

`[~]$ psql -U marg`

`psql (9.4.7)`

`Type "help" for help.`

`marg=> \dt`

`       List of relations`

` Schema | Name  | Type  | Owner `

`--------+-------+-------+-------`

` public | alias | table | marg`

` public | cn616 | table | marg`

` public | pvs   | table | marg`

`(3 rows)`

`marg=> `

 

### Note

Postgresql automatically connects to a database with the same name as the user
name.  In the above example, those tables are in the database named marg.  The
name in the prompt (marg=\>) reflects the name of the database connected to.  To
see the tables in a different database, first connect to it and then run the /dt
command.

`[~]$ psql -U postgres`

`psql (9.4.7)`

`Type "help" for help.`

`postgres=# \c marg`

`You are now connected to database "marg" as user "postgres".`

`marg=# \dt`

`       List of relations`

` Schema | Name  | Type  | Owner `

`--------+-------+-------+-------`

` public | alias | table | marg`

` public | cn616 | table | marg`

` public | pvs   | table | marg`

`(3 rows)`

`marg=# \q`

`[~]`

 

### Alternative way to create a new user and database

`[~]$ psql -U postgres`

`psql (9.4.7)`

`Type "help" for help.`

`postgres=# create user lappd with createdb;`

`CREATE ROLE`

`postgres=# create database lappd;`

`CREATE DATABASE`

`postgres=# alter user lappd with password 'shinynewpassword';`

`ALTER ROLE`

`postgres=# select * from pg_user;`

` usename  | usesysid | usecreatedb | usesuper | usecatupd | userepl |  passwd 
| valuntil | useconfig `

`----------+----------+-------------+----------+-----------+---------+----------+----------+-----------`

` postgres |       10 | t           | t        | t         | t       | ********
|          | `

` marg     |    16387 | t           | f        | f         | f       | ********
|          | `

` lappd    |    16475 | t           | f        | f         | f       | ********
|          | `

`(3 rows)`

`postgres=# `

 

### Why are we not using software from RedHat?

In rhel6, the default postgresql is version 8.4.  We want a newer version than
that.  We could use the version provided by the RedHat Software Collection, but
I didn't see a version of psycopg2 included there.  Since we need that, it was
easier to just add the postgresql 9.4 repo and get the packages we required.
