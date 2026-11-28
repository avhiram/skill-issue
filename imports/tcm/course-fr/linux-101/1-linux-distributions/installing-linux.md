# Installation de Linux

## Télécharger et installer VirtualBox

VirtualBox est un logiciel de virtualisation open source disponible sur Linux, Windows et Mac OS.

- Télécharger **VirtualBox** et **VirtualBox Extension Pack** depuis la [page de téléchargement](https://www.virtualbox.org/wiki/Downloads), selon la plateforme utilisée (Windows dans ce tutoriel).

![](.gitbook/assets/image-20220814155217998.png)

![](.gitbook/assets/image-20220814155334144.png)

- Installer VirtualBox avec les paramètres par défaut.
- Installer VirtualBox Extension Pack.

## Télécharger une image Linux

Ce tutoriel utilise Ubuntu Desktop Linux.

Pour utiliser une autre distribution, consulter la liste des [distributions Linux populaires](linux-distributions.md).

- Télécharger le fichier `.iso` de la version **Ubuntu Desktop LTS** depuis la [page de téléchargement](https://ubuntu.com/download/desktop).

## Créer une machine virtuelle

- Lancer VirtualBox.
- Cliquer sur **New** pour créer une machine virtuelle (**VM**).

![](.gitbook/assets/image-20220814160023790.png)

- Cliquer sur **Expert Mode**.

![](.gitbook/assets/image-20220814163415069.png)

- Renseigner le nom de la VM, son dossier de stockage, son type (**`Linux`**) et sa version (**`Ubuntu 64bit`**).
- Définir la RAM à **`4096 MB`** (4 Go) ou conserver le réglage par défaut **`1024 MB`**.
- Sélectionner `Create a virtual hard disk now`.
- Cliquer sur **Create**.

![](.gitbook/assets/image-20220814162743473.png)

- Définir la taille du disque à **`20 GB`**.
- Choisir le type de disque **`VDI - Dynamically allocated`**.
- Cliquer sur **Create** pour initialiser la machine.

![](.gitbook/assets/image-20220814164656943.png)

- Sélectionner la nouvelle VM dans le gestionnaire, puis cliquer sur **Settings**.

![](.gitbook/assets/image-20220814174252593.png)

- Dans l'onglet **System** :

  - Retirer Floppy de l'ordre de démarrage.
  - Définir Chipset sur **`PIIX3`** (par défaut).
  - Activer **`Enable PAE/NX`** dans Processor.
  - Vérifier que **`Default Paravirtualization`** et **`Enable Nested Paging`** sont sélectionnés dans Acceleration.

![](.gitbook/assets/image-20220814174901665.png)

![](.gitbook/assets/image-20220814174955219.png)

![](.gitbook/assets/image-20220814175137011.png)

- Dans l'onglet **Display**, augmenter la **`Video Memory`** à **`128 MB`**.
- Le **`Graphics Controller`** doit être **`VMSVGA`** pour utiliser VirtualBox Guest Additions.

![](.gitbook/assets/image-20220814175228447.png)

## Installer Linux

- Sélectionner la VM et cliquer sur **Start** pour la démarrer.

![](.gitbook/assets/image-20220814165535424.png)

- Cliquer sur l'icône de fichier pour ouvrir le sélecteur de disque optique.

![](.gitbook/assets/image-20220814165746274.png)

- Cliquer sur **Add**, sélectionner le fichier `.iso` téléchargé, puis le choisir dans la liste avec **Choose**.
- Cliquer sur **Start** pour démarrer la VM avec l'image montée `ubuntu-22.04-desktop-amd64.iso` dans cet exemple.

![](.gitbook/assets/image-20220814170229539.png)

- Attendre le démarrage d'Ubuntu et le menu d'installation.
- Sélectionner la langue puis cliquer sur **Install Ubuntu**.

![](.gitbook/assets/image-20220814171602035.png)

- Sélectionner la disposition du clavier (**Keyboard layout**) et continuer.
- Choisir **`Normal installation`** et cocher les deux cases **Other options** (une connexion Internet est nécessaire).

![](.gitbook/assets/image-20220814171524228.png)

- Choisir **`Erase disk and install Ubuntu`** et poursuivre sans activer le chiffrement.

![](.gitbook/assets/image-20220814172526947.png)

![](.gitbook/assets/image-20220814172653457.png)

- Sélectionner la localisation et le fuseau horaire sur la carte.
- Définir les informations de connexion : `hostname`, `username` et `password`.
- Cliquer sur **Continue** pour lancer l'installation d'Ubuntu.

![](.gitbook/assets/image-20220814173136821.png)

- Redémarrer la VM une fois l'installation terminée.

![](.gitbook/assets/image-20220814174135011.png)

## Installer VirtualBox Guest Additions

Guest Additions active des fonctionnalités avancées de VirtualBox pour améliorer l'intégration entre la VM et la machine hôte, ainsi que l'affichage avec le contrôleur graphique VMSVGA.

- Terminer le démarrage de la VM et se connecter au bureau Ubuntu.
- Dans le menu VirtualBox, sélectionner **Devices - Insert Guest Additions CD image...**.

![](.gitbook/assets/image-20220814180203046.png)

- Lancer le disque VBox_GAs depuis le bureau de la VM.
- Cliquer sur **Run** lorsque l'installation est proposée.
  - Si la fenêtre ne s'ouvre pas automatiquement, ouvrir le disque, faire un clic droit sur **`autorun.sh`** et choisir **Run as a Program**.
  - Saisir le mot de passe pour installer le logiciel.

![](.gitbook/assets/image-20220814180915886.png)

![](.gitbook/assets/image-20220814181134051.png)

- Redémarrer la VM.
- Faire un clic droit sur le disque puis sélectionner **Eject**.

![](.gitbook/assets/image-20220814181848186.png)

- Activer le presse-papiers partagé depuis le menu **`Devices - Shared Clipboard - Bidirectional`**.

![](.gitbook/assets/image-20220814181633168.png)

## Mettre à jour Linux

Maintenir Ubuntu à jour avec l'une des méthodes suivantes.

- Utiliser l'application **Software Updater**.

![](.gitbook/assets/image-20220814182124471.png)

- Ouvrir un terminal (**`Ctrl+Alt+T`**) et exécuter la commande suivante pour mettre à jour le système.
  - Cette commande peut également être utilisée via SSH.

```bash
sudo apt update && sudo apt upgrade -y
```

> Pour installer d'autres distributions Linux, consulter leur documentation officielle.
