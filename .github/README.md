# ucfai's `autobot`
As there's quite a bit to managing a course/club, it's relatively necessary to
have some structure which might be challenging to maintain with the frequency of
changing hands. To overcome this, [@ionlights][git-ionlights] initially
developed a bot to handle this. It's since been further expanded upon by many
others to formulate what now runs many of the managerial and distributed
services of AI@UCF.


## Code Structure
```
autobot            # package root
├── lib            # all the primary functions of the bot go here
│   ├── apis       # any external resources we need to access are done here
│   ├── config     # configurations, e.g. website-specific data, etc.
│   └── ops        # all actions enumerated, with associated funcs
├── meta           # object-oriented containers for use by `tooling` funcs
│   └── groups.py  # sets up specific attributes for each Group
├── templates      # files to either seed or generate content in groups/site
└── main.py        # entrypoint
```

## General Structure
The `bot` should focus on managing 4 different verticals.
1. Generating all the minimal content needed for a given group's semester.
1. Maintaining and updating the website to ensure that all content is publicly,
   and easily, accessible.
1. Performing the routine of various social platforms, e.g. uploading lectures
   to YouTube, architecting the emails to best sent, etc.
1. Onboarding new leadership in a structured manner to make sure that everyone
   has the appropriate access needed on a variety of platforms.

## Documentation
We've taken time to document as thoroughly, and unobtrustively, as possible
&ndash; and you can find a web-based version of the documentation at
https://ucfai.org/bot.
