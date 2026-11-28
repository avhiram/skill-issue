# Hiérarchie du système de fichiers Linux

> [FHS - Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)

![Filesystem Hierarchy Standard](.gitbook/assets/fhs2.png)

- La plupart des distributions Linux utilisent le **[Filesystem Hierarchy Standard](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard)** comme référence pour l’organisation du système Unix.

```bash
# Show the standard with the command:
man hier
```

- Tous les fichiers et répertoires sont organisés sous la racine du système de fichiers **`/`**.

**`/bin`** - Contient les principaux programmes exécutables (binaires).

**`/boot`** - Contient les fichiers de démarrage du système (kernel, initrd).

**`/dev`** - Contient les fichiers de périphériques (souris, disques, entrée et sortie standard, erreur standard).

**`/etc`** - Contient les fichiers de configuration des programmes à l’échelle du système.

**`/home`** - Contient les répertoires personnels des utilisateurs.

**`/lib`** - Contient les bibliothèques partagées essentielles à l’exécution des binaires.

**`/media`** - Point de montage des supports amovibles.

**`/mnt`** - Point de montage des systèmes de fichiers temporaires.

**`/opt`** - Contient les logiciels supplémentaires absents des dépôts de la distribution, les utilitaires et paquets personnalisés accessibles à tous.

**`/proc`** - Fournit des informations sur les processus actifs, le kernel et le matériel.

**`/root`** - Répertoire personnel de l’utilisateur root.

**`/sbin`** - Contient les binaires essentiels réservés à l’utilisateur root.

**`/tmp`** - Contient les fichiers temporaires du système, généralement effacés au démarrage. Ne pas y conserver de données importantes.

**`/usr`** - Contient des sous-répertoires importants ainsi que des programmes et données en lecture seule.

**`/var`** - Contient les données variables des programmes (logs, spool), notamment les journaux de diagnostic.

