# Lecture de fichiers texte

## Commandes

### more

- **`more`** - Affiche le contenu d’un fichier texte page par page, uniquement vers l’avant. Appuyer sur **`q`** pour quitter.

### less

- **`less`** - Affiche le contenu d’un fichier texte avec davantage de possibilités que `more` : navigation ligne par ligne, vers le haut ou vers le bas, recherche et déplacement dans le fichier.
  - Pour effectuer une recherche, utiliser le slash **`/word_to_search`**.
  - Appuyer sur **`q`** pour quitter.

```bash
# Some "less" Commands and Actions
Down arrow, Enter, e, or j - Move forward one line.
Up arrow,y or k	- Move backward one line.
Space bar or f - Move Forward one page.
b - Move Backward one page.
/pattern - Search forward for matching patterns.
?pattern - Search backward for matching patterns.
n - Repeat previous search.
N - Repeat previous search in reverse direction.
g - Go to the first line in the file.
Ng - Go to the N-th line in the file.
G - Go to the last line in the file.
p - Go to the beginning of fthe ile.
Np - Go to N percent into file.
h - Display help.
q - Exit less.
```

### cat

- **`cat`** - Concatène le contenu de plusieurs fichiers vers la sortie standard (stdout).
  - Utile en combinaison avec une redirection de la sortie.


```bash
cat --help
	Usage: cat [OPTION]... [FILE]...
	Concatenate FILE(s) to standard output.
	With no FILE, or when FILE is -, read standard input.
	  -A, --show-all           equivalent to -vET
	  -b, --number-nonblank    number nonempty output lines, overrides -n
	  -e                       equivalent to -vE
	  -E, --show-ends          display $ at end of each line
	  -n, --number             number all output lines
	  -s, --squeeze-blank      suppress repeated empty output lines
	  -t                       equivalent to -vT
	  -T, --show-tabs          display TAB characters as ^I
	  -u                       (ignored)
	  -v, --show-nonprinting   use ^ and M- notation, except for LFD and TAB
	      --help     display this help and exit
	      --version  output version information and exit
	Examples:
	  cat f - g  Output f's contents, then standard input, then g's contents.
	  cat        Copy standard input to standard output.
	  
	  # Send the content of more files to a new file
	  cat file1.txt file2.txt file3.txt > combined.txt
	  cat combined.txt
```

- Afficher le contenu d’un fichier :

```bash
cat /etc/os-release
	PRETTY_NAME="Ubuntu 22.04 LTS"
	NAME="Ubuntu"
	VERSION_ID="22.04"
	VERSION="22.04 LTS (Jammy Jellyfish)"
	VERSION_CODENAME=jammy
	ID=ubuntu
	ID_LIKE=debian
	HOME_URL="https://www.ubuntu.com/"
	SUPPORT_URL="https://help.ubuntu.com/"
	BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
	PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
	UBUNTU_CODENAME=jammy
```

