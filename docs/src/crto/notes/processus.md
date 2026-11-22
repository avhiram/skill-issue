# Process Injection et Defence Evasion

## Processus, thread et module

Un processus fournit un espace d’adressage et un contexte de sécurité. Ses threads exécutent le code. Un module chargé ajoute du code ou des données à cet espace. Dans une chronologie, distinguer la création du processus, le chargement du module et l’activité du thread. Le nom du fichier sur disque ne suffit pas à identifier tout le code qui s’est exécuté en mémoire.

| Famille étudiée | Ce que le terme décrit |
|---|---|
| Process Injection | Du code s’exécute dans l’espace d’un processus. |
| Process Hollowing | L’image exécutée en mémoire peut différer de l’image attendue au lancement. |
| Thread Hijacking | L’exécution d’un thread existant est redirigée. |
| Asynchronous Procedure Call | Windows prévoit un mécanisme de rappel associé à un thread. Sa présence a aussi des usages légitimes. |

## Analyse statique et dynamique

Une analyse statique examine le fichier sans l’exécuter. Dans Ghidra, une fonction reconstruite par le décompilateur est une interprétation du binaire. Les noms et les types proposés peuvent être incomplets. Une analyse dynamique décrit une exécution précise dans un environnement donné. L’absence d’un comportement pendant cette observation laisse ouverte la question de son existence dans d’autres conditions.

## AppLocker, AMSI et télémétrie

AppLocker évalue des règles d’exécution. AMSI permet aux applications participantes de soumettre du contenu à un fournisseur antimalware. Un journal de création de processus répond encore à une autre question : le système a-t-il enregistré le lancement du processus ? Lors d’un exercice, relever le composant à l’origine de chaque événement avant d’en tirer une conclusion.

[Lire les décisions AppLocker](../labs/applocker)
