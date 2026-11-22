# Commandes Windows et SQL

## Identifier le compte courant

Dans la console Windows étudiée, afficher le nom et le SID du compte. Le SID permet de comparer deux relevés même si les noms affichés se ressemblent.

```bat
whoami /user
```

## Lire les groupes du jeton

Dans la même console, relever les SID, les attributs de groupe et le niveau d’intégrité.

```bat
whoami /groups
```

## Lire les privilèges du jeton

Consulter la liste et l’état des privilèges du jeton courant.

```bat
whoami /priv
```

## Lister les tickets Kerberos

Depuis la session Windows étudiée, afficher le cache et relever le principal serveur de chaque ticket.

```bat
klist tickets
```

## Identifier le contexte SQL

Dans une fenêtre de requête connectée à SQL Server, relever les identités et la base en une seule ligne.

```sql
SELECT ORIGINAL_LOGIN() AS login_initial,
       SUSER_SNAME() AS contexte_serveur,
       DB_NAME() AS base_courante,
       USER_NAME() AS utilisateur_base;
```
