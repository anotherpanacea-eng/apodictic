# Privacy Policy

APODICTIC is a skills-based plugin that runs inside the host you use, such as Claude Code,
Cowork, Codex, or a supported ChatGPT workspace. This policy covers the plugin itself.
Your host provider's terms and privacy policy govern content you share with that host.

## What the plugin collects

Nothing. The plugin's author runs no server for it, receives no data from it, and includes no
analytics, telemetry, or tracking.

## Where your files go

The plugin reads the manuscript and notes you point it at, and writes its reports (editorial letters,
audit findings, run logs) into your host's project workspace when file tools are available.
That workspace may be on your machine or hosted by your provider. The plugin does not send
manuscripts or reports to its author. Your host processes the content you share under its
own terms and may store uploaded files and generated artifacts. Saved-project workflows
require persistent workspace support; the plugin does not provide a storage service.

## Network requests

Most workflows make no network requests. The research and citation-checking modes query public
scholarly services to look up sources:
Crossref, OpenAlex, Semantic Scholar, Unpaywall, CORE, PubMed (NCBI), and the Internet Archive's
Wayback Machine. A lookup sends what that service needs to answer it: a DOI, a title and author, a
short search query, or a URL to check. These modes also send a contact email in the request header.
That is a placeholder address unless you set `CROSSREF_MAILTO` or `OPENALEX_MAILTO`. If you set
`S2_API_KEY`, that key is sent only to Semantic Scholar, which issues it. Each service's own privacy
policy applies to the requests it receives.

Some research modes also ask the host to search or fetch web pages with its own web tools. Those
requests go through your host and follow its permission settings.

## Contact

Questions or concerns: open an issue at
https://github.com/anotherpanacea-eng/apodictic/issues.
