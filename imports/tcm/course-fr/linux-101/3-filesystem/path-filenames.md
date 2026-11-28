# Chemins et noms de fichiers

## Espaces dans les noms de fichiers

> Utiliser **`TAB`** pour l’autocomplétion.

```bash
ls
	'file name.txt'
# Single quotes are displayed to make sure "file name.txt" is one entry

cat file name.txt
	cat: file: No such file or directory
	cat: name.txt: No such file or directory
# Bash shell uses spaces between commands arguments
```

- Bonne pratique : éviter les espaces comme séparateurs de mots dans les noms de fichiers.
- Deux méthodes permettent d’indiquer à Bash qu’un espace fait partie du nom :
  - Échapper l’espace avec **`\`** pour qu’il soit traité comme une partie de l’argument.
  - Placer le nom complet entre guillemets doubles (le cours indique de ne pas interpréter les caractères spéciaux entre les guillemets).

```bash
cat file\ name.txt
	Hello Paths!
# TAB on keyboard can also be used for auto completion.

cat "file name.txt" 
	Hello Paths!
```

## Expansion des chemins et noms de fichiers

- Les répertoires et fichiers d’un chemin sont séparés par un slash **`/`**.
- Chaque élément situé entre deux séparateurs est appelé un **segment**.
- Le wildcard le plus courant est l’astérisque **`*`**.

```bash
ls file*.txt
# List the current directory text files that start with the string "file"

ls file?.txt
# List the text files that start with the string "file" and have another character after that.
# ? wildcard = any single character on the command line

ls **/*.txt
# Use ** to search accross multiple segments. ** matches zero or more characters accross multiple directories.
```

- **`[ ]`** indiquent un ensemble de caractères à faire correspondre.

```bash
ls file[123].txt
ls file[1-3].txt
ls file[a-zA-Z].txt

# Only match files that start with the string "file" and another specific character after.
```

## Commandes de lecture des fichiers texte

### head

- **`head`** - Affiche par défaut les 10 premières lignes de chaque fichier.
  - Utiliser l’option **`-n`** pour préciser le nombre de lignes à afficher (ou -NUMBER).

```bash
head words.txt 
	# One
	# Two
	# Three
	# Four
	# Five
	# Six
	# Seven
	# Eight
	# Nine
	# Ten
	
head -n 3 words.txt 
	# One
	# Two
	# Three
	
head -15 words.txt 
	# One
	# Two
	# Three
	# Four
	# Five
	# Six
	# Seven
	# Eight
	# Nine
	# Ten
	# 
	# Alfa
	# Bravo
	# Charlie
	# Delta
```

### tail

- **`tail`** - Affiche par défaut les 10 dernières lignes de chaque fichier.
  - Utiliser l’option **`-n`** pour préciser les lignes à afficher (ou +NUMBER).

```bash
tail words.txt 
	# Delta
	# Echo
	# Foxtrot
	# Golf
	# Hotel
	# India
	# Juliett
	# Kilo
	# Lima
	# Mike
	
tail -n 3 words.txt 
	# Kilo
	# Lima
	# Mike
	
tail -4 words.txt 
	# Juliett
	# Kilo
	# Lima
	# Mike
```

- La commande **tail** permet de surveiller les modifications à la fin d’un fichier, notamment un log.

```bash
tail --help
	-f, --follow[={name|descriptor}]
                           output appended data as the file grows;
                             an absent option argument means 'descriptor'
                             
tail -f /var/log/auth.log
```

### diff

- **`diff`** - Compare les fichiers ligne par ligne et affiche les différences.

```bash
diff words.txt words2.txt 
	
	2c2
	< Two
	---
	> 
	4c4
	< Four
	---
	> 
	6c6
	< Six
	---
	> 
	8c8
	< Eight
	---
	> 
	13c13
	< Bravo
```

