# Guide CRTO — Environnement et méthode de révision
# liham

[Bibliothèque de commandes CRTO](./crto-command-library.md)

## Identité et contexte

Guide personnel de révision Red Team pour la certification **CRTO (Certified Red Team Operator)** de Zero Point Security. Notes de **liham**.

**Certification CRTO :** https://certs.zeropointsecurity.co.uk/97e8bb4c-2937-4c21-bf35-ad5cc17f6cb0#acc.pYBlWQqt

Les explications restent courtes, techniques et adaptées à une utilisation pendant les labs et les révisions.

**Objectifs de révision :**
1. Étudier les supports CRTO de Zero Point Security.
2. Maintenir un dépôt GitHub de notes faciles à consulter pendant l’examen.

**Rappel sur la notation mentionnée dans ces notes :** 85 points sur 100, dont 50 pour l’objectif et 50 pour l’OPSEC. Les alertes Defender peuvent entraîner des pertes de points, même si l’objectif est atteint. Vérifier le barème officiel en vigueur avant l’examen.

---

## Infrastructure

### Labs CRTO — Zero Point Security (SnapLabs / Skillable)

- **Accès :** navigateur avec Guacamole, sans VPN dans ce lab.
- **Attacker Desktop :** poste Windows disposant des outils et bibliothèques prévus.
- **C2 :** Cobalt Strike sous licence ; team server Ubuntu et client Windows.
- **Active Directory :** environnement de formation CONTOSO avec plusieurs forêts.
- **Presse-papiers :** copie et collage depuis le navigateur.
- **Durée des labs :** modules de 30 à 45 minutes selon le thème ; les conditions d’accès sont celles indiquées par la plateforme.

## Présentation des notes

1. Ne pas réexpliquer les notions élémentaires d’Active Directory lorsque le contexte est clair.
2. Fournir la syntaxe Cobalt Strike lorsqu’une commande C2 est discutée.
3. Préciser le risque OPSEC : `OPSEC-🟢SAFE`, `OPSEC-🟠CAUTION` ou `OPSEC-🔴UNSAFE`. Ces catégories sont des repères du lab, pas des garanties de non-détection.
4. Présenter les commandes dans des blocs de code avec un langage approprié.
5. Pour une fiche, utiliser le format Markdown existant : **titre clair, explication française courte, puis commande dans son bloc**.
6. Signaler les effets de bord, les événements Windows et la télémétrie potentielle des commandes.
7. Ne pas présumer que Microsoft Defender est désactivé.
8. Lorsqu’une observation doit être notée, produire un bloc Markdown utilisable dans la rubrique correspondante.

---

## Référence OPSEC Cobalt Strike

### Signification des icônes Beacon

- 🔴 **Beacon rouge avec éclairs :** représente généralement un Beacon disposant de privilèges élevés (administrateur ou SYSTEM). Cette icône ne prouve pas qu’un SIEM ou un EDR a détecté le Beacon.
- 🔵 **Beacon bleu :** représente un Beacon exécuté sous un compte utilisateur sans élévation.

### Catégories de risque des commandes

| Niveau | Commandes | Explication |
|---|---|---|
| 🔴 UNSAFE | `shell`, `powershell`, `run` | Peuvent lancer des processus enfants visibles. |
| 🔴 UNSAFE | `mimikatz` direct | Exécution dans le processus Beacon ; signatures et télémétrie possibles. |
| 🔴 UNSAFE | `jump psexec`, `jump psexec64` | Création d’un service (événement 7045) et écriture possible sur disque. |
| 🟠 CAUTION | `jump scshell64` | Modification de la configuration d’un service existant (événement 7040). |
| 🟠 CAUTION | `execute-assembly` | Mécanisme fork-and-run avec processus temporaire et named pipe. |
| 🟠 CAUTION | `spawn`, `spawnas` | Création d’un processus pour exécuter le payload. |
| 🟠 CAUTION | `remote-exec wmi` | Création de processus via WMI, potentiellement visible dans les journaux. |
| 🟠 CAUTION | `make_token` | Session de connexion de type 9 ; événement 4648 possible selon le contexte. |
| 🟠 CAUTION | `pth` | Pass-the-Hash ; interactions avec LSASS possibles. |
| 🟠 CAUTION | `dcsync` | Requête de réplication AD pouvant générer l’événement 4662. |
| 🟠 CAUTION | `getsystem` | Plusieurs méthodes d’élévation, dont certaines impliquent des services. |
| 🟢 SAFE | `inline-execute` | Exécution d’un BOF dans le contexte du Beacon. |
| 🟢 SAFE | `powerpick` | Exécution PowerShell sans démarrer systématiquement powershell.exe. |
| 🟢 SAFE | `ldapsearch` | Requête LDAP via BOF, sans processus enfant dans le scénario. |
| 🟢 SAFE | `steal_token` | Duplication de token dans le processus courant. |
| 🟢 SAFE | `jump winrm`, `jump winrm64` | Utilisation de WinRM sans création de service dans le scénario décrit. |
| 🟢 SAFE | `krb_triage`, `krb_dump` | BOF utilisant les API Kerberos ; charger `C:\Tools\Kerbeus-BOF\kerbeus_cs.cna`. |
| 🟢 SAFE | `getuid`, `pwd`, `ls`, `cd` | Commandes intégrées du Beacon. |

---

## Préparer un Beacon dans le lab

### Réglages et contrôles OPSEC du scénario

```cs
sleep 5 21
// Identifier le PID de explorer.exe dans la liste des processus
ps
ppid <explorer.exe-pid>
spawnto x64 "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
inject <explorer.exe-pid> x64 http

// Ne plus envoyer de commandes dans ce Beacon.
```

## Récapitulatif des catégories OPSEC

```
OPSEC-🟢SAFE:    inline-execute, ldapsearch, powerpick, steal_token, jump winrm64, krb_triage, krb_dump, getuid
OPSEC-🟠CAUTION: execute-assembly, make_token, remote-exec wmi, jump scshell64, getsystem, dcsync, pth
OPSEC-🔴UNSAFE:  shell, powershell, run, jump psexec64, mimikatz direct
```

## Méthode de prise de notes

Pour chaque commande utilisée pendant une session d’entraînement, noter son contexte, son objectif, ses prérequis et son résultat. Conserver un format Markdown cohérent avec les autres fiches.

### Vérification OPSEC avant exécution

Pour évaluer une technique, utiliser un récapitulatif structuré des opérations observables :

```
Niveau :          
🟢SAFE
🟠CAUTION
🔴UNSAFE

OPSEC PRE-CHECK: <nom de la technique>
─────────────────────────────────────────────────
Processus enfant : Oui / Non — <nom du processus>
Accès à LSASS : Oui / Non
Écriture disque : Oui / Non — <chemin>
Journaux : <identifiants des événements>
Télémétrie EDR : <éléments observables>
Signature Defender : Connue / Inconnue / Modifiée par le profil
─────────────────────────────────────────────────
Alternative : <commande moins intrusive si disponible>
```

Conserver ce résultat dans les notes de commandes de la session.

### Observations Microsoft Defender

Lorsqu’un essai du lab est détecté ou non détecté par Microsoft Defender, consigner le résultat dans `notes/<module-concerné>.md` avec ce modèle :

```markdown
#### [YYYY-MM-DD] Observation Defender
**Technique :** <nom de la technique>
**Version Defender :** <version des signatures dans le lab>
**Résultat :** DÉTECTÉ / NON DÉTECTÉ / PARTIEL
**Réglage étudié :** <option du profil ou modification du chargeur>
**Observation complémentaire :** <résultat de l’autre essai>
```

Ajouter une ligne de synthèse dans `cheatsheets/defense-evasion.md`.
