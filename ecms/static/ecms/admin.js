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
    // Init all parts. Ordering shouldn't matter that much.
    ecms_data.init();
    ecms_tabs.init();
    ecms_layouts.init();
    ecms_plugins.init();

    // Final init call, that really needs to happen last.
    ecms_plugins.post_init();

    // Starting editor
    console.log("Initialized editor, regions=", regions, " itemtypes=", ecms_data.itemtypes, " initial_values=", ecms_data.initial_values);
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( (arguments[0] || '') + this.selector, this ); return this; };
  }


})(window.jQuery || django.jQuery);
