#!/bin/bash
# Ensure newsroom git remote is configured. Run before any push.
cd "$(dirname "$0")"
git remote get-url origin 2>/dev/null || git remote add origin git@github.com:froogooofficial/newsroom.git
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_arlo -o IdentitiesOnly=yes"
