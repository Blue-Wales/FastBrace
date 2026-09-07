# Configuration Management Design Guide

This document describes how configuration is organized in `infrastructure/config/` and why YAML was chosen over other configuration formats.

## Directory Contents

| File                 | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| `settings.dev.yaml`  | Development environment configuration, safe to commit to the repository  |
| `settings.prod.yaml` | Production configuration skeleton; sensitive items must be injected via environment variables |



## Why YAML?



#### Compared with Hardcoded Constants/Config Classes

YAML separates configuration from code: the same codebase just loads a different environment's YAML file to switch, and changing configuration requires no code changes.

- **Configuration coupled to code**: changing configuration means changing code and redeploying; "adjust at deploy time" is impossible;
- **No per-environment differentiation**: development, testing, and production share one set of values, with no per-environment switching;
- **Cannot evolve**: adding configuration items requires repeated changes to the code structure.





#### Compared with Environment Variables (env)

Environment variables are well suited to **injecting secret-type sensitive items** (passwords, tokens, private keys), but not suited to carrying all configuration:

- **Poor readability**: as the business grows and configuration items multiply, environment variables cannot be organized structurally;
- **No nesting support**: grouped configuration such as JWT, database, and email can hardly express hierarchical relationships;
- **No typing or validation**: string-to-int/bool conversion must be handled manually.



