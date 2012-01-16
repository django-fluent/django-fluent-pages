/*
    Quick Fix for Django Ticket #11163
    http://code.djangoproject.com/ticket/11163
*/


(function($)
{
  $.fn.ready( function() {
    $('a.related-lookup').each( function() {
      var script_prefix = location.pathname.substring(0, location.pathname.indexOf('/admin'));
      this.href = this.href.replace('../../..', script_prefix + '/admin').replace('fluent_pages/urlnode', 'fluent_pages/page');
    });
  });
})(window.jQuery || django.jQuery);
