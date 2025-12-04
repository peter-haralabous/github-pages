from sandwich.core.service.markdown_service import markdown_to_html


def test_markdown_to_html_default_works_and_is_safe():
    assert markdown_to_html("# Hello").strip() == "<h1>Hello</h1>"
    assert (
        markdown_to_html("[Click here](http://example.com)").strip()
        == """<p><a href="http://example.com">Click here</a></p>"""
    )
    assert (
        markdown_to_html("[Click here](javascript:alert('XSS-Attack'))").strip()
        == "<p>[Click here](javascript:alert('XSS-Attack'))</p>"
    )
