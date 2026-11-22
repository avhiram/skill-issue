# Domain Trusts et Forest Trusts

## Lire le sens d’une relation

Si RESSOURCES fait confiance à COMPTES, un utilisateur de COMPTES peut être reconnu par RESSOURCES, sous réserve des restrictions configurées. C’est ensuite la ressource qui décide de l’accès. Pour éviter les ambiguïtés d’Inbound et d’Outbound, toujours préciser depuis quel domaine on lit la relation.

| Relation | Depuis RESSOURCES | Depuis COMPTES |
|---|---|---|
| RESSOURCES fait confiance à COMPTES | Outbound | Inbound |
| COMPTES fait confiance à RESSOURCES | Inbound | Outbound |

## Parent-Child Trust et Forest Trust

Une relation parent-enfant dans une forêt Active Directory est bidirectionnelle et transitive. Le domaine enfant reste un domaine distinct avec ses propres principals. Une Forest Trust relie deux forêts et possède un sens et une portée définis. Une relation avec une forêt tierce ne se déduit pas d’une chaîne de Forest Trusts.

## Analyser un refus

Distinguer la résolution du nom de service, l’authentification de l’identité externe et l’autorisation sur la ressource. Avec Selective Authentication, le droit de s’authentifier auprès de l’ordinateur cible intervient aussi. Une ACL de dossier favorable ne suffit donc pas toujours à expliquer le résultat.

Exemple de lab : une utilisatrice de COMPTES reçoit un refus en lecture sur un partage de RESSOURCES. Si le serveur a reconnu son compte et journalisé le refus sur le dossier, examiner les permissions du partage et du système de fichiers. Si l’authentification a échoué avant cette étape, ces permissions ne permettent pas encore d’expliquer l’échec.
