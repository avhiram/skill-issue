# Audit CRTO

## Version de travail

Branche locale `docs/crto-revision`, créée depuis `origin/main` au commit `2b03c903`. La copie Linux personnelle de l’éditeur ne faisait pas partie des fichiers reçus.

## Inventaire des sources

| Dépôt | Révision | Fichiers suivis |
|---|---|---:|
| [CRTO-Notes](https://github.com/miguelarrabalcastro/CRTO-Notes/tree/bb0b7f03972acbf131d4e007e4cfba06cff056b2) | `bb0b7f03` | 13 |
| [CRTO_2025_Notes](https://github.com/Razzlemouse/CRTO_2025_Notes/tree/aee72c0c135137881a577653e2d03ccab865b074) | `aee72c0c` | 13 |
| [CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/tree/decaa7a705d7c024455212fb6ff4f6a9d8b59365) | `decaa7a7` | 131 |

Les deux premières sources organisent les mêmes grands thèmes en espagnol et en anglais. La troisième ajoute notamment des labs S4U et RBCD, AD CS, des fiches AppLocker et des exemples de code. Les 157 chemins ont été inventoriés. La comparaison par empreinte a détecté 2 fichier(s) identique(s) au-delà de la première occurrence. Les PNG ont passé un contrôle de format. Le tri sémantique exhaustif et la revue visuelle individuelle restent ouverts.

## Intégration

| Ensemble | Travail réalisé |
|---|---|
| Notes | Quatre synthèses originales sur Windows, Kerberos et AD, Cobalt Strike et le réseau, SQL Server. Les variantes de délégation figurent dans un tableau commun. |
| Labs | Trois exercices sur les jetons Windows, les identités SQL et la délégation. Le scénario de délégation est fictif. |
| Cheatsheets | Cinq blocs distincts. Les exercices reprennent les commandes nécessaires à leur lecture autonome. |
| Navigation | Page d’attente remplacée, huit pages ajoutées au menu CRTO. Thème VitePress existant utilisé. |
| Illustration | Un schéma Kerberos original dans la note. Les 70 PNG tiers ont été laissés dans leurs sources. |
| Corrections | Aucune commande préexistante dans la page CRTO à corriger. |

Les signatures, certificats personnels et présentations ont été exclus. Aucun extrait de code tiers ni capture tierce importé. Les étapes opérationnelles d’intrusion, d’extraction d’identifiants, de contournement et d’automatisation offensive ne sont pas intégrées.

## Contrôles et limites

Les formes `whoami /user`, `whoami /groups`, `whoami /priv` et `klist tickets` ont été confrontées aux références Windows. La requête SQL combine quatre fonctions de contexte. Les labs Windows et SQL restent à exécuter sur les plateformes correspondantes.

- [whoami](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami)
- [klist](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/klist)
- [ORIGINAL_LOGIN](https://learn.microsoft.com/en-us/sql/t-sql/functions/original-login-transact-sql)
- [Délégation Kerberos](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview)
- [AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/understanding-applocker-rule-behavior)
- [Malleable C2](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2_main.htm)
- [Aggressor Script](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/agressor_script.htm)

Compilation VitePress réussie. Contrôle du HTML produit pour les 9 pages CRTO, des 60 liens et ancres du contenu, et du schéma. Vite signale des bundles dépassant 500 kB. Le moteur Chromium local a refusé de démarrer. Le rendu visuel sur mobile et ordinateur, la recherche et les boutons de copie restent à tester dans un navigateur.
