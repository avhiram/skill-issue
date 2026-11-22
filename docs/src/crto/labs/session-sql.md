# Comparer les identités d’une session SQL

## Objectif et prérequis

Utiliser une connexion personnelle à une instance SQL Server de laboratoire et un éditeur de requêtes. Une seule base accessible suffit pour établir le premier relevé. Pour examiner la portée du principal de base, choisir deux bases auxquelles ce login a déjà accès.

## Procédure

Ouvrir une fenêtre de requête, sélectionner la première base dans le sélecteur et conserver la connexion ouverte.

## Identifier le contexte SQL

Dans une fenêtre de requête connectée à SQL Server, relever les identités et la base en une seule ligne.

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
