/*
  Extra functions for the ECMS admin interface customisations
 */


(function($){

  $(document).ready(onReady);

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
    $("#ecms-tabnav a").click( onTabClick );
  }


  /**
   * Tab button click
   */
  function onTabClick(event)
  {
    event.preventDefault();

    var nav   = $("#ecms-tabnav li");
    var panes = $("#ecms-tabmain .ecms-tab");
    var thisnav = $(event.target).parent("li");

    var href   = event.target.href;
    var active = href.substring( href.indexOf("#") );

    panes.hide().filter("#" + active).show();
    nav.removeClass("active");
    thisnav.addClass("active");
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( this.selector, this ); return this; };
  }



})(django.jQuery);
