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

**Problème :** un service lié uniquement à `127.0.0.1:8000` sur le pivot n'écoute pas sur son IP réseau. Ligolo réserve `240.0.0.1` pour atteindre **le `127.0.0.1` de l'agent sélectionné** à travers son tunnel.

### Ajouter la route spéciale vers le localhost distant

Ajouter la route `240.0.0.1/32` sur Kali via la TUN associée à l'agent concerné, après le démarrage du tunnel.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route add 240.0.0.1/32 dev ligolo
curl -I http://240.0.0.1:8000/
```

`curl` ne réussira que si un serveur HTTP écoute effectivement sur `127.0.0.1:8000` du pivot. Éviter de réutiliser cette même adresse avec plusieurs interfaces simultanées sans contrôler la route.

## Ligolo-ng : double pivot

**Situation :** le pivot B ne peut pas joindre Kali directement, mais peut atteindre l'IP interne du pivot A et son listener TCP. Le premier pivot doit relayer le port Ligolo du deuxième agent vers le proxy sur Kali.

```text
Kali (proxy :11601) ⇐ tunnel TLS ⇒ Pivot A (agent Ligolo)
                                       ↑ connexion de Pivot B vers A:11602
                                       │ listener A → Kali:11601
                                 Pivot B (deuxième agent) → réseau 172.16.30.0/24
```

### Créer un listener sur le premier pivot

Le listener ouvre TCP `11602` **sur le pivot A** et relaie vers TCP `11601` **sur Kali** ; vérifier les pare-feu des deux côtés. Ne pas le confondre avec un port ouvert sur Kali.

<p class="oscp-command-note">Dans la console Ligolo, **session du pivot A** sélectionnée.</p>

```text
listener_add --addr 0.0.0.0:11602 --to 127.0.0.1:11601 --tcp
listener_list
```

### Faire connecter le second agent

Sur le pivot B, l'agent contacte `172.16.20.1:11602` (pivot A) ; ne pas utiliser l'IP de Kali si elle n'est pas routable.

<p class="oscp-command-note">Sur le pivot B: PowerShell si Windows.</p>

```powershell
.\agent.exe -connect 172.16.20.1:11602 -accept-fingerprint EMPREINTE_SHA256
```

**Repère :** `172.16.20.1` est l'interface interne du pivot A et `172.16.20.30` celle du pivot B. Ces adresses sont fictives. Remplacer ces IP par les vraies interfaces trouvées avec `ifconfig`.

### Créer la seconde interface TUN

Créer `ligolo2` sur Kali pour le second tunnel : ne pas faire passer simultanément les deux agents sur la même interface TUN.

<p class="oscp-command-note">Sur Kali: terminal Linux habituel.</p>

```bash
sudo ip tuntap add user "$USER" mode tun ligolo2
sudo ip link set ligolo2 up
```

### Sélectionner le deuxième agent

Dans la console Ligolo, sélectionner la **session du pivot B** avant `ifconfig` et `tunnel_start --tun ligolo2`.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
session
ifconfig
tunnel_start --tun ligolo2
```

### Router le deuxième réseau

Sur Kali, router `172.16.30.0/24` via `ligolo2` et vérifier la route avant de tester un port du second réseau.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route add 172.16.30.0/24 dev ligolo2
ip route get 172.16.30.10
nmap -sT -Pn -n --unprivileged -p 445 172.16.30.10
```

## Listener Ligolo : rendre un service Kali accessible au pivot

Un *listener* ouvre un port TCP sur l'agent sélectionné et redirige les connexions vers un service qui écoute sur le proxy Kali. Pratique pour récupérer un fichier depuis Kali lorsque la cible ne peut pas contacter directement `10.10.14.10`.

### Héberger le fichier sur Kali

Sur Kali, servir le dossier local uniquement sur `127.0.0.1:8000` ; le listener Ligolo exposera ce service sur le pivot.

<p class="oscp-command-note">Sur Kali: terminal Linux séparé.</p>

```bash
mkdir -p ./partage
python3 -m http.server 8000 --bind 127.0.0.1 --directory ./partage
```

### Dans Ligolo, exposer le service HTTP de Kali sur le pivot A

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

Pour **envoyer un fichier vers Kali**, `python3 -m http.server` ne suffit pas (pas d'upload) : utiliser **SMB ou WebDAV** comme expliqué dans la [fiche Transferts de fichiers](./transferts.md). Un listener Ligolo peut acheminer ces protocoles si le port et le service de réception sont configurés.

## Chisel : autre solution de pivot

**Chisel** transporte des redirections TCP et un proxy SOCKS via une connexion client/serveur HTTP encapsulée dans un tunnel chiffré lorsqu'il est configuré en conséquence. Contrairement au tunnel TUN de Ligolo, il peut nécessiter ProxyChains pour les outils qui ne prennent pas en charge SOCKS.

### Démarrer Chisel en mode reverse

Le serveur Chisel de Kali écoute sur TCP `8001` et autorise les redirections inverses demandées par le client distant ; protéger son accès.

<p class="oscp-command-note">Sur Kali: serveur Chisel.</p>

```bash
chisel server --port 8001 --reverse
```

### Rediriger un port interne vers Kali

Le client Chisel sur Windows demande une écoute sur Kali en `8080` vers son propre `127.0.0.1:80` ; un serveur doit réellement écouter sur ce port.

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

Avec `R:1080:socks`, le port SOCKS `1080` est exposé côté serveur Chisel sur Kali ; garder la connexion client active.

<p class="oscp-command-note">Sur le pivot Windows: client Chisel.</p>

```powershell
.\chisel.exe client 10.10.14.10:8001 R:1080:socks
```

### Tester un site interne via SOCKS

Avec `curl --socks5-hostname`, la résolution des noms DNS est déléguée au proxy SOCKS ; l'adresse IP d'exemple n'exige pas de résolution.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
curl --socks5-hostname 127.0.0.1:1080 -I http://172.16.20.10/
```

**ProxyChains :** si l'outil n'accepte pas SOCKS directement, ajouter `socks5 127.0.0.1 1080` à la section `[ProxyList]` de `/etc/proxychains4.conf`, puis utiliser `proxychains4` devant la commande. Vérifier que le serveur SOCKS Chisel est actif ; avec Nmap, utiliser `-sT -Pn` et éviter les scans SYN/UDP à travers ce proxy.

## SSH : alternative simple avec un compte valide

**Quand utiliser SSH ?** Si le pivot dispose d'un serveur SSH accessible et d'un compte autorisé, privilégier les redirections SSH pour les services nécessaires. Pour les transferts de fichiers, utiliser [SCP](./transferts.md).

### Redirection SSH locale

Sur Kali, `-L` ouvre `127.0.0.1:8080` ; le serveur SSH du pivot se connecte ensuite à `172.16.20.10:80`.

<p class="oscp-command-note">Sur Kali: le serveur SSH a accès au service interne.</p>

```bash
ssh -N -L 127.0.0.1:8080:172.16.20.10:80 etudiant@10.10.10.30
```

### Proxy SOCKS par SSH

Sur Kali, `ssh -D` crée un proxy SOCKS sur `127.0.0.1:9050` ; conserver la session SSH ouverte pendant son utilisation.

<p class="oscp-command-note">Sur Kali: accès SSH à un pivot.</p>

```bash
ssh -N -D 127.0.0.1:9050 etudiant@10.10.10.30
```

### Routage réseau avec sshuttle

`sshuttle` achemine les connexions TCP du sous-réseau via SSH ; il ne remplace pas un VPN complet pour tous les protocoles.

<p class="oscp-command-note">Sur Kali: sshuttle et SSH accessibles.</p>

```bash
sshuttle -r etudiant@10.10.10.30 172.16.20.0/24
```

## Tunnel DNS avec dnscat2

Le tunnel DNS dnscat2 est un exemple avancé réservé à un laboratoire où les échanges DNS sont explicitement autorisés. **Ce n'est pas une étape nécessaire pour Ligolo-ng** : elle est conservée séparément pour éviter de mélanger les outils.

### Démarrer le serveur dnscat2

Utiliser un domaine DNS réellement contrôlé par le laboratoire, avec les enregistrements nécessaires pour joindre le serveur, et un secret partagé.

<p class="oscp-command-note">Sur la machine Linux qui héberge le serveur DNS contrôlé.</p>

```bash
dnscat2-server laboratoire.example --secret 'SecretDeTest'
```

### Connecter un client dnscat2

Le client doit utiliser le même domaine et le même secret que le serveur ; vérifier la délégation et l'accès DNS avant le test.

<p class="oscp-command-note">Sur le client Linux de laboratoire.</p>

```bash
./dnscat --secret='SecretDeTest' laboratoire.example
```

Les noms de binaires et les options dnscat2 dépendent de la version compilée ou installée. Exécuter `dnscat2-server --help` et `./dnscat --help` pour la version locale.

## Dépannage Ligolo-ng

| Symptôme | Cause à vérifier |
|---|---|
| L'agent n'apparaît pas | Proxy démarré, IP Kali correcte, TCP 11601 joignable et empreinte TLS valide ? |
| Empreinte TLS refusée | Relever `certificate_fingerprint` sur le proxy actif et recopier l'empreinte sans erreur dans l'agent |
| `no such device` / TUN absent | Vérifier `ip -br link show ligolo` sur Kali ; créer ou sélectionner l'interface TUN appropriée |
| `RTNETLINK answers: File exists` | Une interface ou une route existe déjà ; vérifier `ip -br link` et `ip route` avant toute modification |
| Tunnel lancé mais réseau inaccessible | Contrôler la session sélectionnée, le sous-réseau de l'agent, la route Kali et les pare-feu |
| Second agent non connecté | Vérifier le listener TCP sur pivot A, son IP interne et l'accès depuis pivot B à `11602` |
| Service sur `127.0.0.1` de l'agent inaccessible | Router `240.0.0.1/32` vers la bonne TUN et vérifier que le service écoute sur l'agent |
| Port redirigé muet | Vérifier le service sur Kali, le port `--to`, le port `--addr` sur l'agent et le pare-feu |

## Arrêter et nettoyer

### Fermer le tunnel

Dans Ligolo, sélectionner l'agent concerné avant `tunnel_stop`. Les listeners restent indépendants : consulter `listener_list`, puis arrêter chacun par son identifiant.

<p class="oscp-command-note">Dans la console Ligolo: sélectionner la bonne session.</p>

```text
session
tunnel_stop
listener_list
```

### Supprimer la route après l'examen

Sur Kali, supprimer uniquement les routes ajoutées manuellement et présentes dans `ip route` ; ne pas toucher aux routes VPN préexistantes.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route del 172.16.20.0/24 dev ligolo
sudo ip route del 172.16.30.0/24 dev ligolo2
```

Si les interfaces TUN ont été créées manuellement, vérifier qu'aucune session ne les utilise avant `sudo ip link delete ligolo` ou `sudo ip link delete ligolo2`. Les routes créées automatiquement par des versions récentes peuvent être gérées par Ligolo.

## Sources officielles

- [Ligolo-ng: introduction et limites réseau](https://docs.ligolo.ng/)

- [Ligolo-ng: Quickstart, interface, certificat et routage](https://docs.ligolo.ng/Quickstart/)

- [Ligolo-ng: double pivot](https://docs.ligolo.ng/sample/double/)

- [Ligolo-ng: listeners](https://docs.ligolo.ng/Listeners/)

- [Ligolo-ng: accès au localhost de l'agent](https://docs.ligolo.ng/Localhost/)

- [Ligolo-ng: configuration v0.8 et routes persistantes](https://docs.ligolo.ng/Config-File/)

- [Notes krovs: tunnels complémentaires](https://github.com/krovs/oscp-notes/blob/main/docs/17_port_red_tun.md)