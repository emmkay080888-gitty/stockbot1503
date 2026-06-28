# Custom Sounds for StockBot

Place your custom sound files here to override the generated sounds.

## File Names

| File           | When it plays            |
|----------------|--------------------------|
| `chime.mp3`    | First interaction / page open |
| `click.mp3`    | Every button/link click   |

## Supported Formats

- `.mp3` (preferred — smallest size)
- `.wav` (better quality, larger files)
- `.ogg` (open format)

## How It Works

1. Place your `.mp3` files in this folder
2. Restart the Streamlit app
3. The app automatically detects and uses your custom sounds

If no custom files are found, the app falls back to programmatically generated sounds (no files needed).

## Tips

- Keep sounds short (under 2 seconds) for responsive feedback
- Chime should feel like a welcome/notification sound
- Click should be a subtle, short tap/pop sound
- Lower volume files work best (the app doesn't apply gain adjustment to custom files)
