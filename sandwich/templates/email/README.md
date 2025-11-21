# email templates

We use [mjml](https://mjml.io/) to generate responsive email templates.

1. make changes to `base.mjml` (and update `base_no_cta.mjml` to match)
2. run `npx mjml base.mjml -o base.html && npx mjml base_no_cta.mjml -o base_no_cta.html`

see also [allauth email templates](../account/email/README.md), which use the same base templates.
