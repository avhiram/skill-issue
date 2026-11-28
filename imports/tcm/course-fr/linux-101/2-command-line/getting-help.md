# Obtenir de l’aide en ligne de commande

## Commandes d’aide

### man

- **`man`** - Affiche la page de manuel d’une commande.
- Le contenu est organisé en sections : nom, synopsis, description des arguments et exemples.
- Appuyer sur **`q`** pour quitter le manuel.

```bash
man ls
# man page for the ls command
	LS(1)                                   User Commands                                   LS(1)
	NAME
	       ls - list directory contents
	SYNOPSIS
	       ls [OPTION]... [FILE]...
	DESCRIPTION
	       List information about the FILEs (the current directory by default).  Sort entries
	       alphabetically if none of -cftuvSUX nor --sort is specified.
	       Mandatory arguments to long options are mandatory for short options too.
	       -a, --all
	              do not ignore entries starting with .
	       -A, --almost-all
	              do not list implied . and ..
	       --author
	              with -l, print the author of each file
	       -b, --escape
	              print C-style escapes for nongraphic characters
	       --block-size=SIZE
	              with -l, scale sizes by SIZE when printing them;  e.g.,  '--block-size=M';  see
	              SIZE format below
	       -B, --ignore-backups
	              do not list implied entries ending with ~
	       -c     with  -lt:  sort  by, and show, ctime (time of last modification of file status
	              information); with -l: show ctime and sort by name; otherwise: sort  by  ctime,
	              newest first
	       -C     list entries by columns
	       --color[=WHEN]
	              colorize  the  output;  WHEN  can  be 'always' (default if omitted), 'auto', or
	              'never'; more info below
	       -d, --directory
	              list directories themselves, not their contents
	[...]
```

### info

- **`info`** - Alternative structurée aux pages de manuel, fournissant des informations plus détaillées sur la commande.

```bash
info ls
	# Next: dir invocation,  Up: Directory listing
	# 
	# 10.1 ‘ls’: List directory contents
	# ==================================
	# 
	# The ‘ls’ program lists information about files (of any type, including
	# directories).  Options and file arguments can be intermixed arbitrarily,
	# as usual.
	# 
	#    For non-option command-line arguments that are directories, by
	# default ‘ls’ lists the contents of directories, not recursively, and
	# omitting files with names beginning with ‘.’.  For other non-option
	# arguments, by default ‘ls’ lists just the file name.  If no non-option
	# argument is specified, ‘ls’ operates on the current directory, acting as
	# if it had been invoked with a single argument of ‘.’.
	# 
	#    By default, the output is sorted alphabetically, according to the
	# locale settings in effect.(1)  If standard output is a terminal, the
	# output is in columns (sorted vertically) and control characters are
	# output as question marks; otherwise, the output is listed one per line
	# and control characters are output as-is.
	# 
	#    Because ‘ls’ is such a fundamental program, it has accumulated many
	# options over the years.  They are described in the subsections below;
	# within each section, options are listed alphabetically (ignoring case).
	# The division of options into the subsections is not absolute, since some
	# options affect more than one aspect of ‘ls’’s operation.
	# [...]
```

### command --help

- Documentation intégrée à la commande, présentée sous une forme concise, avec les différentes options et leur utilisation.

```bash
ls --help
	Usage: ls [OPTION]... [FILE]...
	List information about the FILEs (the current directory by default).
	Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.
	
	Mandatory arguments to long options are mandatory for short options too.
	  -a, --all                  do not ignore entries starting with .
	  -A, --almost-all           do not list implied . and ..
	      --author               with -l, print the author of each file
	  -b, --escape               print C-style escapes for nongraphic characters
	      --block-size=SIZE      with -l, scale sizes by SIZE when printing them;
	                               e.g., '--block-size=M'; see SIZE format below
	  -B, --ignore-backups       do not list implied entries ending with ~
	  -c                         with -lt: sort by, and show, ctime (time of last
	                               modification of file status information);
	                               with -l: show ctime and sort by name;
	                               otherwise: sort by ctime, newest first
	  -C                         list entries by columns
	      --color[=WHEN]         colorize the output; WHEN can be 'always' (default
	                               if omitted), 'auto', or 'never'; more info below
	  -d, --directory            list directories themselves, not their contents
	  -D, --dired                generate output designed for Emacs' dired mode
	  -f                         do not sort, enable -aU, disable -ls --color
	  -F, --classify             append indicator (one of */=>@|) to entries
	      --file-type            likewise, except do not append '*'
	      --format=WORD          across -x, commas -m, horizontal -x, long -l,
	                               single-column -1, verbose -l, vertical -C
	      --full-time            like -l --time-style=full-iso
	  -g                         like -l, but do not list owner
	      --group-directories-first
	                             group directories before files;
	                               can be augmented with a --sort option, but any
	                               use of --sort=none (-U) disables grouping
	  -G, --no-group             in a long listing, don't print group names
	[...]
```

## Comprendre les commandes shell

> Pour obtenir des explications détaillées sur les commandes shell complexes, utiliser [explainshell.com](https://explainshell.com/) et [shell.how](https://www.shell.how/).

