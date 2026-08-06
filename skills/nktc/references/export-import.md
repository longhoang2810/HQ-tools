# Export/import NKTC skill to another Hermes agent

Use this when the user asks to export `nktc` for another agent or another Hermes profile.

## Create a portable archive

```bash
EXPORT_ROOT="$HOME/Desktop/nktc-skill-export"
rm -rf "$EXPORT_ROOT" "$HOME/Desktop/nktc-skill-export.tar.gz"
mkdir -p "$EXPORT_ROOT"
cp -R "$HOME/.hermes/skills/productivity/nktc" "$EXPORT_ROOT/nktc"
cat > "$EXPORT_ROOT/IMPORT.md" <<'EOF'
# Import NKTC skill

## Default Hermes profile
mkdir -p ~/.hermes/skills/productivity
cp -R nktc ~/.hermes/skills/productivity/nktc

## Named Hermes profile
mkdir -p ~/.hermes/profiles/<profile>/skills/productivity
cp -R nktc ~/.hermes/profiles/<profile>/skills/productivity/nktc

## Verify
hermes skills list | grep nktc
EOF
cd "$EXPORT_ROOT"
tar -czf "$HOME/Desktop/nktc-skill-export.tar.gz" nktc IMPORT.md
```

Expected output archive:

```text
~/Desktop/nktc-skill-export.tar.gz
```

## Upload/share notes

- If the user asks to upload to Google Drive, first use the Google Workspace skill auth check. If not authenticated, either guide OAuth setup or place the archive in the local Google Drive Desktop folder if mounted.
- Do not include customs source data, generated reports, or user files in the skill export archive. The archive should contain only the reusable skill files (`SKILL.md`, `scripts/`, references/templates if any) and `IMPORT.md`.
- Never include secrets, tokens, local OAuth files, or profile memories in the archive.
