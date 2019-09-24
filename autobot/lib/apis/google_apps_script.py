from autobot.meta.group import Group

# TODO: this needs to use the Google Apps API as denoted here:
# - https://developers.google.com/apps-script/reference/forms/
# - https://developers.google.com/apps-script/api/quickstart/python
# there _is_ an email account for the bot - just let @ionlights know what needs
#   to be generated and point to steps on how to do; will get the response back
#   to you fairly soon


def create_signup_form(grp: Group):
    """This creates the initial sign-up form, which needs to be filled out
    every semester, as we're opting to **_not_** keep a database of any
    sort.
    """
    # make sure you take a look at form validation and just leave comments
    #   in the code about how to add that in - @ionlights will do a final
    #   pass and make said validation
    # copy-pasta any auxiliary text from the existing form:
    # - https://docs.google.com/forms/d/e/1FAIpQLSdZ5ZZ49gUaDD2LbvRMuRgx3_AscFTWHpWDDuQOISTC1MnwIg/viewform
    # - !! ignore the question regarding keys
    # - TODO: add a single-line-text for Shibboleth ID
    raise NotImplementedError()


def create_signout_form(grp: Group):
    """This creates the form to be used at every meeting; we have students
    log their attendance by signing out, as well as giving us
    pseudo-immediate feedback on lecture quality.
    """
    # copy-pasta auxiliary text from the existing form:
    # - https://docs.google.com/forms/d/e/1FAIpQLSeJ9t0I30GbNBQ4OMGRSMYjH0GshVSlbLyBsLV1dbEzGkis6w/viewform
    # - TODO: add a parapgraph text which questions what they've learned
    # - TODO: rework "How'd you hear..." to be a bit more concise for them, while remaining informative for us
    raise NotImplementedError()
