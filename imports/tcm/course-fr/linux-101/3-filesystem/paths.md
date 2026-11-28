# Chemins

- Un chemin indique l’emplacement d’un fichier ou d’un répertoire.

## Chemins absolus

- Un chemin absolu commence toujours **à la racine du système de fichiers** **`/`**.
- Il est valide depuis n’importe quel emplacement du système de fichiers. L’utiliser lorsque l’emplacement est connu.
- Un chemin relatif peut parfois être plus long qu’un chemin absolu. Dans ce cas, privilégier le chemin absolu.

```bash
ls /var/log/syslog
# /var/log/syslog is an absolute path to the syslog file
```

## Chemins relatifs

- Un chemin relatif commence **depuis le répertoire courant** pour atteindre la ressource.
- Il est généralement plus court qu’un chemin absolu et utile dans les projets qui partagent une structure locale de répertoires.

```bash
cd /var
ls log/syslog
# log/syslog is a relative path

ls ./log/syslog
# Using "." it specifies the commands starts in the current working directory

ls ../home/user/Documents/
# ".." is the parrent of the current working directory
```

