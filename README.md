# daml-canton-app

A full end-to-end Canton Network application — KYC identity management built with
Daml smart contracts, Canton JSON Ledger API, CompliDaml compliance audit, and a
live frontend dashboard.

[![Daml](https://img.shields.io/badge/Daml-3.4.0-blue)](https://docs.digitalasset.com/build/3.4/)
[![Canton](https://img.shields.io/badge/Canton-Network-orange)](https://canton.network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quick start

```bash
curl https://get.digitalasset.com/install/install.sh | sh
dpm build
dpm test
dpm sandbox
python api/canton_api.py
open frontend/dashboard.html
```

## GDPR compliance

| Article | Requirement | How satisfied |
|---|---|---|
| Art. 5(1)(c) | Data minimisation | Only necessary KYC fields stored |
| Art. 5(1)(f) | Confidentiality | Observer model — only bank + customer see PII |
| Art. 17 | Right to erasure | Archive choice allows contract deletion |
| Art. 25 | Privacy by design | Privacy is structural, not bolted on |
