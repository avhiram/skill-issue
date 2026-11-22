# Identités dans SQL Server

## Du login à l’utilisateur de base

Une session possède un contexte de sécurité au niveau de l’instance. Dans une base donnée, les permissions s’évaluent aussi à partir du principal de base, de ses rôles et des permissions applicables à l’objet. Un même login peut donc disposer de droits différents dans deux bases de la même instance.

## Lire une session

`ORIGINAL_LOGIN()` identifie le login à l’origine de la connexion. `SUSER_SNAME()` sans argument renvoie le nom associé au contexte de sécurité courant au niveau serveur. `USER_NAME()` sans argument donne l’utilisateur courant de la base. `DB_NAME()` indique la base dans laquelle cette dernière valeur prend son sens.

Si `USER_NAME()` renvoie `dbo`, la session agit en tant que propriétaire dans cette base. Cette seule valeur ne permet pas de déduire le login d’origine ni de reconstruire les permissions sur toute l’instance.

## Quand plusieurs serveurs interviennent

Un linked server définit un accès à une autre source de données. L’identité employée pour cette connexion dépend du mappage configuré et du mode d’authentification. Pour lire une trace distribuée, relever l’instance qui a enregistré chaque événement et le principal qu’elle a effectivement observé. Le nom affiché sur la première instance ne suffit pas à attribuer le contexte sur la seconde.

[Exercice sur les identités SQL](../labs/session-sql)

## SQL CLR et permissions d’exécution

SQL CLR permet à SQL Server d’utiliser des composants écrits en code managé, notamment pour certaines procédures stockées. Dans un inventaire, distinguer l’assembly enregistré, les objets SQL qui le référencent et les permissions d’exécution. La présence d’un assembly indique qu’il est enregistré dans une base. Elle ne date aucune exécution.

Un linked server peut également intervenir dans un appel distant. Pour expliquer un résultat, consigner séparément la configuration du lien, le contexte de sécurité utilisé sur l’autre instance et les droits accordés dans la base distante. Une erreur de connexion et un refus d’accès à un objet se produisent à des étapes différentes.
