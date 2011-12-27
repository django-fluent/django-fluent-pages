/**
 * Main setup for the ecms admin interface.
 */


(function($){

  $(document).ready( onReady );

  // Mark the document as JavaScript enabled.
  $(document.documentElement).addClass("ecms-jsenabled");

  // Speed up IE 6, fix background image flickering
  try { document.execCommand("BackgroundImageCache", false, true); }
  catch(exception) {}


  /**
   * Main init code
   */
  function onReady()
  {
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( (arguments[0] || '') + this.selector, this ); return this; };
  }


})(window.jQuery || django.jQuery);
