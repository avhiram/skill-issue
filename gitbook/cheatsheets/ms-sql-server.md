# Microsoft SQL Server — Énumération et audit

## Objectif

Inventorier les instances SQL Server, examiner les principaux de sécurité et identifier les relations entre serveurs SQL liés.

## Découverte via Active Directory

### Identifier les services MSSQL enregistrés dans Kerberos

```text
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=MSSQLSvc*)) --attributes name,samAccountName,servicePrincipalName
```

**Lecture :** les SPN `MSSQLSvc/hostname:port` peuvent indiquer une instance SQL Server configurée pour l'authentification Kerberos.

### Identifier les groupes liés à SQL Server

```text
ldapsearch (&(samAccountType=268435456)(|(name=*SQL*)(name=*DB*)(name=*Database*))) --attributes distinguishedName,member
```

**Lecture :** la correspondance du nom d'un groupe n'implique pas qu'il dispose de droits SQL élevés.

## Requêtes SQL de diagnostic

### Identifier le serveur

```sql
SELECT @@SERVERNAME AS ServerName;
SELECT @@VERSION AS VersionInfo;
```

### Identifier la connexion actuelle

```sql
SELECT ORIGINAL_LOGIN() AS OriginalLogin, SUSER_SNAME() AS CurrentLogin;
```

### Vérifier le rôle sysadmin

```sql
SELECT IS_SRVROLEMEMBER('sysadmin') AS IsSysadmin;
```

### Afficher les serveurs liés

```sql
SELECT name, product, provider, data_source
FROM sys.servers
WHERE is_linked = 1;
```

### Examiner l'état de xp_cmdshell sans le modifier

```sql
SELECT name, value, value_in_use
FROM sys.configurations
WHERE name = 'xp_cmdshell';
```

**Important :** la requête lit la configuration ; elle n'active pas la fonctionnalité.

## Références d'administration

| Outil | Usage |
| --- | --- |
| SSMS | Administration graphique |
| sqlcmd | Requêtes et scripts SQL |
| PowerUpSQL | Inventaire et évaluation de sécurité |
| SQLRecon | Diagnostic de configuration SQL |

**Source :** [Microsoft SQL Server — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/ms-sql-server.md). La fiche originale contient aussi des procédures offensives non reproduites dans cette adaptation.
