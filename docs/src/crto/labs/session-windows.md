# Interpréter une session Windows

## Objectif et prérequis

Sur un poste Windows de laboratoire, identifier le compte, les groupes et le niveau d’intégrité de la console ouverte. Un compte standard suffit pour la première observation. Pour comparer deux jetons du même administrateur, utiliser un compte de lab autorisé à ouvrir une deuxième console élevée avec UAC actif.

## Relevé initial

Ouvrir une invite de commandes ordinaire. Conserver les sorties suivantes dans l’ordre et noter quelle console les a produites.

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

## Comparer les résultats

Dans la deuxième console, reprendre les trois relevés. Vérifier d’abord le SID du compte, puis comparer l’attribut du groupe Administrateurs et le niveau d’intégrité. Avec deux jetons liés par UAC, on attend le même SID utilisateur et des différences dans les attributs. Avec un autre compte saisi à l’invite UAC, les SID diffèrent et la comparaison porte sur deux identités.

## Dépannage

Avec une seule console standard, terminer l’exercice en identifiant son niveau d’intégrité. Si les sorties sont identiques, vérifier quelle fenêtre a produit chaque relevé et si la seconde a effectivement été élevée.
