
# [Latest paper version (Work in progress)](https://github.com/morganrivers/latex-github-collab/blob/previews/master/paper.pdf)
[![CI](https://github.com/morganrivers/latex-github-collab/actions/workflows/CI.yml/badge.svg)](https://github.com/morganrivers/latex-github-collab/actions/workflows/CI.yml) [[__View Paper Preview__](https://github.com/morganrivers/latex-github-collab/blob/previews/master/paper.pdf)]

## What's the deal with this repository?
The point of this repository is to provide the latest version of my LaTeX papers to anyone who's interested. I'm trying to get better at putting my ideas and work out there in the world, and this is my current strategy. It's a form of [perpetual beta](https://en.wikipedia.org/wiki/Perpetual_beta).

This repository is a copy of the [original latex-github-collab github template](https://github.com/LKedward/latex-github-collab) by Laurence Kedward, which is a github actions workflow based tool to render LaTeX documents on every push to the main branch.

# DELETE INSTRUCTIONS BELOW AFTER CLONING THIS TEMPLATE
Steps to clone:
1. Fix the README.md paper links, CI.yml link, and SVG badge.
   - In the raw markdown for this README.md, there are several `https://github.com/` links. One is a url for the svg badge (a `![CI]` and then a github url), two are links for a `paper.pdf`, and one link is for a `CI.yml`.
   - Change `morganrivers/latex-github-collab` in those links to whatever your username and repository name is.
2. Allow github actions to make pdfs in this repository.
   - Navigate to Settings -> Actions -> general in the github menu above, scroll down to find "Workflow permissions" section.
   - Select the option that says: "Read and write permissions    Workflows have read and write permissions in the repository for all scopes."
   - This is necessary for the github actions to write the paper pdf to the previews branch.
