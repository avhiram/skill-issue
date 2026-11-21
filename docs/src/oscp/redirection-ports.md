---
title: "OSCP · Redirection de ports"
description: "Comprendre et reproduire les redirections SSH, Socat, Plink et netsh."
---

# Redirection de ports

**Objectif :** rendre un service accessible lorsqu'il se trouve derrière un pivot, en sachant **où le port écoute** et **sur quelle machine lancer la commande**. Exemples fictifs : Kali `10.10.14.10`, pivot `10.10.10.30`, service interne `172.16.20.10:80`.

## Choisir la bonne redirection

| Technique | Exécutée sur | Résultat |
|---|---|---|
| SSH `-L` | Kali | Port sur Kali → service accessible depuis le pivot SSH |
| SSH `-R` | Pivot | Port sur Kali (serveur SSH) → service accessible depuis le pivot |
| SSH `-D` | Kali | Proxy SOCKS sur Kali → réseau accessible depuis le pivot |
| Socat | Machine intermédiaire | Port TCP du pivot → service interne |
| Plink `-R` | Windows pivot | Même logique que SSH `-R` avec l'outil PuTTY |
| Windows `netsh portproxy` | Windows pivot, administrateur | Relais TCP entre deux adresses/ports |


**Comprendre les ports :** le **port d'écoute** est le port auquel vous vous connectez ; le **port cible** est celui du service final. La machine qui héberge le port d'écoute dépend de `-L`, `-R` et de l'outil.

## SSH : redirection locale

Vous avez un accès SSH au pivot, qui peut joindre un service interne. **Kali crée un port local** pour joindre ce service.

### Ouvrir la redirection locale

`127.0.0.1:8080` sur Kali redirige vers `172.16.20.10:80` depuis le pivot SSH.

<p class="oscp-command-note">Sur Kali — garder le terminal ouvert.</p>

```bash
ssh -N -L 127.0.0.1:8080:172.16.20.10:80 etudiant@10.10.10.30
```

### Tester le port local

Tester le service HTTP distant depuis la boucle locale de Kali.

<p class="oscp-command-note">Sur Kali — autre terminal.</p>

```bash
curl -I http://127.0.0.1:8080/
```

**`-L` = Local** : le port d'écoute se trouve sur la machine qui lance SSH, ici Kali. `-N` n'ouvre pas de shell distant.

## SSH : redirection distante / inverse

Le pivot peut joindre Kali par SSH, mais Kali ne peut pas accéder directement au service du pivot. Le pivot demande à SSH d'ouvrir un port **sur Kali**.

### Ouvrir un port sur Kali depuis le pivot

`127.0.0.1:9090` écoute sur Kali (serveur SSH), puis conduit au `127.0.0.1:80` du pivot.

<p class="oscp-command-note">Sur le pivot — Linux ou Windows avec client SSH.</p>

```bash
ssh -N -R 127.0.0.1:9090:127.0.0.1:80 kali@10.10.14.10
```

### Tester la redirection inverse

La requête arrive sur le service qui écoute sur le port 80 du pivot.

<p class="oscp-command-note">Sur Kali — autre terminal.</p>

```bash
curl -I http://127.0.0.1:9090/
```

**`-R` = Remote** : le port d'écoute est **sur le serveur SSH** (ici Kali). Le serveur SSH doit permettre ce type de redirection. Avec `127.0.0.1`, ce port n'est pas exposé aux autres machines.

## SSH : proxy SOCKS dynamique

Cette méthode est utile pour des outils capables d'utiliser SOCKS. **À la différence de Ligolo-ng, aucun réseau TUN n'est créé**.

### Ouvrir un proxy SOCKS sur Kali

Le proxy SOCKS écoute uniquement sur `127.0.0.1:9050` de Kali.

<p class="oscp-command-note">Sur Kali — connexion SSH au pivot.</p>

```bash
ssh -N -D 127.0.0.1:9050 etudiant@10.10.10.30
```

### Tester une URL interne via SOCKS

L'option `--socks5-hostname` conserve la résolution de nom côté proxy, quand un nom interne est utilisé.

<p class="oscp-command-note">Sur Kali — autre terminal.</p>

```bash
curl --socks5-hostname 127.0.0.1:9050 -I http://172.16.20.10/
```

Si besoin, ajouter `socks5 127.0.0.1 9050` sous `[ProxyList]` dans `/etc/proxychains4.conf` et utiliser `proxychains4 <commande>`. Pour Nmap derrière SOCKS, commencer par `-sT -Pn`.

## Socat : transfert TCP entre deux ports

Socat est pratique lorsqu'un pivot peut joindre le service interne et qu'un port TCP de ce pivot est accessible depuis Kali.

### Écouter sur le pivot et relayer vers l'interne

Le pivot écoute sur TCP `8080` et retransmet vers `172.16.20.10:80`.

<p class="oscp-command-note">Sur le pivot Linux — dans un laboratoire autorisé.</p>

```bash
socat TCP-LISTEN:8080,bind=0.0.0.0,reuseaddr,fork TCP:172.16.20.10:80
```

### Tester le port exposé par le pivot

Se connecter au port 8080 du pivot.

<p class="oscp-command-note">Sur Kali — autre terminal.</p>

```bash
curl -I http://10.10.10.30:8080/
```

`fork` autorise plusieurs connexions ; `reuseaddr` facilite le redémarrage. `0.0.0.0` expose le port sur les interfaces du pivot : restreindre l'écoute si possible.

## Windows : redirection avec OpenSSH

OpenSSH Client doit être installé sur Windows et Kali doit héberger SSH. Ici, Windows redirige son RDP local (`3389`) vers un port accessible **sur Kali**.

### Créer le tunnel depuis Windows

Le port `9090` est lié à `127.0.0.1` sur Kali. Aucune règle pare-feu entrante Windows n'est nécessaire pour ce port SSH distant.

<p class="oscp-command-note">Sur le pivot Windows — PowerShell.</p>

```powershell
ssh.exe -N -R 127.0.0.1:9090:127.0.0.1:3389 kali@10.10.14.10
```

### Accéder au RDP via la redirection

Un client RDP peut utiliser le port local. La cible doit autoriser la session RDP et les identifiants utilisés.

<p class="oscp-command-note">Sur Kali — terminal Linux.</p>

```bash
xfreerdp3 /v:127.0.0.1:9090 /u:etudiant /dynamic-resolution
```

## Windows : redirection avec Plink

Plink est l'outil SSH en ligne de commande de PuTTY. Utile si le client OpenSSH Windows n'est pas disponible.

### Créer la redirection inverse avec Plink

Conserver la session active. Lors de la première connexion, **vérifier** l'empreinte de la clé SSH du serveur.

<p class="oscp-command-note">Sur Windows — PowerShell ou CMD.</p>

```powershell
.\plink.exe -ssh -N -R 127.0.0.1:9090:127.0.0.1:3389 kali@10.10.14.10
```

Éviter de fournir un mot de passe avec `-pw` dans un historique de terminal ; saisir l'authentification de manière interactive si l'environnement le permet.

## Windows : redirection TCP avec netsh

`netsh interface portproxy` modifie la configuration Windows : **droits administrateur requis**. Seul le trafic TCP est pris en charge ; le service IP Helper doit être opérationnel. Prévoir la suppression de la règle après le test.

### Créer une règle de redirection TCP

Le pivot écoute sur `0.0.0.0:8080` et transmet vers `172.16.20.10:80`.

<p class="oscp-command-note">Sur le pivot Windows — PowerShell administrateur.</p>

```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8080 connectaddress=172.16.20.10 connectport=80
```

### Contrôler la configuration

Lister les règles et vérifier le port d'écoute.

<p class="oscp-command-note">Sur le même Windows — PowerShell.</p>

```powershell
netsh interface portproxy show all
Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8080
```

**Si le pare-feu bloque TCP 8080**, seule une personne autorisée à administrer le poste doit ouvrir le port. Ne pas désactiver tout le pare-feu pour résoudre ce problème.

### Retirer la règle après le test

Supprimer uniquement la redirection créée dans cet exemple.

<p class="oscp-command-note">Sur Windows — PowerShell administrateur.</p>

```powershell
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8080
```

## Ligolo-ng : tunnel complet plutôt que port par port

Si vous avez besoin d'atteindre plusieurs machines du réseau interne, **Ligolo-ng est souvent plus pratique** : il crée une interface TUN et une route réseau, sans ouvrir une redirection par service.

Consulter la [fiche Ligolo-ng pas à pas](./tunneling.md) : tunnel simple, double pivot, accès à `127.0.0.1` du pivot et listeners.

## Dépannage express

| Symptôme | Contrôle |
|---|---|
| Port inaccessible | Service en écoute et adresse de liaison corrects ? |
| SSH `administratively prohibited` | Redirection refusée par le serveur SSH |
| `Address already in use` | Port déjà utilisé : `ss -ltnp` ou `Get-NetTCPConnection` |
| ProxyChains ne répond pas | SOCKS actif et bon port renseigné dans `proxychains4.conf` |
| `netsh` configuré mais muet | IP Helper, port Windows, route et pare-feu |
| Ligolo traverse plusieurs sous-réseaux | Vérifier l'interface TUN et les routes avec la fiche dédiée |


## Références

- [Documentation officielle d'OpenSSH](https://man.openbsd.org/ssh)

- [Microsoft — netsh interface portproxy](https://learn.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-interface-portproxy)

- [Ligolo-ng — Quickstart](https://docs.ligolo.ng/Quickstart/)

- [krovs — exemples de redirection](https://github.com/krovs/oscp-notes/blob/main/docs/17_port_red_tun.md)