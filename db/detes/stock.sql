USE master
GO
IF NOT EXISTS (
   SELECT name
   FROM sys.databases
   WHERE name = N'detes'
)
CREATE DATABASE [detes]
GO
CREATE TABLE stock
(
  [id] INT NOT NULL PRIMARY KEY,
  [exchange] nvarchar(5),
  [code] nvarchar(6)
)
GO

insert into stock values(1, 'SZ', '000001')
GO 

select * from stock
GO