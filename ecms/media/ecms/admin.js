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

  var ajax_root = location.href.substring(0, location.href.indexOf('/cmsobject/') + 11);

  // Public functions
  var regions   = [];   // [ 'main', 'sidebar', .. ]
  var formsets  = [];   // [ { name: "somename_set, auto_id: "id_%s" }, .. ]
  window.ecms_admin = {
    'setRegions':  function(data) { regions   = data; }
  , 'setFormSets': function(data) { formsets  = data; }
  }

  var dom_formsets = {};  // { tab: DOM, items: [ item1, item2 ] }


  /**
   * Main init code
   */
  function onReady()
  {
    // Bind events
    $("#ecms-tabnav a").click( onTabClick );

    // Read DOM data
    read_dom_formsets();

    // Set layout
    var layout_selector = $("#id_layout");
    layout_selector.change( onLayoutChange );

    if( layout_selector.val() != 0
     && $("#ecms-tabbar").is(":hidden"))
    {
      // At firefox refresh, the form field value was restored,
      // so make sure the state is in sync.
      layout_selector.change();
    }
    else
    {
      organize_formset_items();
    }
  }


  function read_dom_formsets()
  {
    var formsets = $("#inlines > div[id$=_set]");
    var items = formsets.children("div:not(.header)");
    for(var i = 0; i < items.length; i++)
    {
      var item = items.eq(i);

      // Get inputs
      var inputs         = item.find("input");
      var input_region   = inputs.filter("[name$=-region]").addClass("ecms-input-region");
      var input_ordering = inputs.filter("input[name$=-ordering]").addClass("ecms-input-ordering");
      var region   = input_region.val();
      var ordering = input_ordering.val();

      // Create administration for first item.
      if(! dom_formsets[region])
      {
        dom_formsets[region] = {
          key:            region
        , input_region:   input_region
        , input_ordering: input_ordering
        , items:          []
        };
      }

      // Append item to administration
      if(!dom_formsets[region].items[ordering])
        dom_formsets[region].items[ordering] = item;
    }
  }


  function organize_formset_items()
  {
    // Move all items to the tabs.
    for(var region_id in dom_formsets)
    {
      region = dom_formsets[region_id];

      // Use orphaned tab for separate content.
      var tab = $("#tab-region-" + region);
      if( tab.length == 0 )
      {
        // Find a different tab, based on the role.
        // This role exists to assist in migrations.


        // Fallback to special tab for orphans
        $("#ecms-tabnav-orphaned").css("display", "inline");
        tab = $("#tab-orphaned");
      }

      // Move items to tab
      if( region.items.length > 0 )
      {
        tab.children(".ecms-region-empty").hide();
        for(var ordering in region.items)
        {
          var item = region.items[ordering];
          tab.append( item.remove() );
        }
      }
    }
  }


  /**
   * The layout has changed.
   */
  function onLayoutChange(event)
  {
    var layout = this.value;
    if( ! layout )
    {
      $("#ecms-tabbar").slideUp();
      return;
    }

    if( event.originalEvent )
    {
      // Real change event
      $("#ecms-tabbar").slideDown();
    }
    else
    {
      // Manual invocation, to restore at refresh
      $("#ecms-tabbar").show();
    }

    // Invalidate tabs
    $("#ecms-tabnav-loading").show();
    $("#ecms-tabnav-orphaned").hide();
    $("#ecms-tabnav > li.ecms-region").remove();
    $("#ecms-tabmain > .ecms-region-tab").remove();

    // Get layout info.
    $.ajax({
      url: ajax_root + "get_layout/" + this.value + "/",
      success: onReceivedLayout,
      dataType: 'json',
      error: function(xhr, textStatus, ex) { alert("Internal ECMS error: failed to fetch layout data!"); }    // can't yet rely on $.ajaxError
    })
  }


  function onReceivedLayout(layout, textStatus, xhr)
  {
    /*
     layout = {id, key, title, regions: [{key, title}, ..]}
    */

    // Hide loading
    var loading_tab = $("#ecms-tabnav-loading").hide();
    var tabnav  = $("#ecms-tabnav");
    var tabmain = $("#ecms-tabmain");

    // Deal with invalid layouts
    if( layout == null )
    {
      alert("Error: no layout information available!");
      return;
    }

    // Cache globally
    regions = layout.regions;

    // Create the appropriate tabs for the regions.
    for( var i = 0, len = regions.length; i < len; i++ )
    {
      var region = regions[i];
      loading_tab.before( $('<li class="ecms-region"><a href="#tab-region-' + region.key + '">' + region.title + '</a></li>') );
      tabmain.append( $('<div class="ecms-tab ecms-region-tab" id="tab-region-' + region.key + '"></div>') );
    }

    // Rebind event
    var tab_links = $("#ecms-tabnav > li.ecms-region > a");
    tab_links.click( onTabClick );

    // Migrate formset items.
    organize_formset_items();

    // Activate first if none active.
    // Put after organize, so orphans tab might be visible
    if( $("#ecms-tabnav > li.active:visible").length == 0 )
      tab_links.eq(0).click();
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

    var activePane = panes.filter("#" + active);

    panes.hide();
    activePane.show();
    nav.removeClass("active");
    thisnav.addClass("active");

    // Auto focus on first editor.
    var firstField = activePane.find(".yui-editor-editable-container:first > iframe, .form-row :input:first").eq(0);
    firstField.focus();
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( this.selector, this ); return this; };
  }

})(django.jQuery);
