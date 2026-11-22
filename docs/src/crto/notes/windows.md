# Windows et contexte de sécurité

## Du compte au jeton

À l’ouverture d’une session, Windows construit un jeton d’accès. Il contient notamment le SID du compte, les SID des groupes, leurs attributs et les privilèges associés. Le nom du compte répond à « qui est connecté ? ». Pour expliquer pourquoi une opération réussit, il faut aussi connaître le jeton utilisé et les permissions de la ressource.

Un processus possède un jeton primaire. Un thread qui traite une requête pour un client peut utiliser un jeton d’impersonation. Deux opérations du même processus peuvent donc être évaluées sous des identités différentes. Pour interpréter un refus, relever le contexte au moment de l’opération.

## UAC et Privilege Escalation

En mode d’approbation administrateur, un membre du groupe Administrateurs peut ouvrir une console avec un jeton filtré. Le SID du groupe peut alors apparaître avec l’attribut « utilisé uniquement pour refuser ». Sa présence dans la liste ne suffit pas à autoriser une opération administrative. Une élévation approuvée ouvre un processus sous un autre contexte de sécurité.

| Observation | Interprétation |
|---|---|
| Même SID utilisateur dans deux consoles | Les consoles représentent le même compte. |
| Niveaux d’intégrité différents | Les processus s’exécutent sous des contraintes différentes. |
| Privilège présent mais désactivé | Le privilège figure dans le jeton. Sa présence seule ne prouve pas son utilisation. |

## Persistence et Elevated Persistence

Pour étudier une persistance, identifier le déclencheur, la configuration qui le définit et le compte d’exécution. Un programme lancé à l’ouverture de session dépend d’une connexion utilisateur. Un service configuré pour démarrer au lancement du système peut fonctionner avant cette connexion. Son contexte dépend du compte configuré pour le service.

La durée de vie et le niveau de privilège sont deux questions distinctes. Un programme peut revenir après chaque connexion avec des droits ordinaires. Une action élevée ponctuelle ne prouve aucune persistance.

## AppLocker

AppLocker organise les règles par collection, notamment exécutables, scripts et installateurs. Une règle peut identifier un fichier par éditeur, chemin ou empreinte. L’empreinte change si le fichier est modifié. Une règle d’éditeur dépend de la signature et des critères retenus. Une règle de chemin dépend aussi des droits d’écriture sur l’emplacement.

Pour expliquer une décision, relever la collection, le mode d’application, l’utilisateur et le fichier. En mode audit, un événement peut décrire ce qui aurait été bloqué même si l’exécution a réussi.

[Exercice sur les jetons Windows](../labs/session-windows)
