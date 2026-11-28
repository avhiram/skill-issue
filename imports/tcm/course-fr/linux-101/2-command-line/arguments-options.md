# Arguments et options des commandes

- Certaines options utilisent un tiret suivi d’un caractère. D’autres utilisent deux tirets suivis d’un nom composé de plusieurs caractères.
- Les formats peuvent être combinés en respectant les règles suivantes :
  - Les options courtes à un caractère peuvent être regroupées.
  - Les options longues ne peuvent pas être regroupées.

## Exemple avec ls

```bash
ls --help
	Usage: ls [OPTION]... [FILE]...
	List information about the FILEs (the current directory by default).
	Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.
	
	Mandatory arguments to long options are mandatory for short options too.
	  -a, --all                  do not ignore entries starting with .
	  -A, --almost-all           do not list implied . and ..
	[...]
	  -I, --ignore=PATTERN       do not list implied entries matching shell PATTERN
	  -k, --kibibytes            default to 1024-byte blocks for disk usage;
	                               used only with -s and per directory totals
	  -l                         use a long listing format
	  -L, --dereference          when showing file information for a symbolic
	                               link, show information for the file the link
	                               references rather than for the link itself
	  -m                         fill width with a comma separated list of entries
	  -n, --numeric-uid-gid      like -l, but list numeric user and group IDs
	[...]
```

- **`ls -al`** - Combiner les options courtes :

```bash
ls -al
	total 100
	drwxr-x--- 16 user user 4096 ago 28 15:15 .
	drwxr-xr-x  3 root root 4096 lug 24 15:19 ..
	-rw-------  1 user user  829 ago  8 10:44 .bash_history
	-rw-r--r--  1 user user  220 lug 24 15:19 .bash_logout
	-rw-r--r--  1 user user 3771 lug 24 15:19 .bashrc
	drwx------ 12 user user 4096 ago 28 14:41 .cache
	drwx------ 12 user user 4096 ago 28 14:41 .config
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Desktop
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Documents
	drwxr-xr-x  3 user user 4096 lug 24 15:59 Downloads
	drwx------  2 user user 4096 ago 28 15:38 .gnupg
	-rw-------  1 user user   20 ago 28 15:15 .lesshst
	drwx------  3 user user 4096 lug 24 15:37 .local
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Music
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Pictures
	-rw-r--r--  1 user user  807 lug 24 15:19 .profile
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Public
	drwx------  4 user user 4096 lug 24 15:59 snap
	drwx------  2 user user 4096 lug 24 15:40 .ssh
	-rw-r--r--  1 user user    0 lug 24 15:37 .sudo_as_admin_successful
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Templates
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-clipboard.pid
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-display-svga-x11.pid
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-draganddrop.pid
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-seamless.pid
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Videos
```

- **`ls --all -l`** - Utiliser les options longues :

```bash
# Same output
ls --all -l
	total 100
	drwxr-x--- 16 user user 4096 ago 28 15:15 .
	drwxr-xr-x  3 root root 4096 lug 24 15:19 ..
	-rw-------  1 user user  829 ago  8 10:44 .bash_history
	-rw-r--r--  1 user user  220 lug 24 15:19 .bash_logout
	-rw-r--r--  1 user user 3771 lug 24 15:19 .bashrc
	drwx------ 12 user user 4096 ago 28 14:41 .cache
	drwx------ 12 user user 4096 ago 28 14:41 .config
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Desktop
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Documents
	drwxr-xr-x  3 user user 4096 lug 24 15:59 Downloads
	drwx------  2 user user 4096 ago 28 15:38 .gnupg
	-rw-------  1 user user   20 ago 28 15:15 .lesshst
	drwx------  3 user user 4096 lug 24 15:37 .local
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Music
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Pictures
	-rw-r--r--  1 user user  807 lug 24 15:19 .profile
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Public
	drwx------  4 user user 4096 lug 24 15:59 snap
	drwx------  2 user user 4096 lug 24 15:40 .ssh
	-rw-r--r--  1 user user    0 lug 24 15:37 .sudo_as_admin_successful
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Templates
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-clipboard.pid
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-display-svga-x11.pid
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-draganddrop.pid
	-rw-r-----  1 user user    5 ago 28 14:41 .vboxclient-seamless.pid
	drwxr-xr-x  2 user user 4096 lug 24 15:37 Videos
```

- **`ls -I`** - Ignorer les éléments correspondant à un motif :

```bash
# Ignore all entries that starts with the letter D:

ls -I "D*"
	Music  Pictures  Public  snap  Templates  Videos

ls --ignore="D*"
	Music  Pictures  Public  snap  Templates  Videos
```

> Faire attention aux arguments attendus par les options lorsqu’on combine plusieurs options courtes. Privilégier le format long.

