from fluent_pages.admin import HtmlPageAdmin


class FlatPageAdmin(HtmlPageAdmin):
    pass

    # Implicitly loaded:
    #change_form_template = "admin/fluent_pages/pagetypes/flatpage/change_form.html"
    # Not defined here explicitly, so other templates can override this function.
    # and use {% extends default_change_form_template %} instead.
