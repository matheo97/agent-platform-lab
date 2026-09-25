# Architecture notes

Short ADRs will land here as modules ship.

## Intent

`agent-platform-lab` is a modular portfolio monorepo. Each `modules/NN-*` directory is independently runnable when marked **done**, and later modules may compose earlier ones.

## Non-goals

- Chatbot / RAG showcase as the primary artifact
- Paid cloud dependency for the happy path
- Shipping personal Obsidian vaults or employer data
