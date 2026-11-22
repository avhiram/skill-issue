# Complément au suivi OSCP

Les cinq premiers blocs de `docs/src/oscp/privileges-linux.md` ont été examinés individuellement et exécutés dans un terminal Linux sans élévation. Chaque commande a retourné le code 0 et une sortie non vide.

| Bloc initial | Commande | Ce que la sortie indique |
| --- | --- | --- |
| 1 | `id` | Identifiants utilisateur et groupe du processus courant et groupes supplémentaires. |
| 2 | `hostname` | Nom d’hôte configuré. |
| 3 | `cat /etc/issue` | Texte de la bannière de connexion locale, personnalisable par l’administrateur. |
| 4 | `cat /etc/os-release` | Informations déclarées par la distribution, si le fichier existe et est lisible. |
| 5 | `uname -a` | Informations sur le noyau et la machine. |

Cumul sur les 1 721 blocs Markdown d’origine : 110 examinés, 1 611 restant sans validation individuelle. Le tableau initial conserve les résultats du premier passage. Les 21 encarts du sélecteur sont comptés séparément.
