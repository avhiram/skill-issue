# Consignes de l’examen CRTO

## Démarrer l’examen

Dans le menu du cours, ouvrir la leçon **Red Team Operator Exam**.

> **Ne pas quitter la page de l’examen** pendant son déroulement. Ouvrir le cours dans un autre onglet ou une autre fenêtre.

Le **Lab ID** figure en bas du panneau d’instructions. Le communiquer en cas de demande au support.

---

## Scénario de l’examen

- Scénario **assume-breach** : aucun Beacon préalablement lancé, mais un accès à une machine **foothold** du réseau interne.
- Le Beacon doit être déployé manuellement. **Il peut être nécessaire de contourner les protections du poste au préalable.**
- Le panneau d’instructions précise l’**operational objective** et les **rules of engagement** (hôtes exclus du périmètre et restrictions).

---

## Barème

| Élément | Points |
|-----------|--------|
| Objectif opérationnel | 50 pts |
| Respect de l’OPSEC | 50 pts |
| **Seuil de réussite** | **85 pts** |

> **Atteindre l’objectif ne suffit pas : les points OPSEC comptent aussi.**
> **Un score OPSEC trop faible entraîne l’échec, même si l’objectif est atteint.**

---

## Critères de notation OPSEC

| Critère | Cause de pénalité | Mesure préventive |
|-----------|--------------------------|------------|
| **Blocage par Defender / AppLocker** | Blocage de l’exécution d’un payload par l’antivirus | Vérifier l’Artifact Kit et le Resource Kit avant l’examen |
| **Connexion sortante depuis un processus inhabituel** | Callback HTTP d’un Beacon depuis un processus qui n’effectue normalement pas de requêtes Web | Utiliser un processus habituel (browser, svchost, dllhost) et configurer `spawnto` and `ppid` |
| **Indicateurs Cobalt Strike par défaut** | Noms de named pipes par défaut et technique d’injection standard | Personnaliser `post-ex.pipename` et `process-inject` dans le Malleable C2 Profile |
| **Lateral Movement suspect** | `jump psexec` / événements de création de services | Privilégier `jump winrm64`, puis `remote-exec wmi` ; utiliser PsExec en dernier recours |
| **Handles LSASS suspects** | Handle direct sur LSASS depuis un processus non-système | Privilégier le BOF `nanodump` ; éviter l’accès direct à LSASS avec Mimikatz |
| **Désactivation des protections** | Désactivation de Defender ou Windows Firewall | **Ne pas désactiver Defender ou Firewall : pénalité automatique** |

---

## Hôtes hors périmètre — Échec immédiat

> *"Une alerte déclenchée sur un hôte hors périmètre entraîne l’échec, même si l’objectif opérationnel a été atteint."*

**Lire les rules of engagement avant toute action.**
Identifier le périmètre avant tout Lateral Movement. Un hôte visible n’est pas nécessairement autorisé.

---

## Limites de temps

| Limite | Valeur |
|-------|-------|
| Temps de Lab | 24 heures cumulées |
| Fenêtre calendaire | 7 jours pour terminer et soumettre |
| Délai entre deux tentatives | 7 jours |
| Temps actif avant disponibilité de la sauvegarde | 15 à 20 minutes |

---

## Sauvegarde de la progression — Deux options à distinguer

<img src="/images/save-progress-in-exam.png" width=860>

| Bouton | Résultat |
|--------|--------|
| **Exit Lab → Save Progress And Exit** | VM sauvegardées, environnement suspendu — **sans risque de clôture** |
| **Exit Lab → End Lab** | **Fin immédiate et irréversible de la tentative d’examen** |

> **Rester actif 15 à 20 minutes avant de pouvoir utiliser Save Progress And Exit.**
> Ne démarrer l’examen que lorsque l’on est prêt : fermer immédiatement l’environnement peut mettre fin à la tentative.

---

## Persistence nécessaire — Ne pas dépendre uniquement de Save Progress

> *"Ne pas compter sur cette fonction pour conserver les Beacons en cours, notamment ceux d’une chaîne P2P. Prévoir une persistence adaptée comme dans un environnement réel."*

Après une reprise, une chaîne Beacon SMB/P2P peut être interrompue. La persistence doit survivre au redémarrage. La configurer **avant** toute pause.

---

## Soumission et notation

- Cliquer sur **Submit** en bas du panneau d’instructions pour terminer l’examen et lancer la notation.
- **Submit est définitif** : éviter tout clic accidentel.
- Ne pas quitter ni fermer la page pendant la notation, qui peut durer plusieurs minutes.
- Après la notation, cliquer sur **Update & Close** pour transmettre le résultat à la plateforme — **sans cette étape, la certification ne peut pas être réclamée.**

---

## Checklist avant l’examen

```
[ ] Lire les rules of engagement et identifier les hôtes hors périmètre
[ ] Se connecter en SSH au team server et mettre à jour le Malleable C2 Profile (stage, post-ex, process-inject)
[ ] Adapter l’Artifact Kit (patch.c), compiler et contrôler avec ThreatCheck
[ ] Compiler le Resource Kit, adapter template.x64.ps1 et contrôler AMSI avec ThreatCheck
[ ] Charger artifact.cna et resources.cna dans le CS Script Manager
[ ] Vérifier le callback Beacon avec Defender activé avant les actions sur cible
[ ] Éviter le processus spawnto par défaut rundll32.exe
[ ] Configurer un motif de named pipes personnalisé dans post-ex.pipename
[ ] Préparer la persistence à mettre en place après le premier check-in Beacon
```
