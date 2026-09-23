# HouseOFA1 Lookbook

Automated build of the HouseOFA1 catalogue. Every day at 05:00 UTC the workflow in
`.github/workflows/update.yml` re-scrapes the source store, rebuilds the catalogue with
stable product codes (`tools/codes.json`), encrypts it with the access code and deploys it
to Netlify. Run it by hand from the Actions tab with "Run workflow".

Secrets required: `ACCESS_CODE`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`.
