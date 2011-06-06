var ecms_layouts = {};

(function($)
{
  var ajax_root = location.href.substring(0, location.href.indexOf('/cmsobject/') + 11);


  /**
   * Initialize this component,
   * bind events and select the first option if there is only one.
   */
  ecms_layouts.init = function()
  {
    var layout_selector = $("#id_layout");
    ecms_layouts._select_single_option( layout_selector );
    layout_selector.change( ecms_layouts.onLayoutChange );
  }


  ecms_layouts.fetch_layout_on_refresh = function()
  {
    var layout_selector = $("#id_layout");

    // Place items in tabs
    var selected_layout_id = layout_selector.val() || 0;
    if( selected_layout_id != ecms_data.initial_values.layout_id )
    {
      // At Firefox refresh, the form field value was restored,
      // Update the DOM content by fetching the data.
      ecms_tabs.hide();
      layout_selector.change();
      return true;
    }

    return false;
  }


  /**
   * If a selectbox has only one choice, enable it.
   */
  ecms_layouts._select_single_option = function(selectbox)
  {
    var options = selectbox[0].options;
    if( ( options.length == 1 )
     || ( options.length == 2 && options[0].value == "" ) )
    {
      selectbox.val( options[ options.length - 1 ].value );
    }
  }


  /**
   * The layout has changed.
   */
  ecms_layouts.onLayoutChange = function(event)
  {
    var layout_id = this.value;
    if( ! layout_id )
    {
      ecms_tabs.hide(true);
      return;
    }

    // Disable content
    ecms_tabs.hide_all_tabs();

    if( event.originalEvent )
    {
      // Real change event, no manual invocation
      ecms_tabs.show(true);
    }

    ecms_layouts.fetch_layout(layout_id);
  }


  ecms_layouts.fetch_layout = function(layout_id)
  {
    // Get layout info.
    $.ajax({
      url: ajax_root + "get_layout/" + layout_id + "/",
      success: ecms_layouts._onReceivedLayout,
      dataType: 'json',
      error: function(xhr, textStatus, ex) { alert("Internal ECMS error: failed to fetch layout data!"); }    // can't yet rely on $.ajaxError
    })
  }


  ecms_layouts._onReceivedLayout = function(layout, textStatus, xhr)
  {
    ecms_tabs.load_layout(layout);
  }

})(window.jQuery || django.jQuery);
