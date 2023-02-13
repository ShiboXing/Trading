USE master;

IF NOT EXISTS (
   SELECT name
FROM sys.databases
WHERE name = N'detes'
)
begin
  CREATE DATABASE [detes]
end;