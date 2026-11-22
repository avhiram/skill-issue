# Interpréter une session Windows

## Objectif et prérequis

Sur un poste Windows de laboratoire, identifier le compte, les groupes et le niveau d’intégrité de la console ouverte. Un compte standard suffit pour la première observation. Pour comparer deux access tokens du même administrateur, utiliser un compte de laboratoire autorisé à ouvrir une seconde console en tant qu’administrateur, avec UAC activé.

## Relevé initial

Ouvrir une invite de commandes ordinaire. Conserver les sorties suivantes dans l’ordre et noter quelle console les a produites.

## Identifier le compte de la console

Le SID identifie le compte. Comparez sa valeur dans les deux consoles pour vérifier si elles utilisent la même identité.

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

## Comparer les résultats

Dans la deuxième console, reprendre les trois relevés. Vérifier d’abord le SID du compte, puis comparer l’attribut du groupe Administrateurs et le niveau d’intégrité. Avec deux access tokens liés par UAC, on attend le même SID utilisateur et des différences dans les attributs. Avec un autre compte saisi à l’invite UAC, les SID diffèrent et la comparaison porte sur deux identités.

## Dépannage

Avec une seule console standard, terminer l’exercice en identifiant son niveau d’intégrité. Si les sorties sont identiques, vérifier quelle fenêtre a produit chaque relevé et si la seconde a effectivement été élevée.
