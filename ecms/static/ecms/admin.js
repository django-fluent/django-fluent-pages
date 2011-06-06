/*
  Extra functions for the ECMS admin interface customisations
 */


(function($){

  $(document).ready( onReady );

  // Mark the document as JavaScript enabled.
  $(document.documentElement).addClass("ecms-jsenabled");

  // Make debugging possible.
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub};

  // Speed up IE 6, fix background image flickering
  try { document.execCommand("BackgroundImageCache", false, true); }
  catch(exception) {}


  // -------- Init code ------

  /**
   * Main init code
   */
  function onReady()
  {
    // Init all parts. Ordering shouldn't matter that much.
    ecms_data.init();
    ecms_tabs.init();
    ecms_layouts.init();
    ecms_plugins. init();

    // Final init call, that really needs to happen last.
    ecms_plugins.post_init();

    // Starting editor
    console.log("Initialized editor, regions=", regions, " itemtypes=", ecms_data.itemtypes, " initial_values=", ecms_data.initial_values);
  }


  // -------- Organizing items in tabs ------

  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( (arguments[0] || '') + this.selector, this ); return this; };
  }

  /**
   * jQuery outerHTML plugin
   * Very simple, and incomplete - but sufficient for here.
   */
  $.fn.get_outerHtml = function( html )
  {
    if( this.length )
    {
      if( this[0].outerHTML )
        return this[0].outerHTML;
      else
        return $("<div>").append( this.clone() ).html();
    }
  }

})(window.jQuery || django.jQuery);
