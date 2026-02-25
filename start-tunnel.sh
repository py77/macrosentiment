#!/bin/bash
# Starts a Cloudflare quick tunnel exposing the backend on port 8002.
# The tunnel URL changes each restart — update Vercel env var after:
#   cd frontend && npx vercel env rm VITE_API_URL production -y
#   echo "<NEW_URL>" | npx vercel env add VITE_API_URL production
#   npx vercel --prod --yes

"/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel --url http://localhost:8002
