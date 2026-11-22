# Lire un scénario de délégation

## Objectif et contexte

Déterminer où chercher l’autorisation de délégation lorsqu’une application web accède à un service de fichiers pour le compte d’un utilisateur. Cet exercice sur dossier utilise trois machines fictives, POSTE pour le client, WEB pour le frontal et FICHIERS pour la ressource.

## Pièces du dossier

| Pièce | Observation fournie |
|---|---|
| Relevé du frontal | Le service web s’exécute sous le compte de service WEB-APP. |
| Configuration de FICHIERS | WEB-APP figure parmi les identités autorisées à représenter des utilisateurs auprès de cette ressource. |
| Journal du service de fichiers | Une requête est attribuée à l’utilisateur du POSTE. |
| Permissions du dossier | L’utilisateur dispose du droit de lecture. Une tentative d’écriture échoue. |

## Procédure

1. Dessiner les deux échanges applicatifs. Pour chacun, indiquer le client réseau, le service destinataire et l’identité que le service doit reconnaître.
2. Identifier le compte utilisé par WEB et la machine sur laquelle la délégation est autorisée.
3. Expliquer comment l’authentification peut réussir alors que la tentative d’écriture échoue.

## Résultat attendu

Le premier échange va de POSTE à WEB. Pour le deuxième, WEB contacte FICHIERS au nom de l’utilisateur. La configuration décrite correspond à Resource-Based Constrained Delegation. L’autorisation accordée au frontal permet de représenter l’utilisateur. Les permissions de l’utilisateur sur le dossier déterminent ensuite s’il peut lire ou modifier le fichier.

## Vérification et dépannage

Si le schéma donne des droits d’écriture à WEB-APP, reprendre la dernière pièce et identifier à qui l’accès est attribué. Si le journal indique seulement une adresse IP, l’identité applicative reste à établir. Les pièces ne contiennent aucun ticket brut ni journal du KDC permettant de dater les échanges Kerberos.
