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

## Relier les observations réseau à une session

Un listener décrit un point de communication. Un profil décrit certains aspects des échanges. Un Named Pipe est un mécanisme de communication entre processus que Windows peut aussi exposer via SMB. Lorsqu’une chronologie mentionne ces trois éléments, consigner pour chacun le protocole observé, les deux extrémités connues et la source de l’information.

Un Beacon Object File (BOF) est un module objet que Beacon peut charger pour accomplir une tâche. Un script Aggressor peut fournir l’interface opérateur associée. Le nom d’une commande dans le client ne révèle donc pas à lui seul le processus, le module ou le transport effectivement observé sur le poste.

## Livraison, ouverture et exécution

Les exemples d’Initial Access mettent en jeu des fichiers de nature différente, notamment raccourcis Windows, compléments Office et installateurs. Documenter séparément la provenance du fichier, son empreinte, son ouverture et toute exécution corrélée. Mark of the Web est un indice de provenance attaché à certains fichiers. Son absence laisse la provenance indéterminée.

SMB et WinRM peuvent intervenir dans l’administration distante. Un partage ouvert, une authentification réussie et l’exécution d’une action distante constituent trois observations distinctes. Pour attribuer une action, rapprocher le compte, la machine de destination, l’heure et le journal du service.
