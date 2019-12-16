# `TODOs` for Winter 2019 (Deadline: Jan 10, 2020)

<style>

* {
    font-family: "Fira Sans", "Open Sans", "Noto Sans", sans-serif;
}
a {
    font-style: italic;
    color: #6d25ff !important;
}
a[href*="ucfai/bot"] {
    background-color: #efefef;
    padding: 0.2em 0.4em;
    font-style: normal;
    font-weight: bold;
    border-radius: 0.1em;
}
/* a[href*="ucfai/bot"]::before { */
    /* content: "Issue: "; */
/* } */
a[href*="ucfai/bot"]::after {
    content: attr(href);
}
a[href="#projects"] {
    font-size: 1.2em;
    font-style: normal;
    font-weight: bold;
    padding-top: 1.5em !important;
}

a[href^="https://github.com/"] {
    background-color: #efefef;
    padding: 0.2em 0.4em;
    font-style: normal;
    font-weight: bold;
    border-radius: 0.1em;
}

h1 + h3 {
    margin-right: 0;
}

t {
    color: #2d2d2d;
    font-weight: bold;
    font-style: normal;
    margin-right: 0.2em;
    padding: 0.2em 0.4em;
    border-radius: 0.1em;
    background-color: #efefef;
}

t[reqd]::after { content: " Required"; }
t[nice]::after { content: " Nice to Have"; }

t[robot]::after { content: " Must be Automated";}
t[human]::after { content: " Human-in-the-loop";}

t[todo]::after { content: " TODO"; }
t[wips]::after { content: " In Progress"; }
t[test]::after { content: " Testing"; }
t[code]::after { content: " Code Review"; }
t[talk]::after { content: " Discussion"; }
t[qa  ]::after { content: " QA"; }
t[done]::after { content: " DONE"; }

pr {
    /* color: #ff5733; */
    /* color: #581845; */
    color: #1893fa;
    font-weight: bold;
    background-color: transparent;
}
pr[text]::before { content: "Project"; }

pr[sub] {
    color: #c70039;
}
pr[sub][text]::before { content: "SubProject"; }

bot {
    background-color: #efefef;
    padding: 0.2em 0.4em;
    border-radius: 0.1em;
    font-weight: bold;
    font-family: "Fira Sans", monospace;
}
bot::before { content: "autobot"; }
</style>

## Motivation &amp; Overview

Over this Winter, we have multiple <pr text>s</pr> to take-up
so <bot></bot> can become more capable. Each of the sections
(list below) pertains to one of the <pr text>s</pr>. Within a
given project, ub-projects and milestones. While the original `autobot` was
built without tests, as [@ionlights][gh-john] is an attrocious developer (and
doesn't wanna hurt his own feelings), **we will be building tests to...**

1. Determine that `autobot` acts as expected.
1. Ensure we're less likely to break already functioning parts of `autobot` as
   we make upgrades.

**Guidelines for <pr text>s</pr>:**

- Each should have a small team (3-4 developers), working on various components.
- _Ideally_, we can each take up a <pr sub text></pr>.

**Guidelines for <pr sub text>s</pr>:**

- Each of these should have 1-2 developers.
- None of the tasks should be considered <t done>:rocket:</t> until the following have been completed:
  1. Features are developed. (Clearly. :sweat_smile:)
  1. Code has been reviewed by someone else
     > <t todo>:memo:</t> decide if they need to be on the same team or different team
  1. QA (that is, **tests**) have been designed, developed, and submitted.
  1. Code, inherently, must pass the **tests** mentioned above.

**Different stages of a <pr sub text>'s</pr> components:**

- <t todo>:memo:</t> still in ideation, discovery, or planning "mode"
- <t wips>:construction:</t> moved from `TODO`-like state to actual development
- <t test>:traffic_light:</t> developing tests to ensure that particular aspects don't fail minimum-viable-functionality of the item
- <t code>:crystal_ball:</t> someone else is taking a look at the code and providing feedback
- <t qa>:gift:</t> final stage of testing, moving to hardware platforms or cloud based on scope
- <t done>:rocket:</t> _**ship it!**_

**Different tags for each <pr sub text></pr>:**

- <t reqd>:key:</t> Needs to be completed by Jan 10, 2020
- <t human>:construction_worker:</t> Can have manual
  execution, for now
- <t robot>:robot:</t> Must be totally integrated
  into <bot></bot> and run based on `cron` (timers) and `webhooks`.
- <t nice>:ramen:</t> For the Jan 10, 2020 deadline
  &ndash; these aren't required to be met; but should be left on the roadmap.

<!--
# HTML Snippets for each of the task tiers, so we can keep track of them using
# this Markdown document.

<t todo>:memo:</t>
<t wips>:construction:</t>
<t test>:traffic_light:</t>
<t code>:crystal_ball:</t>
<t qa>:gift:</t>
<t done>:rocket:</t>

<t reqd>:key:</t>
<t robot>:robot:</t>
<t nice>:ramen:</t>
--->

# The <pr id="projects" text>s</pr>:

- [Video Pipeline](#video)
- [Semester Pipeline](#semester)
- [Website Pipeline](#website)
- [Analytics Pipeline](#analytics)

**Details for each <t todo>:memo:</t> are elaborated on in their respective
Github issues.**

# <pr id="video"> Video Pipeline </pr>

[:arrow_up: Back to Projects](#projects)

**Overall Team**
[@aehevia][gh-anthony]

- [Sync Capture](#sync-capture)
- [Automatic Rendering](#auto-render)
- [YouTube Uploader](#yt-upload)

## <pr id="sync-capture" sub> Sync Capture </pr>

### <t reqd>:key:</t> [](ucfai/bot#24) <t human>:construction_worker:</t>

**Description** To automate editing, we need to sync both the presenter's screen
and the live-video of their meeting. For an example, [check this
out][cbmm-demis]. We record our lecturer's screen using OBS and use a standard
camera to actually process the recording of the lecturer.

[cbmm-demis]: https://www.youtube.com/watch?v=cEOAerVz3UU

### <t reqd>:key:</t> Tasks

1. <t todo>:memo:</t> Automatic Recording
1. <t todo>:memo:</t> Recording Confirmation

## <pr id="auto-render" sub> Automatic Rendering </pr>

### <t reqd>:key:</t> [](ucfai/bot#25) <t human>:construction_worker:</t>

**Description** Video editing is no small task, it's also a rather expensive one
(especially if we choose to pay someone). To avoid this, we're building a
pipeline that ingests the OBS and lecturer footage. Then, it throws them on a
background that's generated in the same way our banners are. Finally, it renders
the video into a YouTube/Vimeo-compatible format.

### <t reqd>:key:</t> Tasks

1. <t test>:traffic_light:</t> Validate automated rendering script works (and
   determine points of improvement)
1. <t todo>:memo:</t> Integrate `imgkit` and automatic rendering
1. <t todo>:memo:</t> Fallback to <t human>:construction_worker:</t> rendering
   if need be (that is, allow a human to use the bot to render)

### <t nice>:ramen:</t> Tasks

1. <t todo>:memo:</t> Improve render performance
1. <t todo>:memo:</t> Improve render output quality
1. <t todo>:memo:</t> Implement audio normalization

## <pr id="yt-upload" sub> YouTube Uploader </pr>

### <t reqd>:key:</t> [](ucfai/bot#26)

**Description** Take the video that came out of [Automatic
Rendering](#automatic-rendering) and upload it to AI@UCF's YouTube/Vimeo
account. This should trigger an update to the group's syllabus as well as the Discord.

### <t reqd>:key:</t> Tasks

1. <t todo>:memo:</t> Decide on a YouTube/Vimeo account for AI@UCF
   ([@ionligts][gh-john], [@sirroboto][gh-justin])
1. <t todo>:memo:</t> Integrate YouTube API with <bot></bot> to push properly
   (and correctly) formatted uploads
1. <t todo>:memo:</t> Get the URL from the new video and modify they appropriate
   group's syllabus so <bot></bot> knows to update the appropriate channels.

### <t nice>:ramen:</t> Tasks

1. <t todo>:memo:</t> Have the Discord bot ping the appropriate
   `#general-<group>` channel about the new video

---

# <pr id="semester"> Semester Pipeline </pr>

[:arrow_up: Back to Projects](#projects)

**Overall Team**
[@ionlights][gh-john]
[@sirroboto][gh-justin]

- [Augment `semester-upkeep`](#upkeep)
- [Total Automation of <bot></bot>](#total-auto)

## <pr id="upkeep" sub> Augment `semester-upkeep` </pr>

### <t reqd>:key:</t> [](ucfai/bot#27)

**Description**

### <t reqd>:key:</t> Tasks

1. <t test>:traffic_light:</t>
   Enable `semester-upkeep` for single meetings, rather than doing batch run
1. <t test>:traffic_light:</t>
   Provide greater detail on `nbgrader` errors
1. <t test>:traffic_light:</t>
   Enable YAML control of Kaggle GPU notebooks
1. <t test>:traffic_light:</t>
   Migrate <bot></bot> to a VPS (e.g. GCP)
1. <t test>:traffic_light:</t>
   Allow for custom, "far-off," dates to be set for meetings

### <t nice>:ramen:</t> Tasks

1. <t todo>:memo:</t>
   `diff` Jupyter Notebooks from current repo's copy and our host's copy. (For
   now, would be a Kaggle Kernel `diff` with a local copy of the Notebook.)

## <pr id="total-auto" sub> Total Automation of <bot></bot> </pr>

### <t reqd>:key:</t> [](ucfai/bot#29)

**Description**

### <t reqd>:memo:</t> Tasks

1. <t todo>:memo:</t>
   Anytime a meeting notebook is PR'd, evaluate its candidacy as a valid
   notebook that can be merged back in to the group's repository.
1. <t todo>:memo:</t>
   Anytime a notebook (from any group) is merged back into the group's `master`
   branch, rebuild the website the propagate the new changes.

### <t nice>:ramen:</t> Tasks

1. <t todo>:memo:</t>
   `diff` Jupyter Notebooks from current repo's copy and our host's copy. (For

<br>

# <pr id="website"> Website Pipeline </pr>

[:arrow_up: Back to Projects](#projects)

**Overall Team**
[@ionlights][gh-john]
[@sirroboto][gh-justin]

- [General Website Maintenance](#web-maintenance)
- [Hugo Migration (from Jekyll)](#hugo-migrate)
- [<bot>'s</bot> Documentation)](#autobot-docs)
- [AI@UCF's Documentation)](#ucfai-docs)

## <pr id="web-maintenance" sub> General Website Maintenance </pr>

### <t reqd>:key:</t> [](ucfai/bot#30)

**Description**

### <t reqd>:key:</t> Tasks

1. <t todo>:memo:</t>
   Add buttons for **Slides** and **YouTube**
1. <t todo>:memo:</t>
   Feedback redirects, for each group
1. <t talk>:pill:</t>
   automated maintenance features need to know pathing/structure)</font>

### <t nice>:ramen:</t> Tasks

1. <t todo>:memo:</t>
   Automatic updating of each group's meeting schedule on homepage
1. <t todo>:memo:</t>
   Automatic addition/updating of coordinators, both past and present along with
   an overview of their contributions to the AI@UCF
1. <t todo>:memo:</t>
   A general set of tutorials that are semester independent, e.g. putting up the
   "Math Camp" and having that as part of the **Hackpack**

## <pr id="hugo-migrate" sub> Hugo Migration (from Jekyll) </pr>

### <t nice>:ramen:</t> [](ucfai/bot#31)

**Description**
This would entail transitioning ucfai.org from it's current half-baked Jekyll
approach to a more featureful, quicker, Hugo site. The particular template we're
looking to use is [`hugo-academic`][academic]. The driving factors behind this
are that `hugo-academic` gives us the following:

> 1. Easy author creation (basically, make a directory and provide a summary.)
> 1. Automatic author aggregation
> 1. Support for making project/research pages
> 1. Integrated "documentation" framework (allows for internal documentation
>    along with additional pages like the **Hackpack**)
> 1. Integrated "course" framework (allows for treating each semester like a `course`)

### <t reqd>:key:</t> Tasks

1. <t todo>:memo:</t>
   Reformat <bot>'s</bot> `NotebookExporters` to properly
   output for Hugo's expected content layout
1. <t todo>:memo:</t>
   Adjust directory structure for each group to follow `hugo-academic's`
   expected layout

[academic]: https://sourcethemes.com/academic/

## <pr id="autobot-docs" sub> <bot>'s</bot> Documentation </pr>

### <t reqd>:key:</t> [](ucfai/bot#32)

**Description** <bot></bot> is a little intimidating. Especially when you consider how much of AI@UCF it runs. To make things a bit easier to hack-on/maintain, it's important we have documentation that outlines things like...

> 1. Information flow
> 1. What should/n't be configured
>    1. How to configure those things
> 1. How to extend <bot></bot>

### <t reqd>:key:</t> Tasks

1. <t test>:traffic_light:</t>
   Document the process of creating a group's semester
1. <t test>:traffic_light:</t>
   Document the process of editing/creating a particular meeting
1. <t test>:traffic_light:</t>
   Document the meeting creation process
1. <t test>:traffic_light:</t>
   Document the meeting creation process

## <pr id="ucfai-docs" sub> AI@UCF's Documentation </pr>

### <t reqd>:key:</t> [](ucfai/bot#33)

**Description** Running a student organization is both time-consuming and
challenging. To ease this burden on future leaders, we should document our
processes and thoughts on particular matters that are bound to come up. (While
Discord is searchable, it's honestly not that great.) Some examples:

> 1. Comments from past presidents, directors, and coordinators
> 1. Guiding principles (especially concerned the focus of the club)
>    1. The people who run the group will change, but these fields are far from
>       fully researched
>    1. Things to consider when making decisions and summaries of past decisions
>       (as it's likely many things may come up througout AI@UCF's lifetime).

### <t reqd>:key:</t> Tasks

1. <t test>:traffic_light:</t>
   Document the process of creating a group's semester
1. <t test>:traffic_light:</t>
   Document the process of editing/creating a particular meeting
1. <t test>:traffic_light:</t>
   Document the meeting creation process
1. <t test>:traffic_light:</t>
   Document the meeting creation process

<br>

# <pr id="analytics"> Analytics Pipeline </pr>

[:arrow_up: Back to Projects](#projects)

**Overall Team:**
[@ionlights][gh-john]
[@sirroboto][gh-justin]

- [Data Aggregation and Analysis](#data-sci)

## <pr id="data-sci" sub> Data Aggregation and Analysis </pr>

### <t reqd>:key:</t> [](ucfai/bot#34) <t robot>:robot:</t>

**Description**

### <t reqd>:key:</t> Tasks

1. <t wips>:construction:</t>
   Ingest Card Reader Data
1. <t todo>:memo:</t>
   Query CECS <font color=red>(will have to wait until Spring 2020)</font>
1. <t wips>:construction:</t>
   Compute attendance point and distributional statistics

### <t nice>:ramen:</t> Tasks

1. Develop qualitative metrics that can be somewhat easily collected and reported

---

## Contributions

[:arrow_up: Back to Projects](#projects)

### Winter 2019 Development Team

<!-- Winter 2019 Development Team -->

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
|     |     |     |     |     |
|     |     |     |     |     |

[gh-john]: https://github.com/ionlights
[gh-justin]: https://github.com/sirroboto
[gh-anthony]: https://github.com/aehevia
[gh-brett]: https://github.com/
[gh-david]: https://github.com/
[gh-dillon]: https://github.com/
[gh-nick]: https://github.com/
[gh-kyle]: https://github.com/
[gh-freddy]: https://github.com/
[gh-brandon]: https://github.com/
