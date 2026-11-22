# Audit CRTO

## Version de travail

Branche locale `docs/crto-revision`, créée depuis `origin/main` au commit `2b03c903`. La copie Linux personnelle de l’éditeur ne faisait pas partie des fichiers reçus.

## Inventaire des sources

| Dépôt | Révision | Fichiers suivis |
|---|---|---:|
| [CRTO-Notes](https://github.com/miguelarrabalcastro/CRTO-Notes/tree/bb0b7f03972acbf131d4e007e4cfba06cff056b2) | `bb0b7f03` | 13 |
| [CRTO_2025_Notes](https://github.com/Razzlemouse/CRTO_2025_Notes/tree/aee72c0c135137881a577653e2d03ccab865b074) | `aee72c0c` | 13 |
| [CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/tree/decaa7a705d7c024455212fb6ff4f6a9d8b59365) | `decaa7a7` | 131 |

Les deux premières sources organisent les mêmes grands thèmes en espagnol et en anglais. La troisième ajoute notamment des labs S4U et RBCD, AD CS, des fiches AppLocker et des exemples de code. Les 157 chemins ont été inventoriés. La comparaison par empreinte a détecté 2 fichier(s) identique(s) au-delà de la première occurrence. Les PNG ont passé un contrôle de format. Les 70 captures ont été examinées en planches de vignettes. Le texte de chaque capture n’a pas été transcrit. Aucune licence de réutilisation des captures n’a été identifiée dans les inventaires des trois révisions.

## Intégration

| Ensemble | Travail réalisé |
|---|---|
| Notes | Dix notes sur Windows, Kerberos, AD CS, Active Directory, les trusts, Cobalt Strike, Credential Access, les processus, la persistance et SQL Server. Les variantes de délégation figurent dans un tableau commun. |
| Labs | Cinq exercices sur les access tokens Windows, les identités SQL, la délégation, AppLocker et les certificats. Le scénario de délégation est fictif. |
| Cheatsheets | Dix blocs distincts dans deux fiches. Les exercices reprennent les commandes nécessaires à leur lecture autonome. |
| Navigation | Page d’attente remplacée, dix-sept pages ajoutées au menu CRTO. Thème VitePress existant utilisé. |
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

Compilation VitePress réussie. Contrôle du HTML produit pour les 18 pages CRTO, des 119 liens et ancres du contenu, et du schéma. Vite signale des bundles dépassant 500 kB. Le moteur Chromium local a refusé de démarrer. Le rendu visuel sur mobile et ordinateur, la recherche et les boutons de copie restent à tester dans un navigateur.

## Couverture par famille de fichiers

Les repères ci-dessous indiquent où lire les mécanismes associés. Une correspondance thématique ne signifie pas que chaque variante ou commande source a été reprise.

| Famille source | Pages ou rubrique | Traitement |
|---|---|---|
| Clavier, Evasion, AppLocker, artefacts, Ghidra | Process Injection et Defence Evasion · Journaux et stratégie Windows | Langues, analyse statique et décisions AppLocker. Procédures de contournement exclues. |
| Initial Access, Beacon, Aggressor Script, Malleable C2 | Cobalt Strike et opérations réseau | Rôles, livraisons, tâches et observations réseau. Génération de payloads exclue. |
| Discovery, Post-Exploitation, LDAP, GPO | Discovery dans Active Directory · Windows et contexte de sécurité | Objets, relations, stratégies et contexte Windows. Collecte offensive automatisée exclue. |
| Persistence, Elevated Persistence, Privilege Escalation | Services Windows et Persistence · Windows et contexte de sécurité | Déclencheurs, permissions, services et comptes. Procédures d’exploitation exclues. |
| Credential Access, User Impersonation, Domain Dominance | Credential Access et User Impersonation · Kerberos et Active Directory | Objets de sécurité, réplication et catégories de tickets. Extraction et falsification exclues. |
| Kerberos, Unconstrained / Constrained Delegation, RBCD, S4U | Kerberos et Active Directory · Lab délégation | Modèles de délégation et lecture d’une autorisation. Les variantes opérationnelles, dont la substitution de service, ne sont pas reproduites. |
| MS SQL, SQL CLR, linked servers | Identités dans SQL Server · Lab SQL | Identités, modules et contexte des appels distants. |
| Domain Trusts, Forest Trusts, parent-enfant, Inbound / Outbound | Domain Trusts et Forest Trusts | Sens des relations, authentification et autorisation. |
| AD CS, ESC1, ESC2, ESC3, ESC4, ESC8 | Active Directory Certificate Services · Lab certificat | Modèles, usages, émissions et services web. |
| Lateral Movement, WinRM, Proxy, SOCKS | Cobalt Strike et opérations réseau | Lecture des flux, rôle du relais et limites d’attribution. |
| Exemples C, C++, Aggressor Script | Process Injection et Defence Evasion · Cobalt Strike et opérations réseau | Familles de mécanismes expliquées. Code d’injection et automatisation offensive exclus. |
| Exam Instructions, recommandations, attestations, modèle de rapport, anecdotes | Hors des cours techniques | Aucune règle d’examen ni donnée personnelle reprise. Le modèle tiers n’a pas été redistribué. |

Contrôle de forme sur 15 occurrences de blocs, correspondant à 10 commandes ou requêtes distinctes. Chaque bloc est précédé d’un titre et d’un paragraphe explicatif. Les labs reprennent les commandes qui leur sont nécessaires.

Références supplémentaires pour les journaux, les commandes et les paramètres Windows.

- [AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/using-event-viewer-with-applocker)
- [Get-WinEvent](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent)
- [Get-FileHash](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash)
- [gpresult](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/gpresult)
- [Get-WinUserLanguageList](https://learn.microsoft.com/en-us/powershell/module/international/get-winuserlanguagelist)
- [Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/)
- [Évaluations AD CS](https://learn.microsoft.com/en-us/defender-for-identity/security-posture-assessments/certificates)
- [Événements Kerberos](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/appendix-l--events-to-monitor)

## Correspondance des 19 fiches et 25 labs de CRTO Study Notes

Chaque ligne situe la synthèse du sujet. Les labs source et les exercices originaux de SKILL-ISSUE ont des procédures distinctes.

| Fichier technique dans la source | Note associée dans SKILL-ISSUE |
|---|---|
| `cheatsheets/Post-Exploitation-Privilege-Escalation-Enumeration.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `cheatsheets/adcs.md` | [Active Directory Certificate Services](docs/src/crto/notes/adcs.md) |
| `cheatsheets/applocker.md` | [Windows et contexte de sécurité](docs/src/crto/notes/windows.md) |
| `cheatsheets/cobalt-strike-primer.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `cheatsheets/credential-access.md` | [Credential Access et User Impersonation](docs/src/crto/notes/credential-access.md) |
| `cheatsheets/defense-evasion.md` | [Process Injection et Defence Evasion](docs/src/crto/notes/processus.md) |
| `cheatsheets/discovery.md` | [Discovery dans Active Directory](docs/src/crto/notes/discovery.md) |
| `cheatsheets/domain-dominance.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `cheatsheets/elevated-persistence.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `cheatsheets/forest-domain-trusts.md` | [Domain Trusts et Forest Trusts](docs/src/crto/notes/trusts.md) |
| `cheatsheets/initial-access.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `cheatsheets/kerberos.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `cheatsheets/lateral-movement.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `cheatsheets/ms-sql-server.md` | [Identités dans SQL Server](docs/src/crto/notes/sql-server.md) |
| `cheatsheets/persistence.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `cheatsheets/pivoting.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `cheatsheets/post-exploitation.md` | [Windows et contexte de sécurité](docs/src/crto/notes/windows.md) |
| `cheatsheets/privilege-escalation.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `cheatsheets/user-impersonation.md` | [Credential Access et User Impersonation](docs/src/crto/notes/credential-access.md) |
| `labs/2-Cobalt-Strike-Primer.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `labs/Constrained-Delegation-kerberos-lab.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/Discovery-lab.md` | [Discovery dans Active Directory](docs/src/crto/notes/discovery.md) |
| `labs/Elevated-Persistence-lab.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `labs/Inbound-Trusts-lab.md` | [Domain Trusts et Forest Trusts](docs/src/crto/notes/trusts.md) |
| `labs/Initial-Access-lab.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `labs/Lateral-Movement-lab.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `labs/Outbound-Trusts-lab.md` | [Domain Trusts et Forest Trusts](docs/src/crto/notes/trusts.md) |
| `labs/Parent-Child-Trusts.md` | [Domain Trusts et Forest Trusts](docs/src/crto/notes/trusts.md) |
| `labs/Persistence-lab.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `labs/Privilege-Escalation-lab.md` | [Services Windows et Persistence](docs/src/crto/notes/services-persistence.md) |
| `labs/RBCD-lab.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/S4U2self-lab.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/SQL-Servers-lab.md` | [Identités dans SQL Server](docs/src/crto/notes/sql-server.md) |
| `labs/Service-Name-Substitution-Kerberos-lab.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/Unconstrained-Delegation-Kerberos-lab.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/User-Impersonation-lab.md` | [Credential Access et User Impersonation](docs/src/crto/notes/credential-access.md) |
| `labs/applocker-challenge.md` | [Windows et contexte de sécurité](docs/src/crto/notes/windows.md) |
| `labs/credential-access-challenge-commands.md` | [Credential Access et User Impersonation](docs/src/crto/notes/credential-access.md) |
| `labs/defence-evasion-lab-Malleable.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
| `labs/dpersist1.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/esc1.md` | [Active Directory Certificate Services](docs/src/crto/notes/adcs.md) |
| `labs/esc8.md` | [Active Directory Certificate Services](docs/src/crto/notes/adcs.md) |
| `labs/kerberos-challenge.md` | [Kerberos et Active Directory](docs/src/crto/notes/kerberos.md) |
| `labs/pivoting-SOCKS-lab.md` | [Cobalt Strike et opérations réseau](docs/src/crto/notes/cobalt-strike.md) |
