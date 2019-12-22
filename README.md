# ucfai's `autobot`

As managing a course/club is rather involved, coupled with the
ever-changing-hands-nature of such a group, it becomes difficult to onboard
newcomers on the processes and structures that have been settled upon by prior
folks. To overcome this, [@ionlights][git-ionlights] initially developed a bot
to handle this. Since then, many others have contributed to expanding `autobot`'s
capabilities to handle nearly all of the managerial and distributed tasks of AI@UCF.

[git-ionlights]: https://github.com/ionlights

## Documentation

<font color=red>**This is currently under development.**</font>

We've taken time to document as thoroughly, and unobtrustively, as possible
&ndash; and you can find a web-based version of the documentation at
https://ucfai.org/docs/admin/bot.

# Development

## Code Structure

```bash
autobot
├── apis           # any external resource we need access to are defined here.
├── log.py         # logging, mixed-in with Python's `logger`
├── main.py        # package entrypoint, parsers, and high-level operations
├── meta           # OO-like containers for Groups, Coordinators, and Meetings
│   └── groups.py  # sets up specific attributes for each Group
├── safety.py      # figures out the right paths and configurations
├── templates      # these are used for creating semesters, banners, etc.
└── utils          # specific actions, since these don't quite make sense in OO
```

## General Structure

`autobot` focuses on managing 4 different verticals:

1. Generate minimal content needed for a given `group`'s semester.
1. Maintain and update the website to ensure content is publicly accessible.
1. Perform routine genertion for various social platforms, e.g. uploading meetings
   to YouTube, generating email and instagram banners, etc.
1. Onboard new leadership to make sure everyone has appropriate access on a
   variety of plaforms we use in managing AI@UCF.

## Installation

Just about everything is packaged in a `conda` environment. To install you need
to make sure you have [Anaconda][anaconda] or [Miniconda][miniconda] on your
system. Once installed, proceed with the following:

[anaconda]: https://www.anaconda.com/distribution/
[miniconda]: https://docs.conda.io/en/latest/miniconda.html

```bash
$ conda env create -f envs/{macos,linux}.yml  # pick one of the OSes
$ conda activate ucfai-admin  # or `source activate ucfai-admin`
$ pip install -e .  # make sure you're in the same place as this README
$ autobot -h  # this should output something that looks like "help"
```

Since you're probably developing the `autobot`, make sure you have the related
groups laid out like the following `tree` output shows:

```bash
ucfai
├── bot
├── core
├── data-science
├── intelligence
└── supplementary
```

**Note:** If you need help decrypting any files ending in `.gpg`, contact
[@ionlights][git-ionlights].
