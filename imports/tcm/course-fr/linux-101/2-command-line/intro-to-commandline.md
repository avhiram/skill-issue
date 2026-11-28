# Introduction à la ligne de commande

## Invite de commande

- Le prompt affiche le **nom de l’utilisateur**, suivi du symbole **`@`**, du **nom de la machine (hostname)**, du séparateur **`:`**, du répertoire de travail actuel et du symbole **`# Introduction à la ligne de commande

## Invite de commande

- **.

```bash
user@ubuntuVM:~$
# current_user @ host_name : current_working_directory $
# user = current_user
# ubuntuVM = hostname
# ~ = user's home directory
# $ = logged in as a normal user

root@ubuntuVM:/home/user#
# # = logged in as the root user
```

### whoami

- **`whoami`** - Affiche le nom de l’utilisateur actuel.

```bash
user@ubuntuVM:~$ whoami
	user
```

- **Linux distingue les majuscules des minuscules**, y compris dans les commandes.

### hostname

- **`hostname`** - Affiche le nom de la machine actuelle.

```bash
user@ubuntuVM:~$ hostname
	ubuntuVM
```

### pwd

- **`pwd`** - Affiche le répertoire de travail actuel.

```bash
user@ubuntuVM:~$ pwd
	/home/user

# ~ is shorthand for the home directory
```

### ls

- **`ls`** - Liste le contenu d’un répertoire.

```bash
user@ubuntuVM:~$ ls
	Desktop  Documents  Downloads  Music  Pictures  Public  snap  Templates  Videos
```

### cd

- **`cd`** - Change le répertoire de travail.

```bash
user@ubuntuVM:~$ cd Downloads
user@ubuntuVM:~/Downloads$
# the current working directory changed

user@ubuntuVM:~/Downloads$ cd ..
# to go back to the parrent directory
user@ubuntuVM:~$
```

> Utiliser **`cd`** seul pour revenir au répertoire personnel de l’utilisateur actuel.

```bash
user@ubuntuVM:~$ cd /tmp/
user@ubuntuVM:/tmp$ cd
user@ubuntuVM:~$
```

![](.gitbook/assets/image-20220828150837433.png)

### alias

- **`alias`** - Liste les alias Bash.

```bash
alias
    alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
    alias egrep='egrep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias grep='grep --color=auto'
    alias l='ls -CF'
    alias la='ls -A'
    alias ll='ls -alF'
    alias ls='ls --color=auto'
```

