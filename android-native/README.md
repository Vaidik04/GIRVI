# Girvi Native Android (No Python/Flask)

This folder contains a **native Android implementation** of the Girvi workflow in Kotlin using:
- Jetpack Compose UI
- Room local database
- MVVM + StateFlow

## What this replaces
- No Python
- No Flask server
- No external API required for basic usage

## Included workflows
- Add customers
- Create loan transactions
- Track dashboard totals (active loan amount and recovered amount)

## Open in Android Studio
1. Open Android Studio.
2. Select `android-native` as the project root.
3. Let Gradle sync.
4. Run on emulator/device.

## Notes
- This is an offline-first foundation mirroring core entities from the Flask app (`Customer`, `Loan`, `Payment`).
- You can extend this with authentication, photo capture, reminders, exports, and cloud sync.
