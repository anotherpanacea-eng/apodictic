# Privacy Policy

APODICTIC is a plugin that runs inside your own Claude client (Claude Code, Claude desktop, or another
host that loads it). This policy covers the plugin itself. Your use of Claude is covered by
Anthropic's own terms and privacy policy.

## What the plugin collects

Nothing. The plugin's author runs no server for it, receives no data from it, and includes no
analytics, telemetry, or tracking.

## Where your files go

The plugin reads the manuscript and notes you point it at, and writes its reports (editorial letters,
audit findings, run logs) into your project folder on your own machine. It does not upload them
anywhere. Claude reads the content you share with it in the usual way, under Anthropic's terms.

## Network requests

Most workflows make no network requests. The research and citation-checking modes query public
scholarly services to look up sources:
Crossref, OpenAlex, Semantic Scholar, Unpaywall, CORE, PubMed (NCBI), and the Internet Archive's
Wayback Machine. A lookup sends what that service needs to answer it: a DOI, a title and author, a
short search query, or a URL to check. These modes also send a contact email in the request header.
That is a placeholder address unless you set `CROSSREF_MAILTO` or `OPENALEX_MAILTO`. If you set
`S2_API_KEY`, that key is sent only to Semantic Scholar, which issues it. Each service's own privacy
policy applies to the requests it receives.

Some research modes also ask Claude to search or fetch web pages with its own web tools. Those
requests go through your Claude client and follow its permission settings.

## Contact

Questions or concerns: open an issue at
https://github.com/anotherpanacea-eng/apodictic/issues.
