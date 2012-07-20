/*
    Quick Fix for Django Ticket #11163, needed for Django 1.3
    http://code.djangoproject.com/ticket/11163
*/


(function($)
{
  $.fn.ready( function() {
    $('a.related-lookup').each(function() {
      var script_prefix = location.pathname.substring(0, location.pathname.indexOf('/admin'));
      this.href = this.href.replace('../../..', script_prefix + '/admin');
    });
  });
})(window.jQuery || django.jQuery);
