# Cobalt Strike et opérations réseau

## Beacon et Team Server

L’opérateur utilise le client Cobalt Strike pour transmettre ses tâches au Team Server, qui coordonne les sessions Beacon. Beacon est l’agent qui traite ces tâches dans le contexte du processus qui l’héberge. Une session affichée dans l’interface renseigne sur les échanges connus du serveur. Pour déterminer si une tâche a abouti, il faut retrouver son résultat.

Lors de l’analyse d’une chronologie, distinguer l’heure à laquelle l’opérateur demande une action, celle à laquelle l’agent récupère la tâche et celle à laquelle le serveur reçoit le résultat. Avec un agent qui communique par intervalles, ces trois instants peuvent différer.

## Aggressor Script et Malleable C2 Profiles

Aggressor Script étend le comportement du client, par exemple ses menus et le traitement d’événements. Un Malleable C2 Profile décrit entre autres la représentation des échanges réseau de Beacon. Pour interpréter une observation, identifier la couche concernée. Un libellé personnalisé dans l’interface relève du client. La forme d’un échange HTTP dépend notamment du profil et du transport.

## Lateral Movement, Pivoting et SOCKS

Le Lateral Movement désigne le passage d’un système à un autre. Le Pivoting utilise un intermédiaire pour atteindre un réseau ou un service. Un proxy SOCKS relaie les connexions d’applications configurées pour l’utiliser. Un accès réseau possible et un accès applicatif autorisé constituent deux résultats différents.

Si le service enregistre une connexion depuis le relais, son journal identifie uniquement la machine qui lui a transmis la connexion. Pour attribuer la demande initiale, il faut rapprocher son horodatage des journaux du relais et de l’application cliente. Un décalage d’horloge ou plusieurs utilisateurs simultanés limitent cette attribution.

## Initial Access, Post-Exploitation et OPSEC

Dans un compte rendu, dater la première exécution confirmée, identifier le compte associé et décrire les actions ultérieures avec leurs preuves. Une livraison de fichier, son ouverture et son exécution constituent trois événements différents. Une alerte liée à des identifiants ne suffit pas à établir quels secrets ont été lus ou utilisés. Consigner la source, l’heure et la limite de chaque observation permet de situer les phases du scénario.
