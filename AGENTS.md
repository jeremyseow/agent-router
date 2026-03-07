# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

The rules specified here is to guide you in implementing the user's requirement based on various principles and guidelines. This helps to achieve consistency and reliability as LLMs tend to be probabilistic. Also, refer to industry standards and best practices when making any changes.

## Operating Principles

**1. Check for codebase first**
- Before writing new code, check if the existing functionality already exists. If it does, use it or possibly refactor it.
- When interacting with libraries, frameworks, or APIs, find or ask user for link to documentations and understand them before implementing.
- run `uv sync` to sync dependencies.

**2. Incremental changes**
- For big changes, don't try to implement everything in one go.
- Make small incremental changes and test after each change.
- This helps to catch errors early and makes it easier to debug.

**3. Self-anneal when things break**
- Read error message and stack trace
- Fix the code and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the documentation with what you learned (API limits, timing, edge cases). Whenever you encounter an error, refer to this document and if the same issue has occurred before, and try the attempted solution.
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite code to accommodate → test → update documentation.

**4. Update documentation as you learn**
- Documentation are living documents. When you discover architectural issues, API constraints, better approaches, common errors, or timing expectations—update the documentation. But don't create or overwrite documentation without asking unless explicitly told to. Documentation are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded). 

**5. Update the README.md and ensure that it is up to date and consistent with the codebase**
- Maintain a README.md with high level architecture diagram of the system. This should be a technical document that explains the system in detail. 
- Explain design choices and trade-offs in the documentation. 
- Give a quick overview of the project struture and what goes where.
- Quick start guide for setting up the project locally and how to test or run it.


## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the code
3. Test the code, make sure it works
4. Update the documentation
5. System is now stronger

## File Organization

**Directory structure:**
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `docs/` - documentation on the design of the service. logs of issues and bugs, root cause, and solutions.
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)
iverables live in cloud services (Google Sheets, Slides, etc.) where the user can access them. Everything in `.tmp/` can be deleted and regenerated.
- `README.md` - High level overview of the project. Include sequence diagrams of various flows, or any other diagrams that would help understand the system. Explain design choices and trade-offs in the documentation. Give a quick overview of the project struture and what goes where.

## Summary

You sit between human intent and execution. Take instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.


