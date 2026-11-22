# Services Windows et Persistence

## Lire les permissions d’un service

Un service possède une configuration, un programme à lancer et un compte d’exécution. Ces trois éléments ont des permissions distinctes. Le droit de démarrer un service ne donne pas nécessairement le droit de modifier sa configuration. Les permissions sur le fichier exécutable relèvent du système de fichiers.

| Sujet du cours | Ce qu’il faut établir |
|---|---|
| Weak Service Permissions | Qui peut modifier l’objet service, et quelles opérations ce droit autorise. |
| Weak File Permissions | Qui peut modifier le fichier ou son répertoire, en tenant compte des permissions héritées. |
| Unquoted Service Path | Comment Windows interprète le chemin configuré. Un espace dans ce chemin ne suffit pas à démontrer un impact. |
| DLL Search Order | Quelle bibliothèque le processus a effectivement chargée et depuis quel emplacement. |
| PATH | Quel environnement et quel ordre de recherche s’appliquaient au processus au moment de l’exécution. |

## Identifier le déclencheur

Les mécanismes de Persistence se distinguent par le moment de l’exécution et le compte utilisé. Les Run Keys, le Startup Folder et les Logon Scripts sont liés à la connexion de l’utilisateur. Un PowerShell Profile dépend du démarrage d’un hôte qui charge ce profil. Une Scheduled Task dépend de son déclencheur, de ses conditions et du principal configuré. Un service peut démarrer avant toute connexion interactive.

WMI Eventing associe un événement à un traitement. Une inscription permanente peut survivre au processus qui l’a créée. Pour les tâches, les services et WMI, séparer dans le relevé la configuration enregistrée, le déclenchement observé et le résultat de l’action.

## Interpréter Elevated Persistence

« Elevated » décrit les privilèges du contexte d’exécution. La présence d’une tâche planifiée ne prouve pas qu’elle s’exécute avec des privilèges élevés. Relever le compte configuré, ses droits et les conditions d’exécution. Si aucun historique n’est disponible, consigner la configuration observée et laisser la dernière exécution indéterminée.
