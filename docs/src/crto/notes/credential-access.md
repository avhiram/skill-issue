# Credential Access et User Impersonation

## Quel objet représente l’identité ?

Une session Windows peut faire intervenir un access token, un ticket Kerberos et des données conservées pour une authentification ultérieure. Ces objets ont des portées différentes. Le SID affiché dans une console identifie le compte localement. Pour déterminer sous quelle identité un serveur de fichiers a accepté une connexion, il faut aussi examiner ce que le serveur a enregistré.

| Objet | Rôle | Limite d’interprétation |
|---|---|---|
| Access token | Décrit le contexte de sécurité d’un processus ou d’un thread | Sa présence ne prouve pas qu’un service distant a accepté ce compte. |
| TGT | Permet au client de demander des tickets de service au KDC | Sa présence ne prouve aucun accès à un fichier. |
| Service ticket | Identifie un service destinataire et possède une durée de validité | Le service vérifie aussi les droits sur la ressource. |
| Données de connexion mises en cache | Peuvent permettre une ouverture de session de domaine hors connexion | Une ouverture de session réussie ne prouve pas qu’un contrôleur de domaine a répondu. |

## Credential Manager, navigateurs et Credential Guard

Credential Manager conserve des informations d’authentification pour certaines applications et ressources. Un navigateur peut également gérer ses propres données de connexion. Dans un rapport, préciser quel magasin a été observé, sous quel compte et sur quelle machine. La présence d’une entrée établit son existence à l’instant du relevé. Pour attribuer une connexion ultérieure à cette entrée, il faut une autre preuve.

Credential Guard utilise la sécurité fondée sur la virtualisation pour isoler certains secrets d’authentification. Sa portée dépend du type de secret. Un état « activé » ne renseigne pas, à lui seul, sur la protection des mots de passe conservés par une application tierce.

## Token Impersonation, Pass the Hash et Pass the Ticket

Le Token Impersonation concerne le contexte utilisé par un thread pour agir au nom d’un client. Pass the Hash désigne la réutilisation d’un secret dérivé du mot de passe dans une authentification compatible. Pass the Ticket concerne la réutilisation d’un ticket Kerberos. Dans un compte rendu, distinguer le mécanisme supposé, le protocole réellement observé et l’identité reconnue par le service.

## Kerberoasting et Shadow Credentials

Kerberoasting concerne la résistance du secret d’un compte de service lorsqu’un ticket de service est disponible pour une vérification hors ligne. Une demande de ticket est aussi une opération Kerberos ordinaire. Son existence seule ne démontre ni la récupération du mot de passe ni son utilisation.

Shadow Credentials concerne les informations de clé associées à un objet Active Directory. Pour analyser une modification, établir le propriétaire de l’objet, la provenance de la clé et la justification du changement. Un environnement qui emploie légitimement l’authentification par clé peut contenir ces informations.

[Comparer les contextes Windows](../labs/session-windows)
