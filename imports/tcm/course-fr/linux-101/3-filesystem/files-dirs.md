# Manipulation des fichiers et répertoires

## Commandes

### touch

- **`touch`** - Met à jour les dates d’accès et de dernière modification de chaque fichier à l’heure actuelle.
  - Si le fichier indiqué n’existe pas, touch le crée.
  - Cette commande est souvent utilisée pour créer des fichiers vides plutôt que pour modifier leur horodatage.

```bash
ls -l notes.txt
	-rw-rw-r-- 1 user user 0 ago 28 18:36 notes.txt

touch notes.txt
ls -l notes.txt
	-rw-rw-r-- 1 user user 0 ago 28 18:38 notes.txt
# Timestamp is updated to the current time
```

### cp

- **`cp`** - Copie un fichier source vers un fichier de destination.

```bash
cp notes.txt notes-copy.txt
```

### mv

- **`mv`** - Déplace un fichier.
  - Permet aussi de renommer un fichier ou un répertoire au même emplacement.

```bash
mv notes.txt ./Desktop
```

### rm

- **`rm`** - Supprime les fichiers ou répertoires.
  - Supprime le fichier sans le placer dans la corbeille.
  - Utiliser les options appropriées pour limiter les suppressions accidentelles.

```bash
rm -i ./Desktop/notes.txt
rm: remove regular empty file './Desktop/notes.txt'? y
```

### mkdir

- **`mkdir`** - Crée des répertoires.

```bash
mkdir project
# Creates project directory
```

### rmdir

- **`rmdir`** - Supprime un répertoire vide.

```bash
rmdir project/
rmdir: failed to remove 'project/': Directory not empty

# Use "rm" to delete a non-empty directory, recursively removing all the directory contents without confirmation:
rm -rf project/
```

