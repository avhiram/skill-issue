# Comparer les identités d’une session SQL

## Objectif et prérequis

Utiliser une connexion personnelle à une instance SQL Server de laboratoire et un éditeur de requêtes. Une seule base accessible suffit pour établir le premier relevé. Pour comparer les résultats entre deux bases, choisissez deux bases accessibles avec le même login.

## Procédure

Ouvrir une fenêtre de requête, sélectionner la première base dans le sélecteur et conserver la connexion ouverte.

## Identifier le login et l’utilisateur SQL

Exécutez cette requête dans SQL Server pour comparer le login initial, le contexte serveur et l’utilisateur de la base active.

```sql
SELECT ORIGINAL_LOGIN() AS login_initial,
       SUSER_SNAME() AS contexte_serveur,
       DB_NAME() AS base_courante,
       USER_NAME() AS utilisateur_base;
```

## Vérifier les résultats

La requête renvoie une ligne de quatre colonnes. Dans la même fenêtre, sélectionner la deuxième base et relancer la requête. Vérifier que la colonne base_courante change et que le login initial reste identique. L’utilisateur de base peut avoir un nom identique dans les deux bases.

## Dépannage

Si la base affichée reste identique, vérifier le sélecteur de la fenêtre active. Si une seule base est accessible, interpréter les quatre valeurs du premier relevé et consigner cette limite.
