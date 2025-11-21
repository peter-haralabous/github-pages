# allauth email templates

https://docs.allauth.org/en/latest/common/email.html

override subject & message body by creating files here that override the defaults.

if there's only a `.txt` template provided, we'll interpret it as Markdown and wrap it in our HTML email wrapper.
for a fully custom email, create a `.html` template instead.
