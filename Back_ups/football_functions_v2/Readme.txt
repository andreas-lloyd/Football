All functions have pretty ambiguous names - the definition comes from where they are loaded (e.g. suburls scrape_urls just scrapes suburls)

In generic functions we have functions that are used at various points in the process

In specific functions we have functions that vary depending on the source - but the functions within are relatively similar

### TO ADD ###
Have to confirm the imports in the specific functions

Proper error reproting / where it should be

Fix the dates so that the default is today but modifiable

Maybe change base and suburls to just work with "organ loc"

### TO CONFIRM ###
Could include the scrape_url part as in generic - feeding in the mode etc.
	Only thing I don't like is that we get from file one place and directories another

Thinking of also including a "processes" section where we can save the pipeline processes that will be used in the "grand script" at the end

This would be thinks like "get_sublinks" etc.

I think in the main script we should define all paths etc. - then feed those paths in and do all data loading in functions (i.e. to keep things local)