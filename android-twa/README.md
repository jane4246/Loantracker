# Android APK wrapper for LoanTrack Demo

## Before you start

Deploy the PWA version of LoanTrack to Render. Confirm the app opens correctly in Chrome on Android and that Chrome offers **Install app** or **Add to Home screen**.

## Create a test APK with Bubblewrap

1. Install Node.js, Java and Android command-line tools on a development computer.
2. Install Bubblewrap: `npm install -g @bubblewrap/cli`
3. Replace every `YOUR-LOANTRACK-URL` value in `twa-manifest.json` with your Render subdomain, without `https://`.
4. From this `android-twa` folder run: `bubblewrap init --manifest https://YOUR-LOANTRACK-URL.onrender.com/static/manifest.webmanifest`
5. Keep the generated signing key safe. Build the APK: `bubblewrap build`
6. Install the generated `app-release-signed.apk` on your own Android phone for testing.

## Make it full-screen

After Bubblewrap creates the signed APK, obtain its SHA-256 signing-certificate fingerprint. In the Render service environment, add:

```text
ANDROID_PACKAGE_NAME=com.yourname.loantrackdemo
ANDROID_SHA256_CERT_FINGERPRINT=YOUR_SHA256_FINGERPRINT
```

Redeploy Render. LoanTrack then publishes `/.well-known/assetlinks.json` dynamically. Android verifies the association between the APK and your Render site; only then can it open as a full-screen Trusted Web Activity. Until then, it may show as a normal browser tab, which is safe for testing.

This wrapper is for fictional-demo use only. Do not publish it under a bank name, logo or package identity without written authorization.
