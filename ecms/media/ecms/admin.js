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

  // Global vars
  var dom_formsets = {};  // { tab: DOM, items: [ item1, item2 ] }
  var has_load_error = false;

  // Constants
  var REGION_ROLE_MAIN = 'm';
  var REGION_ROLE_SIDEBAR = 's';
  var REGION_ROLE_RELATED = 'r';


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

    // Select default layout of there is only one.
    var options = layout_selector[0].options;
    if( ( options.length == 0 )
     || ( options.length == 2 && options[0].value == "" ) )
    {
      layout_selector.val( options[ options.length - 1 ] .value );
    }

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
      var inputs   = item.find("input");
      var region   = inputs.filter("[name$=-region]").addClass("ecms-input-region").val();;
      var ordering = inputs.filter("input[name$=-ordering]").addClass("ecms-input-ordering").val();

      // Create administration for first item.
      if(! dom_formsets[region])
      {
        dom_formsets[region] = {
          key:   region
        , items: []
        };
      }

      // Append item to administration
      if(!dom_formsets[region].items[ordering])
        dom_formsets[region].items[ordering] = item;
    }
  }


  function organize_formset_items()
  {
    // Get default region.
    var default_region_id = get_region(REGION_ROLE_MAIN, 1);
    var roles_seen = {};

    // Move all items to the tabs.
    for(var region_id in dom_formsets)
    {
      region = dom_formsets[region_id];

      if( region_id == '' )
      {
        region_id = default_region_id;
      }
      else
      {
        if(roles_seen[region_id] == null)
          roles_seen[region_id] = 1;
        else
          roles_seen[region_id]++;
      }

      // Use orphaned tab for separate content.
      var tab = $("#tab-region-" + region_id);
      if( tab.length == 0 )
      {
        // Find a different tab, based on the role.
        // This role exists to assist in migrations.
        fallback_region_id = get_region(region.role || REGION_ROLE_MAIN, roles_seen[region.key]);
        if( fallback_region_id )
        {
          tab = $("#tab-region-" + fallback_region_id);
          region_id = fallback_region_id;
        }

        if( tab.length == 0 )
        {
          // Fallback to special tab for orphans
          $("#ecms-tabnav-orphaned").css("display", "inline");
          tab = $("#tab-orphaned");
        }
      }

      // Move items to tab
      if( region.items.length > 0 )
      {
        tab.children(".ecms-region-empty").hide();

        // Move all items to that tab.
        // Restore item values upon restoring fields.
        for(var ordering in region.items)
        {
          var item   = region.items[ordering];
          var itemId = item.attr("id");

          // Remove the item.
          disable_wysiwyg(item);
          var values = get_input_values(item);
          tab.append( item.remove() );

          // Fetch the node reference as it was added to the DOM.
          item = tab.children("#" + itemId);
          region.items[ordering] = item;

          // Re-enable the item
          set_input_values(item, values);
          enable_wysiwyg(item);
        }
      }
    }

    // In case a previous set of tabs was invalidated,
    // they can be removed now. The sub items are migrated.
    cleanup_old_tabs();
  }


  /**
   * Find the desired region, including the preferred occurrence of it.
   */
  function get_region(role, preferredNr)
  {
    var candidate = null;
    var itemNr = 0;
    for(var i = 0; i < regions.length; i++)
    {
      var region = regions[i];
      if(region.role == role)
      {
        candidate = region.key;
        itemNr++;

        if( itemNr == preferredNr || !preferredNr )
          return candidate;
      }
    }

    return candidate;
  }


  function get_input_values(root)
  {
    var inputs = root.find(":input");
    var values = {};
    for(var i = 0; i < inputs.length; i++)
    {
      var input = inputs.eq(i);
      values[input.attr("name")] = input.val();
    }

    return values;
  }


  function set_input_values(root, values)
  {
    var inputs = root.find(":input");
    for(var i = 0; i < inputs.length; i++)
    {
      var input = inputs.eq(i);
      var value = values[input.attr("name")];
      if(value != null)
        input.val(value);
    }
  }

  function disable_wysiwyg(root)
  {
    var textareas = root.find("textarea.vLargeTextField").toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg_disable("e:" + textarea.name);
    }
  }

  function enable_wysiwyg(root)
  {
    var textareas = root.find("textarea.vLargeTextField");

    if( ! django_wysiwyg_is_loaded() )
    {
      if( ! has_load_error )
      {
        textareas.before("<p><em style='color:#cc3333'>Unable to load WYSIWYG editor, is the system connected to the Internet?</em></p>").show();
        has_load_error = true;
      }

      return;
    }

    textareas = textareas.toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg_enable("e:" + textarea.name, textarea.id);
    }
  }

  function invalidate_tabs()
  {
    // Invalidate tab titles
    $("#ecms-tabnav-loading").show();
    $("#ecms-tabnav-orphaned").hide();
    $("#ecms-tabnav > li.ecms-region").remove();

    var tabmain = $("#ecms-tabmain");
    var height = tabmain.height();
    if( height )
    {
      tabmain.css("height", height + "px");  // set fixed height to avoid scrollbar/footer flashing.
    }
    tabmain.children(".ecms-region-tab").removeClass("ecms-region-tab").addClass("ecms-region-oldtab").attr("id",null).hide();
  }

  function cleanup_old_tabs()
  {
    var tabmain = $("#ecms-tabmain");
    tabmain.children(".ecms-region-oldtab").remove();

    // After children height recalculations / wysiwyg initialisation, restore auto height.
    setTimeout( function() { tabmain.css("height", ''); }, 100 );
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

    // Disable content
    invalidate_tabs();

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
