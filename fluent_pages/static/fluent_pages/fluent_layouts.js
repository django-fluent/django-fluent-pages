/**
 * This file deals with the high level layout switching / fetching layout info.
 * When a new layout is fetched, it is passed to the cp_tabs to rebuild the tabs.
 */
var fluent_layouts = {};

(function($)
{
  var ajax_root = location.href.substring(0, location.href.indexOf('/fluent_pages/page/') + 19);
  var initial_layout_id = null;


  /**
   * Initialize this component,
   * bind events and select the first option if there is only one.
   */
  fluent_layouts.init = function(real_initial_layout_id)
  {
    var layout_selector = $("#id_layout");
    fluent_layouts._select_single_option( layout_selector );
    layout_selector.change( fluent_layouts.onLayoutChange );

    // Firefox will restore form values at refresh.
    // Know what the real initial value was.
    initial_layout_id = real_initial_layout_id
  }


  fluent_layouts.fetch_layout_on_refresh = function()
  {
    var layout_selector = $("#id_layout");

    // Place items in tabs
    var selected_layout_id = layout_selector.val() || 0;
    if( selected_layout_id != initial_layout_id )
    {
      // At Firefox refresh, the form field value was restored,
      // Update the DOM content by fetching the data.
      cp_tabs.hide();
      layout_selector.change();

      console.log("<select> box updated on load, fetching new layout; old=", initial_layout_id, "new=", selected_layout_id);
      return true;
    }

    return false;
  }


  /**
   * If a selectbox has only one choice, enable it.
   */
  fluent_layouts._select_single_option = function(selectbox)
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
  fluent_layouts.onLayoutChange = function(event)
  {
    var layout_id = this.value;
    if( ! layout_id )
    {
      cp_tabs.hide(true);
      return;
    }

    // Disable content
    cp_tabs.expire_all_tabs();

    if( event.originalEvent )
    {
      // Real change event, no manual invocation made above
      cp_tabs.show(true);
    }

    fluent_layouts.fetch_layout(layout_id);
  }


  fluent_layouts.fetch_layout = function(layout_id)
  {
    // Get layout info.
    $.ajax({
      url: ajax_root + "get_layout/" + parseInt(layout_id) + "/",
      success: function(layout, textStatus, xhr)
      {
        // Ask to update the tabs!
        cp_tabs.load_layout(layout);
      },
      dataType: 'json',
      error: function(xhr, textStatus, ex)
      {
        alert("Internal CMS error: failed to fetch layout data!");    // can't yet rely on $.ajaxError
      }
    })
  }

})(window.jQuery || django.jQuery);
