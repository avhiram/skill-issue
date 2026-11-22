# Commandes Windows et SQL

## Identifier le compte de la console

Le SID identifie le compte. Il permet de reconnaître le même utilisateur dans plusieurs sessions.

```bat
whoami /user
```

## Afficher les groupes de l’access token

La colonne des attributs indique le rôle de chaque groupe dans les contrôles d’accès. La liste contient aussi le niveau d’intégrité du processus.

```bat
whoami /groups
```

## Vérifier les privilèges du processus

La colonne d’état indique quels privilèges de l’access token sont activés dans cette console.

```bat
whoami /priv
```

## Lister les tickets Kerberos

Le cache de la session Windows indique le service destinataire et la période de validité de chaque ticket.

```bat
klist tickets
```

## Identifier le login et l’utilisateur SQL

Exécutez cette requête dans SQL Server pour comparer le login initial, le contexte serveur et l’utilisateur de la base active.

```sql
SELECT ORIGINAL_LOGIN() AS login_initial,
       SUSER_SNAME() AS contexte_serveur,
       DB_NAME() AS base_courante,
       USER_NAME() AS utilisateur_base;
```
